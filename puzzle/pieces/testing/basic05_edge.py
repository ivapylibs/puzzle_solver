#!/usr/bin/python3
# ============================ basic05_edge ===========================
#
# @brief    Test script for the most basic functionality of edge matcher
#           for regular puzzle pieces. (60p img)
#
# NOTE: 09/15: BROKEN CODE. NEED TO FIX.
# ============================ basic05_edge ===========================

#
# @file     basic05_edge.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/01  [created]
#
# ============================ basic05_edge ===========================

# ==[0] Prep environment
import os

import cv2
import improcessor.basic as improcessor
import matplotlib.pyplot as plt
import numpy as np
import similaritymeasures

from puzzle.parse.fromSketch import FromSketch
from puzzle.piece import Regular

from puzzle.board import Board
from puzzle.builder.gridded import Gridded, CfgGridded
from puzzle.parser import boardMeasure, CfgBoardMeasure
from puzzle.parse.fromSketch import FromSketch
from puzzle.pieces.edge import Edge
from puzzle.piece import Regular
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread('../../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread('../../../testing/data/puzzle_60p_AdSt408534841.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[1.2] Extract info from theImage & theMask to obtain a board instance
#
puzzParm = CfgBoardMeasure()
puzzParm.minArea = 5000
theLayer = boardMeasure(puzzParm)

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[1.3] Create a Grid instance and explode it into two new boards
#

print('Running through test cases. Will take a bit.')

theParams = CfgGridded()
theParams.minArea = 5000
theParams.pieceConstructor = 'Regular'
theParams.reorder = True

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams)
                                         


epImage, epBoard = theGrid.explodedPuzzle(dx=100, dy=100)

# ==[1.4] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

#improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
#                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),), cv2.dilate, (np.ones((3, 3), np.uint8),))
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),))
theMaskMea = improc.apply(epImage)

# cv2.imshow('debug', theMaskMea)
# cv2.waitKey()

theParams = CfgGridded()
print(theParams)
theParams.update(dict(minArea=1000, pieceConstructor='Regular', reorder=True))
print('Done')

theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea, theParams)

#===[1.5] Focus on a single puzzle piece and duplicate it with a new location
#

theRegular_A = theGrid.pieces[36]
theRegular_B = theGridMea.pieces[36]

# ==[2] Create a new board
#
theBoard = Board()
theBoard.addPiece(theRegular_A)
theBoard.addPiece(theRegular_B)

# ==[3] Create an edge matcher
#

theMatcher = Edge()

# ==[4] Display the new board and the comparison result.
#
print('Should see True.')
# DEBUG/IAMHERE: Crashes at this point now. Moving on.
print(theMatcher.compare(theRegular_A, theRegular_B, method=similaritymeasures.pcm))

theBoard.display()

plt.show()

#
# ============================ basic05_edge ===========================
