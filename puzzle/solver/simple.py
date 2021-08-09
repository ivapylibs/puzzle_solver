#========================== puzzle.solver.simple =========================
#
# @class    puzzle.solver.simple
#
# @brief    A basic puzzle solver that just puts puzzle pieces where they
#           belong based on sequential ordering.
#
# @file     simple.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   WHO WHO
# @date     2021/08/06  [started]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================== puzzle.solver.simple =========================

#===== Dependencies / Packages
#
WHAT

#===== Class Helper Elements
#


#
#========================== puzzle.solver.simple =========================
#

class simple:

  #=============================== simple ==============================
  #
  # @brief  Constructor for the simple puzzle solver.  Assumes existence
  #         of solution state and current puzzle state, with both
  #         already sequentially ordered to match.
  #
  def __init__(self, theSol, thePuzzle):

    self.desired = theSol               # @< Desired/solution puzzle state.
    self.current = thePuzzle            # @< Actual puzzle state.
    self.match   = 1:theSol.length()    # @< Mapping from current to desired.

    self.plan = None

  #============================== takeTurn =============================
  #
  # @brief  Perform a single puzzle solving action, which move a piece
  #         to its correct location.
  #
  def takeTurn(self, thePlan = None):

    if not self.plan:
      if not thePlan:
        # Check current puzzle against desired for correct placement boolean
        # Find lowest false instance
        # Establish were it must be placed to be correct.
        # Move to that location.
        pass
      else:
        # Get and apply move from thePlan
        # Plans not figured out yet, so ignore for now.
        pass
    else:
      # Get and apply move from self.plan
      # Plans not figured out yet, so ignore for now.
      pass

  #============================ planOrdered ============================
  #
  # @brief      Plan is to just solve in order.
  #
  def planOrdered(self):

    self.plan = None    # EVENTUALLY NEED TO CODE. IGNORE FOR NOW.

  #=========================== planGreedyTSP ===========================
  #
  # @brief      Generate a greedy plan based on TS-like problem.
  #
  # The travelling salesman problem is to visit a set of cities in a
  # path optimal manner.  This version applies the same idea in a greed
  # manner. That involves finding the piece closest to the true
  # solution, then placing it.  After that it seearches for a piece that
  # minimizes to distance to pick and to place (e.g., distance to the
  # next piece + distance to its true location).  That piece is added to
  # the plan, and the process repeats until all pieces are planned.
  #
  def planGreedyTSP(self):

    self.plan = None    # EVENTUALLY NEED TO CODE. IGNORE FOR NOW.


#
#========================== puzzle.solver.simple =========================
