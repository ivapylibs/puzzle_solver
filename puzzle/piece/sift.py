# ================================ puzzle.piece.sift ================================
#
# @brief    Uses sift features to establish similarity.
#
# ================================ puzzle.piece.sift ================================
#
# @file     sift.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/07 [created]
#
#
# ================================ puzzle.piece.sift ================================

# Tricks to pickle cv2.keypoint objects https://stackoverflow.com/a/48832618/5269146
import copyreg

# ===== Environment / Dependencies
#
import cv2
import numpy as np
from skimage.measure import ransac
from skimage.transform import AffineTransform

from puzzle.piece.matchSimilar import matchSimilar
from puzzle.piece.template import template
from puzzle.utils.dataProcessing import calculateMatches


def _pickle_keypoints(point):
    return cv2.KeyPoint, (*point.pt, point.size, point.angle,
                          point.response, point.octave, point.class_id)


copyreg.pickle(cv2.KeyPoint().__class__, _pickle_keypoints)


#
# ================================ puzzle.piece.moments ================================
#
class sift(matchSimilar):

    def __init__(self, tau=5, theThreshMatch = 0.5):
        """
        @brief  Constructor for the puzzle piece sift class.

        Args:
            tau: The threshold param to determine similarity.
        """

        self.theThreshMatch = theThreshMatch
        super(sift, self).__init__(tau)

    @staticmethod
    def kpFeaExtract(piece):
        """
        @brief  Compute sift features from the raw puzzle data.

        Args:
            piece: A template instance saving a piece's info.

        Returns:
            The sift keypoints & the sift descriptor.

        """

        if issubclass(type(piece), template):
            if piece.y.kpFea:
                return piece.y.kpFea
        else:
            raise ('The input type is wrong. Need a template instance.')

        sift_builder = cv2.SIFT_create()

        # Focus on the puzzle piece image with mask
        theImage = np.zeros_like(piece.y.image)
        theImage[piece.y.rcoords[1], piece.y.rcoords[0], :] = piece.y.appear

        # theImage = white_balance(theImage)

        kp, des = sift_builder.detectAndCompute(theImage, None)

        piece.y.kpFea = (kp, des)

        return kp, des

    def process(self, piece):
        """
        @brief  Process the puzzle piece.

        Returns:
            The processed feature.
        """

        return sift.kpFeaExtract(piece)

    def score(self, yA, yB):
        """
        @brief  Compute the score between two passed puzzle piece data.

        Args:
            yA: A template instance saving a piece's info.
            yB: A template instance saving a piece's info.

        Returns:
            The distance between the two passed puzzle piece data.
        """

        kp_A, des_A = self.process(yA)
        kp_B, des_B = self.process(yB)

        matches = calculateMatches(des_A, des_B, self.theThreshMatch)
        distance = 100 * (len(matches) / min(len(kp_A), len(kp_B)))

        return distance

    def compare(self, piece_A, piece_B):
        """
        @brief  Compare between two passed puzzle piece data.
                See https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_matcher/py_matcher.html
                and https://scikit-image.org/docs/dev/auto_examples/transform/plot_matching.html

        Args:
            piece_A: A template instance saving a piece's info.
            piece_B: A template instance saving a piece's info.

        Returns:
            Comparison result & rotation angle(degree).
        """

        # Score is to calculate the similarity while it will call the feature extraction process inside
        kp_A, des_A = self.process(piece_A)
        kp_B, des_B = self.process(piece_B)

        matches = calculateMatches(des_A, des_B)
        distance = 100 * (len(matches) / min(len(kp_A), len(kp_B)))

        # Estimate affine transform model using all coordinates

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

        # Robustly estimate affine transform model with RANSAC
        if len(src) > 3:
            model_robust, inliers = ransac((src, dst), AffineTransform, min_samples=3,
                                           residual_threshold=2, max_trials=100)
            outliers = inliers == False

            # # Debug only
            # fig, ax = plt.subplots(nrows=1, ncols=1)
            # inlier_idxs = np.nonzero(inliers)[0]
            # src2 = np.array([[i[1]-piece_A.rLoc[1], i[0]-piece_A.rLoc[0]] for i in src])
            # dst2 = np.array([[i[1]-piece_B.rLoc[1], i[0]-piece_B.rLoc[0]] for i in dst])
            #
            # # Follow row, col order in plot_matches
            # plot_matches(ax, piece_A.y.image, piece_B.y.image, src2, dst2,
            #              np.column_stack((inlier_idxs, inlier_idxs)), matches_color='b')
            #
            # plt.show()

            return distance > self.tau, np.rad2deg(model_robust.rotation), model_robust.params
        else:
            return distance > self.tau, np.rad2deg(model.rotation), model.params

#
# ================================ puzzle.piece.sift ================================
