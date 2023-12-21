#!/usr/bin/python3
#================================ basic01 ================================
#
# @brief    Test script for the most basic functionality of parser
#           class. (Two circles)
#
#================================ basic01 ================================

#
# @file     basic01.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @author   Patricio A. Vela,       pvela@gatech.edu
#
# @date     2021/08/01  [created]
# @date     2023/09/08  [modified]
#
#
# NOTES:
#   80 columns or more.
#================================ basic01 ================================


import cv2
#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.parser import boardMeasure, CfgBoardMeasure

#==[1] Create image
#
theImage = np.zeros((100, 100, 3))

# Basic setting to draw a circle
center_coordinates = (25, 25)
radius = 10
color = (255, 0, 0)
thickness = -1

theImage = cv2.circle(theImage, center_coordinates, radius, color, thickness)

center_coordinates = (55, 55)
radius = 15
color = (0, 255, 0)
thickness = -1

theImage = cv2.circle(theImage, center_coordinates, radius, color, thickness)

#==[2] Create mask: can be tight or bbox. The code should have tight mask.
#
theMask = np.full((100, 100), False, dtype=bool)
if True:
  theMask = np.any(theImage,2)              # Tight.
else:
  theMask[15:36, 15:36] = True              # Bbox. Just to have option to reproduce
  theMask[40:71, 40:71] = True              #   original test script.  Not best choice.


#==[3] Extract info from theImage & theMask to obtain a board instance
#
boardOpts = CfgBoardMeasure()

theLayer = boardMeasure(params=boardOpts)
theLayer.measure(theImage, theMask)

theBoard = theLayer.bMeas

#==[4] Display the original image. Should see two circle pieces.
#
print('Should see two circle pieces.')
plt.imshow(theImage)
#plt.show()

#==[5] Display the resulting image. Should see two circle pieces in a cropped region.
#
print('Should see two circle pieces in a cropped region.')
fh = theBoard.display_mp()
plt.show()

#
#================================ basic01 ================================
