#================================ puzzle.piece.moments ================================
#
# @brief    Uses shape moments to establish similarity.
#
#================================ puzzle.piece.moments ================================

#
# @file     moments.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/24 [created]
#           2021/07/28 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#================================ puzzle.piece.moments ================================

#===== Environment / Dependencies
#
import cv2
import math
import numpy as np

from puzzle.piece.matchDifferent import matchDifferent
from puzzle.piece.template import template, puzzleTemplate
#
#================================ puzzle.piece.moments ================================
#
class moments(matchDifferent):

  #=============================== puzzle.piece.moments ==============================
  #
  # @brief  Constructor for the puzzle piece moments class.
  #
  def __init__(self, tau=-float('inf')):
    super(moments, self).__init__(tau)

  #=========================== process ==========================
  #
  # @brief  Compute moments from the raw puzzle data.
  #         See https://learnopencv.com/shape-matching-using-hu-moments-c-python/
  #
  # @param[in]  y    A template instance or puzzleTemplate instance saving a piece's info.
  #
  # @param[out]  huMoments    A list of huMoments value
  #
  def process(self, y):

    if isinstance(y, template):
      y = y.y
    elif isinstance(y, puzzleTemplate):
      pass
    else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

    moments = cv2.moments(y.contour)
    huMoments = cv2.HuMoments(moments)
    for i in range(7):
      huMoments[i] = -1 * math.copysign(1.0, huMoments[i]) * math.log10(1e-06+abs(huMoments[i]))

    return huMoments

  #=============================== score ===============================
  #
  # @brief  Compute the score between two passed puzzle piece data.
  #
  # @param[in]  yA    A template instance or puzzleTemplate instance saving a piece's info.
  # @param[in]  yB    A template instance or puzzleTemplate instance saving a piece's info.
  #
  # @param[out]  distance    The distance between the two passed puzzle piece data.
  #
  def score(self, yA, yB):

    huMoments_A= self.process(yA)
    huMoments_B= self.process(yB)

    distance = np.sum(np.abs(huMoments_B-huMoments_A))

    return distance



#
#================================ puzzle.piece.moments ================================
