#================================ moments ================================
#
# @brief    Uses shape moments to establish similarity.
#
#================================ moments ================================

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
#================================ moments ================================

import cv2
import math
import numpy as np

from puzzle.piece.matchDifferent import matchDifferent


class moments(matchDifferent):

  #=============================== moments ==============================
  #
  # @brief  Constructor for the puzzle piece matchSimilar class.
  #
  # @todo
  # Decide later if initialization/calibration data can be passed
  # at instantiation.
  #
  def __init__(self, y =None, tau=float('inf')):
    super(moments, self).__init__(y, tau)

  #=========================== process ==========================
  #
  # @brief  Compute moments from the raw puzzle data.
  #         See https://learnopencv.com/shape-matching-using-hu-moments-c-python/
  #
  # @param[in]  y    a dataclass saving a piece's info
  #
  # @param[out]  huMoments    a list of huMoments value
  #
  def process(self, y):

    moments = cv2.moments(y.mask)
    huMoments = cv2.HuMoments(moments)
    for i in range(7):
      huMoments[i] = -1 * math.copysign(1.0, huMoments[i]) * math.log10(1e-06+abs(huMoments[i]))

    return huMoments

  #=============================== score ===============================
  #
  # @brief  Compute the score between passed puzzle piece data and
  #         stored puzzle piece.
  #
  # @param[in]  yM    a dataclass saving a passed puzzle piece's info
  #
  # @param[out]  distance    score between passed puzzle piece data and
  #                          stored puzzle piece.
  #
  def score(self, yM):

    huMoments_A= self.process(self.y)
    huMoments_B= self.process(yM)

    distance = np.sum(np.abs(huMoments_B-huMoments_A))

    return distance


  #============================== compare ==============================
  #
  # @brief  Compare a measured puzzle piece to this particular one. 
  #
  # @param[in]  yM    a puzzleTemplate instance saving a passed puzzle piece's info
  #
  # @param[out]       directly call the function from the super class
  #
  def compare(self, yM):

    return super().compare(yM)


#
#================================ moments ================================
