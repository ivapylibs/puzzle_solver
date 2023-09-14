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
#
#======================= puzzle.piece.matchSimilar =======================

#===== Environment / Dependencies
#
from puzzle.piece.matcher import Matcher

# Tricks to pickle cv2.keypoint objects https://stackoverflow.com/a/48832618/5269146
import copyreg

#===== Environment / Dependencies
#
import cv2
import numpy as np
from skimage.measure import ransac
from skimage.transform import AffineTransform

from puzzle.piece.matcher import MatchSimilar
from puzzle.piece.template import Template
from puzzle.utils.dataProcessing import calculateMatches


#
#---------------------------------------------------------------------------
#=================================== SIFT ==================================
#---------------------------------------------------------------------------

def _pickle_keypoints(point):
    return cv2.KeyPoint, (*point.pt, point.size, point.angle,
                          point.response, point.octave, point.class_id)


copyreg.pickle(cv2.KeyPoint().__class__, _pickle_keypoints)


#
# ================================ puzzle.piece.moments ================================
#
class Sift(MatchSimilar):
  """!
  @brief    Uses sift features to establish similarity.
  """

  #============================= __init__ ============================
  #
  def __init__(self, tau=10, theThreshMatch=0.5):
    """!
    @brief  Constructor for the puzzle piece histogram class.

    @param[in]  tau             Threshold param to determine similarity for SIFT feature.
    @param[in]  theThreshMatch  Threshold to determine match (0-1).
    """
    self.theThreshMatch = theThreshMatch
    super(Sift, self).__init__(tau)

  #========================== extractFeature =========================
  #
  def extractFeature(piece):
    """
    @brief  Compute sift features from the raw puzzle data.

    @param[in]  piece   Puzzle piece to use.

    @param[out]  kp     SIFT keypoints.
    @param[out]  des    SIFT descriptor.
    """

    if issubclass(type(piece), Template):
      if piece.y.kpFea:
        return piece.y.kpFea
    else:
      raise ('The input type is wrong. Need a template instance.')

    # https://stackoverflow.com/questions/60065707/cant-use-sift-in-python-opencv-v4-20
    # # For opencv-python
    sift_builder = cv2.SIFT_create()

    # Focus on the puzzle piece image with mask
    theImage = np.zeros_like(piece.y.image)
    theImage[piece.y.rcoords[1], piece.y.rcoords[0], :] = piece.y.appear

    # theImage = white_balance(theImage)

    kp, des = sift_builder.detectAndCompute(theImage, None)

    piece.y.kpFea = (kp, des)

    return kp, des

  #============================== score ==============================
  #
  def score(self, piece_A, piece_B):
    """
    @brief Compute the score between two passed puzzle piece data.

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] Distance of the feature vectors. (Overload if not proper).
    """

    kp_A, des_A = self.extractFeature(piece_A)
    kp_B, des_B = self.extractFeature(piece_B)

    if des_A is None or des_B is None:
      return 0

    matches = calculateMatches(des_A, des_B, self.theThreshMatch)

    distance = 100 * (len(matches) / min(len(kp_A), len(kp_B)))

    return distance

  #============================= compare =============================
  #
  def compare(self, piece_A, piece_B):
    """
    @brief  Compare between two passed puzzle piece data.
            This member function should be overloaded. Currently returns false
            so that all comparisons fail.

    See https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_matcher/py_matcher.html
    and https://scikit-image.org/docs/dev/auto_examples/transform/plot_matching.html

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] Comparison result & rotation angle(degree) & other params.
    """

    # Score is to calculate the similarity while it will call the feature extraction process inside
    kp_A, des_A = self.process(piece_A)
    kp_B, des_B = self.process(piece_B)

    matches = calculateMatches(des_A, des_B)
    distance = 100 * (len(matches) / min(len(kp_A), len(kp_B)))

    # Estimate affine transform model using all coordinates

    if len(matches)!=0:
      src = []
      dst = []

      for match in matches:
        src.append(kp_A[match[0].queryIdx].pt)
        dst.append(kp_B[match[0].trainIdx].pt)
      src = np.array(src)
      dst = np.array(dst)

      # It only makes sense for translation if both piece images have the same origin


      src = np.array(src) + piece_A.rLoc
      dst = np.array(dst) + piece_B.rLoc


      model = AffineTransform()
      model.estimate(src, dst)

      # Note: model.translation is not 100% consistent with what we what. Use pieceLocation instead.

      return distance > self.tau, np.rad2deg(model.rotation), model.params
    else:
      return False, None, None

    ## Robustly estimate affine transform model with RANSAC. However, too slow
    # if len(src) > 3:
    #     model_robust, inliers = ransac((src, dst), AffineTransform, min_samples=3,
    #                                    residual_threshold=2, max_trials=100)
    #     outliers = inliers == False
    #
    #     # # Debug only
    #     # fig, ax = plt.subplots(nrows=1, ncols=1)
    #     # inlier_idxs = np.nonzero(inliers)[0]
    #     # src2 = np.array([[i[1]-piece_A.rLoc[1], i[0]-piece_A.rLoc[0]] for i in src])
    #     # dst2 = np.array([[i[1]-piece_B.rLoc[1], i[0]-piece_B.rLoc[0]] for i in dst])
    #     #
    #     # # Follow row, col order in plot_matches
    #     # plot_matches(ax, piece_A.y.image, piece_B.y.image, src2, dst2,
    #     #              np.column_stack((inlier_idxs, inlier_idxs)), matches_color='b')
    #     #
    #     # plt.show()
    #
    #     return distance > self.tau, np.rad2deg(model_robust.rotation), model_robust.params
    # else:
    #     return distance > self.tau, np.rad2deg(model.rotation), model.params

#
#======================= puzzle.piece.matchSimilar =======================
