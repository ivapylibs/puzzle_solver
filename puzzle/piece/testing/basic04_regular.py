#!/usr/bin/python3
#============================ basic04_regular ===========================
#
# @brief    Test script for the most basic functionality of template
#           puzzle piece class.
#
#============================ basic04_regular ===========================

#
# @file     basic04_regular.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/17  [modified]
#
#============================ basic04_regular ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2

import improcessor.basic as improcessor
from puzzle.parser.fromSketch import fromSketch
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.builder.gridded import gridded, paramGrid
from puzzle.piece.regular import regular

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')


#==[1.1] Create an improcesser to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                  cv2.GaussianBlur, ((3, 3), 0,),
                  cv2.Canny, (30, 200,),
                  improcessor.basic.thresh, ((10,255,cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000))

theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()

#==[1.3] Focus on a single puzzle piece
#
theTemplate = theBoardSol.pieces[6]

theRegular = regular(theTemplate)


#==[2] Process the puzzle piece to obtain the segmented contours
#

output = theRegular.process()

#==[3] Display the puzzle piece and the extracted info
#
theMask = theRegular.y.mask
cv2.imshow('demo', aa)
cv2.waitKey()


#
#============================ basic04_regular ===========================
