#======================= puzzle.piece.matchSimilar =======================
#
# @brief    Sub-classes of this derived class branch use similarity
#           scores for determining wheter two puzzle pieces match.
#
# Similarity scores are interpreted as bigger being more likely to be a
# match and smaller being less likely to be a match. There will usually
# be lower and upper limits for the similarity score.
#
#======================= puzzle.piece.matchSimilar =======================

#
# @file     matchSimilar.py
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
#======================= puzzle.piece.matchSimilar =======================

from puzzle.piece.matcher import matcher


class matchSimilar(matcher):

  #============================ matchSimilar ===========================
  #
  # @brief  Constructor for the puzzle piece matchSimilar class.
  #
  # @todo
  # Decide later if initialization/calibration data can be passed
  # at instantiation.
  #
  def __init__(self, tau=float('inf')):
    super(matcher, self).__init__(tau)

  #=========================== setMeasurement ==========================
  #
  # @brief  Pass along to the instance a measurement of the puzzle
  #         piece.
  #
  def setMeasurement(self, y):
    super().setMeasurement(y)
    self.y = self.process(y)

  #============================== compare ==============================
  #
  # @brief  Compare a measured puzzle piece to this particular one. 
  #
  def compare(self, yM):

    # score is to calculate the similarity while it will call the feature extraction process inside
    simScore = self.score(yM)

    return simScore > self.tau

#
#======================= puzzle.piece.matchSimilar =======================
