# ================================ puzzle.piece.pca ================================
#
# @brief    Uses pca to calculate rotation.
#
# ================================ puzzle.piece.pca ================================
#
# @file     pca.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/03 [created]
#
#
# ================================ puzzle.piece.pca ================================

# ===== Environment / Dependencies
#
import numpy as np

from puzzle.piece.matchDifferent import MatchDifferent
from puzzle.piece.template import Template


#
# ================================ puzzle.piece.pca ================================
#
class PCA(MatchDifferent):

    def __init__(self, tau=-float('inf')):
        """
        @brief  Constructor for the puzzle piece pca class.

        Args:
            tau: The threshold param to determine difference.
        """

        super(PCA, self).__init__(tau)

    def process(self, piece):
        """
        @brief  Compute PCA feature from the raw puzzle data.

        Args:
            piece: A puzzleTemplate instance saving a passed puzzle piece's info

        Returns:
            The rotation of the main vector.
        """

        if issubclass(type(piece), Template):
            yfeature = PCA.getEig(piece.y.contour)
            theta = np.arctan2(yfeature['v1'][1], yfeature['v1'][0])

            return theta
        else:
            raise TypeError('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

    def score(self, piece_A, piece_B):
        """
        @brief  Compute the score between two passed puzzle piece data.

        Args:
            piece_A: A template instance saving a piece's info.
            piece_B: A template instance saving a piece's info.

        Returns:
            distance: The degree distance between passed puzzle piece data and stored puzzle piece. (counter-clockwise)
        """

        theta_A = self.process(piece_A)
        theta_B = self.process(piece_B)

        distance = np.rad2deg(theta_B - theta_A)

        return distance

    @staticmethod
    def getEig(img):
        """
        @brief  To find the major and minor axes of a blob.
                See https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/ for details.

        Args:
            img: A mask image.

        Returns:
            dict: A dict saving centerized points, main vectors.
        """
        y, x = np.nonzero(img)
        x = x - np.mean(x)
        y = y - np.mean(y)
        coords = np.vstack([x, y])
        cov = np.cov(coords)
        evals, evecs = np.linalg.eig(cov)
        sort_indices = np.argsort(evals)[::-1]
        v1 = evecs[:, sort_indices[0]]  # Eigenvector with largest eigenvalue
        v2 = evecs[:, sort_indices[1]]

        dict = {
            'x': x,
            'y': y,
            'v1': v1,
            'v2': v2,
        }

        return dict

#
# ================================ puzzle.piece.pca ================================
