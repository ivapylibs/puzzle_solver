#================================ puzzle.piece.pca ================================
#
# @brief    Uses pca to calculate rotation.
#
#================================ puzzle.piece.pca ================================

#
# @file     pca.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/03 [created]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#================================ puzzle.piece.pca ================================

#===== Environment / Dependencies
#
import cv2
import math
import numpy as np

from puzzle.piece.matchDifferent import matchDifferent

#
#================================ puzzle.piece.pca ================================
#
class pca(matchDifferent):

  #=============================== puzzle.piece.pca ==============================
  #
  # @brief  Constructor for the puzzle piece matchDifferent class.
  #
  # @todo
  # Decide later if initialization/calibration data can be passed
  # at instantiation.
  #
  def __init__(self, y =None, tau=float('inf')):
    super(pca, self).__init__(y, tau)

  #=========================== process ==========================
  #
  # @brief  Compute moments from the raw puzzle data.
  #         See https://learnopencv.com/shape-matching-using-hu-moments-c-python/
  #
  # @param[in]  y    A puzzleTemplate instance saving a piece's info
  #
  # @param[out]  theta    The rotation of the main vector.
  #
  def process(self, y):
    yfeature = pca.getEig(y.contour)
    theta = np.arctan2(yfeature['v1'][1], yfeature['v1'][0])

    return theta

  #=============================== score ===============================
  #
  # @brief  Compute the score between passed puzzle piece data and
  #         stored puzzle piece.
  #
  # @param[in]  yM    A puzzleTemplate instance saving a passed puzzle piece's info
  #
  # @param[out]  distance    The degree distance between passed puzzle piece data and
  #                          stored puzzle piece. (counter-clockwise)
  #
  def score(self, yM):

    theta_A= self.process(self.y)
    theta_B= self.process(yM)

    distance = np.rad2deg(theta_B - theta_A)

    return distance

  # ============================== getEig ==============================
  #
  # @brief  To find the major and minor axes of a blob.
  #         See https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/ for details.
  #
  # @param[in]   img       A mask image
  # @param[out]  dict      A dict saving centerized points, main vectors
  #
  @staticmethod
  def getEig(img):
    y, x = np.nonzero(img)
    x = x - np.mean(x)
    y = y - np.mean(y)
    coords = np.vstack([x, y])
    cov = np.cov(coords)
    evals, evecs = np.linalg.eig(cov)
    sort_indices = np.argsort(evals)[::-1]
    v1 = evecs[:, sort_indices[0]]  # Eigenvector with largest eigenvalue
    v2 = evecs[:, sort_indices[1]]

    dict = {
      'x': x,
      'y': y,
      'v1': v1,
      'v2': v2,
    }

    return dict

#
#================================ puzzle.piece.pca ================================
