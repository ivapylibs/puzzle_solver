#========================= puzzle.piece.matcher =========================
#
# @brief    Derived class from puzzle piece template that adds
#           operations for comparing puzzle pieces and performing puzzle
#           solving.  This class is a base-type class and most of the
#           member functions will do nothing and require overloading.
#           The ones that don't should be for some generic
#           functionality.
#
#========================= puzzle.piece.matcher =========================

#
# @file     matcher.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/25 [created]
#           2021/07/31 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================= puzzle.piece.matcher =========================

from puzzle.piece.template import template

#
#========================= puzzle.piece.matcher =========================
#

class matcher(template):

  #============================== matcher ==============================
  #
  # @brief  Constructor for the puzzle.piece.matcher class.
  #
  def __init__(self, y = None, tau = float("NaN")):

    super(matcher, self).__init__(y)

    self.tau = tau  # @< Threshold to use when comparing, if given.

  #============================== process ==============================
  #
  # @brief  Process the raw puzzle piece data to obtain the encoded
  #         description of the piece. Use to recognize the piece given
  #         new measurements in the future.
  #
  # This member function should be overloaded.
  #
  def process(self, yM):
    pass

  #=============================== score ===============================
  #
  # @brief  Compute the score between passed puzzle piece data and
  #         stored puzzle piece.
  #
  # This member function should be overloaded. Currently returns NaN to
  # indicate that a score cannot be computed.
  #
  def score(self, yM):
    # @note
    # Yunzhi: since this function should be overloaded. It is better to raise an error here.
    raise NotImplementedError

  #============================== compare ==============================
  #
  # @brief  Compare a measured puzzle piece to this particular one. 
  #
  # This member function should be overloaded. Currently returns false
  # so that all comparisons fail.
  #
  def compare(self, yM):
    # @note
    # Yunzhi: since this function should be overloaded. It is better to raise an error here.
    raise NotImplementedError
#
#========================= puzzle.piece.matcher =========================
