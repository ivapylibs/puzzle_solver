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

from puzzle.board import board
from puzzle.piece.edge import edge


#
# ================================ puzzle.clusters.byShape ================================
#
class byShape(board):

    # =============================== puzzle.clusters.byShape ==============================
    #
    # @brief  Constructor for the byShape class.
    #
    #
    def __init__(self, thePuzzle, extractor=edge()):
        super(byShape, self).__init__(thePuzzle)

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
            self.feature[piece.id] = [self.feaExtractor.shapeFeaExtract(piece.edge[i]) for i in range(len(piece.edge))]

#
# ================================ puzzle.clusters.byShape ================================
