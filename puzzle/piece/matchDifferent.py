# ====================== puzzle.piece.matchDifferent ======================
#
# @brief    Sub-classes of this derived class branch use similarity
#           scores for determining wheter two puzzle pieces match.
#
# Difference scores are interpreted as smaller being more likely to be a
# match and bigger being less likely to be a match. There will usually
# be lower and upper limits for the difference score.
#
# ====================== puzzle.piece.matchDifferent ======================
#
# @file     matchDifferent.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/24 [created]
#           2021/07/30 [modified]
#
#
# ====================== puzzle.piece.matchDifferent ======================

# ===== Environment / Dependencies
#
from puzzle.piece.matcher import matcher


#
# ========================= puzzle.piece.matchDifferent =========================
#
class matchDifferent(matcher):

    def __init__(self, tau=-float('inf')):
        """
        @brief  Constructor for the puzzle piece matchDifferent class.

        Args:
          tau: The threshold param to determine difference.
        """

        super(matchDifferent, self).__init__(tau)

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
        diffScore = self.score(piece_A, piece_B)

        return diffScore < self.tau

#
# ====================== puzzle.piece.matchDifferent ======================
