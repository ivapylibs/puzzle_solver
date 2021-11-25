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

from copy import deepcopy
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.board import Board
from puzzle.simulator.agent import Agent


@dataclass
class ParamST():
    """
    @param canvas_H             The height of the whole scene
    @param canvas_W             The width of the whole scene
    """
    canvas_H: int = 200  # <- The height of the scene
    canvas_W: int = 200  # <- The width of the scene


class SimTimeLess():
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

    def __init__(self, init_board: Board, sol_board: Board, agent: Agent, param: ParamST = ParamST()):
        self.init_board = init_board  # Initial board
        self.sol_board = sol_board  # Solution board
        self.cur_board = init_board  # The current board. At first it will be only the inital board
        self.agent = agent  # The agent
        self.param = param

        # let the agent be aware of the solution board
        self.agent.setSolBoard(sol_board)

    def simulate(self, vis=False, vis_pause_time=1, **kwargs):
        """
        Simulate until done

        @param[in]  vis             If True, will visualize the scene after each simulation step
        @param[in]  vis_pause_time  Pause time for visualization
        @param[in]  **kwargs        The parameter for visualize function. See its API for detail
        """
        SUCCESS = True
        while (SUCCESS):
            SUCCESS = self.simulate_step()
            if vis:
                self.display(mode="scene", **kwargs)
                plt.pause(0.01)

    def simulate_step(self):
        """
        The simulation step.
        For the timeless simulator, the simulation step will fully execute the agent's next action
        """
        theSuccessFlag, action, action_arg = self.agent.process(self.cur_board, execute=True)
        return theSuccessFlag

    def display(self, mode="scene", pickColorA=None, title=None, ax=None):
        """
        Visualization. It offers the following functionality
        1. Visualize the initial board
        2. Visualize the solution board
        3. Visualize the current scene, including the agent and the current board

        @param[in]  mode            "initBoard", "solBoard", "scene"(default)
        @param[in]  pickColorA      The option to display a different color of the agent when 
                                    the agent has a puzzle piece in hand.
                                    It is only for visualization, the real color of the agent won't be changed
                                    If None(default), then will use the original agent color for visualization
        @param[in]  title           The title
        @param[in]  ax              The axis for drawing
        """
        # determine the axis
        if ax is None:
            plt.figure()
            ax = plt.gca()

        # visualization 
        canvas = np.ones(
            (self.param.canvas_H, self.param.canvas_W, 3),
            dtype=np.uint8
        ) * 255

        if mode == "initBoard":
            self.init_board.toImage(canvas, BOUNDING_BOX=False)

        elif mode == "solBoard":
            self.sol_board.toImage(canvas, BOUNDING_BOX=False)

        elif mode == "scene":
            # the current board
            self.cur_board.toImage(canvas, BOUNDING_BOX=False)

            # the agent
            if (pickColorA is not None) and (self.agent.cache_piece is not None):
                appear_cache = deepcopy(self.agent.app.y.appear)
                new_appear = np.repeat(pickColorA[np.newaxis, :], repeats=self.agent.app.y.appear.shape[0], axis=0)
                self.agent.app.y.appear = new_appear
                self.agent.placeInImage(canvas, CONTOUR_DISPLAY=False)
                self.agent.app.y.appear = appear_cache
            else:
                self.agent.placeInImage(canvas, CONTOUR_DISPLAY=False)

        ax.imshow(canvas)
        ax.set_title(title)
