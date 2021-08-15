#!/usr/bin/python3
#============================ basic01_simple ===========================
#
# @brief    Test script for the most basic functionality of simple class.
#           Perform a single action.
#
#============================ basic01_simple ===========================

#
# @file     basic01_simple.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/14  [created]
#
#============================ basic01_simple ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2

from puzzle.parser.fromLayer import fromLayer

from puzzle.manager import manager
from puzzle.solver.simple import simple

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png', cv2.IMREAD_GRAYSCALE)
_ , theMaskSol = cv2.threshold(theMaskSol,10,255,cv2.THRESH_BINARY)

#==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()

#==[2] Create image & mask for measurement
#
theImageMea = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image.png')
theMaskMea = cv2.imread(cpath + '/../../testing/data/shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

#==[2.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.process(theImageMea,theMaskMea)
theBoardMea = theLayer.getState()

#==[3] Display the current & solution board
#
f, axarr = plt.subplots(1,3)

theBoardMea_img = theBoardMea.toImage(ID_DISPLAY=True)
theBoardSol_img = theBoardSol.toImage()
axarr[0].imshow(theBoardMea_img)
axarr[0].title.set_text('Original measured board')

axarr[1].imshow(theBoardSol_img)
axarr[1].title.set_text('Solution board')

#==[4] Create match by manager
#
theManager = manager(theBoardSol)
theManager.process(theBoardMea)

#==[5] Create simple instance and set up the match
#
theSolver = simple(theBoardSol, theBoardMea)

theManager = manager(theBoardSol)
theManager.process(theBoardMea)

theSolver.setMatch(theManager.pAssignments)

#==[6] Start the solver to take turns, display the updated board.
#
theSolver.takeTurn()

theBoardMea_img = theSolver.current.toImage(ID_DISPLAY=True)
axarr[2].imshow(theBoardMea_img)
axarr[2].title.set_text('Current measured board')
plt.show()

#
#============================ basic01_simple ===========================
