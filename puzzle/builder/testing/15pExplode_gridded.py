#!/usr/bin/python3
# ============================ 15pExplode_gridded ===========================
#
# @brief    Test script for explodedPuzzle function.
#           (15p with touching case)
#
# ============================ 15pExplode_gridded ===========================

#
# @file     15pExplode_gridded.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/15  [created]
#
# ============================ 15pExplode_gridded ===========================


import os

import cv2
import improcessor.basic as improcessor
# ==[0] Prep environment
import matplotlib.pyplot as plt

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.parser.fromSketch import fromSketch
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)
theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer(paramPuzzle(areaThresholdLower=5000))

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[1.3] Display the solution board
#
f, axarr = plt.subplots(1, 2)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0].imshow(bSource)
axarr[0].title.set_text('Source solution board')

# ==[2] Create an Grid instance and explode it
#

print('Running through test cases. Will take a bit.')

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=paramGrid(areaThresholdLower=5000))

epImage, _ = theGrid.explodedPuzzle(dx=100, dy=100)

axarr[1].imshow(epImage)
axarr[1].title.set_text('Exploded view')

plt.show()
#
# ============================ 15pExplode_gridded ===========================
