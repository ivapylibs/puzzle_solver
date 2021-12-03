# =========================== puzzle.solver.base ==========================
#
# @class    puzzle.solver.base
#
# @brief    A basic puzzle solver that just puts puzzle pieces where they
#           belong based on sequential ordering.
#
# =========================== puzzle.solver.base ==========================
#
# @file     base.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/06 [created]
#           2021/08/12 [modified]
#
# =========================== puzzle.solver.base ==========================

# ===== Environment / Dependencies
#

# ===== Helper Elements
#


#
# =========================== puzzle.solver.base ==========================
#

class Base:

    def __init__(self, theSol, thePuzzle):
        """
        @brief  Constructor for the base puzzle solver class.  Assumes
                existence of solution state and current puzzle state.
        Args:
            theSol: The solution board.
            thePuzzle: The actual board.
        """

        self.desired = theSol  # @< Desired/solution puzzle board.
        self.current = thePuzzle  # @< Actual puzzle board.

    def setCurrBoard(self, theBoard):
        self.current = theBoard

    def takeTurn(self, thePlan=None):
        """
        @brief  Perform a single puzzle solving action, which move a piece
                to its correct location. Base class is empty and should be
                overloaded.

        Args:
            thePlan: A specific desired action plan.

        """

        pass

#
# =========================== puzzle.solver.base ==========================
