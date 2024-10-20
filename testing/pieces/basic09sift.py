#!/usr/bin/python3
#================================ basic09sift ================================
##@file
# @brief    Test script that matches a single piece against all other pieces
#           in a puzzle. Ideally there should be a single match, but that's
#           not how things go.
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/01  [created]
#
# @ingroup  TestPuzzle_Tracking
# @quitf

#================================ basic09sift ================================
#
# NOTE
#   Indent is 2 spaces. Column width is 85+.
#
#================================ basic09sift ================================

#==[0] Prep environment

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

#==[1.5] Focus on a single puzzle piece and compare to all pieces in the "duplicate" puzzle.
#        The matching approach employs SIFT.
#
theMatcher = SIFTCV()
theRegular_A = theGrid.pieces[36]

isMatch = []
for k in theGridMea.pieces:
  print(f"---- {k} ----")
  result = theMatcher.compare(theRegular_A, theGridMea.pieces[k])
  isMatch.append(result[0])

print(isMatch)

#
#================================ basic09sift ================================
