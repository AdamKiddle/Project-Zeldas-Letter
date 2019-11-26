# Project-Zeldas-Letter
Python simulator for OoT and MM's actor heap. Finds solutions to heap-placement problems.

# User Guide
The simulator works by allocating and deallocating actors at a series of user-defined "steps".
Edit "actorset.txt" to set the version and list the actors you want to allocate in at each step.

Format is:

STEP X
ACTOR_ID, DEALLOCATION_STEP
ACTOR_ID, DEALLOCATION_STEP
ACTOR_ID, DEALLOCATION_STEP

Actors with a deallocation step X will de-alloacte at the end of step X (after all the actors of that step have allocated).

# Display Heap
You can run "PZL.py" and type in "heap" to display the heap at the end of each step in "actorset.txt"

# Solution Finder
You can run "PZL.py" and press Enter to find solution.
This mode uses "actorpool.txt" to inject random actors at a chosen step (replacing whatever else was defined for that step in "actorset.txt". Then, based on what you've chosen as "actor1" and "actor2", you can compare their relative positions in the heap. You must set the variables at the top:

actor1_id = actor id
actor2_id =  actor id
actor1_step =  step at which to look this actor
actor2_step =  step at which to look for this actor
offset = (actor2 position memory location - actor1 memory location)

Then, by adding actors with deallocation timers to a step, you are creating your "pool" of available actors.
e.g.

step 0
0x0010, 3
0x00DA, 3
0x00DA, 3

In OoT this would mean your pool of actors contains 1 bomb and 2 chus. The simulator randomly picks actors from the pool and injects them into step 0. These would all de-allocate at the end of step 3.
