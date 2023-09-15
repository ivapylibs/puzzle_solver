#!/usr/bin/python3
#================================ basic02 ================================
#
# @brief    Test script for the most basic functionality of parser
#           class. (Shape data from image files)
#
#================================ basic02 ================================

#
# @file     basic02.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/01  [created]
#
# NOTES:
#   80 columns or more.
#
#   2023/09/08:     Class changes tested.  Works.
#
#================================ basic02 ================================


import os

import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt

#from puzzle.parser.fromLayer import FromLayer
from puzzle.parser import boardMeasure, CfgBoardMeasure

#fpath = os.path.realpath(__file__)
#cpath = fpath.rsplit('/', 1)[0]

#==[1] Load image and mask
#
theImage = cv2.imread('../data/shapes_color_six_image.png')
theMask  = cv2.imread('../data/shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

#==[2] Instantiate board measure object. 
#      Extract info from theImage & theMask to obtain a board instance
#
theLayer = boardMeasure()
theLayer.measure(theImage, theMask)

#==[3] Display the original image. Should see some puzzle pieces.
#      Display the board image. Should see some puzzle pieces in a cropped region.
#
print('Should see some puzzle pieces.')
plt.imshow(theImage)

print('Should see the same puzzle pieces in a cropped region.')
theBoard = theLayer.bMeas
fh = theBoard.display_mp()
plt.show()

#
#================================ basic02 ================================
