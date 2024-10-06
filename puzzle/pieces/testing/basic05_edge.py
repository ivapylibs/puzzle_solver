#!/usr/bin/python3
#================================= basic05_edge ================================
##@file
# @brief    Test script for the most basic functionality of edge matcher
#           for regular puzzle pieces. (60p img)
#
# The code creates a gridded puzzle instance, duplicates it by exploding 
# the puzzle and creating a new gridded instance.  There are effectively
# two different puzzles but with exact same appearance.  Matching can
# be controlled by selecting similar or different indices.
#
# @ingroup  TestingPuzzle
# @quitf
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/01  [created]
#
#================================= basic05_edge ================================

# ==[0] Prep environment
import os
import pkg_resources

import cv2
import numpy as np
import similaritymeasures

import matplotlib.pyplot as plt
import ivapy.display_cv as display

import improcessor.basic as improcessor
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

#==[1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImageSol    = cv2.imread(prefix + 'balloon.png')
theMaskSol_src = cv2.imread(prefix + 'puzzle_60p_AdSt408534841.png')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)
theImageSol = cropImage(theImageSol, theMaskSol_src)

#====[1.1] Create an improcessor to obtain the mask.
#
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#====[1.2] Extract info from theImage & theMask to obtain a board instance
#
puzzParm = CfgBoardMeasure()
puzzParm.minArea = 5000
theLayer = boardMeasure(puzzParm)
theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

#==[2] Create a Grid instance and as the "source" board.
#
print("First gridded pass. Regular image and mask")
theParams = CfgGridded()
theParams.update(dict(minArea=5000, pieceBuilder='Regular',reorder=True))

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams)

#==[3]  Create a new Grid instance from an exploded puzzle. These pieces are
#       well separated.  That makes the processing easier. As easy as having
#       a puzzle piece mask.  Also set to give similar puzzle IDs/ordering.
#
print("Second gridded pass. Exploded image and mask")
epImage, epBoard = theGrid.explodedPuzzle(dx=75, dy=75)

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),))
theMaskMea = improc.apply(epImage)

theParams = CfgGridded()
theParams.update(dict(minArea=1000, pieceBuilder='Regular',reorder=True))

theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea, theParams)

#DEBUG VISUAL
#theGridMea.display_mp()
#plt.show()


#==[4]  Create a new board and focus on a single puzzle piece duplicated with a
#       new location.  Comparing them with an Edge matcher should give a True.
#
print("Now doing simple puzzle comparison.")
theBoard = Board()

theRegular_A = theGrid.pieces[36]
theRegular_B = theGridMea.pieces[36]

theBoard.addPiece(theRegular_A)
theBoard.addPiece(theRegular_B)

#====[4.1] Create an edge matcher
#
theMatcher = Edge()

#====[4.2] Display the new board and the comparison result.
#
print('Should see True.\n')
isMatch = theMatcher.compare(theRegular_A, theRegular_B, method=similaritymeasures.pcm)
print(f'\n\n{isMatch}')

print('Close figure or hit key in window to terminate.')
theBoard.display_mp()
plt.show()

#
#================================= basic05_edge ================================
