#!/usr/bin/python3
#============================ rotate_template ===========================
#
# @brief    Test script for the rotation function of the puzzle piece.
#           (60p img)
#
#============================ rotate_template ===========================

#
# @file     rotate_template.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/19  [created]
#
#============================ rotate_piece ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
from copy import deepcopy

from puzzle.utils.imageProcessing import cropImage

import improcessor.basic as improcessor
import similaritymeasures

from puzzle.parser.fromSketch import fromSketch
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.piece.regular import regular

from puzzle.builder.gridded import gridded, paramGrid

from puzzle.piece.edge import edge

from puzzle.board import board

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_60p_AdSt408534841.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)


#==[1.1] Create an improcesser to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                  cv2.GaussianBlur, ((3, 3), 0,),
                  cv2.Canny, (30, 200,),
                  improcessor.basic.thresh, ((10,255,cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#==[1.2] Extract info from theImage & theMask to obtain a board instance.
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000))

theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()

#==[1.3] Focus on a single puzzle piece.
#

thePiece_A = theBoardSol.pieces[36]

#==[1.4] Rotate the puzzle piece.
#

theRotate = thePiece_A.rotatePiece(90)

bigImage = np.zeros((1000, 1000, 3), dtype='uint8')
thePiece_A.placeInImage(bigImage)

theRotate_B = theRotate.rotatePiece(270)
theRotate_B.placeInImage(bigImage)

#==[2] Display.
#
plt.figure()
plt.title("Test the rotation function of the puzzle piece. \n Should see two matched puzzle pieces.")
plt.imshow(bigImage)

plt.show()

#
#============================ rotate_template ===========================
