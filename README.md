# Arkania
A rich, complex, 2d grid-based world for multi-agent reinforcement learning development.
A future version may become a continuous world.


## Current Status:
* A simple, discrete environment is working, I believe.
* A detailed description of the action space, and the state space are included in the code for simpl_env.py
  attached to the SimpleEnv class.
* The reward is 1 for each step survived and -1000 for death
* An example, human-interface for the world is provided in _example.py_.  See the code for the keys to use.
* To use the environment in your code, if your in the main project repo, you can refer to arkania as a package.
  Again, see _example.py_ for how to import the environment.

## RL Problem Definition:

### State Space:
* Provided as a dictionary that will contain:
  * health
      * Number from 0 to 100 showing the level of health.  A health of zero (or less) results in death
  * energy
      * Number from 0 to 100 showing level of energy available.  All actions consume energy.
        Resting replenishes energy.
  * food
      * Number from 0 to 100 showing the level of food in the agent.  At food < 25, energy is decreased more
        quickly than normal. At food <= 0, health decreases over time.
  * water 
      * Number from 0 to 100 showing level of water in the agent.  At water < 25, energy decreases more quickly
        than normal.  At water <= 0, health decreases rapidly (such that death in 2 days' worth of turns)
  * in_hand
    * An indicator of what is held by the agent at that time.  The possible values are:
      * 0 = Nothing, hand is empty
      * 1 = Food in hand
      * 2 = Water in hand 
      * 3 = A Stone is in hand
  * sight
    * A <2N+1 x 2N+1> matrix of what the agent can see (other than itself).  The center square will
      represent where the player is.  There will be an integer value in each cell of the matrix.  The site 
      matrix is represented like a math matrix with <rows x colunns> so the point X, Y would be 
      sight_matrix[Y, X].
    * The range of values in the sight matrix will be:
      * 0 = GRASS
      * 1 = BEACH (near danger, yields water)
      * 2 = CLIFF-EDGE (near danger)
      * 3 = FOREST-EDGE (near danger)
      * 4 = ROCK-WALL (impassable)
      * 5 = DROPOFF beyond the CLIFF EDGE (death)
      * 6 = WATER (death)
      * 7 = DARK-FOREST (death)
      * 8 = PLANT-STAGE-1
      * 9 = PLANT-STAGE-2
      * 10 = PLANT-STAGE-3
      * 11 = PLANT-READY-TO-HARVEST (yields food)
      * 12 = FOOD (on the ground which can be picked up -- yields food)
      * 13 = STONE (can be picked up, can be thrown)
      * 14 = PREDATOR (seeks agent, kills agent)

### Action Space:
* Provided to the environment as a single integer for what action to take on that turn.  Possible values are:
  * 0 = REST 
  * 1 = MOVE NORTH
  * 2 = MOVE EAST
  * 3 = MOVE SOUTH
  * 4 = MOVE WEST
  * 5 = PICK UP OBJECT on same tile as agent
  * 6 = PUT DOWN OBJECT on same tile as agent
  * 7 = CONSUME ITEM IN HAND
  * 8 = THROW OBJECT NORTH
  * 9 = THROW OBJECT EAST
  * 10 = THROW OBJECT SOUTH
  * 11 = THROW OBJECT WEST


## Features

### 1. Resources to be collected, used, consumed, or stored
* Food 
* Water
* Small Rocks (not currently in SimpleEnv)

### 2. Things it must avoid
* starvation
* thirst
* cliffs
* Dark, evil forest
* Drowning in deep water.
* Predators (Not currently in SimpleEnv)

### 3. Calendar and day / night cycle
* Food growth patterns are seasonal.  One quarter of the calendar (winter) has plants die and not regrow until (winter) is over.
* A day / night cycle where food grows during the day and predators are more active at night.

### 4. Potential action space: 
* Turn left / right
* Move north / south / east / west
* Pick up object in front of agent
   * An agent can carry up to two objects at a time -- one in each hand
   * Dominant hand must be empty for the agent to pick something up
* Use object in dominant hand
* Set down object in dominant hand on the Tile in front of the agent
* Consume resource in front of agent (typically food or water)
* Move object in front of agent
   * This could essentially be grabbing hold of the object in front of the
   agent, and then in a subsequent turn normal move actions (N/S/E/W and Turns) would manipulate the object.
   * Potential actions then would be: Take hold of object in front of agent, and Release object that is held.
    

## Potential Reinforcement learning goals

* Multi-agent environment / learning
* Capacity for communication by symbols (Single letter "words")
* Include some form of symbolic Knowledge Representation and Reasoning
