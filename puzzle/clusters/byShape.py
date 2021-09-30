# ================================ puzzle.clusters.byShape ================================
#
# @brief    Extract shape features for all the pieces in a given puzzle board.
#
# ================================ puzzle.clusters.byShape ================================
#
# @file     byShape.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/29 [created]
#
#
# ================================ puzzle.clusters.byShape ================================

# ===== Environment / Dependencies
#
import numpy as np
from puzzle.board import board
from puzzle.piece.moments import moments

from puzzle.piece.histogram import histogram
import sklearn.cluster

import scipy.cluster.hierarchy as hcluster

#
# ================================ puzzle.clusters.byShape ================================
#
class byShape(board):

    def __init__(self, thePuzzle, extractor=moments()):
        """
        @brief  Constructor for the byShape class.

        Args:
            thePuzzle: The input puzzle board.
            extractor: A matcher instance.
        """

        super(byShape, self).__init__(thePuzzle)

        self.feaExtractor = extractor

        # A list of feature for all the puzzle pieces
        self.feature = []
        self.feaLabel = []

    def process(self):
        """
        @ brief Extract shape features from the data.
        """

        for piece in self.pieces:
            self.feature.append(self.feaExtractor.shapeFeaExtract(piece).flatten())
        self.feature = np.array(self.feature)

        # From 0
        yhat = hcluster.fclusterdata(self.feature, 0.5, criterion="distance")-1

        self.feaLabel = yhat
#
# ================================ puzzle.clusters.byShape ================================
