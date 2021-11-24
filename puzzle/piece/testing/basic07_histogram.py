#!/usr/bin/python3
# ============================ basic06_histogram ===========================
#
# @brief    Test script for the most basic functionality of histogram features
#           for puzzle pieces. (60p img)
#
# ============================ basic06_histogram ===========================

#
# @file     basic06_histogram.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/29  [created]
#
# ============================ basic06_histogram ===========================

# ==[0] Prep environment
import os

import cv2
import improcessor.basic as improcessor
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.board import Board
from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.parser.fromLayer import FromLayer, ParamPuzzle
from puzzle.parser.fromSketch import FromSketch
from puzzle.piece.histogram import Histogram
from puzzle.piece.regular import Regular
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_60p_AdSt408534841.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer(ParamPuzzle(areaThresholdLower=5000))

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[1.3] Create an Grid instance and explode it into two new boards
#

print('Running through test cases. Will take a bit.')

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                         theParams=ParamGrid(areaThresholdLower=5000, pieceConstructor=Regular,
                                                             reorder=True))

epImage, epBoard = theGrid.explodedPuzzle(dx=100, dy=100)

# ==[1.4] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                           cv2.dilate, (np.ones((3, 3), np.uint8),)
                           )
theMaskMea = improc.apply(epImage)

# cv2.imshow('debug', theMaskMea)
# cv2.waitKey()

theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea,
                                            theParams=ParamGrid(areaThresholdLower=1000, pieceConstructor=Regular,
                                                                reorder=True))

# ==[1.5] Focus on a single puzzle piece and duplicate it with a new location
#

theRegular_A = theGrid.pieces[1]
theRegular_B = theGridMea.pieces[1]

# ==[2] Create a new board
#
theBoard = Board()
theBoard.addPiece(theRegular_A)
theBoard.addPiece(theRegular_B)

# ==[3] Create an edge matcher
#

theMatcher = Histogram()

# ==[4] Display the new board and the comparison result.
#
print('Should see True.')
print(theMatcher.compare(theRegular_A, theRegular_B))

theBoard.display()

plt.show()

#
# ============================ basic06_histogram ===========================
