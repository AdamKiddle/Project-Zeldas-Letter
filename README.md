# Project-Zeldas-Letter
Python simulator for OoT and MM's actor heap. Finds solutions to heap-placement problems.<br/>

You will need Python 3 and the numpy module.

# User Guide
The simulator works by allocating and deallocating actors at a series of user-defined "steps". A step may correspond to loading a new room and unloading a previous one, destroying certain actors like enemies or bombs, or spawning extra actors such as bushes in bush circles or projectiles from a deku scrub. It's essentially how we break up the history of what happens in the heap.<br/>

# actorset.txt
The file "actorset.txt" contains the info about what actors are loaded at each step. It also contains the version you're currently using. Choose version from these strings (not case-sensitive):<br/>

* "OoT_NTSC_1.0"
* "OoT_NTSC_1.1"
* "OoT_NTSC_1.2"
* "OoT_PAL_1.0"
* "OoT_PAL_1.1"
* "OoT_U_GC"
* "OoT_E_GC"
* "OoT_J_GC"
* "OoT_U_MQ"
* "OoT_E_MQ"
* "OoT_J_MQ"
* "MM_J_1.0"
* "MM_J_1.1"
* "MM_U_1.0"
* "MM_PAL_1.0"
* "MM_PAL_1.1"
* "MM_GC_J"
* "MM_GC_U"
* "MM_GC_E"

Underneath the version, you can start listing what actors you want to spawn at each step. You can fetch these from the OoT and MM ultimate spreadsheets, under the "Actors by room" sheet. Be careful to vet these carefully, they do not contain room transition actors such as doors and load planes so these will need to be added manually. Some listed actors on the MM spreadsheet may not spawn during day or night so should be removed appropriately. The format for "actorset.txt" is:<br/>

``
STEP X
ACTOR_ID, DEALLOCATION_STEP
ACTOR_ID, DEALLOCATION_STEP # You can add comments with the hash symbol at any point
ACTOR_ID, DEALLOCATION_STEP
.
.

STEP Y
ACTOR_ID, DEALLOCATION_STEP
ACTOR_ID, DEALLOCATION_STEP
ACTOR_ID, DEALLOCATION_STEP
.
.

``
When the program reaches step X, actors listed under step X allocate into the heap. After this, any actors that had previously been allocated with a "deallocation step" X will deallocate. For a practical example, see "Examples" section.<br/>

# actorpool.txt
If you are trying to solve an SRM problem which requires a grabbed actor to be at some position relative to another actor, you would use the solution-finder mode which uses the "actorpool.txt" file along with "actorset.txt". "actorpool.txt" contains information about the grabbed actor, the actor which you want to SRM and lists of possible actors to inject into the sequence in order to achieve this. <br/>

The start of the file contains 5 variables:

*actor1_id - This is the actor ID of the grabbed actor
*actor2_id - This is the actor ID of the actor we wish to SRM
*actor1_step - This is the step at which to find the grabbed actor
*actor2_step - This is the step at which to find the actor we wish to SRM (usually the final step)
*offset - This is the desired offset between the grabbed actor and the SRM actor. Calculated as (actor2 memory position - actor1 memory position)

After this, we write the step that we want to inject actors at. Under each step we list the pool of actors that we want to inject from at that step.
``
STEP A
ACTOR_ID, DEALLOCATION_STEP
ACTOR_ID, DEALLOCATION_STEP
ACTOR_ID, DEALLOCATION_STEP
.
.

STEP Z 
ACTOR_ID, DEALLOCATION_STEP
ACTOR_ID, DEALLOCATION_STEP # You can add comments with the hash symbol at any point
ACTOR_ID, DEALLOCATION_STEP
.
.

``

The actors listed under each step are the "pools" of actors that the simulator can choose from. It may pick any number of actors from this pool and allocate them in any order during the relevant step. Or it may pick none at all. The actor placement is generated randomly each time the simulaton runs.<br/>

Note that if you list an actor pool at a particular step, that step in "actorset.txt" will be ignored. "actorpool.txt" has priority. See examples below in the "Examples" section.<br/>

# Main Program
You can run the software by running "PZL.py". PZL is a command-line program with two different modes. The first is heap-display and the second is solution-finder.<br/>

Heap-display can be reached by typing "heap". This runs the simulator through the list of steps in "actorset.txt", allocating and de-allocating actors at the correct steps as it goes. The contents of the heap at the end of each step is then printed to the console. This is a good way to make sure you've set up "actorset.txt" correctly for a given room as you can check the results against Spectrum.<br/>

Solution-finder mode uses "actorpool.txt" to inject random actors at a chosen step. Then, based on what you've chosen as "actor1" and "actor2", you can compare their relative positions in the heap. If the relative positions of actor1 and actor2 match the required offset, the actorset will be dumped to a file in actorset_dump. In this mode, the simulation will keep running forever, until you close python, dumping solution actorsets as it goes.

# Examples
TODO
