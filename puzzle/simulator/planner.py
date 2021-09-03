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

from puzzle.solver.base import base as solver_base 
from puzzle.manager import manager

class Base():
    """
    Define the general planner planning process. 

    @param[in]  manager         The manager instance responsible for determining the association between the measured board and the solution board
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
        """
        # manager process the measured board to establish the association
        self.manager.process(meaBoard)

        # solver use the association to plan which puzzle to move to where
        # TODO: still need to determine what should be the output of the solver
        solver_out = self.solver.takeTurn()

        # plan a sequence of actions to achieve whatever is the solver_out
        return self.plan(solver_out)


    def plan(self, solver_out):
        raise NotImplementedError("The base class assume no method for action planning. Needs to be overwritten by children classes")

class Planner_step(Base):
    def __init__(self, solver: solver_base, manager: manager) -> None:
        super().__init__(solver, manager) 
    
    def plan(self, solver_out):
        """
        For this class, the idea is to use a fixed sequence of action to 
        """
        pass
    