#!/usr/bin/python3
#============================== basic07_histogram ==============================
#
# @brief    Test script for the most basic functionality of histogram features
#           for puzzle pieces. (60p img)
#
#============================== basic07_histogram ==============================

#
# @file     basic07_histogram.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/29  [created]
#
#============================== basic07_histogram ==============================

#==[0] Prep environment
#
import os

import cv2
import improcessor.basic as improcessor
import matplotlib.pyplot as plt
import numpy as np

from puzzle.board import Board
from puzzle.builder.gridded import Gridded, CfgGridded
from puzzle.parser import boardMeasure, CfgBoardMeasure
from puzzle.parse.fromSketch import FromSketch
from puzzle.piece import Regular
from puzzle.pieces.sift import Sift
from puzzle.utils.imageProcessing import cropImage
from puzzle.pieces.matchDifferent import HistogramCV

from puzzle.parse.fromLayer import FromLayer, ParamPuzzle   # @todo  Needs updating.

import camera.utils.display as display

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Load data, instantiate puzzle pieces, and create source plus measurement boards
#       so that pieces from them may be compared.  The measurement board is such that
#       its pieces are placed in the same ordering as for the source board.  Thus
#       comparison of mismatched indices should always return false, and comparison
#       of the same index should return true.
#

#==[1.1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../../testing/data/puzzle_60p_AdSt408534841.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

#==[1.2] Create an improcessor to obtain the mask.
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

#==[1.3] Create an Grid instance and explode it into two new boards
#
print('Running through test cases. Will take a bit.')

theParams = CfgGridded()
theParams.update(dict(minArea=1000, pieceConstructor=Regular, reorder=True))

theGrid   = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams)

epImage, epBoard = theGrid.explodedPuzzle(dx=100, dy=100)

#==[1.4] Create a new Grid instance from the images
#

# @note Not a fair game to directly use the epBoard. Make problem easy??
#       Instead, should restart from images

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),)
                           #cv2.dilate, (np.ones((3, 3), np.uint8),)    # Why dilate??
                           )
# @todo Dilate does not work here.  Most likely applied to get enlarge puzzle pieces so 
#       that they fit better.  The implementation is off.  May need override or helper
#       function just like improcessor.basic.thresh though that one should be thresh_cv
#       or cvThresh or anything that labels it as coming from OpenCV for programmer to
#       be aware.    PAV 2023/11/13.
# @todo To what degree can most of this computation benefit from Perceiver?
#
theMaskMea = improc.apply(epImage)

theParams = CfgGridded()
theParams.update(dict(minArea=1000, pieceConstructor=Regular, reorder=True))

theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea, theParams)

#==[2] Focus on a single puzzle piece for comparison with a Histogram matcher.
#
theRegular_A = theGrid.pieces[1]
theRegular_B = theGridMea.pieces[1]

theMatcher = HistogramCV()

print('Should see True.')
print(theMatcher.compare(theRegular_A, theRegular_B))

#==[3] Create board with the two compared pieces and display them.
#
theBoard = Board()
theBoard.addPiece(theRegular_A)
theBoard.addPiece(theRegular_B)
theBoard.display_mp()

plt.show()

#
#============================== basic07_histogram ==============================
