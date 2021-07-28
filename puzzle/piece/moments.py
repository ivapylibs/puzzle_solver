#================================ moments ================================
#
# @brief    Uses shape moments to establish similarity.
#
#================================ moments ================================

#
# @file     moments.m
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/07/24
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#================================ moments ================================

from puzzle.piece.matchSimilar import matchSimilar


class moments(matchSimilar):

  #=============================== moments ==============================
  #
  # @brief  Constructor for the puzzle piece matchSimilar class.
  #
  # @todo Decide later if initialization/calibration data can be passed
  # at instantiation.
  #
  def __init__(self):
    super(matchSimilar, self).__init__()

  #=========================== process ==========================
  #
  # @brief  Compute moments from the raw puzzle data.
  #
  def process(self, y):
    pass
    # PUT CODE HERE FOR THE MOMENTS OR CONTOUR EXTRACTION.
    # WHATEVER WORKS FOR OPENCV.

  #=============================== score ===============================
  #
  # @brief  Compute the score between passed puzzle piece data and
  #         stored puzzle piece.
  #
  def score(self, yM):
    pass
    # PUT THE COMPARISON PART HERE.


  #============================== compare ==============================
  #
  # @brief  Compare a measured puzzle piece to this particular one. 
  #
  def compare(self, yM):
    pass

    # IS IT POSSIBLE TO USE THE SUPER CLASS MEMBER FUNCTION, OR DOES
    # SOMETHING DIFFERENT NEED TO BE DONE?
    # WHAT MEMBER FUNCTIONS SHOULD BE OVERLOADED?

  # WHAT ELSE SHOULD BE HERE IN THE INTERFACE?
  # BUILD OUT AS NEEDED FROM THE REMOVAL OF CODE FROM THE
  # DETECTOR_PUZZLE CLASS TO HERE.

#
#================================ moments ================================
