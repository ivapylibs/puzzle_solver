# ========================= puzzle.solver.twoAgent ========================
#
# @class    puzzle.solver.twoAgent
#
# @brief    A puzzle solver that uses two turn-taking puzzle solvers to
#           complete a puzzle problem. 
#
# ========================= puzzle.solver.twoAgent ========================
#
# @file     twoAgent.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/11 [created]
#           2021/08/12 [modified]
#
#
# ========================= puzzle.solver.twoAgent ========================

# ===== Environment / Dependencies
#

import numpy as np

from puzzle.solver.simple import simple


# ===== Helper Elements
#


#
# ========================= puzzle.solver.twoAgent ========================
#

class twoAgent(simple):

    def __init__(self, theSol, thePuzzle, agent1=None, agent2=None):
        """
        @brief  Derived from the simple puzzle solver, it also takes in two
                solver build functiond to seed with information.  Defaults
                to simple solvers if none given.
        Args:
            theSol: The solution board.
            thePuzzle: The actual board.
            agent1: The agent 1.
            agent2: The agent 2.
        """

        super(twoAgent, self).__init__(theSol, thePuzzle)

        if agent1 is None:
            agent1 = simple(theSol, thePuzzle)

        if agent2 is None:
            agent2 = simple(theSol, thePuzzle)

        self.agents = [agent1, agent2]  # Make a list/array.
        self.iMove = 0  # Move index.

    def setMatch(self, match):
        """
        @brief  Set up the match

        Args:
            match: The match between the id in the measured board and the solution board.
        """

        for agent in self.agents:
            agent.match = np.array(match)

    # ============================== takeTurn =============================
    #
    # @brief  Perform a single puzzle solving action, which move a piece
    #         to its correct location.
    #
    def takeTurn(self, thePlan=None, defaultPlan='order'):
        """

        Args:
            thePlan: A specific desired action plan.
            defaultPlan: The default plan strategy.

        Returns:
            plan (The action plan)
        """

        print(f'It is agent {self.iMove}\'s turn:')

        plan = self.agents[self.iMove].takeTurn(thePlan=thePlan, defaultPlan=defaultPlan)

        if (self.iMove == 0):  # Toggle back and forth between agents.
            self.iMove = 1
        else:
            self.iMove = 0

        return plan

#
# ========================= puzzle.solver.twoAgent ========================
