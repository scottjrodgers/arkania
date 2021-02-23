# Arkania
A rich, complex, 2d grid-based world for multi-agent reinforcement learning development.
A future version may become a continuous world.


## Features

### 1. Resources to be collected, used, consumed, or stored
* Food 
* Water
* Small Rocks

### 2. Things it must avoid
* starvation
* thirst
* a cliff
* predators

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
