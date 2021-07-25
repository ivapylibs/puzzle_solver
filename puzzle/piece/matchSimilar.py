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
# @file     matchSimilar.m
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/07/24
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
  # @todo Decide later if initialization/calibration data can be passed
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
    super(matcher, self).setMeasurement(y)
    self.x = self.process(y);

  #============================== compare ==============================
  #
  # @brief  Compare a measured puzzle piece to this particular one. 
  #
  def bComp = compare(self, yM)
    xM = self.process(yM)

    simScore = self.score(xM);
    # Need to figure out how to process next step which checks whether
    # the score is indicative of similarity or not. For now, going with
    # false result.
    return (diffScore > self.tau)

#
#======================= puzzle.piece.matchSimilar =======================
