#=========================== puzzle.piece.base ===========================
#
# @brief    The base class for puzzle piece specification or description
#           encapsulation.
#
#=========================== puzzle.piece.base ===========================

#
# @file     base.m
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/07/24
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#=========================== puzzle.piece.base ===========================


class base:

  #================================ base ===============================
  #
  # @brief  Constructor for the puzzle.piece.base class.
  #
  def __init__(self):
    self.x = []     # @< The local description of the puzzle piece.
    self.y = []     # @< The puzzle piece measurement data.

  #=========================== setMeasurement ==========================
  #
  # @brief  Pass along to the instance a measurement of the puzzle
  #         piece.
  #
  def setMeasurement(self, y):
    self.y = y

  #============================== process ==============================
  #
  # @brief  Process the raw puzzle piece data to obtain the encoded
  #         description of the piece. Use to recognize the piece given
  #         new measurements in the future.
  #
  # This member function should be overloaded.
  #
  def xM = process(self, yM):
    xM = yM

  #=============================== score ===============================
  #
  # @brief  Compute the score between passed puzzle piece data and
  #         stored puzzle piece.
  #
  # This member function should be overloaded. Currently returns NaN to
  # indicate that a score cannot be computed.
  #
  def sval = score(self, yM)
    sval = float("NaN")

  #============================== compare ==============================
  #
  # @brief  Compare a measured puzzle piece to this particular one. 
  #
  # This member function should be overloaded. Currently returns false
  # so that all comparisons fail.
  #
  def bComp = compare(self, yM)
    bComp = false

#
#=========================== puzzle.piece.base ===========================
