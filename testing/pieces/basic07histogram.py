#!/usr/bin/python3
#=============================== basic07histogram ==============================
##@file
# @brief    Test script for the most basic functionality of histogram features
#           for puzzle pieces. (60p img)
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Patricio A. Vela        pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#
# @date     2024/10/20  [aligned with Perceiver updates and documented]
# @date     2021/09/29  [created]
#
# @quitf
#
#=============================== basic07histogram ==============================

#==[0] Prep environment
#
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
from puzzle.pieces.sift import Sift
from puzzle.utils.imageProcessing import cropImage
from puzzle.pieces.matchDifferent import HistogramCV

from puzzle.parse.fromLayer import FromLayer, ParamPuzzle   
# @todo  Needs updating. FromLayer is not the most current way to implement it.
#        Most of the work equivalent to FromLayer is already in board
#        measurement/perceiver.
#
from puzzle.parse.fromSketch import FromSketch




#==[1] Load data, instantiate puzzle pieces, and create source plus measurement boards
#       so that pieces from them may be compared.  The measurement board is such that
#       its pieces are placed in the same ordering as for the source board.  Thus
#       comparison of mismatched indices should always return false, and comparison
#       of the same index should return true.
#

#==[1.1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')
theImageSol = cv2.imread(prefix  + 'balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(prefix + 'puzzle_60p_AdSt408534841.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

#==[1.2] Create an improcessor to obtain the mask.
#
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((150, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc) 
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#==[1.2] Create an Grid instance from theImage & theMask.    This is considered to be
#        the target or ground truth board.
#
print('Running through test cases. Will take a bit.')

theParams = CfgGridded()
theParams.update(dict(minArea=100, pieceBuilder=Regular, reorder=True))

theGrid   = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams)

#==[2] Create a new Grid instance by exploding the original board.
#      Here association or comparison should be easy and known since image is pretty
#      much duplicated.
#
epImage, epBoard = theGrid.explodedPuzzle(dx=100, dy=100)
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((1, 255, cv2.THRESH_BINARY),))
theMaskMea = improc.apply(epImage)

#DEBUG VISUAL - IF processing is off, then grid won't be correct. Maybe not even a grid.
#plt.imshow(epImage)
#plt.figure()
#plt.imshow(theMaskMea)
#plt.show()

theParams  = CfgGridded()
theParams.update(dict(minArea=100, pieceBuilder=Regular, reorder=True))
theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea, theParams)

#==[3] Focus on a three puzzle pieces for comparison with a Histogram matcher.
#      Use correct match first, then a couple of wrong matches.
#
theRegular_A = theGrid.pieces[1]
theRegular_B = theGridMea.pieces[1]

theMatcher = HistogramCV()

print('Should see True, False, False.')
print(theMatcher.compare(theRegular_A, theRegular_B))

theBoard1 = Board()
theBoard1.addPiece(theRegular_A)
theBoard1.addPiece(theRegular_B)

theRegular_B = theGridMea.pieces[2]
print(theMatcher.compare(theRegular_A, theRegular_B))

theBoard2 = Board()
theBoard2.addPiece(theRegular_A)
theBoard2.addPiece(theRegular_B)

theRegular_B = theGridMea.pieces[4]
print(theMatcher.compare(theRegular_A, theRegular_B))

theBoard3 = Board()
theBoard3.addPiece(theRegular_A)
theBoard3.addPiece(theRegular_B)

#==[3] Display compared pieces as added to boards.
#
theBoard1.display_mp()
theBoard2.display_mp()
theBoard3.display_mp()
plt.show()

#
#=============================== basic07histogram ==============================
