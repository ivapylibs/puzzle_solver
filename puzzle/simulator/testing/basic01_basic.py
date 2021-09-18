#!/usr/bin/python3
#============================ basic01_basic ===========================
#
# @brief    Test script for the most basic functionality of the
#           basic class. (6 shapes img)
#
#============================ basic01_basic ===========================

#
# @file     basic01_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/22  [created]
#
#============================ basic01_basic ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
from copy import deepcopy

from puzzle.parser.fromLayer import fromLayer
from puzzle.simulator.basic import basic

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Create image & mask for measurement
#
theImageMea = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image.png')
theMaskMea = cv2.imread(cpath + '/../../testing/data/shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

#==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.process(theImageMea,theMaskMea)
theBoardMea = theLayer.getState()

#==[2] Create a simulator
#
theSim = basic(theBoardMea)
newPiece = deepcopy(theSim.puzzle.pieces[1])

#==[3] Display
#

#==[3.1] Display the original board
#
f, axarr = plt.subplots(1,5)
theSim_img = theSim.toImage(ID_DISPLAY=True)
axarr[0].imshow(theSim_img)
axarr[0].title.set_text('Original \n Focus on piece 1')

#==[3.2] Set the puzzle piece location & display
#
pLocs = {1: [50,50]}
theSim.setPieces(pLocs)

theSim_img = theSim.toImage(ID_DISPLAY=True)
axarr[1].imshow(theSim_img)
axarr[1].title.set_text('After placement \n at (50,50)')

#==[3.3] Drag the puzzle piece & display
#
pVec = {1: [200,0]}
theSim.dragPieces(pVec)

theSim_img = theSim.toImage(ID_DISPLAY=True)
axarr[2].imshow(theSim_img)
axarr[2].title.set_text('After drag \n by (200,0) ')

#==[3.3] Add a new puzzle piece & display
#

theSim.addPiece(newPiece)

theSim_img = theSim.toImage(ID_DISPLAY=True)
axarr[3].imshow(theSim_img)
axarr[3].title.set_text('Add a new piece')

#==[3.4] Remove a puzzle piece & display
#
theSim.rmPiece(3)

theSim_img = theSim.toImage(ID_DISPLAY=True)
axarr[4].imshow(theSim_img)
axarr[4].title.set_text('Remove puzzle piece 3')

plt.show()

#
#============================ basic01_basic ===========================
