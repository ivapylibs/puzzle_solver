#=========================== puzzle.solver.base ==========================
#
# @class    puzzle.solver.base
#
# @brief    A basic puzzle solver that just puts puzzle pieces where they
#           belong based on sequential ordering.
#
#=========================== puzzle.solver.base ==========================

# @file     base.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   WHO WHO
# @date     2021/08/06  [started]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#=========================== puzzle.solver.base ==========================

#===== Dependencies / Packages
#
WHAT

#===== Class Helper Elements
#


#
#=========================== puzzle.solver.base ==========================
#

class base:

  #================================ base ===============================
  #
  # @brief  Constructor for the base puzzle solver class.  Assumes
  #         existence of solution state and current puzzle state.
  #
  def __init__(self, theSol, thePuzzle):

    self.desired = theSol               # @< Desired/solution puzzle state.
    self.current = thePuzzle            # @< Actual puzzle state.

  #============================== takeTurn =============================
  #
  # @brief  Perform a single puzzle solving action, which move a piece
  #         to its correct location. Base class is empty and should be
  #         overloaded.
  #
  def takeTurn(self, thePlan = None):
    pass

#
#=========================== puzzle.solver.base ==========================
