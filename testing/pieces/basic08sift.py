#!/usr/bin/python3
# ============================ basic06_sift ===========================
#
# @brief    Test script for the most basic functionality of sift features
#           for puzzle pieces. (60p img)
#
# NOTE: 09/15: BROKEN CODE. NEED TO FIX.
# ============================ basic06_sift ===========================

#
# @file     basic06_sift.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/01  [created]
#
# ============================ basic06_sift ===========================

# ==[0] Prep environment

import os
import pkg_resources

import cv2
import improcessor.basic as improcessor
import matplotlib.pyplot as plt
import numpy as np

from puzzle.board import Board
from puzzle.builder.gridded import Gridded, CfgGridded
from puzzle.parser import boardMeasure, CfgBoardMeasure
from puzzle.parse.fromSketch import FromSketch
from puzzle.piece import Regular
#from puzzle.pieces.sift import Sift
from puzzle.pieces.matchSimilar import SIFTCV
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')
theImageSol = cv2.imread(prefix + 'balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(prefix + 'puzzle_60p_AdSt408534841.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

#==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#==[1.2] Extract info from theImage & theMask to obtain a board instance
#
puzzParm = CfgBoardMeasure()
puzzParm.minArea = 500

theLayer = boardMeasure(puzzParm)

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

#==[1.3] Create a Grid instance and explode it into two new boards
#

print('Running through test cases. Will take a bit.')
gridParm = CfgGridded()
gridParm.minArea = areaThresholdLower=500
gridParm.pieceConstructor = 'Regular'
gridParm.reorder = False

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, gridParm)

epImage, epBoard = theGrid.explodedPuzzle(dx=100, dy=100)

#==[1.4] Create a new Grid instance from the images
#
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))
                           #cv2.dilate, (np.ones((3, 3), np.uint8),))
theMaskMea = improc.apply(epImage)

theGridOpt =  CfgGridded()
theGridOpt.pieceConstructor = 'Regular'
theGridOpt.tauMinArea = 1000

theParams = CfgGridded()
theParams.update(dict(areaThresholdLower=1000, pieceConstructor=Regular, reorder=False))
theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea, theGridOpt)

# ==[1.5] Focus on a single puzzle piece and duplicate it with a new location
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

theMatcher = SIFTCV()

# ==[4] Display the new board and the comparison result.
#
print('Should see True.')
print(theMatcher.compare(theRegular_A, theRegular_B))

theBoard.display_mp()
plt.show()

#
# ============================ basic06_sift ===========================
