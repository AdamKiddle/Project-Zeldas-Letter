# Project-Zeldas-Letter
Python simulator for OoT and MM's actor heap. Finds solutions to heap-placement problems.<br/>

# User Guide
The simulator works by allocating and deallocating actors at a series of user-defined "steps".<br/>
Edit "actorset.txt" to set the version and list the actors you want to allocate in at each step.<br/><br/>

Format is:<br/><br/>

STEP X<br/>
ACTOR_ID, DEALLOCATION_STEP<br/>
ACTOR_ID, DEALLOCATION_STEP<br/>
ACTOR_ID, DEALLOCATION_STEP<br/><br/>

Actors with a deallocation step X will de-alloacte at the end of step X (after all the actors of that step have allocated).<br/><br/>

# Display Heap
You can run "PZL.py" and type in "heap" to display the heap at the end of each step in "actorset.txt"<br/><br/>

# Solution Finder
You can run "PZL.py" and press Enter to find solution.<br/>
This mode uses "actorpool.txt" to inject random actors at a chosen step (replacing whatever else was defined for that step in "actorset.txt". Then, based on what you've chosen as "actor1" and "actor2", you can compare their relative positions in the heap. You must set the variables at the top:<br/><br/>

actor1_id = actor id<br/>
actor2_id =  actor id<br/>
actor1_step =  step at which to look this actor<br/>
actor2_step =  step at which to look for this actor<br/>
offset = (actor2 position memory location - actor1 memory location)<br/><br/>

Then, by adding actors with deallocation timers to a step, you are creating your "pool" of available actors.<br/>
e.g.<br/><br/>

step 0<br/>
0x0010, 3<br/>
0x00DA, 3<br/>
0x00DA, 3<br/><br/>

In OoT this would mean your pool of actors contains 1 bomb and 2 chus. The simulator randomly picks actors from the pool and injects them into step 0. These would all de-allocate at the end of step 3.
