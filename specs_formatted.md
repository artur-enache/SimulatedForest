# Simulated Forest — Specification

## Overview

The simulation is simple: there are several entitites living in a forest. Some entities require food that other entities provide, and the entities can reproduce based on some conditions. The mechanics can be similar to rock paper scissors.

The simulation moves in **"ticks"**; for example, the state updates every 5 seconds.

---

## Entities

### Full Entity Set (Example)

For example, the forest can have:

- Grass
- Trees
- Mushrooms
- Rabbits
- Deer
- Wolves

With the following rules:

- Grass grows by itself after X ticks, provided it has some space where it can move
- Trees grow provided there are both mushrooms and grass present near an empty square
- Mushrooms grow where animals die
- Rabbits eat grass
- Deer eat grass and mushrooms
- Wolves eat rabbits and deer

---

### Simplified Entity Set

Ok, this seems like too many systems to include. Let's simplify:

| Entity | Symbol |
|--------|--------|
| Empty square | 🟫 |
| Grass | 🌱 |
| Rabbits | 🐇 |
| Wolves | 🐺 |

---

## Mechanics

### Grass

Grass grows, provided there are already X instances of grass present; there is a small chance that 1 grass can appear randomly on any one square.

### Rabbits

Rabbits eat grass. Once they have eaten Y grass, and if there are 2 rabbits present, they produce a baby rabbit.

### Wolves

Wolves eat rabbits. Once they have eaten Z rabbits, and if there are 2 wolves present, they produce a baby wolf.

---

## Entity Behavior

### Baby Rabbit

The baby rabbit consumes less grass than a grown adult for a while. If it survives, it grows into a full rabbit & consumes the regular amount of food.

### Hunger & Health (Rabbit)

The rabbit has both a **hunger** and a **health** bar.

- Hunger decreases by an amount every tick.
- Once hunger falls below a threshold, the rabbit seeks a source of grass.
- If enough ticks pass without finding food, the rabbit loses an amount of health.
- Once the health reaches 0, the rabbit dies & is deinstanced.
- If the rabbit consumes an instance of grass, the grass is deinstanced & the rabbit's hunger is reset to full.

### Hunger & Health (Wolf)

The wolf operates exactly the same as the rabbit, with two differences: the thresholds are different, and they eat rabbits.

---

## Forest Representation

I also need a way to represent the forest. It can be a **matrix**, where each "cell" stores three values:

```
grass_id, rabbit_id, wolf_id
```

Instances of G, R and W cannot occupy the same space twice.

But there also need to be some **global counts** for how many rabbits, grass and wolves there exist.

---

## Class Design

### Access Patterns

- **G** accesses this `forest_matrix` and also the global grass count, to understand when & where to instance itself.
- **R** accesses the forest matrix, the global rabbit count, and the global grass count to understand:
  - when & where to instance itself
  - where grass is
- **W** accesses the forest matrix and also the global rabbit count, to understand:
  - when & where to instance itself
  - where rabbits are

G R W can be classes, each tracking their instance counts in their own class attribute.

---

### F Class (Forest)

Should the forest also be a class? I think so.

**Responsibilities:**

- Initialize the empty matrix; the matrix is a list of lists — each cell is a list of bools `[grass_id, rabbit_id, wolf_id]`
- Based on this matrix, a visual representation can be displayed to the user
- Define *getters* for the G R W counts; the F class can be a centralized store of the state of the board; G R W can then query the F instance for the counts of other classes, instead of them accessing themselves directly
- Define *setters* for `grass_id`, `rabbit_id`, `wolf_id`; but I need to think about how to query & update the state of the matrix on each tick in an efficient way; another more optimal way would be for each G R W instance to store their own spatial coordinates, which F can get; then F can simply query every single instance of G R W on each tick, get their coordinates, and update the F matrix
- Define *getters* for the same values, which F will use to draw the board; this needs to be optimized — the matrix will be queried on every tick after all
- When R W need to find food, they also need to find the locations of: nearest G, nearest R respectively; so F must have a method to query the matrix for the nearest neighbor to a given G and R, and then pass this information back to the R or W that asked for it
- F needs a way to: calculate the shortest path to a G or R, and pass the next cell that a R or W needs to move to; on the next tick, if G has deinstanced or R moved, the path must be recalculated & the first cell in the path must be provided again; if the original G is still there, or R did not move, then provide the next cell in the original path
- *Optional:* should F have a queue (or stack?) for all the operations it needs to perform? if each tick takes place every 5s, then it makes sense to perform all required operations between ticks (n, n+1), not simply when it's the n+1 tick; and when n+1 arrives, the only thing to be done is to redraw the forest

---

## Recap: F Class

### Attributes

- **Simulation tick count**, incrementing every X seconds
- **Matrix:**

```
Matrix = [
    [grass_id, rabbit_id, wolf_id],
    [grass_id, rabbit_id, wolf_id],
    [grass_id, rabbit_id, wolf_id],
    [grass_id, rabbit_id, wolf_id]
]
```
---

### Methods

#### `update_matrix(instances)`

Method that applies to any instance of G R W and is used to update their position in the matrix; it gets the required position by querying the instance passed to it.

1. Gets a list of instances (in the main loop: first all G, then all R, then all W)
2. Iterates over them, and extracts the positions and saves them in a list of tuples — a queue: `[('r', 0, 1), ('g', 0, 1), ('w', 1, 3)]`
3. After iterating, resets the matrix to the blank state
4. Processes the queue and updates the matrix based on the values in these tuples

> *I don't care about storing which specific rabbit/grass/wolf exists in a specific cell.*

---

#### `get_cell(position)`

A method to get the values of each square; used for drawing the board.

---

#### `find_path(caller, position)`

A method for calculating the shortest path from a given starting position to a cell with `grass_id` / `rabbit_id`.

- Uses some kind of search algorithm
- Receives: calling instance identifier and its position (gets called when an instance is "hungry")
- After calculating the path to the nearest G/R, it stores: the caller identifier, the calculated path, an index starting at 0 (representing which step in the path was already provided), and the coordinates to the target
- Provides the first step in the path & the target coordinates to the calling instance (target coords. are needed so the caller understands when it has reached that square)
- Stores this step in the same data structure as the path & coordinates
- If a tick passes without being called for a path, clear the stored values in this data structure
- If the same caller asks for the path again, check if the target (G or R) still exists at the original coordinates:
  - If **yes**: provide the second step in the existing path
  - If **no**: repeat the calculation step

This method has two params: start_instance, target_instance; it can do two things:
- If target_instance (a string, 'grass' or 'rabbit'), it finds the path to a target as described above
- If !target_instance, it finds & returns an empty cell that is nearest to an instance of the same type as the start_instance; if there is no start_instance in the matrix, return a random set of coordinates in the matrix 

---

#### Optional: Operation Queue

A queue for scheduling all of this work in the forest instance. But it probably makes sense to schedule the work in the main game loop, not inside of a forest instance.

---

*That deals with the Forest Class. Next up: Grass, Rabbit, Wolves classes, and finally the Game Loop.*

## Grass Class

### Attributes

This class needs the following attributes:
- instance count / class attribute
- number of parents required for reproduction / class attribute
- health / instance attribute
- attrition / class attribute; determines how much health is lost every tick
- position as coordinates of the forest matrix / instance attribute

Methods:
- instantiation (health, attrition); but how is the position determined? The forest must somehow give this instance a "free" position that it can use to instance itself
- reproduce; check if the conditions are met (# of parents; space available in the matrix); I think this belongs in the game loop, not in the class definition
- position getter
- position setter

### Questions
Well, I have several questions about how the grass object is supposed to work:
- where is it instanced? 
- should the grass class keep track of each of its instance positions? it sounds like it would just duplicate the forest matrix for no good reason; but then how do I know which of these instances to move around the board (in the case of R and W)
- should these classes (G R W) inherit from something? They do have common characteristics: health, # of parents required, position, count, and the grass can also have a "hunger" threshold - it just wouldn't get replenished by anything
- should these classes also keep track of the ticker internally? Who/what will decrement the hunger meter on every tick?

Sounds like I need a base class LivingBeing, which comes with:

#### Attributes
- count (class; + getter / setter)
- health (instance; + getter / setter)
- parents required (class)
- position (instance; + getter / setter)
- hunger (instance; + getter / setter, set at beginning)
- health damage
- hunger threshold (class)
- hunger attrition (class)
- list of instances (class; + getter / setter)

#### Methods
Instantiate: the position is provided from the main game loop

Seek food: if hunger < threshold, then: rabbit seeks nearest grass; wolf seeks nearest rabbit; it asks for the position of nearest target from the forest object; grass doesn't seek anything here Reproduction: verify if internal hunger is higher than the threshold, and if count > # parents (ignore baby state for the beginning; all populations are adults by default);

Starvation: if hunger = 0, reduce health by damage; if hunger > 0, reduce hunger by attrition; if hunger = 0 and health = 0 die (remove all references of this instance from where they are set)
