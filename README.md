# Project-Zeldas-Letter
Python simulator for OoT and MM's actor heap. Finds solutions to heap-placement problems.<br/>

You will need Python 3 and the numpy module.

# User Guide
The simulator works by allocating and deallocating actors at a series of user-defined "steps". A step may correspond to loading a new room and unloading a previous one, destroying certain actors like enemies or bombs, or spawning extra actors such as bushes in bush circles or projectiles from a deku scrub. It's essentially how we break up the history of what happens in the heap.<br/>

## actorset.txt
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

```
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

```
When the program reaches step X, actors listed under step X allocate into the heap. After this, any actors that had previously been allocated with a "deallocation step" X will deallocate. For a practical example, see "Examples" section.<br/>

## actorpool.txt
If you are trying to solve an SRM problem which requires a grabbed actor to be at some position relative to another actor, you would use the solution-finder mode which uses the "actorpool.txt" file along with "actorset.txt". "actorpool.txt" contains information about the grabbed actor, the actor which you want to SRM and lists of possible actors to inject into the sequence in order to achieve this. <br/>

The start of the file contains 5 variables:

* actor1_id - This is the actor ID of the grabbed actor
* actor2_id - This is the actor ID of the actor we wish to SRM
* actor1_step - This is the step at which to find the grabbed actor
* actor2_step - This is the step at which to find the actor we wish to SRM (usually the final step)
* offset - This is the desired offset between the grabbed actor and the SRM actor. Calculated as (actor2 memory position - actor1 memory position)

After this, we write the step that we want to inject actors at. Under each step we list the pool of actors that we want to inject from at that step.
```
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

```

The actors listed under each step are the "pools" of actors that the simulator can choose from. It may pick any number of actors from this pool and allocate them in any order during the relevant step. Or it may pick none at all. The actor placement is generated randomly each time the simulaton runs.<br/>

Note that if you list an actor pool at a particular step, that step in "actorset.txt" will be ignored. "actorpool.txt" has priority. See examples below in the "Examples" section.<br/>

## Main Program
You can run the software by running "PZL.py". PZL is a command-line program with two different modes. The first is heap-display and the second is solution-finder.<br/>

Heap-display can be reached by typing "heap". This runs the simulator through the list of steps in "actorset.txt", allocating and de-allocating actors at the correct steps as it goes. The contents of the heap at the end of each step is then printed to the console. This is a good way to make sure you've set up "actorset.txt" correctly for a given room as you can check the results against [Spectrum](https://wiki.cloudmodding.com/oot/App:Spectrum).<br/>

Solution-finder mode uses "actorpool.txt" to inject random actors at a chosen step. Then, based on what you've chosen as "actor1" and "actor2", you can compare their relative positions in the heap. If the relative positions of actor1 and actor2 match the required offset, the actorset will be dumped to a file in actorset_dump. In this mode, the simulation will keep running forever, until you close python, dumping solution actorsets as it goes.<br/>

# Examples
## Setting up Steps in "actorset.txt"
Let's take an example from Ocarina of Time. Let's say I wanted to enter the main room of deku tree. The first thing we need to do is fill in "step 0" with all the actors that allocate when we enter this room. First we start with scene actors, which are doors and loading planes. This room has 3 - two doors and a load plane. These always come first in the actorset. You can use [Spectrum](https://wiki.cloudmodding.com/oot/App:Spectrum) to find out what these are and what order the spawn in. So we would start filling in "actorset.txt" like this:

```
version=oot_ntsc_1.0

# Enter main room
Step 0 
0x002E,2 # Door to scrub room
0x002E,1 # Door to compass room
0x0023,1 # Loading plane to B1
```

Notice how I've given the door to the scrub room a larger deallocation step - that's because I plan to enter that room at step 1 and so I want this door in particular to stay loaded after Step 1. But anyway let's continue filling in Step 0. You can get the rest of the actors from this room of the deku tree from the [OoT Ultimate Spreadsheet](https://docs.google.com/spreadsheets/d/1Sl_ay1qPxTrs6xBTpVeqhKFrJjOGYyh3Tg1W0Ch5aHw/edit#gid=640593027). Deku tree is map 0 and the main room is room 0. We copy the actor numbers from this spreadsheet into step 0, and give them deallocation step 1.

```
version=oot_ntsc_1.0

# Enter main room
Step 0 
0x002E,2 # Door to scrub room
0x002E,1 # Door to compass room
0x0023,1 # Loading plane to B1
0x0095,1 # Skullwalltulas
0x0095,1
0x0095,1
0x0037,1 # Skulltulas
0x0037,1
0x0037,1
0x0125,1 # Grass
0x0125,1
0x0125,1
0x0125,1
0x0125,1
0x0055,1 # Deku Babas
0x0055,1
0x0055,1
0x000A,1
0x000F,1 # Central web
0x011B,1 # navi "You can open doors"
0x011B,1 # navi "look at this web"
0x011B,1 # navi "You can open doors"
0x011B,1 # navi "You can climb vines"
0x011B,1 #^
0x011B,1 #^
0x011B,1 #^
0x011B,1 #^
0x011B,1 #^
0x0015,1 # Heart pickups
0x0015,1
```
Note that I've added the "0x" before hex numbers, you don't have to do that (and in fact if you're copying from the spreadsheet it won't have the "0x").<br/>

Now we have all the actors from the main room, we can save this text file and run PZL. Type "heap" to see all the actors and overlays loaded at step 0. We should get the following output:

```
step 0
0x1E2210 0x002E INSTANCE
0x1E23B0 0x002E INSTANCE
0x1E2550 0x0023 INSTANCE
0x1E26D0 0x0095 OVERLAY
0x1E5EF0 0x0095 INSTANCE
0x1E63F0 0x0095 INSTANCE
0x1E68F0 0x0095 INSTANCE
0x1E6DF0 0x0037 OVERLAY
0x1E9A90 0x0037 INSTANCE
0x1EA030 0x0037 INSTANCE
0x1EA5D0 0x0037 INSTANCE
0x1EAB70 0x0125 OVERLAY
0x1EC080 0x0125 INSTANCE
0x1EC240 0x0125 INSTANCE
0x1EC400 0x0125 INSTANCE
0x1EC5C0 0x0125 INSTANCE
0x1EC780 0x0125 INSTANCE
0x1EC940 0x0055 OVERLAY
0x1F0410 0x0055 INSTANCE
0x1F0850 0x0055 INSTANCE
0x1F0C90 0x0055 INSTANCE
0x1F10D0 0x000A OVERLAY
0x1F2C40 0x000A INSTANCE
0x1F2E60 0x000F OVERLAY
0x1F4600 0x000F INSTANCE
0x1F4870 0x011B OVERLAY
0x1F4E90 0x011B INSTANCE
0x1F5000 0x011B INSTANCE
0x1F5170 0x011B INSTANCE
0x1F52E0 0x011B INSTANCE
0x1F5450 0x011B INSTANCE
0x1F55C0 0x011B INSTANCE
0x1F5730 0x011B INSTANCE
0x1F58A0 0x011B INSTANCE
0x1F5A10 0x011B INSTANCE
0x1F5B80 0x0015 INSTANCE
0x1F5D50 0x0015 INSTANCE
```

We can compare this to Spectrum if we want to check it's accuracy - if it's not correct then it's likely we haven't accounted for some extra actors allocating or de-allocating. Once we're happy, we can move on to step 1 which is going to be loading the scrub room.<br/>

The next room has 2 doors, however one of the doors (the one we entered from) was already allocated in the previous step (we gave it an allocation timer 2). So we only need to specify one door at this step:
```
Step 1
0x002E,2 # Door to slingshot room
```
Now we add in the actors from this room. The only thing in this room other than doors is a deku scrub - and by reading the spreadheet you may be tempted to just write down the deku scrub and that's it. But we need to be careful - deku scrubs are actually two actors - one for the scrub and then one for the flower. They both have the same actor number, just a different parameter. By looking at Spectrum you can notice actors like this which may be different from what the spreadsheet says.
```
Step 1
0x002E,2 # Door to slingshot room
0x0192,2 # Scrub
0x0192,2 # Scrub flower
```
Putting everything together we end up with the "actorpool.txt" file looking like this:
```
version=oot_ntsc_1.0

# Enter main room
Step 0 
0x002E,2 # Door to scrub room
0x002E,1 # Door to compass room
0x0023,1 # Loading plane to B1
0x0095,1 # Skullwalltulas
0x0095,1
0x0095,1
0x0037,1 # Skulltulas
0x0037,1
0x0037,1
0x0125,1 # Grass
0x0125,1
0x0125,1
0x0125,1
0x0125,1
0x0055,1 # Deku Babas
0x0055,1
0x0055,1
0x000A,1
0x000F,1 # Central web
0x011B,1 # navi "You can open doors"
0x011B,1 # navi "look at this web"
0x011B,1 # navi "You can open doors"
0x011B,1 # navi "You can climb vines"
0x011B,1 #^
0x011B,1 #^
0x011B,1 #^
0x011B,1 #^
0x011B,1 #^
0x0015,1 # Heart pickups
0x0015,1

# Enter scrub room
Step 1
0x002E,2 # Door to slingshot room
0x0192,2 # Scrub
0x0192,2 # Scrub flower
```

Now when we run PZL.py and print the heap we get the heap dump at both step 0 and step 1, with step 1 being:

```
step 1
0x1E2210 0x002E INSTANCE
0x1F5F20 0x002E INSTANCE
0x1F60C0 0x0192 OVERLAY
0x1F7B20 0x0192 INSTANCE
0x1F7DA0 0x0192 INSTANCE
```

## Further Techniques in "actorset.txt"
Let's take the above example and be more specific. Firstly, let's say we want the web in the main room to already be broken when we enter the deku tree.  You may think that in order to achieve this you should delete the entry for the web - this isn't actually correct. All actors in this room will allocate into the heap regardless of whether they should be cleared or not. It's only once all actors are allocated that they will start checking if they need to be cleared or not. This means that cleared actors such as webs or gold skulltulas will allocate into the heap and then deallocate from the heap as soon as everything is loaded in, leaving a gap.<br/>

We can achieve this by giving these actors a deallocation step of 0. This will deallocate them as soon as the whole room loads. Also note that if the web is gone in the main room of deku tree, the navi text for the web is also gone. <br/>

Let's also read the "you can open doors here" text and drop 2 bombs before we enter the scrub room, just to shift things around a bit. To do that we will introduce some new steps in-between the two ones we previously had.
```
version=oot_ntsc_1.0

# Enter main room
Step 0 
0x002E,4 # Door to scrub room
0x002E,3 # Door to compass room
0x0023,3 # Loading plane to B1
0x0095,3 # Skullwalltulas
0x0095,3
0x0095,3
0x0037,3 # Skulltulas
0x0037,3
0x0037,3
0x0125,3 # Grass
0x0125,3
0x0125,3
0x0125,3
0x0125,3
0x0055,3 # Deku Babas
0x0055,3
0x0055,3
0x000A,3
0x000F,0 # Central web
0x011B,1 # navi "You can open doors"
0x011B,0 # navi "look at this web"
0x011B,1 # navi "You can open doors"
0x011B,3 # navi "You can climb vines"
0x011B,3 #^
0x011B,3 #^
0x011B,3 #^
0x011B,3 #^
0x011B,3 #^
0x0015,3 # heart pickups
0x0015,3

# Read navi text for door
Step 1

# Drop 2 bombs
Step 2
0x0010,3
0x0010,3

# Enter scrub room
Step 3
0x002E,4 # Door to slingshot room
0x0192,4 # Scrub
0x0192,4 # Scrub flower
```
Notice what we've done. We've created "step 1" which represents reading the navi text and we've also added a step 2 for dropping 2 bombs.<br/>

The bombs and the majority of the initial room actors now have a deallocation step "3" as we want them to deallocate when we enter the next room at step 3. The web and the navi text for the web have deallocation step "0" because we want them to deallocate as soon as we load the room. Finally, the navi text for the door has a deallocation step "1", because we want them to deallocate when we read the door text at step 1.<br/>

If you look carefully, you may notice that Step 1 wasn't actually neccessary, we could've given the navi text for the door a deallocation step of 0 and the heap would've ended up exactly the same. But it's up to you however you want to lay out your steps, and there are often multiple ways of achieving the same thing and some are more readable than others.

## Setting up Pools in "actorpool.txt"

