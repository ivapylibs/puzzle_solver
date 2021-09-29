# ================================ puzzle.piece.histogram ================================
#
# @brief    Use histogram for color to establish similarity.
#
# ================================ puzzle.piece.histogram ================================
#
# @file     histogram.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/29 [created]
#
#
# ================================ puzzle.piece.histogram ================================

import math

# ===== Environment / Dependencies
#
import cv2
import numpy as np

from puzzle.piece.matchDifferent import matchDifferent
from puzzle.piece.template import template


#
# ================================ puzzle.piece.histogram ================================
#
class histogram(matchDifferent):

    def __init__(self, tau=0.3):
        """
        @brief  Constructor for the puzzle piece histogram class.

        Args:
            tau: The threshold param to determine difference.
        """

        super(histogram, self).__init__(tau)

    @staticmethod
    def colorFeaExtract(piece):
        """
        @brief  Compute histogram from the raw puzzle data.
                See https://opencv-tutorial.readthedocs.io/en/latest/histogram/histogram.html

        Args:
            piece: A template instance saving a piece's info.

        Returns:
            The histogram.
        """

        if issubclass(type(piece), template):
            if piece.y.colorFea:
                return piece.y.colorFea
        else:
            raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

        # cv2.imshow('demo', piece.y.mask)
        # cv2.waitKey()

        # Convert to HSV space for comparison, see https://theailearner.com/tag/cv2-comparehist/
        img_hsv = cv2.cvtColor(piece.y.image, cv2.COLOR_RGB2HSV)
        hist = cv2.calcHist([img_hsv], [0, 1], piece.y.mask, [180, 256], [0, 180, 0, 256])
        cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        # hist = cv2.calcHist([piece.y.image], [0, 1, 2], piece.y.mask, [32, 32, 32],
        #                     [0, 256, 0, 256, 0, 256])

        piece.y.colorFea = hist

        return hist

    def process(self, piece):
        """
        @brief  Process the puzzle piece.

        Returns:
            The processed feature.
        """

        return histogram.colorFeaExtract(piece)

    def score(self, piece_A, piece_B):
        """
        @brief  Compute the score between two passed puzzle piece data.

        Args:
            piece_A: A template instance saving a piece's info.
            piece_B: A template instance saving a piece's info.

        Returns:
            Distance.
        """

        hist_A = self.process(piece_A)
        hist_B = self.process(piece_B)

        # Range from 0-1, smaller means closer
        distance = cv2.compareHist(hist_A, hist_B, cv2.HISTCMP_BHATTACHARYYA)

        return distance

#
# ================================ puzzle.piece.histogram ================================
