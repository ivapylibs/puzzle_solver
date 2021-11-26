# ========================= puzzle.simulator.planner ========================
#
# @class    puzzle.simulator.planner
#
# @brief    The planner for producing the action sequence to solve the puzzle.
# @note     Yunzhi: more like a wrapper of solver & manager in the test script.
#
# ========================= puzzle.simulator.planner ========================
#
# @file     planner.py
#
# @author   Yiye Chen,               yychen2019@gatech.edu
#           Yunzhi Lin,              yunzhi.lin@gatech.edu
# @date     2021/09/02 [created]
#           2021/11/25 [modified]
#
#
# ========================= puzzle.simulator.planner ========================

class Planner:
    def __init__(self, solver, manager):
        self.solver = solver
        self.manager = manager

    def setSolBoard(self, solBoard):
        self.solver.desired = solBoard
        self.manager.solution = solBoard

    def process(self, meaBoard, COMPLETE_PLAN=True):
        """
        @brief  Draft the action plan given the measured board.

        Args:
            meaBoard: The measured board.
            COMPLETE_PLAN: Whether to plan the whole sequence.

        Returns:
            plan(The action plan for the simulator to perform)
        """

        # manager process the measured board to establish the association
        self.manager.process(meaBoard)

        # Solver use the association to plan which next puzzle to move to where
        self.solver.current = meaBoard
        self.solver.setMatch(self.manager.pAssignments, self.manager.pAssignments_rotation)
        plan = self.solver.takeTurn(defaultPlan='order', COMPLETE_PLAN=COMPLETE_PLAN)

        return plan
