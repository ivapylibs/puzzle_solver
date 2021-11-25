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

import math
import sys
from copy import deepcopy
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from puzzle.simulator.simTimeless_yunzhi import SimTimeLess, ParamSTL


# from puzzle.simulator.agent import Agent

@dataclass
class ParamST(ParamSTL):
    """
    @param  canvas_H            The height of the whole scene
    @param  canvas_W            The width of the whole scene
    ------------------ Below are related to time ---------------------
    @param  delta_t             Unit: s(econd). The time length for a simulation step.
    @param  speed               Unit: pixel/s. The speed of the agent movement
    @param  static_duration     Unit: s(econd). The duration of the static actions
    """
    delta_t: float = 0.1
    speed: float = 100
    static_duration: float = 0.1


class SimTime(SimTimeLess):
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

    def __init__(self, thePuzzle, agent, param=ParamST()):

        super(SimTime, self).__init__(thePuzzle, agent, param=param)

        # # self.init_board = init_board  # Initial board
        # # self.sol_board = sol_board  # Solution board
        # # self.cur_board = init_board  # The current board. At first it will be only the inital board
        # self.agent = agent  # The agent
        # self.param = param

        # self.canvas = np.zeros(
        #     (self.param.canvas_H, self.param.canvas_W, 3),
        #     dtype=np.uint8
        # )

        self.timer = self.param.static_duration  # The timer

        # let the agent be aware of the solution board
        # self.agent.setSolBoard(sol_board)
        self.frames = []
        self.pointer = 0

    def _move_step(self, target_loc):
        """
        Move a step given the target location
        Note that the target location might not be reachable within a step's time length

        @param[in]  target_loc          The target location of the "move"

        @param[out] flag_finish        Binary. Indicator of whether the target location
                                        has been reached
        """
        # distance
        delta_x = target_loc[0] - self.agent.app.rLoc[0]
        delta_y = target_loc[1] - self.agent.app.rLoc[1]
        distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

        # determine where to end up
        step_loc = np.array([-1, -1])
        if distance >= self.param.delta_t * self.param.speed:
            x_step = delta_x * (self.param.delta_t * self.param.speed) / distance
            y_step = delta_y * (self.param.delta_t * self.param.speed) / distance
            step_loc[0] = self.agent.app.rLoc[0] + x_step
            step_loc[1] = self.agent.app.rLoc[1] + y_step
            flag_finish = False
        else:
            step_loc[0] = target_loc[0]
            step_loc[1] = target_loc[1]
            flag_finish = True

        # execute
        self.agent.execute(self.puzzle, "move", step_loc)

        return flag_finish

    def _pause_step(self):
        assert self.cache_action != "move"

        # If have not been executed, then execute first before pause there
        if abs(self.timer - self.param.static_duration) < 1e-04:
            self.agent.execute(self.puzzle, self.cache_action, self.cache_arg)

        # Continue to run the timer
        self.timer -= self.param.delta_t

        # If timer is below zero, then it is up!
        if self.timer < 0:
            flag_finish = True
        else:
            flag_finish = False

        return flag_finish

    def reset_cache(self):
        self.cache_arg = None
        self.cache_action = None
        self.timer = self.param.static_duration

    def simulate_step(self):
        """
        Overwrite the simulate_step function
        """

        if self.cache_action is None:
            return True
        elif self.cache_action == "move":
            # The move action
            flag_finish = self._move_step(self.cache_arg)
        else:
            # The static actions
            flag_finish = self._pause_step()

        # if the cached action is finished, reset the cache and the timer
        if flag_finish:  # < Whether the current cached action has been finished
            self.reset_cache()

        return flag_finish

    def update(self, i):

        if self.pointer < len(self.frames):
            im = self.im.set_data(self.frames[self.pointer])
            self.pointer = self.pointer + 1
        else:
            im = self.im.set_data(self.frames[len(self.frames) - 1])

        return im,

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
        self.im = plt.imshow(theImage)

        self.frames.append(theImage)

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

            cache_image = self.puzzle.toImage(np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY,
                                              BOUNDING_BOX=False)

            self.frames = []

            while 1:

                finish_flag = self.simulate_step()

                if finish_flag is True:
                    cache_image = self.puzzle.toImage(np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY,
                                                      BOUNDING_BOX=False)

                theImage = deepcopy(cache_image)
                self.agent.placeInImage(theImage, CONTOUR_DISPLAY=False)

                self.frames.append(theImage)
                # im.set_data(theImage)
                # self.fig.canvas.draw()
                # plt.pause(0.001)

                if finish_flag is True:
                    self.pointer = 0
                    break

            # plt.show()

        self.animation = FuncAnimation(self.fig, self.update, frames=30000, interval=1)

        self.fig.canvas.mpl_connect('key_press_event', press)

        # plt.draw()
        plt.show()
