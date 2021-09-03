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
            puzzle.simulator.testing.basic02/basic03_withSolver.py
        It:
        1. uses the manager to process the measured board and get the correspondence
            between it and the solution board
        2. use the solver to process the correspondence to establish the next action goal
        3. The planner needs to plan to achieve the goal
        """
        # manager process the measured board to establish the association
        self.manager.process(meaBoard)

        # solver use the association to plan which puzzle to move to where
        # TODO: still need to determine what should be the output of the solver
        self.solver.setMatch(self.manager.pAssignments)
        solver_out = self.solver.takeTurn()

        # plan a sequence of actions to achieve whatever is the solver_out
        return self.plan(solver_out)


    def plan(self, solver_out):
        raise NotImplementedError("The base class assume no method for action planning.\
             Needs to be overwritten by children classes")

class Planner_step(Planner_Base):
    def __init__(self, solver: solver_base, manager: manager) -> None:
        super().__init__(solver, manager) 
    
    def plan(self, solver_out):
        """
        For this class, the idea is to use a predefined sequence of actions 
        to accomplish what is planned by the solver
        """
        pass
    