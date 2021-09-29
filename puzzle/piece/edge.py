# ================================ puzzle.piece.edge ================================
#
# @brief    Uses edge features to establish similarity.
#
# ================================ puzzle.piece.edge ================================

#
# @file     edge.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/26 [created]
#
#
# ================================ puzzle.piece.edge ================================

# ===== Environment / Dependencies
#
import cv2
import numpy as np

from puzzle.piece.matchDifferent import matchDifferent
from puzzle.piece.regular import regular, EdgeDes


#
# ================================ puzzle.piece.edge ================================
#
class edge(matchDifferent):

    def __init__(self, tau_shape=100, tau_color=400):
        """
        @brief  Constructor for the puzzle piece edge class.
                150 for lab space/400 for RGB space
        Args:
            tau_shape: The threshold for the shape feature.
            tau_color: The threshold for the color feature.
        """

        super(edge, self).__init__()

        self.tau_shape = tau_shape
        self.tau_color = tau_color

    @staticmethod
    def shapeFeaExtract(edge, method=None):
        """
        @brief  Extract the edge shape feature from an input image of the edge.

        Args:
            edge: An EdgeDes instance.
            method: The comparison method, we have two modes: type or shape coords.

        Returns:
            Shape feature.
        """

        if method == 'type':
            shapeFea = edge.type
        else:
            y, x = np.nonzero(edge.mask)
            shapeFea = np.hstack((x.reshape(-1, 1), y.reshape(-1, 1)))

        return shapeFea

    @staticmethod
    def colorFeaExtract(edge, feaLength=300):
        """
        @brief  Extract the edge color feature from an input image of the edge.

        Args:
            edge:  An EdgeDes instance.
            feaLength: The resized feature vector length setting.

        Returns:
            The resized feature vector.
        """
        y, x = np.nonzero(edge.mask)

        # Extract the valid pts
        pts = edge.image[y, x]

        # Expand dim for further processing
        feaOri = np.expand_dims(pts, axis=0)

        # Resize to a unit length
        feaResize = cv2.resize(feaOri, (feaLength, 1))

        # # # @todo Yunzhi: May need to double check the color space
        # feaResize = cv2.cvtColor(feaResize, cv2.COLOR_RGB2Lab)

        return feaResize.astype('float32')

    def process(self, y, method=None):
        """
        @brief  Compute features from the data.

        Args:
          y: An EdgeDes instance.
          method: The method option.

        Returns:
          The shape & color feature vector.
        """

        feature_shape = edge.shapeFeaExtract(y, method=method)
        feature_color = edge.colorFeaExtract(y)

        return [feature_shape, feature_color]

    def score(self, piece_A, piece_B, method='type'):
        """
        @brief  Compute the score between two passed puzzle piece data.

        Args:
            piece_A: A template instance saving a piece's info.
            piece_B: A template instance saving a piece's info.
            method: We use some built-in functions in similaritymeasures
                    (pcm/frechet_dist/area_between_two_curves/curve_length_measure/dtw)
                    or just the types of the edges.

        Returns:
            The shape & color distance between the two passed data.

        """

        def dis_shape(feature_shape_A, feature_shape_B, method=method):

            if method == 'type':
                if feature_shape_A == feature_shape_B:
                    distance = 0
                else:
                    distance = float('inf')
            else:
                distance = method(feature_shape_A, feature_shape_B)
            # For dtw
            if isinstance(distance, tuple):
                distance = distance[0]
            return distance

        def dis_color(feature_color_A, feature_color_B):

            distance = np.mean(np.sum((feature_color_A[0] - feature_color_B[0]) ** 2, axis=1) ** (1. / 2))

            return distance

        distance_shape = []
        distance_color = []

        if type(piece_A) != type(piece_B):
            raise TypeError('Input should be of the same type.')
        else:
            if isinstance(piece_A, regular):

                for i in range(4):
                    feature_shape_A, feature_color_A = self.process(piece_A.edge[i], method=method)
                    feature_shape_B, feature_color_B = self.process(piece_B.edge[i], method=method)

                    distance_shape.append(dis_shape(feature_shape_A, feature_shape_B, method=method))
                    distance_color.append(dis_color(feature_color_A, feature_color_B))

            elif isinstance(piece_A, EdgeDes):
                feature_shape_A, feature_color_A = self.process(piece_A, method=method)
                feature_shape_B, feature_color_B = self.process(piece_B, method=method)
                distance_shape.append(dis_shape(feature_shape_A, feature_shape_B, method=method))
                distance_color.append(dis_color(feature_color_A, feature_color_B))

            else:
                raise TypeError('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

        return distance_shape, distance_color

    def compare(self, piece_A, piece_B, method='type'):
        """
        @brief  Compare between two passed puzzle piece data.

        Args:
            piece_A: A template instance saving a piece's info.
            piece_B: A template instance saving a piece's info.
            method: The method option.

        Returns:
          The comparison result.
        """
        # score is to calculate the similarity while it will call the feature extraction process inside

        distance_shape, distance_color = self.score(piece_A, piece_B, method=method)

        if (np.array(distance_shape) < self.tau_shape).all() and (np.array(distance_color) < self.tau_color).all():
            return True
        else:
            return False

#
# ================================ puzzle.piece.edge ================================
