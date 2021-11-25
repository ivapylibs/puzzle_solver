# ========================= puzzle.simulator.simTimeless ========================
#
# @class    puzzle.simulator.SimTimeless
#
# @brief    The simulator that simulate the puzzle solving process
#           without any time effect.
#           The agent will observe the board and attempt to solve it until finished
#
# ========================= puzzle.simulator.simTimeless ========================
#
# @file     simTimeless.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/10
#
#
# ========================= puzzle.simulator.simTimeless ========================

import sys
from copy import deepcopy
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np

from puzzle.simulator.basic import Basic


# from puzzle.simulator.agent import Agent

@dataclass
class ParamSTL:
    """
    @param canvas_H             The height of the whole scene
    @param canvas_W             The width of the whole scene
    """
    canvas_H: int = 2500  # <- The height of the scene
    canvas_W: int = 3500  # <- The width of the scene
    displacement: int = 100  # <- The unit movement of the agent


class SimTimeLess(Basic):
    """
    @brief: The timeless simulator class that simulates the puzzle solving progress.

    The class stores an initial board, a solution board, and an agent instance.
    During the simulation, the simulator will execute the following process:
    1. Let the agent observe the board
    2. Let the agent process the board, which means:
        2.1 Plan actions if don't know what to do (no more stored actions)
        2.2 Execute the next planned actions
    3. If no more process result, meaning no more plans or actions to be executed,
        then end the simulation. Otherwise repreat the above process

    @param[in]  init_board          The initial board
    @param[in]  sol_board           The solution board
    @param[in]  agent               The puzzle solving agent
    @param[in]  param               The parameters
    """

    def __init__(self, thePuzzle, agent, param=ParamSTL()):

        super(SimTimeLess, self).__init__(thePuzzle)

        # self.init_board = init_board  # Initial board
        # self.sol_board = sol_board  # Solution board
        # self.cur_board = init_board  # The current board. At first it will be only the inital board
        self.agent = agent  # The agent
        self.param = param

        self.canvas = np.zeros(
            (self.param.canvas_H, self.param.canvas_W, 3),
            dtype=np.uint8
        )

        # cached action, argument, and time
        self.cache_action = None  # The next action to execute
        self.cache_arg = None  # The next action argument

        # let the agent be aware of the solution board
        # self.agent.setSolBoard(sol_board)

    def display(self, ID_DISPLAY=True, CONTOUR_DISPLAY=True):
        """
        @brief  Displays the current puzzle board.

        Args:
            ID_DISPLAY: Flag indicating ID_DISPLAY or not.
            CONTOUR_DISPLAY: Flag indicating CONTOUR_DISPLAY or not.
        """

        if not self.fig:
            self.fig = plt.figure()

        theImage = self.puzzle.toImage(np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY, BOUNDING_BOX=False)
        self.agent.placeInImage(theImage, CONTOUR_DISPLAY=False)
        im = plt.imshow(theImage)

        def press(event):
            print('press', event.key)
            sys.stdout.flush()

            if event.key == 'up':
                self.cache_action = "move"
                self.cache_arg = np.array([0, -self.param.displacement]) + self.agent.app.rLoc
            elif event.key == 'left':
                self.cache_action = "move"
                self.cache_arg = np.array([-self.param.displacement, 0]) + self.agent.app.rLoc
            elif event.key == 'down':
                self.cache_action = "move"
                self.cache_arg = np.array([0, self.param.displacement]) + self.agent.app.rLoc
            elif event.key == 'right':
                self.cache_action = "move"
                self.cache_arg = np.array([self.param.displacement, 0]) + self.agent.app.rLoc
            elif event.key == 'z':
                self.cache_action = "pick"
                self.cache_arg = None
            elif event.key == 'c':
                self.cache_action = "place"
                self.cache_arg = None

            self.agent.execute(self.puzzle, self.cache_action, self.cache_arg)

            cache_image = self.puzzle.toImage(np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY,
                                              BOUNDING_BOX=False)

            theImage = deepcopy(cache_image)
            self.agent.placeInImage(theImage, CONTOUR_DISPLAY=False)
            plt.pause(0.001)

            im.set_data(theImage)
            self.fig.canvas.draw()

        self.fig.canvas.mpl_connect('key_press_event', press)

        plt.show()
