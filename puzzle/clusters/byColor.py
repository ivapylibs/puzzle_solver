#================================ puzzle.clusters.byColor ================================
#
# @brief    Extract color features for all the pieces in a given puzzle board.
#
#================================ puzzle.clusters.byColor ================================

#
# @file     byColor.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/29 [created]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#================================ puzzle.clusters.byColor ================================

#===== Environment / Dependencies
#
import cv2
import math
import numpy as np

from puzzle.piece.regular import regular, EdgeDes

from puzzle.piece.moments import moments
from puzzle.piece.edge import edge

from puzzle.board import board
#
#================================ puzzle.clusters.byColor ================================
#
class byColor(board):

  #=============================== puzzle.clusters.byColor ==============================
  #
  # @brief  Constructor for the byColor class.
  #
  #
  def __init__(self, thePuzzle, extractor=edge()):

    super(byColor, self).__init__(thePuzzle)

    self.feaExtractor = extractor

    # A dict of id & feature for all the puzzle pieces
    self.feature = {}

  #=========================== process ==========================
  #
  # @brief  Extract features from the data.
  #
  #
  def process(self):

    for piece in self.pieces:
      self.feature[piece.id] = [self.feaExtractor.colorFeaExtract(piece.edge[i]) for i in range(len(piece.edge))]

#
#================================ puzzle.clusters.byColor ================================
