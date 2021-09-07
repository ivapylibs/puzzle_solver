#================================ puzzle.piece.sift ================================
#
# @brief    Uses sift features to establish similarity.
#
#================================ puzzle.piece.sift ================================

#
# @file     sift.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/07 [created]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#================================ puzzle.piece.sift ================================

#===== Environment / Dependencies
#
import cv2
import math
import numpy as np

from puzzle.utils.dataProcessing import calculateMatches

from puzzle.piece.matchSimilar import matchSimilar
from puzzle.piece.template import template, puzzleTemplate
#
#================================ puzzle.piece.moments ================================
#
class sift(matchSimilar):

  #=============================== puzzle.piece.moments ==============================
  #
  # @brief  Constructor for the puzzle piece moments class.
  #
  def __init__(self, tau=5):
    super(sift, self).__init__(tau)

  #=========================== process ==========================
  #
  # @brief  Compute sift features from the raw puzzle data.
  #         See https://github.com/adumrewal/SIFTImageSimilarity/blob/master/SIFTSimilarityInteractive.ipynb
  #
  # @param[in]  y    A template instance or puzzleTemplate instance saving a piece's info.
  #
  # @param[out]  kp    The sift keypoints.
  # @param[out]  des    The sift descriptor.
  #
  def process(self, y):

    if isinstance(y, template):
      y = y.y
    elif isinstance(y, puzzleTemplate):
      pass
    else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')


    sift_builder = cv2.SIFT_create()
    kp, des = sift_builder.detectAndCompute(y.image, None)

    return kp, des

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

    kp_A, des_A= self.process(yA)
    kp_B, des_B= self.process(yB)

    matches = calculateMatches(des_A, des_B)
    distance = 100 * (len(matches) / min(len(kp_A), len(kp_B)))

    return distance



#
#================================ puzzle.piece.sift ================================
