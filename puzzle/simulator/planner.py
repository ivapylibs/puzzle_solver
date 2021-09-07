#========================= puzzle.simulator.planner ========================
#
# @class    puzzle.simulator.planner
#
# @brief    The planner for producing the action sequence to solve the puzzle
#
#========================= puzzle.simulator.planner ========================

#
# @file     planner.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/02
#
#
#========================= puzzle.simulator.planner ========================

import numpy as np
from puzzle.solver.base import base as solver_base 
from puzzle.manager import manager

class Planner_Base():
    """
    Define the general planner planning process. 

    @param[in]  manager         The manager instance responsible for determining the \
                                association between the measured board and the solution board
    @param[in]  solver          The solver instance responsible for plan the execution order
    """
    def __init__(self, solver:solver_base, manager:manager) -> None:
        self.solver = solver
        self.manager = manager
    
    def setSolBoard(self, solBoard):
        self.solver.desired = solBoard
        self.manager.solution = solBoard
    
    def process(self, meaBoard):
        """
        The process procedure when observed an measured board

        Part of the process follow the one in the 
            puzzle.simulator.testing.basic02/basic03_60pSolver.py
        It:
        1. uses the manager to process the measured board and get the correspondence
            between it and the solution board
        2. use the solver to process the correspondence to establish the next action goal
        3. The planner needs to plan to achieve the goal

        @param[in]  meaBoard            The measured board

        @param[out] flag                Whether the new actions is successfully planned
        @param[out] actions             a list of actions
        @param[out] action_args         the argument of the action.
                                        If the argument is about a piece, then return the piece idx
                                        If the argument is a location, then it is direcly an 2-d array
        """
        # manager process the measured board to establish the association
        self.manager.process(meaBoard)

        # solver use the association to plan which next puzzle to move to where
        self.solver.current = meaBoard
        self.solver.setMatch(self.manager.pAssignments)
        flag, puzzle_idx, target_loc = self.solver.takeTurn()

        # if no plan found, probably means the puzzle is solved
        if not flag:
            return flag, None, None
        # plan a sequence of actions to achieve whatever is the solver_out
        else:
            actions, action_args = self.plan(meaBoard, puzzle_idx, target_loc)
            return flag, actions, action_args


    def plan(self, puzzle_idx, target_loc):
        raise NotImplementedError("The base class assume no method for action planning.\
             Needs to be overwritten by children classes")

class Planner_Fix(Planner_Base):
    """
    This class assumes a fixed sequence of actions to accomplish the puzzle piece assembly plan
    produced by the solver. The fixed sequence is:
    1. Move from initial location to the puzzle piece location
    2. pick the piece
    3. Move to the target piece location (with the piece in hand)
    4. Place the piece
    5. Move back to the initial location

    @param[in]  solver              The solver 
    @param[in]  manager             The manager
    @param[in]  init_location       The agent's initial location. Can be None when creating the instance,
                                    But needs to be set before planning. Default is None 
    """
    def __init__(self, solver: solver_base, manager: manager, init_loc=None) -> None:
        super().__init__(solver, manager) 
        self.init_loc = init_loc
    
    def plan(self, meaBoard, puzzle_idx, target_loc):
        """
        Hard code the sequence of action to move a piece in the board to the target location

        @param[in]  meaboard            The measured board
        @param[in]  puzzle_idx          The index of the next puzzle piece to assemble in the meaBoard
        @param[in]  target_loc          The target location of the selected puzzle piece

        @param[out] actions             The list of action labels to assemble the selected piece
        @param[out] action_args         The list of arguments for the action. If an action needs no argument, 
                                        then store None
        """
        assert self.init_loc is not None,"Please set the init location first"

        actions = []
        action_args = []

        # move to the piece location
        actions.append('move')
        action_args.append(meaBoard.pieces[puzzle_idx].rLoc)
        # pick
        actions.append('pick')
        action_args.append(puzzle_idx)
        # move to the target location
        actions.append('move')
        action_args.append(target_loc)
        # place
        actions.append('place')
        action_args.append(None)
        # move back tot the initial location
        actions.append('move')
        action_args.append(self.init_loc)

        return actions, action_args
    
    def setInitLoc(self, init_loc:np.ndarray):
        """
        Set the init location

        @param[in]  init_loc        The initial location
        """
        self.init_loc = init_loc

    