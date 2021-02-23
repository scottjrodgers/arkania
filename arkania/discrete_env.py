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
        for i in range(1, 25 + 1):
            fname = f"graphics/sprites/Simple_Tiles{i}.png"
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


class Plant:
    def __init__(self, env, uid, x, y, stage):  # stage is 0 to 3
        self.env = env
        self.uid = uid
        self.x = x
        self.y = y
        self.stage = stage
        self.stages = [FOOD_1, FOOD_2, FOOD_3, FOOD_4]

    def step(self):
        pass

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
        self.hand_1 = None
        self.hand_2 = None
        self.facing = NORTH

    def draw(self):
        self.env.tiles.draw(self.env.viewer, AGENT, self.x, self.y, light=self.env.light)
        # TODO: Draw items in hands
        # TODO: Some way to show the way it's facing

    def move_north(self):
        pass

    def move_east(self):
        pass

    def move_south(self):
        pass

    def move_west(self):
        pass

    def turn_left(self):
        pass

    def turn_right(self):
        pass

    def pick_up(self):
        pass

    def put_down(self):
        pass

    def swap_hands(self):
        pass

    def use_item(self):
        pass


class DiscreteEnv(gym.Env):
    def __init__(self, seed=2021):
        self.seed = seed
        self.viewer = None
        self.map = np.zeros((18, 18), dtype=int)
        self.tiles = Tileset()
        self.light = 1.0
        self.time = 0
        self.day = 0
        self.season = 0

    def reset(self):
        self._cleanup()
        self._init()

    def step(self, action):
        """
        Takes one step of action in the environment and returns the resulting state and reward information
        :param action:
        :return:
        """

        # time update
        # self.time += 0.5
        if self.time < 40:
            self.light = 1.0
        elif self.time < 50:
            self.light = 1.0 - (self.time - 40) * 0.05
        elif self.time < 70:
            self.light = 0.5
        elif self.time < 80:
            self.light = 0.5 + (self.time - 70) * 0.05
        else:
            self.light = 1.0
            self.time = 0
            self.day += 1
            if self.day >= 20:
                self.day = 0
                self.season += 1
                if self.season > 3:
                    self.season = 0

        # Results
        state = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        reward = 0
        is_done = False
        debug = {}
        return np.array(state), reward, is_done, debug

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

        # Highlight

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

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
            plant = Plant(self, idx, rnd.randint(1, 16), rnd.randint(4, 15), rnd.randint(0, 3))
            self.plants.append(plant)

        # Stones
        self.stones = []
        for idx in range(15):
            plant = Stone(self, idx, rnd.randint(1, 16), rnd.randint(4, 15))
            self.plants.append(plant)

        self.foods = []

    def _cleanup(self):
        """
        clean up memory and resources
        """


if __name__ == "__main__":
    test_env = DiscreteEnv()
    test_env.reset()
    steps = 0

    while True:
        st, rwd, done, dbg = test_env.step(None)
        test_env.render()
        time.sleep(0.02)
