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

# ===== Environment / Dependencies
#

from puzzle.board import board
from puzzle.piece.edge import edge


#
# ================================ puzzle.clusters.byColor ================================
#
class byColor(board):

    # =============================== puzzle.clusters.byColor ==============================
    #
    # @brief  Constructor for the byColor class.
    #
    #
    def __init__(self, thePuzzle, extractor=edge()):
        super(byColor, self).__init__(thePuzzle)

        self.feaExtractor = extractor

        # A dict of id & feature for all the puzzle pieces
        self.feature = {}

    # =========================== process ==========================
    #
    # @brief  Extract features from the data.
    #
    #
    def process(self):
        for piece in self.pieces:
            self.feature[piece.id] = [self.feaExtractor.colorFeaExtract(piece.edge[i]) for i in range(len(piece.edge))]

#
# ================================ puzzle.clusters.byColor ================================
