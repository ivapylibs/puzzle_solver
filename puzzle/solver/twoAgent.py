#========================= puzzle.solver.twoAgent ========================
#
# @class    puzzle.solver.twoAgent
#
# @brief    A puzzle solver that uses two turn-taking puzzle solvers to
#           complete a puzzle problem. 
#
#========================= puzzle.solver.twoAgent ========================

#
# @file     twoAgent.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/11 [created]
#           2021/08/12 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================= puzzle.solver.twoAgent ========================

#===== Dependencies / Packages
#
from puzzle.solver.simple import simple

#===== Class Helper Elements
#


#
#========================= puzzle.solver.twoAgent ========================
#

class twoAgent(simple):

  #=============================== simple ==============================
  #
  # @brief  Derived from the simple puzzle solver, it also takes in two
  #         solver build functiond to seed with information.  Defaults
  #         to simple solvers if none given.
  #
  def __init__(self, theSol, thePuzzle, agent1 = None, agent2 = None):

    super(twoAgent, self).__init__(theSol, thePuzzle)

    if not agent1:
      agent1 = simple(theSol, thePuzzle)

    if not agent2:
      agent2 = simple(theSol, thePuzzle)

    self.agents = [agent1, agent2]      # Make a list/array.
    self.iMove = 0                     # Move index.

  #============================== takeTurn =============================
  #
  # @brief  Perform a single puzzle solving action, which move a piece
  #         to its correct location.
  #
  def takeTurn(self, thePlan = None):

    self.agents[self.iMove].takeTurn()

    if (self.iMove == 0):       # Toggle back and forth between agents.
      self.iMove = 1
    else:
      self.iMove = 0

#
#========================= puzzle.solver.twoAgent ========================
