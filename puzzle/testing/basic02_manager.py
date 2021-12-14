#!/usr/bin/python3
# ============================= basic02_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (6 shapes img)
#
#
# ============================= basic02_manager =============================
#
# @file     basic02_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/02 [created]
#
# ============================= basic02_manager =============================

# ==[0] Prep environment
import os
import cv2
import matplotlib.pyplot as plt

from puzzle.manager import Manager
from puzzle.parser.fromLayer import FromLayer

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.imread(cpath + '/../testing/data/shapes_color_six_image_solution.png', cv2.IMREAD_GRAYSCALE)
_, theMaskSol = cv2.threshold(theMaskSol, 10, 255, cv2.THRESH_BINARY)

# ==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer()
theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[2] Create image & mask for measurement
#
theImageMea = cv2.imread(cpath + '/../testing/data/shapes_color_six_image.png')
theMaskMea = cv2.imread(cpath + '/../testing/data/shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

# ==[3] Create a manager
#
theManager = Manager(theBoardSol)

theManager.process(theImageMea, theMaskMea)

# ==[4] Display. Should see some ids on the puzzle pieces
# while the ids in the assignment board refer to the ids in the solution board.
#
bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)
bSolImage = theManager.solution.toImage(ID_DISPLAY=True)

f, axarr = plt.subplots(1, 2)
axarr[0].imshow(bMeasImage)
axarr[0].title.set_text('Measurement')
axarr[1].imshow(bSolImage)
axarr[1].title.set_text('Solution')

# Show assignment
print('The first index refers to the measured board while the second one refers to the solution board.')
print(theManager.pAssignments)

plt.show()
#
# ============================= basic02_manager =============================
