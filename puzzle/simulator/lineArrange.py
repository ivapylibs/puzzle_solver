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
# TODO: need to build a foo manager (and possibily also a solver) for the lineArrange puzzle in this file
# 
#========================= puzzle.simulator.lineArrange ========================

#===== Dependencies / Packages 
#
from dataclasses import dataclass
from puzzle import solver
import matplotlib.pyplot as plt
import numpy as np
import copy

from puzzle.board import board
from puzzle.simulator.basic import basic
from puzzle.simulator.agent import Agent
from puzzle.builder.arrangement import arrangement, paramArrange
from puzzle.solver.base import base as solver_base
from puzzle.manager import manager, managerParms

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

        solBoard = copy.deepcopy(initBoard)    
        for i in range(len(solBoard.pieces)):
            rLoc = solBoard.pieces[i].rLoc
            solBoard.pieces[i].setPlacement((targetX, rLoc[1]))
        return lineArrange(initBoard, solBoard, initHuman)


class manager_LA(manager):
    """
    Develop a simplified manager tailored to the lineArrange task

    Compare to a real manager, it:
    1. Establish the correspondence either by hard code or by order, instead of using the visual clue
       The reason is all puzzle pieces in this simulator have the same outlook 
    """
    def __init__(self, solution:board, theParms:managerParms=managerParms()):
        super().__init__(solution, theParms=theParms)

        # self.solution             The solution board
        # self.pAssignment          meas-to-sol association

    def set_pAssignments(self, pAssign):
        """
        set the pAssignments via the user input. 
        The pAssignment is the data storing the meaBoard/solBoard association

        @param[in]  pAssign         a list of (2, ). mea-to-sol index
        """
        # sanity check. The solution piece idx can not exceed the 
        # the size of the stored solution board
        sol_idxs = np.array([pair[1] for pair in pAssign])
        assert np.amax(sol_idxs) <= self.solution.size() - 1,\
            "The assignment exceed the stored solution board size. \
                Please check the assignment"
        
        # store the assignment
        self.pAssignments = pAssign

    def set_pAssignments_board(self, meaBoard:board):
        """
        This function create an assignment from a measured board,
        which assumes that the measured and the solution are one-to-one corresponded.
        i.e. the first piece of the meaBoard corresponds to the first piece of the solBoard,
            the second to second, etc.

        @param[in]  meaBoard        The measured board, whose size must be the same as the self.solution(board)
        """
        # sanity check - size should match
        assert meaBoard.size() == self.solution.size(),\
            "The input board size does not match the solution's"

        # process the board to get a pAssign
        pAssign = []
        for i in range(meaBoard.size()):
            pAssign.append(np.array([i, i]))
        
        # set the assignment
        self.set_pAssignments(pAssign)
    
    def measure(self, *argv):
        """
        Overwrite the measure. Now this simulator does not it to really measure the board,
        because all pieces have the same visual clue.

        Assginement will be directly set
        """
        return 

class solver_LA(solver_base):
    """
    Develop a simple solver tailored to the lineArrange task

    Compared to the solver.simple, it:
    1. Will output the planned action in some form instead of directly change the board
        TODO: This function might be worthy to be developed into a new solver base class for the future use. 
            But put it here for now
    2. Only planByOrder since here we don't really have any score with all puzzles having the same appearance
    """

    def __init__(self, theSol, thePuzzle):
        super().__init__(theSol, thePuzzle)
    
    def setMatch(self, match):
        pass
    
    def takeTurn(self, thePlan=None):
        pass
        return super().takeTurn(thePlan=thePlan)

    def planByOrder(self):
        pass
        return None