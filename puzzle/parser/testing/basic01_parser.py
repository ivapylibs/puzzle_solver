#!/usr/bin/python3
#============================ basic01_parser ===========================
#
# @brief    Test script for the most basic functionality of parser
#           class. (Two circles)
#
#============================ basic01_parser ===========================

#
# @file     basic01_parser.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/01  [created]
#
#============================ basic01_parser ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import cv2

from puzzle.parser.fromLayer import fromLayer

#==[1] Create image
#
theImage = np.zeros((100,100,3))

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

#==[2] Create mask
#
theMask = np.full((100,100), False, dtype=bool)
theMask[15:35,15:35] = True
theMask[40:70,40:70] = True


#==[3] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.measure(theImage,theMask)

theBoard = theLayer.bMeas

#==[4] Display the original image. Should see two circle pieces.
#
print('Should see two circle pieces.')
plt.imshow(theImage)
plt.show()

#==[5] Display the resulting image. Should see two circle pieces in a cropped region.
#
print('Should see two circle pieces in a cropped region.')
fh = theBoard.display()
plt.show()

#
#============================ basic01_parser ===========================
