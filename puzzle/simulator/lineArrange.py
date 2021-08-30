#========================= puzzle.simulator.lineArrange ========================
#
# @class    puzzle.simulator.lineArrange
#
# @brief    This is the simulation of a simple puzzle playing task, the goal of 
#           which is to arrange a set of puzzle pieces into a line.
#           The simulation will be used for test the activity analyzer's capacity
#
#========================= puzzle.simulator.lineArrange ========================

#
# @file     lineArrange.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/08/29
#
#
#========================= puzzle.simulator.lineArrange ========================

#===== Dependencies / Packages 
#
from dataclasses import dataclass
import matplotlib.pyplot as plt
import copy

from puzzle.board import board
from puzzle.simulator.basic import basic
from puzzle.simulator.agent import Agent
from puzzle.builder.arrangement import arrangement, paramArrange

#===== Class Helper Elements
#

@dataclass
class paramLineArrange(paramArrange):
    pass

#
#========================= puzzle.simulator.lineArrange ========================
#

class lineArrange(basic):
    """
    The simulation class of an agent finishing a simple line-arrangement puzzle task,
    in which the goal is to arrange all the puzzle pieces into a line.

    @param[in]  initBoard           board. The initial puzzle board. 
    @param[in]  solBoard            board. The solution puzzle board. 
    @param[in]  initHuman           Agent. The initial human agent.
    @param[in]  theFig              plt.Figure. The figure handle for display. Optional
    @param[in]  params              paramLineArrange. Other parameters
    """
    def __init__(self, initBoard:board, solBoard:board, initHuman:Agent,
                 theFig=None, params:paramLineArrange=paramLineArrange()):
        super().__init__(initBoard, theFig=theFig)

        self.initBoard = initBoard
        self.solBoard = solBoard

        # the arrangement instance for comparing the current status with the solutions
        self.progress_checker = arrangement(solBoard=solBoard, theParams=params)

        # the hand
        self.hand = None
    

    def display(self):
        pass

    def simulate_step(self, delta_t):
        """
        Simulate a step.

        @param[in]  delta_t      The time length of the simulation step
        @param[out]  state       The current state. 
        @param[out]  activity    The current activity.
        """
        # 1. execute a step
        # 2. output the state, and activity
        state = self._get_state()
        activity = self._get_activity()
        return state, activity

    def _get_state(self):
        pass

    def _get_activity(self):
        pass

    
    @staticmethod
    def buildSameX(targetX, initBoard:board, initHuman:Agent, theFig=None, 
                    params:paramLineArrange=paramLineArrange()):
        """
        @brief: Build a lineArrange instance in which the goal is to simply horizontally move 
                the puzzle pieces from the initial location to a target X coordinate.
        
        @param[in]  targetX          The target X coordinate
        """

        solBoard = copy.deepcopy(initBoard)     # TODO: should be built according to the targetX and the initBoard
        return lineArrange(initBoard, solBoard, initHuman)
