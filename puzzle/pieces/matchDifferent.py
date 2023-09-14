#======================= puzzle.piece.matchDifferent =======================
#
# @brief    Sub-classes of this derived class branch use difference
#           scores for determining whether two puzzle pieces match.
#
# Difference scores are interpreted as smaller being more likely to be a
# match and bigger being less likely to be a match. There will usually
# be lower and upper limits for the difference score.
#
#======================= puzzle.piece.matchDifferent =======================

# @file     matchDifferent.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/24 [created]
#           2021/07/30 [modified]
#
#
#======================= puzzle.piece.matchDifferent =======================

#====== Environment / Dependencies
#
import numpy as np
import cv2
import math
from puzzle.piece.matcher import MatchDifferent
from puzzle.piece.template import Template

#
#---------------------------------------------------------------------------
#================================= Distance ================================
#---------------------------------------------------------------------------
#
class Distance(MatchDifferent):

  #============================= __init__ ============================
  #
  def __init__(self, tau=35):
    """!
    @brief  Constructor for the puzzle piece histogram class.

    @param[in]  tau     Threshold param to determine difference.
    """
    super(Histogram, self).__init__(tau)

  #========================== extractFeature =========================
  #
  def extractFeature(piece):
    """
    @brief Get the puzzle centroid value.

    @param[in]  piece   Puzzle piece to use.

    @param[out]  Centroid "feature" vector.
    """

    if issubclass(type(piece), Template):
      return piece.y.XXXcentroidXXX
    else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

#
#---------------------------------------------------------------------------
#================================ Histogram ================================
#---------------------------------------------------------------------------
#

class Histogram(MatchDifferent):

  #============================= __init__ ============================
  #
  def __init__(self, tau=0.3):
    """
    @brief  Constructor for the puzzle piece histogram class.

    @param[in]  tau     Threshold param to determine difference.
    """

    super(Histogram, self).__init__(tau)

  #========================== extractFeature =========================
  #
  def extractFeature(piece): 
    """
    @brief Compute histogram from the raw puzzle data.
           See https://opencv-tutorial.readthedocs.io/en/latest/histogram/histogram.html

    @param[in]  piece   Puzzle piece to use.

    @param[out] Puzzle piece histogram.
    """

    if issubclass(type(piece), Template):
      if len(piece.y.colorFea) > 0:
        return piece.y.colorFea
    else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

    #DEBUG
    #cv2.imshow('demo', piece.y.mask)
    #cv2.waitKey()

    # Convert to HSV space for comparison, see https://theailearner.com/tag/cv2-comparehist/
    img_hsv = cv2.cvtColor(piece.y.image, cv2.COLOR_RGB2HSV)
    hist = cv2.calcHist([img_hsv], [0, 1], piece.y.mask, [int(180/3), int(256/2)], [0, 180, 0, 256])
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    piece.y.colorFea = hist

    return hist

  #============================== score ==============================
  #
  def score(self, piece_A, piece_B):
    """
    @brief Compute the score between two passed puzzle piece data.

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] Distance of the feature vectors. (Overload if not proper).
    """

    hist_A = self.extractFeature(piece_A)
    hist_B = self.extractFeature(piece_B)

    # Range from 0-1, smaller means closer
    return  cv2.compareHist(hist_A, hist_B, cv2.HISTCMP_BHATTACHARYYA)

#
#---------------------------------------------------------------------------
#================================= Moments =================================
#---------------------------------------------------------------------------
#

class Moments(MatchDifferent):
  """! 
  @brief    Uses shape moments to establish similarity.
  """

  #============================= __init__ ============================
  #
  def __init__(self, tau=5):
    """
    @brief  Constructor for the puzzle piece moments class.

    @param[in]  tau     Threshold param to determine difference.
    """

    super(Moments, self).__init__(tau)

  #========================== extractFeature =========================
  #
  def extractFeature(piece):
    """
    @brief  Compute moments from the raw puzzle data.


    See https://learnopencv.com/shape-matching-using-hu-moments-c-python/

    @param[in]  piece   Puzzle piece to use.

    @param[out]  huMoments: A list of huMoments value.
    """

    if issubclass(type(piece), Template):
      if len(piece.y.shapeFea) > 0:
        return piece.y.shapeFea
    else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

    moments = cv2.moments(piece.y.contour)
    huMoments = cv2.HuMoments(moments)
    for i in range(7):
      huMoments[i] = -1 * math.copysign(1.0, huMoments[i]) * math.log10(1e-06 + abs(huMoments[i]))

    piece.y.shapeFea = huMoments
    return huMoments

  #============================== score ==============================
  #
  def score(self, piece_A, piece_B):
    """
    @brief Compute the score between two passed puzzle piece data.

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] Distance of the feature vectors. (Overload if not proper).
    """

    huMoments_A = self.extractFeature(piece_A)
    huMoments_B = self.extractFeature(piece_B)

    distance = np.sum(np.abs(huMoments_B - huMoments_A))

    return distance

#
#---------------------------------------------------------------------------
#=================================== PCA ===================================
#---------------------------------------------------------------------------
#
class PCA(MatchDifferent):
  """!
  @brief    Uses pca to calculate rotation.

  WHAT IS GOING ON HERE???  WHAT IS THE POINT OF THIS PARTICULAR MATCHER??
  """

  #============================= __init__ ============================
  #
  def __init__(self, tau=-float('inf')):
    """!
    @brief  Constructor for the puzzle piece histogram class.

    @param[in]  tau     Threshold param to determine difference.
    """
    super(PCA, self).__init__(tau)

  #========================== extractFeature =========================
  #
  def extractFeature(piece):
    """
    @brief Get the puzzle centroid value.

    @param[in]  piece   Puzzle piece to use.

    @param[out]  The rotation of the main vector.
    """
    if issubclass(type(piece), Template):
      yfeature = PCA.getEig(piece.y.contour)
      theta = np.arctan2(yfeature['v1'][1], yfeature['v1'][0])

      return theta
    else:
      raise TypeError('Input type is wrong. Need template instance or puzzleTemplate instance.')

  #============================== score ==============================
  #
  def score(self, piece_A, piece_B):
    """
    @brief Compute the score between two passed puzzle piece data.

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] The degree distance between passed puzzle piece data and stored puzzle piece. (counter-clockwise)
    """

    theta_A = self.extractFeature(piece_A)
    theta_B = self.extractFeature(piece_B)

    return np.rad2deg(theta_B - theta_A)

  #=============================== getEig ==============================
  #
  @staticmethod
  def getEig(img):
    """
    @brief  To find the major and minor axes of a blob.


    See https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/ for details.

    Args: img: A mask image.

    Returns: dict: A dict saving centerized points, main vectors.
    """
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
#======================= puzzle.piece.matchDifferent =======================
