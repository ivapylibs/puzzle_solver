# ======================= puzzle.piece.matchSimilar =======================
#
# @brief    Sub-classes of this derived class branch use similarity
#           scores for determining wheter two puzzle pieces match.
#
# Similarity scores are interpreted as bigger being more likely to be a
# match and smaller being less likely to be a match. There will usually
# be lower and upper limits for the similarity score.
#
# ======================= puzzle.piece.matchSimilar =======================
#
# @file     matchSimilar.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/24 [created]
#           2021/07/30 [modified]
#
#
# ======================= puzzle.piece.matchSimilar =======================

# ===== Environment / Dependencies
#
from puzzle.piece.matcher import matcher


#
# ================================ puzzle.piece.matchSimilar ================================
#
class matchSimilar(matcher):

    def __init__(self, tau=float('inf')):
        """
        @brief  Constructor for the puzzle piece matchSimilar class.

        Args:
          tau: The threshold param to determine similarity.
        """

        super(matchSimilar, self).__init__(tau)

    def compare(self, piece_A, piece_B):
        """
        @brief  Compare between two passed puzzle piece data.

        Args:
          piece_A: A template instance saving a piece's info.
          piece_B: A template instance saving a piece's info.

        Returns:
          Comparison result
        """

        # score is to calculate the similarity while it will call the feature extraction process inside
        simScore = self.score(piece_A, piece_B)

        return simScore > self.tau

#
# ======================= puzzle.piece.matchSimilar =======================
