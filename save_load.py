import numpy as np
import sys
import os
import tools as t

EMPTY_ID = -1

def get_actorset():
    """
    Loads the data from 'actorset.txt' into an actoset array usable by the program.
    Also reads the OoT/MM version used by the program.
    """
    # Read from our actorset file
    if not os.path.exists('actorset.txt'):
        sys.exit("'actorset.txt' not found in directory!")
    f = open("actorset.txt", "r")
    
    # Read each line and process into expected string format:
    p_lines = []
    comma_idx = []
    for line in f:
        line_info = t.process_line(line)
        p_lines.append(line_info[0])
        comma_idx.append(line_info[1])
    f.close()
    
    # Go through the text to find the last step needed
    last_step = None
    for this_line in p_lines:
        if str.lower(this_line[:4]) == "step":
            if not len(this_line) > 4:
                sys.exit("Missing step number in 'actorset.txt'")
            elif last_step == None:
                last_step = int(this_line[4:])
            else:
                num = int(this_line[4:])
                if num > last_step:
                    last_step = num
    if last_step == None:
        sys.exit("Missing step number in 'actorset.txt'")         
         
    # Now initialise our actorset list
    acs = []
    for i in range(last_step+1):
        acs.append([])
    
    # Go through each line and add stuff to the actor set:
    this_step = None
    version = None
    for i in range(len(p_lines)):
        # Unpack this line's variables:
        this_line = p_lines[i]
        this_comma_idx = comma_idx[i]
        length = len(this_line)
        
        # If the line is empty, ignore it
        if length != 0:
            # Check for key phrases "version" and "step"
            if length > 7:
                if str.lower(this_line[:7]) == "version":
                    version = this_line[7:]
                elif str.lower(this_line[:4]) == "step":
                    this_step = int(this_line[4:])
            elif length > 4:
                if str.lower(this_line[:4]) == "step":
                    this_step = int(this_line[4:])            
            if len(this_comma_idx) > 1:
                sys.exit("More than one comma found in a line from 'actorset.txt'.")
                
            # Or, check if it's a line with 1 comma and values either side
            elif len(this_comma_idx) == 1:
                idx = this_comma_idx[0]
                if idx == 0 or idx == len(this_line) - 1:
                    sys.exit("Found comma at start or end of line in 'actorset.txt'.")
                elif this_step == None:
                    sys.exit("Actors in 'actorset.txt' listed before step number.")
                else:
                    # Unpack values either side of comma
                    actor_id = this_line[:idx] 
                    despawn = this_line[idx + 1:]
                    
                    # And append to our actor set
                    if np.size(acs[this_step]) == 0:
                        acs[this_step] = np.array([[int(actor_id,16),int(despawn)]])
                    else:
                        acs[this_step] = np.append(acs[this_step], np.array([[int(actor_id,16),int(despawn)]]),axis=0)
    return acs, version

def get_actorpool(acs):
    """
    Loads the data from 'actorpool.txt' into an actoset array usable by the program.
    Also reads key properties about the actors we're searching for.
    """
    # Read from our actorpool file
    if not os.path.exists('actorpool.txt'):
        sys.exit("'actorpool.txt' not found in directory!")
    
    # Open the text file and read all the lines.
    f = open("actorpool.txt", "r")
    # Read each line and process:
    p_lines = []
    comma_idx = []
    for line in f:
        line_info = t.process_line(line)
        p_lines.append(line_info[0])
        comma_idx.append(line_info[1])
    f.close()
    
    # We also want to get some other data out of this file:
    actor1_id = EMPTY_ID
    actor2_id = EMPTY_ID
    actor1_step = EMPTY_ID
    actor2_step = EMPTY_ID
    offset = EMPTY_ID
    
    # Get the actor number and the despawn timer.
    final_step = len(acs) - 1
    this_step = None
    actorpool = []
        
    # Go through each line and add stuff to the actor set:
    for i in range(len(p_lines)):
        this_line = p_lines[i]
        this_comma_idx = comma_idx[i]
        length = len(this_line)
        
        if length != 0:
            # Check for various keywords                    
            if length > 4:
                if str.lower(this_line[:4]) == "step":
                    this_step = int(this_line[4:]) 
                    if this_step > final_step:
                        print(this_step,final_step)
                        sys.exit("Referenced step number in 'actorpool.txt' isn't established in 'actorset.txt'.")
            if length > 6:
                if str.lower(this_line[:6]) == "offset":
                    offset = int(this_line[6:],16)
            if length > 9:
                if str.lower(this_line[:9]) == "actor1_id":
                    actor1_id = int(this_line[9:],16)
                elif str.lower(this_line[:9]) == "actor2_id":
                    actor2_id = int(this_line[9:],16)
            if length > 11:
                if str.lower(this_line[:11]) == "actor1_step":
                    actor1_step = int(this_line[11:])
                elif str.lower(this_line[:11]) == "actor2_step":
                    actor2_step = int(this_line[11:])
            
            # And check for actors to add to the pools:
            if len(this_comma_idx) > 2:
                sys.exit("More than three arguments found in a line in 'actorpool.txt'.")                
            elif len(this_comma_idx) == 1 or len(this_comma_idx) == 2:
                idx = this_comma_idx[0]
                if idx == 0 or idx == len(this_line) - 1:
                    sys.exit("Found comma at start or end of line in 'actorpool.txt'.")
                elif this_step == None:
                    sys.exit("Actors in 'actorpool.txt' listed before step number.")
                else:
                    actor_id = this_line[:idx]
                    if len(this_comma_idx) == 1:
                        despawn = this_line[idx+1:]
                        actorpool.append([this_step,int(actor_id,16),int(despawn),EMPTY_ID])
                    else:
                        if int(actor_id,16) != 0xF0:
                            sys.exit("Three arguments found in a line in 'actorpool.txt' which isn't blue fire.")
                        else:
                            idx1 = this_comma_idx[1]
                            despawn1 = this_line[idx+1:idx1]
                            despawn2 = this_line[idx1+1:]
                            actorpool.append([this_step,int(actor_id,16),int(despawn1),int(despawn2)])
        
    if len(actorpool) == 0:
        sys.exit("No actors have been given in 'actorpool.txt'.")
        
    return actorpool, actor1_id, actor2_id, actor1_step, actor2_step, offset


def save_actorset(acs,version):
    """
    save the given actorset to a file in "actorset_dump"
    """
    dir_path = 'actorset_dump'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    versions =[
        "OoT_NTSC_1.0",
        "OoT_NTSC_1.1",
        "OoT_NTSC_1.2",
        "OoT_PAL_1.0" ,
        "OoT_PAL_1.1" ,
        "OoT_U_GC"    ,
        "OoT_E_GC"    ,
        "OoT_J_GC"    ,
        "OoT_U_MQ"    ,
        "OoT_E_MQ"    ,
        "OoT_J_MQ"    ,
        "MM_J_1.0"    ,
        "MM_J_1.1"    ,
        "MM_U_1.0"    ,
        "MM_PAL_1.0"  ,
        "MM_PAL_1.1"  ,
        "MM_GC_J"     ,
        "MM_GC_U"     ,
        "MM_GC_E"     
    ]
   
    # Make folders if they don't exist
    for v in versions:
        if not os.path.exists(dir_path + '\\' + v):
            os.makedirs(dir_path + '\\' + v)
    
    path = None
    # Make folders if they don't exist
    for v in versions:
        if not os.path.exists(dir_path + '\\' + v):
            os.makedirs(dir_path + '\\' + v)
    
    # Get the version directory
    for v in versions:
        if str.lower(version) == str.lower(v):
            path = dir_path + '\\' + v
            break
        
    # Invalid version?
    if path == None:    
        sys.exit("No valid version has been given in 'actorset.txt'.")
    
    # The number to give the file will be the number of files in the directory at the time.
    file_num = len(os.listdir(str(path)))
    
    # Start writing the actor sets out
    with open(path + "\\actorset"+str(file_num)+".txt", 'w+') as the_file:
        the_file.write("version:" + version+"\n\n")
        for i in range(len(acs)):
            the_file.write("Step "+str(i)+"\n")
            for j in range(len(acs[i])):
                the_file.write(t.get_hex(acs[i][j,0],4) + "," + str(acs[i][j,1]) + "\n")
            the_file.write('\n')
    return