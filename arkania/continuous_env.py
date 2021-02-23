"""
The continuous version
TODO: Implement this later... eventually
"""

import numpy as np
import gym
# from gym.utils import colorize, EzPickle


class ContinuousEnv(gym.Env):

    def __init__(self):
        self.reset()

    def _destroy(self):
        """
        clean up memory and resources
        :return:
        """
        pass

    def reset(self):
        """
        This actually does the initialization
        :return:
        """
        self._destroy()
        # initialize world

    def step(self, action):
        """
        Takes one step of action in the environment and returns the resulting state and reward information
        :param action:
        :return:
        """
        state = [1, 2, 3]
        reward = 0
        done = False
        debug = {}
        return np.array(state), reward, done, debug

    def render(self, mode='human'):
        pass

