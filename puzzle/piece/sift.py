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
from skimage.measure import ransac
from skimage.transform import warp, AffineTransform

from puzzle.utils.dataProcessing import calculateMatches
from puzzle.piece.matchSimilar import matchSimilar
from puzzle.piece.template import template, puzzleTemplate
#
#================================ puzzle.piece.moments ================================
#
class sift(matchSimilar):

  def __init__(self, tau=5):
    '''
    @brief  Constructor for the puzzle piece moments class.
    '''
    super(sift, self).__init__(tau)

  def process(self, y):
    '''
    @brief  Compute sift features from the raw puzzle data.
    See https://github.com/adumrewal/SIFTImageSimilarity/blob/master/SIFTSimilarityInteractive.ipynb

    :param y: A template instance or puzzleTemplate instance saving a piece's info.
    :return: The sift keypoints & the sift descriptor.
    '''
    if isinstance(y, template):
      y = y.y
    elif isinstance(y, puzzleTemplate):
      pass
    else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')


    sift_builder = cv2.SIFT_create()

    theImage = np.zeros_like(y.image)
    theImage[y.rcoords[1], y.rcoords[0], :] = y.appear
    kp, des = sift_builder.detectAndCompute(theImage, None)

    # @todo Maybe it is wrong to put y.image here
    # kp, des = sift_builder.detectAndCompute(y.image, None)

    return kp, des

  def score(self, yA, yB):
    '''
    @brief  Compute the score between two passed puzzle piece data.

    :param yA: A template instance or puzzleTemplate instance saving a piece's info.
    :param yB: A template instance or puzzleTemplate instance saving a piece's info.
    :return: The distance between the two passed puzzle piece data.
    '''
    kp_A, des_A= self.process(yA)
    kp_B, des_B= self.process(yB)

    matches = calculateMatches(des_A, des_B)
    distance = 100 * (len(matches) / min(len(kp_A), len(kp_B)))

    return distance

  def compare(self, yA, yB):
    '''
    @brief Compare between two passed puzzle piece data.
    See https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_matcher/py_matcher.html
    and https://scikit-image.org/docs/dev/auto_examples/transform/plot_matching.html

    :param yA: A template instance or puzzleTemplate instance saving a piece's info.
    :param yB: A template instance or puzzleTemplate instance saving a piece's info.
    :return: Comparison result & rotation angle(degree).
    '''

    # score is to calculate the similarity while it will call the feature extraction process inside
    kp_A, des_A = self.process(yA)
    kp_B, des_B = self.process(yB)

    matches = calculateMatches(des_A, des_B)
    distance = 100 * (len(matches) / min(len(kp_A), len(kp_B)))

    # estimate affine transform model using all coordinates

    src = []
    dst = []

    for match in matches:
      src.append(kp_A[match[0].queryIdx].pt)
      dst.append(kp_B[match[0].trainIdx].pt)
    src = np.array(src)
    dst = np.array(dst)
    model = AffineTransform()
    model.estimate(src, dst)

    # robustly estimate affine transform model with RANSAC
    model_robust, inliers = ransac((src, dst), AffineTransform, min_samples=3,
                                   residual_threshold=2, max_trials=100)
    outliers = inliers == False

    return distance > self.tau, model_robust.rotation

#
#================================ puzzle.piece.sift ================================
