#!/usr/bin/python3
#=============================== basic04_regular ===============================
#
# @brief    Test script for the most basic functionality of regular
#           puzzle piece class; a regular piece with 4 edges.
#
# Demonstration of the corner recovery process for the puzzle piece.  Takes
# an image and a puzzle template, then creates a puzzle for regular piece
# processing.  
#
# Only applies the side extraction process to a single piece.  It can be
# manually adjusted, but does not perform more extensive testing across
# multiple puzzle pieces.  
#
# Limited additional testing has discovered that the parameter settings and
# processing does not lead to consistent detection of four corners.
# Sometimes it is more, sometimes less.  The more corners makes sense
# because some pieces have corner-like elements for the interior puzzle
# piece carve outs.   These need to be excluded.  Four pieces need to be
# consistently obtained.
# 
#=============================== basic04_regular ===============================

#
# @file     basic04_regular.py
#
# @author   Patricio A. Vela        pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/17  [created]
#
#=============================== basic04_regular ===============================


import os
import pkg_resources

import cv2
import numpy as np
import improcessor.basic as improcessor
from camera.utils import display

# ==[0] Prep environment

import matplotlib.pyplot as plt

from puzzle.parser import boardMeasure, CfgBoardMeasure
import detector.inImage as detector

from puzzle.parse.fromSketch import FromSketch
from puzzle.piece import Regular


#===[1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImageSol = cv2.imread(prefix + 'balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(prefix + 'puzzle_15p_123rf.png')

#===[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = detector.inImage(improc)
theDet.process(theMaskSol_src)
theMaskSol = theDet.getState().x

#==[1.2] Extract info from theImage & theMask to obtain a board instance
#
puzzParm = CfgBoardMeasure()
puzzParm.minArea = 50

theLayer = boardMeasure(puzzParm)

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

theBoardSol.display_mp(ID_DISPLAY=True)

#==[1.3] Focus on a single puzzle piece
#

theTemplate = theBoardSol.pieces[5]
theRegular  = Regular.upgradeTemplate(theTemplate)

#==[2] Display the puzzle piece and the extracted info.
#
print('Should see [3,1,2,2], which means LEFT: FLAT, RIGHT: IN, TOP: OUT, BOTTOM: OUT')
theRegular.printEdgeType()

theImage = theRegular.toImage()

f, axarr = plt.subplots(1, 2)

axarr[0].imshow(theImage)
axarr[0].title.set_text('The segmented puzzle piece')

axarr[1].imshow(theRegular.class_image, cmap='rainbow')
axarr[1].title.set_text('The segmented 4 edges')

plt.show()

#
#=============================== basic04_regular ===============================
