#====================== puzzle.piece.matchDifferent ======================
#
# @brief    Sub-classes of this derived class branch use similarity
#           scores for determining wheter two puzzle pieces match.
#
# Difference scores are interpreted as smaller being more likely to be a
# match and bigger being less likely to be a match. There will usually
# be lower and upper limits for the difference score.
#
#====================== puzzle.piece.matchDifferent ======================

#
# @file     matchDifferent.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/24 [created]
#           2021/07/30 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#====================== puzzle.piece.matchDifferent ======================

#===== Environment / Dependencies
#
from puzzle.piece.matcher import matcher

#
#========================= puzzle.piece.matchDifferent =========================
#
class matchDifferent(matcher):

  #=========================== matchDifferent ==========================
  #
  # @brief  Constructor for the puzzle piece matchDifferent class.
  #
  # @todo
  # Decide later if initialization/calibration data can be passed
  # at instantiation.
  #
  def __init__(self, y = None, tau=-float('inf')):
    super(matchDifferent, self).__init__(y, tau)

  #============================== compare ==============================
  #
  # @brief  Compare a measured puzzle piece to this particular one. 
  #
  # @param[in]  yM    A puzzleTemplate instance saving a passed puzzle piece's info
  #
  # @param[out]       Return comparison result
  #
  def compare(self, yM):

    # score is to calculate the similarity while it will call the feature extraction process inside
    diffScore = self.score(yM)

    return diffScore < self.tau

#
#====================== puzzle.piece.matchDifferent ======================
