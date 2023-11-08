#!/usr/bin/python3
# ============================ basic04_regular ===========================
#
# @brief    Test script for the most basic functionality of regular
#           puzzle piece class. (regular piece with 4 edges)
#
#
# @note 09/15: DOES NOT RUN. THERE ARE ISSUES. CODE IS BROKEN.
# ============================ basic04_regular ===========================

#
# @file     basic04_regular.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/17  [created]
#
# ============================ basic04_regular ===========================


import os

import cv2
import numpy as np
import improcessor.basic as improcessor

# ==[0] Prep environment

import matplotlib.pyplot as plt

from puzzle.parser import boardMeasure, CfgBoardMeasure
import detector.inImage as detector

from puzzle.parse.fromSketch import FromSketch
from puzzle.piece import Regular

#fpath = os.path.realpath(__file__)
#cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread('../../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread('../../../testing/data/puzzle_15p_123rf.png')

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           #cv2.GaussianBlur, ((3, 3), 0,),
                           #cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

# @todo Weird approach to puzzle piece extraction.  Why not just threshold?  The image
#       should permit such an activity.  After thresholding, just need to grab the
#       connected components.  To thin out the borders, skeletonization may be in order.
#       Each one is a puzzle piece mask.  Apply to the image and it is done.  Of course,
#       the image may need to be cropped or resized so that the puzzle mask fits.  The best
#       approach is to get the aspect ratio and match them (crop puzzle to match aspect
#       ratio).  After that resize the image to match the target dimensions of the mask.
#       Apply the mask to recover puzzle pieces.
#
# @note Applying just a threshold without edge detection and without blurring, works fine.
#       Delete this comment once verified to work.
# 
# @note Acceptable for now, but should really adjust.  What does this say about Yunzhi's
#       understanding of the problem? Ability to think through a simple problem?
#       Won't fully know until testing out above approach.  It might actually align with
#       puzzle board piece detection approach, since that also uses connected components
#       (or should???).
#
theDet = detector.inImage(improc)
theDet.process(theMaskSol_src)
theMaskSol = theDet.getState().x

# ==[1.2] Extract info from theImage & theMask to obtain a board instance
#
puzzParm = CfgBoardMeasure()
puzzParm.minArea = 50

theLayer = boardMeasure(puzzParm)

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

theBoardSol.display_mp(ID_DISPLAY=True)
plt.show()

# ==[1.3] Focus on a single puzzle piece
#

theTemplate = theBoardSol.pieces[0]
theRegular  = Regular(theTemplate)
# IAMHERE: CRASHES HERE.

# ==[2] Display the puzzle piece and the extracted info.
#
print('Should see [3,1,2,2], which means LEFT: FLAT, RIGHT: IN, TOP: OUT, BOTTOM: OUT')
theRegular.displayEdgeType()

theImage = theRegular.toImage()

f, axarr = plt.subplots(1, 2)

axarr[0].imshow(theImage)
axarr[0].title.set_text('The segmented puzzle piece')

axarr[1].imshow(theRegular.class_image, cmap='rainbow')
axarr[1].title.set_text('The segmented 4 edges')

plt.show()

#
# ============================ basic04_regular ===========================
