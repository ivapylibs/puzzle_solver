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

import matplotlib.pyplot as plt

from puzzle.builder.board import board
from puzzle.clusters.byShape import byShape
from puzzle.piece.template import template

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Create puzzle pieces.
#

theBoard = board()
for i in range(3):
    squarePiece_A = template.buildSquare(100, color=(255, 0, 0), rLoc=(200, i*150+140))
    theBoard.addPiece(squarePiece_A)

    squarePiece_B = template.buildSphere(40, color=(255, 0, 0), rLoc=(600, i*150+140))
    theBoard.addPiece(squarePiece_B)

theBoard.display(CONTOUR_DISPLAY=False, ID_DISPLAY=True)

# ==[2] Create a cluster instance and process the puzzle board.
#

theShapeCluster = byShape(theBoard)
theShapeCluster.process()

# ==[3] Display the extracted features.
#

print('Should see 6 pieces of 2 different shapes. They are clustered into 2 groups.')
print('The number of pieces:', len(theShapeCluster.feature))
print('The cluster label:', theShapeCluster.feaLabel)

plt.show()

#
# ============================ basic01_byColor ===========================
