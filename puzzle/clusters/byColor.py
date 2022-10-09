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
import cv2
import scipy.cluster.hierarchy as hcluster
from sklearn.cluster import AgglomerativeClustering

from puzzle.builder.board import Board
from puzzle.piece.histogram import Histogram


# ===== Helper Elements
#

@dataclass
class ParamColorCluster:
    tauDist: float = 0.5


#
# ================================ puzzle.clusters.byColor ================================
#
class ByColor(Board):

    def __init__(self, thePuzzle, extractor=Histogram(), theParams=ParamColorCluster):
        """
        @brief  Constructor for the byColor class.

        Args:
            thePuzzle: The input puzzle board.
            extractor: A matcher instance.
            theParams: The param for threshold.
        """

        super(ByColor, self).__init__(thePuzzle)

        self.feaExtractor = extractor

        # A list of feature for all the puzzle pieces
        self.feature = []
        self.feaLabel = []

        self.params = theParams

    def process(self):
        """
        @brief Extract color features from the data.
        """

        for key in self.pieces:
            piece = self.pieces[key]
            self.feature.append(self.feaExtractor.colorFeaExtract(piece).flatten())
        self.feature = np.array(self.feature)

        distance_matrix = np.zeros((len(self.feature), len(self.feature)))

        for i in range(len(self.feature)):
            for j in range(len(self.feature)):
                # https://docs.opencv.org/5.x/d8/dc8/tutorial_histogram_comparison.html
                # https://vovkos.github.io/doxyrest-showcase/opencv/sphinx_rtd_theme/enum_cv_HistCompMethods.html
                distance_matrix[i][j] = cv2.compareHist(self.feature[i], self.feature[j], 3)

        model = AgglomerativeClustering(affinity='precomputed', n_clusters=None, linkage='complete', distance_threshold=self.params.tauDist).fit(distance_matrix)
        # model = sklearn.cluster.AgglomerativeClustering(affinity='precomputed', n_clusters=2, linkage='complete').fit(distance_matrix)

        self.feaLabel = model.labels_
        # print(model.labels_)


        # It seems that the provided distance metric is not good enough.
        # # From 0
        # yhat = hcluster.fclusterdata(self.feature, self.params.tauDist, criterion="distance") - 1
        # self.feaLabel = yhat

#
# ================================ puzzle.clusters.byColor ================================
