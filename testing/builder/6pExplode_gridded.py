#!/usr/bin/python3
# ============================ 6pExplode_gridded ===========================
#
# @brief    Test script for explodedPuzzle function. (6 shapes img)
#
#
# ============================ 6pExplode_gridded ===========================

#
# @file     6pExplode_gridded.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/15  [created]
#
# ============================ 6pExplode_gridded ===========================


import os

import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt

from puzzle.builder.gridded import Gridded
from puzzle.parser.fromLayer import FromLayer

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2GRAY)
_, theMaskSol = cv2.threshold(theMaskSol, 10, 255, cv2.THRESH_BINARY)

# ==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer()
theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[1.2] Display the solution board
#
f, axarr = plt.subplots(1, 2)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0].imshow(bSource)
axarr[0].title.set_text('Source Board')

# ==[2] Create a Grid instance and explode it
#

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol)

epImage, _ = theGrid.explodedPuzzle()

axarr[1].imshow(epImage)
axarr[1].title.set_text('Exploded view')

plt.show()

#
# ============================ 6pExplode_gridded ===========================
