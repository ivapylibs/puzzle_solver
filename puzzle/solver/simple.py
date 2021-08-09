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

  #============================== takeTurn =============================
  #
  # @brief  Perform a single puzzle solving action, which move a piece
  #         to its correct location.
  #
  def takeTurn(self):

    # Check current puzzle against desired for correct placement boolean
    # Find lowest false instance
    # Establish were it must be placed to be correct.
    # Move to that location.

    pass

#
#========================== puzzle.solver.simple =========================
