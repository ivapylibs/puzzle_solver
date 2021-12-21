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

from dataclasses import dataclass

# ===== Environment / Dependencies
#
import numpy as np
import scipy.cluster.hierarchy as hcluster

from puzzle.builder.board import Board
from puzzle.piece.edge import Edge
from puzzle.piece.moments import Moments


# ===== Helper Elements
#

@dataclass
class ParamShapeCluster:
    tauDist: float = 0.5


#
# ================================ puzzle.clusters.byShape ================================
#
class ByShape(Board):

    def __init__(self, thePuzzle, extractor=Moments(), theParams=ParamShapeCluster):
        """
        @brief  Constructor for the byShape class.

        Args:
            thePuzzle: The input puzzle board.
            extractor: A matcher instance.
        """

        super(ByShape, self).__init__(thePuzzle)

        self.feaExtractor = extractor

        # A list of feature for all the puzzle pieces
        self.feature = []
        self.feaLabel = []

        self.params = theParams

    def process(self):
        """
        @ brief Extract shape features from the data.
        """

        if issubclass(type(self.feaExtractor), Edge):
            for piece in self.pieces:
                # Currently, the label is based on the type of the piece edge
                self.feature.append(self.feaExtractor.shapeFeaExtract(piece, method='type').flatten())
                num = np.count_nonzero(self.feature[-1] == 3)
                self.feaLabel.append(num)
        else:

            for piece in self.pieces:
                self.feature.append(self.feaExtractor.shapeFeaExtract(piece).flatten())
            self.feature = np.array(self.feature)

            yhat = hcluster.fclusterdata(self.feature, self.params.tauDist, criterion="distance") - 1
            self.feaLabel = yhat

#
# ================================ puzzle.clusters.byShape ================================
