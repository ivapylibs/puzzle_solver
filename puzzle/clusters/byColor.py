# ================================ puzzle.clusters.byColor ================================
#
# @brief    Extract color features for all the pieces in a given puzzle board.
#
# ================================ puzzle.clusters.byColor ================================
#
# @file     byColor.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/29 [created]
#
#
# ================================ puzzle.clusters.byColor ================================

from dataclasses import dataclass

# ===== Environment / Dependencies
#
import numpy as np
import scipy.cluster.hierarchy as hcluster

from puzzle.builder.board import board
from puzzle.piece.histogram import histogram


# ===== Helper Elements
#

@dataclass
class paramColorCluster:
    taudist: float = 0.5


#
# ================================ puzzle.clusters.byColor ================================
#
class byColor(board):

    def __init__(self, thePuzzle, extractor=histogram(), theParams=paramColorCluster):
        """
        @brief  Constructor for the byColor class.

        Args:
            thePuzzle: The input puzzle board.
            extractor: A matcher instance.
            theParams: The param for threshold.
        """

        super(byColor, self).__init__(thePuzzle)

        self.feaExtractor = extractor

        # A list of feature for all the puzzle pieces
        self.feature = []
        self.feaLabel = []

        self.params = theParams

    def process(self):
        """
        @ brief Extract color features from the data.
        """

        for piece in self.pieces:
            self.feature.append(self.feaExtractor.colorFeaExtract(piece).flatten())
        self.feature = np.array(self.feature)

        # From 0
        yhat = hcluster.fclusterdata(self.feature, self.params.taudist, criterion="distance") - 1

        # # Define the model
        # model = sklearn.cluster.MeanShift()

        # # Assign a cluster to each example, from 0
        # yhat = model.fit_predict(self.feature)

        self.feaLabel = yhat

#
# ================================ puzzle.clusters.byColor ================================
