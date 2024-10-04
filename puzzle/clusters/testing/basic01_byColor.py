#!/usr/bin/python3
# ============================ basic01_byColor ===========================
#
# @brief    Test script for basic functionality of byColor
#
# ============================ basic01_byColor ===========================

#
# @file     basic01_byColor.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/29  [created]
#
# ============================ basic01_byColor ===========================


# ==[0] Prep environment
import os
import copy
import matplotlib.pyplot as plt

from puzzle.builder.board import Board
from puzzle.clusters.byColor import ByColor
from puzzle.piece.template import Template


fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Create puzzle pieces.
#

theBoard = Board()
for i in range(3):
    squarePiece_A = Template.buildSquare(100, color=(255, 0, 0), rLoc=(200, i * 150 + 140))
    theBoard.addPiece(squarePiece_A)

    squarePiece_B = Template.buildSquare(100, color=(0, 255, 0), rLoc=(600, i * 150 + 140))
    theBoard.addPiece(squarePiece_B)

    squarePiece_C = Template.buildSquare(100, color=(0, 255, 255), rLoc=(1000, i * 150 + 140))
    theBoard.addPiece(squarePiece_C)

# theBoard.display(CONTOUR_DISPLAY=False, ID_DISPLAY=True)

# ==[2] Create a cluster instance and process the puzzle board.
#

theColorCluster = ByColor(theBoard)
theColorCluster.process()

# ==[3] Display the extracted features.
#

print('Should see 9 pieces of 3 different colors. They are clustered into 3 groups.')
print('The number of pieces:', len(theColorCluster.feature))
print('The cluster label:', theColorCluster.feaLabel)

# Copy and paste a new board but with the cluster label displayed.
theBoard2 = copy.deepcopy(theBoard)
for key in theBoard2.pieces:
    theBoard2.pieces[key].id = theColorCluster.feaLabel[key]

theBoard2.display(CONTOUR_DISPLAY=True, ID_DISPLAY=True)

plt.show()

#
# ============================ basic01_byColor ===========================
