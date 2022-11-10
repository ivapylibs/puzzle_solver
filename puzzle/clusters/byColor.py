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
from sklearn.cluster import AgglomerativeClustering
from sklearn import metrics
from scipy.optimize import linear_sum_assignment

from puzzle.builder.board import Board
from puzzle.piece.histogram import Histogram

# ===== Helper Elements
#

@dataclass
class ParamColorCluster:
    tauDist: float = 0.5
    cluster_num: int = 2
    cluster_mode: str = 'threshold' # 'threshold' or 'number'

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

        self.feature_dict = {}

        # A dict of featureLabel, id: label
        self.feaLabel_dict = {}

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

        if self.params.cluster_mode == 'threshold':
            # Using threshold
            model = AgglomerativeClustering(affinity='precomputed', n_clusters=None, linkage='complete', distance_threshold=self.params.tauDist).fit(distance_matrix)
        elif self.params.cluster_mode == 'number':
            model = AgglomerativeClustering(affinity='precomputed', n_clusters=self.params.cluster_num, linkage='complete').fit(distance_matrix)
        else:
            raise ValueError('Unknown cluster mode!')

        self.feaLabel = model.labels_

        for key in self.pieces:
            self.feaLabel_dict[key] = self.feaLabel[key]

        # Collect the features for each cluster
        for idx, cluster_id in enumerate(self.feaLabel):
            if cluster_id not in self.feature_dict:
                self.feature_dict[cluster_id] = []

            self.feature_dict[cluster_id].append(self.feature[idx])

        # Aggregate & normalize the features in each cluster
        for i in self.feature_dict:
            feature_processed = np.sum(np.array(self.feature_dict[i]), axis=0)
            cv2.normalize(feature_processed, feature_processed, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            self.feature_dict[i] = feature_processed

        # print(model.labels_)

    def score(self, cluster_id_pred_dict, method='label'):
        """
        @brief  Score the clustering result. See https://scikit-learn.org/stable/modules/clustering.html#overview-of-clustering-methods

        Args:
            cluster_id_pred_dict: The predicted cluster id for each piece.
            method: The method to score the clustering result. ['label', 'histogram']

        Returns:
            The score of the clustering result.
        """

        if method == 'label':
            labels_pred = []
            labels_true = []
            for k, v in cluster_id_pred_dict.items():
                labels_pred.append(v)
                labels_true.append(self.feaLabel_dict[k])

            rand_score = metrics.rand_score(labels_true, labels_pred)

            return rand_score

        elif method == 'histogram':

            # Collect the features for each cluster
            feature_pred_dict = {}
            for piece_id, cluster_id in cluster_id_pred_dict.items():
                if cluster_id not in feature_pred_dict:
                    feature_pred_dict[cluster_id] = []
                feature_pred_dict[cluster_id].append(self.feature[piece_id])

            # Aggregate & normalize the features in each cluster
            for i in feature_pred_dict:
                feature_processed = np.sum(np.array(feature_pred_dict[i]), axis=0)
                cv2.normalize(feature_processed, feature_processed, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
                feature_pred_dict[i] = feature_processed

            # Score is the sum of the distance between the aggregated features in each cluster
            distance_matrix = np.zeros((len(feature_pred_dict), len(self.feature_dict)))

            for i in range(len(feature_pred_dict)):
                for j in range(len(self.feature_dict)):
                    # https://docs.opencv.org/5.x/d8/dc8/tutorial_histogram_comparison.html
                    # https://vovkos.github.io/doxyrest-showcase/opencv/sphinx_rtd_theme/enum_cv_HistCompMethods.html
                    distance_matrix[i][j] = cv2.compareHist(feature_pred_dict[i], self.feature_dict[j], 3)

            row_ind, col_ind = linear_sum_assignment(distance_matrix, maximize=True)

            score = 0
            for i,j in zip(row_ind, col_ind):
                score += distance_matrix[i][j]

            return score





#
# ================================ puzzle.clusters.byColor ================================
