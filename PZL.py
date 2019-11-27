import numpy as np
import sys
from random import seed
seed()

import tools as t
import save_load as io

EMPTY_ID = -1
FILLER_ID = 10001
UNLIMITED = 0xFFFFF
ARR_SIZE = 10000

start_address = None 
node_size = None
bugs_id = None
bf_id = None
lookup = None

def place_next_node(nodes, prev_idx):
    # Work out the address of the new node:
    prev_address = nodes[prev_idx,0]
    offset = nodes[prev_idx,2]
    this_address = prev_address + node_size + offset
    
    # find where the next node was before:
    next_idx = nodes[prev_idx,5]

    # How much space will be between this node and the next node?
    if next_idx == -1:
        this_space = UNLIMITED
    else:       
        next_address = nodes[next_idx,0]
        this_space = next_address - (this_address + node_size)
    
    # Find the first available spot in the nodes array:
    this_idx = np.argwhere(nodes[:,0] == 0)[0,0]
    
    # write a node here:
    nodes[this_idx] = np.array([this_address,-1,this_space,-1,-1,next_idx])
    nodes[prev_idx,5] = this_idx
    return nodes

def allocate(nodes, actor_id, actor_type, size, dal_timer):
    
    # Find nodes who's next chunk of space is empty
    idx1 = nodes[:,1] == -1
    # Find nodes who's next chunk of space is big enough
    idx2 = nodes[:,2] >= size
    # Find nodes where both of these things are true:
    idx3 = np.logical_and(idx1,idx2)
    
    # The candidate node with the earliest address is where we will place it.
    nodes_copy = np.ones_like(nodes)*0xFFFFFF
    nodes_copy[idx3] = nodes[idx3]
    
    # Find the candidate node with the earliest address:
    node_idx = np.argmin(nodes_copy[:,0])
    
    # Update the node with some of the new info:
    nodes[node_idx,1] = actor_type
    nodes[node_idx,3] = actor_id
    nodes[node_idx,4] = dal_timer

    # If there's enough space to place a new node, do it:
    found_space = nodes[node_idx,2]
    
    if found_space > (size + node_size):
        # Set the size of the space after this node to be the size of the actor
        nodes[node_idx,2] = size
        # Now add the node on the end:
        nodes = place_next_node(nodes,node_idx)
    
    return nodes
        

def allocate_check(nodes, actor):
    # Unpack the actor info
    actor_id = actor[0]
    dal_timer = actor[1]
    
    
    # Get the relevant row in the actor lookup table:
    lookup_row = lookup[lookup[:,0] == actor_id]
    if np.size(lookup_row) == 0:
        sys.exit("Actor id "+t.get_hex(actor_id,4)+" is not a valid actor. Check 'actorset.txt' and 'actorset.txt' for typos.")
    lookup_row = lookup_row[0]
           
    # First we check if an overlay with this actor id exists in the heap yet:     
    if not np.any(np.logical_and(nodes[:,1] == 1, nodes[:,3] == actor_id)):
        # if the allocation type == 0, add it to the heap:
        if lookup_row[3] == 0:
            ovl_size = lookup_row[1]
            nodes = allocate(nodes, actor_id, 1, ovl_size, -1)
    
    # Now we allocate the instance:
    inst_size = lookup_row[2]
    nodes = allocate(nodes, actor_id, 2, inst_size, dal_timer)
    
    return nodes

def allocate_set(nodes,acset):
    # Allocate each actor as we go through the actor set:
    for j in range(len(acset)):
        nodes = allocate_check(nodes, acset[j])
        
    return nodes

def deallocate_instance(nodes,step):
    d_idx = nodes[:,4] == step
    nodes[d_idx,1] = -1
    nodes[d_idx,3] = -1
    nodes[d_idx,4] = -1
    return nodes

def deallocate_overlay(nodes):
    # Get all ids of all the overlays currently allocated
    overlay_ids = nodes[nodes[:,1] == 1,3]
    for i in range(len(overlay_ids)):
        # Find which nodes preceed this id
        id_nodes = nodes[:,3] == overlay_ids[i]
        # Find which nodes are instances:
        inst_nodes = nodes[:,1] == 2
        
        # If there aren't any instances with this id...
        if not np.any(np.logical_and(id_nodes,inst_nodes)):
            #... Then deallocate this overlay:
            d_idx = nodes[:,3] == overlay_ids[i]
            nodes[d_idx,1] = -1
            nodes[d_idx,3] = -1
            nodes[d_idx,4] = -1
            
    return nodes
    
def deallocate(nodes,step):
    # find all actors whose deallocation step has been reached and empty:
    nodes = deallocate_instance(nodes,step)
    
    # Find all overlays who exist without instances and empty:
    nodes = deallocate_overlay(nodes)
    
    # Finally, remove nodes that are "floating"
    this_idx = 0
    finished_dealocating = False
    
    while not finished_dealocating:
        next_idx = nodes[this_idx,5]
        # If the current node is the end node:
        if next_idx == -1:
            # Exit
            finished_dealocating = True
            break
        
        # If the next node is the end node:
        elif nodes[next_idx,5] == -1:
            # And if the current node is empty afterwards:
            if nodes[this_idx,1] == -1:    
                # Deallocate the next node.
                nodes[next_idx] = np.zeros(6)
                
                # And update the current one to be an end node.
                nodes[this_idx,1] = -1
                nodes[this_idx,2] = UNLIMITED
                nodes[this_idx,3] = -1
                nodes[this_idx,4] = -1
                nodes[this_idx,5] = -1
                
            finished_dealocating = True
            break
        
        # else if the space after this node and space after next node are both empty:
        elif np.logical_and(nodes[this_idx,1] == -1, nodes[next_idx,1] == -1):
            # Then prepare to delete the next node by updating this node's info:
            new_space = nodes[this_idx,2] + node_size + nodes[next_idx,2]
            new_next = nodes[next_idx,5]
            
            nodes[this_idx,2] = new_space
            nodes[this_idx,5] = new_next
            
            # And now actually delete the next node
            nodes[next_idx] = np.zeros(6)
        
        this_idx = next_idx
    return nodes

def display_heap(nodes,show_nodes = False):
    # Loop through until we've displayed all entities.
    this_idx = 0
    display_completed = False    
    while not display_completed:
        # Unpack properties about this node
        this_addr = nodes[this_idx,0]
        this_type = nodes[this_idx,1]
        this_id = nodes[this_idx,3]
        
        # Get the index of the next node
        next_idx = nodes[this_idx,5]
        
        # If we want to show nodes:
        if show_nodes:
            ad = ('0x{:06X}').format(this_addr)
            print(ad, "NODE", t.get_hex(nodes[this_idx,2],4))
        
        # If we're at the final node, stop:
        if next_idx == -1:
            display_completed = True
            break
        
        # If we're not at the final node, print the proceeding instance/ovl
        else:
            if this_type == 1:
                ad_str = ('0x{:06X}').format(this_addr + node_size)
                id_str = ('0x{:04X}').format(this_id)
                print(ad_str, id_str, "OVERLAY")
            elif this_type == 2:
                ad_str = ('0x{:06X}').format(this_addr + node_size)
                id_str = ('0x{:04X}').format(this_id)
                print(ad_str, id_str, "INSTANCE")

        # Prepare to proceed to next node
        this_idx = next_idx
    print()
    return
        
def get_location(nodes,actor_id):
    idx = np.logical_and(nodes[:,1] == 2, nodes[:,3] == actor_id)
    return nodes[idx,0]

def main(acs, show_heap = False, actor1_id = None, actor2_id = None, actor1_step = None, actor2_step = None):
    """
    Node should have: [
    0 Address, (if spot is unused/uninitialised, we use value 0)
    1 type of thing in next spot, (-1 = empty, 1 = overlay, 2 = instance)
    2 space in next spot (only matters if empty, UNLIMITED if unlimited space.),
    3 actor ID of thing in next spot (-1 if none)
    4 deallocation timer of the thing in next spot (-1 if anything other than an instance)
    5 index of the next node (-1 if there's no next node)
    ]
    """
    # First we make our nodes array:
    nodes = np.zeros([ARR_SIZE,6], dtype=int)
    # Place an immutable node at the start:
    nodes[0,:] = np.array([start_address,-1,UNLIMITED,-1,-1,-1])
    
    # Go through each actor set
    for i in range(len(acs)):
        
        # If it's not empty, allocate it
        if np.size(acs[i]) != 0:
            nodes = allocate_set(nodes,acs[i])
        
        # Now perform a deallocate step:
        nodes = deallocate(nodes,i)
        
        # Get the locations of desired actors
        if actor1_id != None:
            if i == actor1_step:
                actor1_pos = np.array(get_location(nodes,actor1_id))
            elif i == actor2_step:
                actor2_pos = np.array(get_location(nodes,actor2_id))
        
        if show_heap:
            print("step",i)
            display_heap(nodes)
    if actor1_id != None:
        return actor1_pos, actor2_pos
    else:
        return

def add_from_pool(this_acs,actor_id,timer):
    # Adds actors to the set.
    if np.size(this_acs) == 0:
        this_acs = np.array([[actor_id,timer]])
    else:
        this_acs = np.append(this_acs, np.array([[actor_id,timer]]),axis=0)
    return this_acs

def solution_finder(acset):
    # This is for modifying all the data randomly until we get a result that we want.
    acpool, actor1_id, actor2_id, actor1_step, actor2_step, offset = io.get_actorpool(acset)
    num_sets = len(acset)
                
    # Loop, keep finding solutions.
    while True:
        acs = acset
        acp = np.array(acpool)
        
        # For each step, see if we have actors in the pool
        for i in range(num_sets):
            this_acp = acp[acp[:,0] == i]
            num_actors = len(this_acp)
            # If we do,
            if num_actors != 0:
                # Empty the set
                acs[i] = np.array([[]])
                # Pick a random actors
                idx = t.pick_random(num_actors)
                actors = this_acp[idx]
                # Add each one to the actorset according to their rules.
                for j in range(len(actors)):
                    actor_id = actors[j,1]
                    timer1 = actors[j,2]
                    timer2 = actors[j,3]
                    if actor_id == bugs_id:
                        # Spawn 3 bugs:
                        for k in range(3):
                            acs[i] = add_from_pool(acs[i],actor_id,timer1)
                    elif actor_id == bf_id:
                        # Spawn 19 blue fire:
                        if timer2 == EMPTY_ID:
                            for k in range(19):
                                acs[i] = add_from_pool(acs[i],actor_id,timer1)
                        else:
                            acs[i] = add_from_pool(acs[i],actor_id,timer2)
                            for k in range(8):
                                acs[i] = add_from_pool(acs[i],actor_id,timer1)
                            for k in range(10):
                                acs[i] = add_from_pool(acs[i],actor_id,timer2)
                    else:
                        acs[i] = add_from_pool(acs[i],actor_id,timer1)
                    
        # Run the main simulation and get the positions of the deisred actors:
        actor1_pos, actor2_pos = main(acs,False,actor1_id, actor2_id,actor1_step, actor2_step)
        
        # Find if any of the sets of found actors are the desired offset away:
        POS1, POS2 = np.meshgrid(actor1_pos,actor2_pos)
        print(t.get_hex(actor1_pos),t.get_hex(actor2_pos))
        print(t.get_hex(actor2_pos - actor1_pos))
        print()
        if np.any(POS2 - POS1 == offset):
            print("SOLUTION FOUND")
            io.save_actorset(acs,version)

def version_setter(version):
    versions = [
        ["OoT_NTSC_1.0",0x30, 0x1E21E0],
        ["OoT_NTSC_1.1",0x30, 0x1E23A0],
        ["OoT_NTSC_1.2",0x30, 0x1E2AA0],
        ["OoT_PAL_1.0" ,0x30, 0x1E0220],
        ["OoT_PAL_1.1" ,0x30, 0x1E0260],
        ["OoT_U_GC"    ,0x10, 0x1E3360],
        ["OoT_E_GC"    ,0x10, 0x1E0AE0],
        ["OoT_J_GC"    ,0x10, 0x1E32E0],
        ["OoT_U_MQ"    ,0x10, 0x1E32A0],
        ["OoT_E_MQ"    ,0x10, 0x1E0AA0],
        ["OoT_J_MQ"    ,0x10, 0x1E32E0],
        ["MM_J_1.0"    ,0x30, 0x40b330],
        ["MM_J_1.1"    ,0x30, 0x40b670],
        ["MM_U_1.0"    ,0x10, 0x40B140],
        ["MM_PAL_1.0"  ,0x10, 0x4025E0],
        ["MM_PAL_1.1"  ,0x10, 0x402980],
        ["MM_GC_J"     ,0x10, 0x3A5870],
        ["MM_GC_U"     ,0x10, 0x3A5880],
        ["MM_GC_E"     ,0x10, 0x39D4D0],
        ]
    
    lookup_path = None
    found_version = False
    for i in range(len(versions)):
        if str.lower(version) == t.process_line(str.lower(versions[i][0]))[0]:
            found_version = True
            node_size = versions[i][1]
            start_address = versions[i][2]
            if str.lower(version)[:3] == "oot":
                bugs_id = 0x20
                bf_id = 0xF0
                lookup_path = "oot_actors.pzl"
            elif str.lower(version[:4]) == "mm_j":
                bugs_id = 0x16
                bf_id = -1
                lookup_path = "mmj_actors.pzl"
            else:
                bugs_id = 0x16
                bf_id = -1
                lookup_path = "mm_actors.pzl"
    if not found_version:
        sys.exit("No valid version has been given in 'actorset.txt'.")
                
    return lookup_path, node_size, bugs_id, bf_id, start_address 

to_exit = False
while not to_exit:
    print("Press enter to search for a solution using 'actorset.txt' and 'actorpool.txt'.")
    print("Type \"heap\" to display the results heap at each step of 'actorset.txt'")
    print("Type \"exit\" to exit.")
    search_mode = input()
    if str.lower(search_mode) == "exit":
        to_exit = True
    elif search_mode == str.lower("heap"):
        acs, version = io.get_actorset()
        lookup_path, node_size, bugs_id, bf_id, start_address = version_setter(version)
        if lookup_path == None:
            print("Invalid version in actorpool.txt")
        else:
            lookup = np.loadtxt(lookup_path, dtype='<U16', delimiter = ',',skiprows=1)
            lookup = np.vectorize(lambda x: int(x,16))(lookup)
            main(acs,True)
    else:
        acs, version = io.get_actorset()
        lookup_path, node_size, bugs_id, bf_id, start_address = version_setter(version)
        if lookup_path == None:
            print("Invalid version in actorpool.txt")
        else:
            lookup = np.loadtxt(lookup_path, dtype='<U16', delimiter = ',',skiprows=1)
            lookup = np.vectorize(lambda x: int(x,16))(lookup)
        solution_finder(acs)
