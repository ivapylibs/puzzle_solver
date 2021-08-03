#!/usr/bin/python3
#============================= basic02_manager =============================
#
# @brief    Tests the core functionality of the puzzle.board class.
#
#
#============================= basic02_manager =============================

#
# @file     basic02_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/02 [created]
#
#============================= basic02_manager =============================

#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2


from puzzle.parser.fromLayer import fromLayer
from puzzle.manager import manager

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.imread(cpath + '/../testing/data/shapes_color_six_image_solution.png', cv2.IMREAD_GRAYSCALE)
_ , theMaskSol = cv2.threshold(theMaskSol,10,255,cv2.THRESH_BINARY)

#==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.measure(theImageSol,theMaskSol)
theBoardSol = theLayer.bMeas

#==[2] Create image & mask for measurement
#
theImageMea = cv2.imread(cpath + '/../testing/data/shapes_color_six_image.png')
theMaskMea = cv2.imread(cpath + '/../testing/data/shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

#==[3] Create a manager
#
theManager = manager(theBoardSol)

theManager.measure(theImageMea,theMaskMea)

#==[4] Display. Should see some ids on the puzzle pieces
# while the ids in the assignment board refer to the ids in the solution board.
#
bMeasImage = theManager.bMeas.toImage(ID_DISPLAY = True)
bsolImage = theManager.solution.toImage(ID_DISPLAY = True)
bAssignedImage = theManager.bAssigned.toImage(ID_DISPLAY = True, ID_SOLUTION = True)

plt.figure()
f, axarr = plt.subplots(1,3)
axarr[0].imshow(bMeasImage)
axarr[0].title.set_text('Measurement')
axarr[1].imshow(bsolImage)
axarr[1].title.set_text('Solution')
axarr[2].imshow(bAssignedImage)
axarr[2].title.set_text('Assignment')

plt.show()
#
#============================= basic02_manager =============================
