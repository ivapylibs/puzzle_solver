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

  def __init__(self, tau=5):
    """
    @brief  Constructor for the puzzle piece matchDifferent class.

    Args:
      tau: The threshold param to determine difference.
    """

    super(moments, self).__init__(tau)

  def process(self, piece):
    """
    @brief  Compute moments from the raw puzzle data.
    See https://learnopencv.com/shape-matching-using-hu-moments-c-python/

    Args:
      piece: A template instance saving a piece's info.

    Returns:
      A list of huMoments value.
    """
    if isinstance(piece, template):
      moments = cv2.moments(piece.y.contour)
      huMoments = cv2.HuMoments(moments)
      for i in range(7):
        huMoments[i] = -1 * math.copysign(1.0, huMoments[i]) * math.log10(1e-06 + abs(huMoments[i]))

      return huMoments
    else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')


  def score(self, piece_A, piece_B):
    """
    @brief  Compute the score between two passed puzzle piece data.

    Args:
      piece_A: A template instance saving a piece's info.
      piece_B: A template instance saving a piece's info.

    Returns:
      Distance.
    """

    huMoments_A= self.process(piece_A)
    huMoments_B= self.process(piece_B)

    distance = np.sum(np.abs(huMoments_B-huMoments_A))

    return distance



#
#================================ puzzle.piece.moments ================================
