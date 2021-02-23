"""
Arkania Grid-Based World Simulation

Inferface:
    init() - initializes a world from scratch
    cleanup() - deallocate any memory and clean up resources
    step() - execute a single timestep
    render() - render the world in its current state
"""
import numpy as np
import random as rnd
import gym
import time
from gym.envs.classic_control.rendering import Geom, Viewer
import pyglet
from pyglet.gl import *
# from gym.utils import colorize, EzPickle

VIEWPORT_W = 800
VIEWPORT_H = 600

GRASS = 0
WATER = 1
SHADE = 2
BEACH_E = 3
BEACH_N_OLD = 4
BEACH_S = 5
BEACH_NE = 6
BEACH_SE = 7
CLIFF_W = 8
CLIFF_SW = 9
ROCK = 10
FORESTEDGE = 11
FOREST = 12
AGENT = 13
PREDATOR = 14
STONE = 15
FOOD_1 = 16
FOOD_2 = 17
FOOD_3 = 18
FOOD_4 = 19
LIGHT = 20
BEACH_N = 21
CLIFF_E = 22
CLIFF_SE = 23
FOOD = 24
HAND = 25
WATER_IN_HAND = 26
STONE_IN_HAND = 27
FOOD_IN_HAND = 28

NUM_SPRITES = 29


PLANT = 101

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

turn_left = [WEST, NORTH, EAST, SOUTH]
turn_right = [EAST, SOUTH, WEST, NORTH]


class Tile(Geom):
    def __init__(self, subimg, x, y, width, height, light=1.0):
        super().__init__()
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.set_color(light, light, light)
        self.flip = False
        self.img = subimg

    def render1(self):
        self.img.blit(self.x, self.y, width=self.width, height=self.height)


class Tileset:
    def __init__(self):
        self.tiles = []
        for i in range(1, NUM_SPRITES + 1):
            fname = f"arkania/graphics/sprites/Simple_Tiles{i}.png"
            self.tiles.append(pyglet.image.load(fname))

    def draw(self, viewer, tile_id, x, y, offset_x=0, offset_y=0, light=1.0):
        """
        Blit one of the subimages to the screen in the block given by x and y
        :param viewer: the rendering.Viewer object
        :param tile_id: which tile to blit (0 to 14 for now)
        :param x: the column or which cell in the x direction
        :param y: the row or which cell in the y direction
        :param offset_x: offset within the tile
        :param offset_y: offset within the tile
        :param light: the brightness of light
        :return: N/A
        """
        tile_img = self.tiles[int(tile_id)]
        viewer.add_onetime(Tile(tile_img, 12 + x * 32 + offset_x, 12 + y * 32 + offset_y, 32, 32, light))


class Stone:
    def __init__(self, env, uid, x, y):
        self.uid = uid
        self.env = env
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.in_air = 0

    def throw(self, x, y, direction):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.in_air = 2  # number of turns that it stays in air
        if direction == NORTH:
            self.vy = 1
        elif direction == SOUTH:
            self.vy = -1
        elif direction == EAST:
            self.vx = 1
        elif direction == WEST:
            self.vx = -1

    def draw(self):
        self.env.tiles.draw(self.env.viewer, STONE, self.x, self.y, light=self.env.light)

    def step(self):
        """
        Checks if the Stone hits anything in the two tiles ahead / step
        If in_air > 0 then do the following checks:
        - If the next tile is STONE then the stone false in the current tile
        - If the next tile is FOREST or WATER then the stone is lost
        - If the next tile less than 0 or greater than 17 in either x or y, then the stone is lost
        - If the next tile is a predator, the predator is killed, and the stone falls where the predator was
        - If the next tile is another Agent, the agent loses 50 energy and the stone falls where the agent is
        :return: None
        """

        if self.in_air > 0:
            for _ in range(2):
                nxt_x = self.x + self.vx
                nxt_y = self.y + self.vy


class Food:
    def __init__(self, env, uid, x, y):
        self.uid = uid
        self.env = env
        self.x = x
        self.y = y

    def draw(self):
        self.env.tiles.draw(self.env.viewer, FOOD, self.x, self.y, light=self.env.light)

    def step(self):
        pass


class Plant:
    def __init__(self, env, uid, x, y, stage):  # stage is 0 to 3
        self.env = env
        self.uid = uid
        self.x = x
        self.y = y
        self.stage = stage
        self.counter = 0
        self.stages = [FOOD_1, FOOD_2, FOOD_3, FOOD_4]

    def step(self):
        self.counter += 1
        if self.counter > 50:
            self.counter = 0
            self.stage = min([3, self.stage + 1])

    def draw(self):
        self.env.tiles.draw(self.env.viewer, self.stages[self.stage], self.x, self.y, 0, 13, light=self.env.light)

    def picked(self):
        self.stage = 0


class Agent:
    def __init__(self, env, uid, x, y):
        self.uid = uid
        self.env = env
        self.x = x
        self.y = y
        self.food = 100.0
        self.water = 100.0
        self.energy = 100.0
        self.health = 100.0
        self.in_hand = None
        self.facing = NORTH
        self.age = 0

    def draw(self):
        self.env.tiles.draw(self.env.viewer, AGENT, self.x, self.y, light=self.env.light)
        # TODO: Draw items in hands
        # TODO: Some way to show the way it's facing

    #-----------------------------------------------------------------------------------------------
    def what_is_in_hand(self):
        if type(self.in_hand) == int and self.in_hand == WATER:
            return 2
        elif type(self.in_hand) == Food:
            return 1
        elif type(self.in_hand) == Stone:
            return 3
        return 0

    def step(self):
        if self.energy < 0:
            self.energy = 0
        self.age += 1
        self.water -= 1
        self.food -= 1
        if self.water < 25.0:
            self.energy -= 1
        if self.water <= 0:
            self.water = 0.0
            self.health -= 100 / 80
        if self.food < 25.0:
            self.energy -= 1
        if self.food <= 0:
            self.food = 0
            self.health -= 25 / 80

    #==================================================
    # ACTION SPACE
    #===================================================
    def move_north(self):
        if self.energy >= 2:
            self.energy -= 2
            if self.y == 17:
                self.health = 0
            else:
                ahead = self.env.map[self.y + 1, self.x]
                if ahead != ROCK:
                    self.y += 1
                if ahead in [FOREST, WATER]:
                    self.health = 0

    def move_east(self):
        if self.energy >= 2:
            self.energy -= 2
            if self.x == 17:
                self.health = 0
            else:
                ahead = self.env.map[self.y, self.x + 1]
                if ahead != ROCK:
                    self.x += 1
                if ahead in [FOREST, WATER]:
                    self.health = 0

    def move_south(self):
        if self.energy >= 2:
            self.energy -= 2
            if self.y == 0:
                self.health = 0
            else:
                ahead = self.env.map[self.y - 1, self.x]
                if ahead != ROCK:
                    self.y -= 1
                if ahead in [FOREST, WATER]:
                    self.health = 0

    def move_west(self):
        if self.energy >= 2:
            self.energy -= 2
            if self.x == 0:
                self.health = 0
            else:
                ahead = self.env.map[self.y, self.x - 1]
                if ahead != ROCK:
                    self.x -= 1
                if ahead in [FOREST, WATER]:
                    self.health = 0

    def pick_up(self):
        if self.energy >= 1:
            self.energy -= 1
            if self.in_hand is None:
                # check plants ready to harvest
                found = False
                for p in self.env.plants:
                    if p.x == self.x and p.y == self.y and p.stage == 3:
                        self.env.food_id += 1
                        self.in_hand = Food(self.env, self.env.food_id, -1, -1)
                        p.stage = 0
                        p.counter = 0
                        break

                # check for water
                if not found:
                    if self.env.map[self.y, self.x] in [BEACH_E, BEACH_N_OLD, BEACH_S, BEACH_NE, BEACH_SE, BEACH_N]:
                        self.in_hand = WATER
                        found = True

                # check for food on ground
                if not found:
                    for f in self.env.foods:
                        if f.x == self.x and f.y == self.y:
                            self.in_hand = f
                            f.x = -1
                            f.y = -1
                            self.env.foods.remove(f)
                            break

                # check for stone on ground
                if not found:
                    for s in self.env.stones:
                        if s.x == self.x and s.y == self.y:
                            self.in_hand = s
                            s.x = -1
                            s.y = -1
                            self.env.stones.remove(s)
                            break

    def put_down(self):
        if self.energy >= 1:
            self.energy -= 1
            if self.in_hand is not None:
                if type(self.in_hand) == Stone:
                    s = self.in_hand
                    s.x = self.x
                    s.y = self.y
                    self.env.stones.append(s)
                if type(self.in_hand) == Food:
                    f = self.in_hand
                    f.x = self.x
                    f.y = self.y
                    self.env.foods.append(f)
                self.in_hand = None

    def consume_item(self):
        if self.in_hand is not None:
            if type(self.in_hand) == int and self.in_hand == WATER:
                self.in_hand = None
                self.water += 20
                if self.water > 100:
                    self.health -= (self.water - 100) / 2
                    self.energy -= (self.water - 100) / 2
                    self.water = 100
            elif type(self.in_hand) == Food:
                self.in_hand = None
                self.food += 35
                if self.food > 100:
                    self.health -= (self.food - 100) / 2
                    self.energy -= (self.food - 100) / 2
                    self.food = 100
            elif type(self.in_hand) == Stone:
                self.health -= 45
                self.energy -= 45
                self.in_hand = None

    def throw_north(self):
        pass

    def throw_south(self):
        pass

    def throw_east(self):
        pass

    def throw_west(self):
        pass

    def rest(self):
        self.food += 0.5
        self.water += 0.5
        if self.food >= 25 and self.water >= 25:
            self.health += 1
            self.energy += 3
        else:
            self.health += 0
            self.energy += 2
        if self.health > 100:
            self.health = 100
        if self.energy > 100:
            self.energy = 100


class SimpleEnv(gym.Env):
    """
    Action-Space - provided as a single integer
      0 = REST
      1 = MOVE NORTH
      2 = MOVE EAST
      3 = MOVE SOUTH
      4 = MOVE WEST
      5 = PICK UP OBJECT on same tile as agent
      6 = PUT DOWN OBJECT on same tile as agent
      7 = CONSUME ITEM IN HAND
      8 = THROW OBJECT NORTH
      9 = THROW OBJECT EAST
     10 = THROW OBJECT SOUTH
     11 = THROW OBJECT WEST

    State-Space - provided as a dictionary
      health - number from 0 to 100 showing the level of health.  A health of zero (or less) results in death
      energy - number from 0 to 100 showing level of energy available.  All actions consume energy.
               Eating food and drinking water replenish energy.  Resting replenishes energy.
      food - number from 0 to 100 showing the level of food in the agent.  At food < 25, energy is decreased more
             quickly than normal. At food <= 0, health decreases over time.
      water - number from 0 to 100 showing level of water in the agent.  At water < 25, energy decreases more quickly
              than normal.  At water <= 0, health decreases rapidly (such that death in 2 days' worth of turns)
      in_hand - an indicator of what is held by the agent at that time:
              The possible values are:
              0 = Nothing, hand is empty
              1 = Food in hand
              2 = Water in hand
              3 = A Stone is in hand
      sight - a <2N+1 x 2N+1> matrix of what the agent can see (other than itself).  The center square will represent
              where the player is.  There will be an integer value in each cell of the matrix.  The site matrix is
              represented like a math matrix with <rows x colunns> so the point X, Y would be sight_matrix[Y, X].
              The range of values in the sight matrix will be:
              0 = GRASS
              1 = BEACH (near danger, yields water)
              2 = CLIFF-EDGE (near danger)
              3 = FOREST-EDGE (near danger)
              4 = ROCK-WALL (impassable)
              5 = DROPOFF beyond the CLIFF EDGE (death)
              6 = WATER (death)
              7 = DARK-FOREST (death)
              8 = PLANT-STAGE-1
              9 = PLANT-STAGE-2
             10 = PLANT-STAGE-3
             11 = PLANT-READY-TO-HARVEST (yields food)
             12 = FOOD (on the ground which can be picked up -- yields food)
             13 = STONE (can be picked up, can be thrown)
             14 = PREDATOR (seeks agent, kills agent)
    """

    #-----------------------------------------------------------------------------------------------
    def __init__(self, seed=2021):
        self.seed = seed
        self.viewer = None
        self.map = np.zeros((18, 18), dtype=int)
        self.objects = np.zeros((18, 18), dtype=int)
        self.tiles = Tileset()
        self.light = 1.0
        self.food_id = 0

    #-----------------------------------------------------------------------------------------------
    def reset(self):
        self._cleanup()
        self._init()

    #-----------------------------------------------------------------------------------------------
    def get_sight_matrix(self, agent):
        tile_map = [0, 6, 5, 1, 1, 1, 1, 1, 2, 2, 4, 3, 7, -1, 14, 13, 8, 9, 10, 11, -1, 1, 2, 2, 12, -99, -99]
        size = 6
        smat = np.zeros((2 * size + 1, 2 * size + 1), dtype=int)
        for r in range(2 * size + 1):
            for c in range(2 * size + 1):
                x = agent.x - size + c
                y = agent.y + size - r
                v = -999
                if 0 <= x <= 17 and 0 <= y <= 17:
                    tile = self.map[y, x]
                    v = tile_map[tile]
                else:
                    if x >= 0 and y >= 0:
                        if x >= y:
                            v = 5   # DROPOFF
                        else:
                            v = 7   # DARK FOREST
                    elif x < 0 and y >= 0:
                        if 17-x >= y:
                            v = 5
                        else:
                            v = 7
                    elif x >= 0 and y < 0:
                        if 17-x >= y:
                            v = 4
                        else:
                            v = 5
                    elif x < 0 and y < 0:
                        if x >= y:
                            v = 4
                        else:
                            v = 5
                smat[r, c] = v

        for p in self.plants:
            r = agent.y - p.y + size
            c = p.x - agent.x + size

            if 0 <= r <= 2*size and 0 <= c <= 2*size:
                smat[r, c] = 8 + p.stage

        for f in self.foods:
            r = agent.y - f.y + size
            c = f.x - agent.x + size

            if 0 <= r <= 2*size and 0 <= c <= 2*size:
                smat[r, c] = 12

        for s in self.stones:
            r = agent.y - s.y + size
            c = s.x - agent.x + size

            if 0 <= r <= 2*size and 0 <= c <= 2*size:
                smat[r, c] = 13

        # smat[size, size] = 8

        return smat

    #-----------------------------------------------------------------------------------------------
    def step(self, action):
        """
        Takes one step of action in the environment and returns the resulting state and reward information
        :param action:
        :return:
        """

        self.agent.step()

        # lame way to call the agent actions...
        if action == 0:
            self.agent.rest()
        elif action == 1:
            self.agent.move_north()
        elif action == 2:
            self.agent.move_east()
        elif action == 3:
            self.agent.move_south()
        elif action == 4:
            self.agent.move_west()
        elif action == 5:
            self.agent.pick_up()
        elif action == 6:
            self.agent.put_down()
        elif action == 7:
            self.agent.consume_item()
        elif action == 8:
            self.agent.throw_north()
        elif action == 9:
            self.agent.throw_east()
        elif action == 10:
            self.agent.throw_south()
        elif action == 11:
            self.agent.throw_west()

        for p in self.plants:
            p.step()

        for s in self.stones:
            s.step()

        for f in self.foods:
            f.step()

        state = {'health': self.agent.health,
                 'energy': self.agent.energy,
                 'food': self.agent.food,
                 'water': self.agent.water,
                 'in_hand': self.agent.what_is_in_hand(),
                 'sight': self.get_sight_matrix(self.agent)}

        # this can eventually be a log of information about 'why' different things happened in response to actions
        debug = {}

        # Results
        reward = 1
        is_done = False
        if self.agent.health <= 0:
            reward = -1000
            is_done = True
        return state, reward, is_done, debug

    #-----------------------------------------------------------------------------------------------
    def render(self, mode='human'):
        if self.viewer is None:
            self.viewer = Viewer(VIEWPORT_W, VIEWPORT_H)
        # self.viewer.set_bounds(0, self.VIEWPORT_W, 0, self.VIEWPORT_H)

        self.viewer.draw_polygon([
            (0, 0),
            (VIEWPORT_W, 0),
            (VIEWPORT_W, VIEWPORT_H),
            (0, VIEWPORT_H),
        ], color=(0.0, 0.0, 0.0))
        self.viewer.draw_polygon([
            (0, 0),
            (VIEWPORT_H, 0),
            (VIEWPORT_H, VIEWPORT_H),
            (0, VIEWPORT_H),
        ], color=(0.3, 0.3, 0.3))

        # Terrain
        for r in range(18):
            for c in range(18):
                self.tiles.draw(self.viewer, self.map[r, c], c, r, light=self.light)

        # Stones
        for s in self.stones:
            s.draw()

        # Food
        for f in self.foods:
            f.draw()

        # Plants
        order_queues = [[] for i in range(18)]
        for p in self.plants:
            order_queues[p.y].append(p)
        for y in range(17, 0, -1):
            for p in order_queues[y]:
                p.draw()

        # Creatures
        self.agent.draw()

        # Shade
        for r, c, num in self.dark_areas:
            for _ in range(num):
                self.tiles.draw(self.viewer, SHADE, c, r)
                self.tiles.draw(self.viewer, SHADE, 17 - c, r)

        # draw time scale
        # TODO: Timescales

        #---------------------------------
        # Draw what is in hand
        #---------------------------------
        hand_x, hand_y = 19, 10
        self.tiles.draw(self.viewer, HAND, hand_x, hand_y)
        in_hand = self.agent.what_is_in_hand()
        if in_hand == 1:
            self.tiles.draw(self.viewer, FOOD_IN_HAND, hand_x, hand_y)
        if in_hand == 2:
            self.tiles.draw(self.viewer, WATER_IN_HAND, hand_x, hand_y)
        if in_hand == 3:
            self.tiles.draw(self.viewer, STONE_IN_HAND, hand_x, hand_y)

        #---------------------------------
        # draw player stats:
        #---------------------------------
        white = (1.0, 1.0, 1.0)
        red = (0.6, 0.1, 0.1)
        green = (0.1, 0.6, 0.1)
        blue = (0.1, 0.1, 0.8)
        yellow = (0.7, 0.7, 0.2)
        black = (0, 0, 0)
        bright_red = (1, 0, 0)

        bar_coords = [617, 662, 707, 752]

        for x in bar_coords:
            x2 = x + 30
            y1 = 18
            y2 = 18 + 302
            self.viewer.draw_polyline([(x, y2), (x, y1), (x2, y1), (x2, y2)], color=white, linewidth=1)

        agent = self.agent

        # Health Level
        x1 = bar_coords[0]
        x2 = x1 + 29
        y1 = 18
        y2 = y1 + 3 * agent.health + 1
        self.viewer.draw_polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], color=red)

        # Energy Level
        x1 = bar_coords[1]
        x2 = x1 + 29
        y1 = 18
        y2 = y1 + 3 * agent.energy + 1
        self.viewer.draw_polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], color=yellow)

        # FOOD Level
        x1 = bar_coords[2]
        x2 = x1 + 29
        y1 = 18
        y2 = y1 + 3 * agent.food + 1
        self.viewer.draw_polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], color=green)

        # WATER Level
        x1 = bar_coords[3]
        x2 = x1 + 29
        y1 = 18
        y2 = y1 + 3 * agent.water + 1
        self.viewer.draw_polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], color=blue)

        # Top Bar
        for x in bar_coords:
            self.viewer.draw_polyline([(x, 320), (x + 30, 320)], color=white, linewidth=1)

        danger_levels = [20, 20, 19 + 3 * 25, 19 + 3 * 25]

        for x, y in zip(bar_coords, danger_levels):
            self.viewer.draw_polyline([(x, y+2), (x+8, y+2), (x+8, y-1), (x, y-1)], color=black, linewidth=1)
            self.viewer.draw_polygon([(x, y+1), (x+7, y+1), (x+7, y-1), (x, y-1)], color=bright_red)
            self.viewer.draw_polyline([(x+29, y+2), (x+22, y+2), (x+22, y-1), (x+29, y-1)], color=black, linewidth=1)
            self.viewer.draw_polygon([(x+29, y+1), (x+22, y+1), (x+22, y-1), (x+29, y-1)], color=bright_red)

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    #-----------------------------------------------------------------------------------------------
    def _init(self):
        """
        This actually does the initialization
        """

        self.season = 0
        self.day = 0
        self.time = 0

        # BACKGROUND TILES
        for r in range(18):
            for c in range(18):
                self.map[r, c] = GRASS
        for r in range(4, 16):
            self.map[r, 0] = CLIFF_W
            self.map[r, 17] = CLIFF_E
        for c in range(0, 18):
            self.map[0, c] = ROCK
            self.map[17, c] = FOREST
            self.map[16, c] = FORESTEDGE
        for i in range(0, 3):
            self.map[i + 1, 0] = ROCK
            self.map[i + 1, 4] = ROCK
            self.map[3, i] = ROCK

            self.map[i + 1, 17] = ROCK
            self.map[i + 1, 13] = ROCK
            self.map[3, 17 - i] = ROCK
        for i in range(5, 13):
            self.map[1, i] = WATER
            self.map[2, i] = WATER
            self.map[3, i] = BEACH_N
        self.map[15, 0] = CLIFF_SW
        self.map[15, 17] = CLIFF_SE
        self.dark_areas = [(1, 1, 4),
                           (1, 2, 3),
                           (1, 3, 2),
                           (2, 1, 3),
                           (2, 2, 2),
                           (2, 3, 1),
                           (3, 3, 1)]

        # CREATURES
        self.agent = Agent(self, 1, 9, 9)

        # PLANTS
        self.plants = []
        for idx in range(12):
            while True:
                x, y = rnd.randint(1, 16), rnd.randint(4, 15)
                if self.objects[y, x] == 0:
                    self.objects[y, x] = PLANT
                    break

            stage = rnd.randint(0, 3)
            plant = Plant(self, idx, x, y, stage)
            self.plants.append(plant)

        # Stones - DISABLED in SIMPLE ENV
        self.stones = []
        # for idx in range(15):
        #     while True:
        #         x, y = rnd.randint(1, 16), rnd.randint(4, 15)
        #         if self.objects[y, x] == 0:
        #             self.objects[y, x] = STONE
        #             break
        #
        #     stone = Stone(self, idx, rnd.randint(1, 16), rnd.randint(4, 15))
        #     self.stones.append(stone)

        # Empty at first, but can be filled as things are set down
        self.foods = []

    #-----------------------------------------------------------------------------------------------
    def _cleanup(self):
        """
        clean up memory and resources
        """
