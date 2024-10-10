#!/usr/bin/python3
#============================ basic02_parser ===========================
## @file     basic02_parser.py
# @brief    Test script for the most basic functionality of parser
#           class. (Shape data)
#
# @quitf
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/01  [created]
#
#============================ basic02_parser ===========================


import os
import pkg_resources


import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt

from puzzle.parse.fromLayer import FromLayer

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Generate puzzle board from a loaded image and mask.
#
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImage = cv2.imread(prefix + 'shapes_color_six_image.png')
theMask = cv2.imread(prefix + 'shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

#---[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer()
theLayer.measure(theImage, theMask)
theBoard = theLayer.bMeas

#==[2] Display the original image. Should see some puzzle pieces.
#      Display the board. Should see some puzzle pieces in a cropped region.
#
print('Should see some puzzle pieces.')
lt.imshow(theImage)
plt.show()

#
print('Should see some puzzle pieces in a cropped region.')
fh = theBoard.display()
plt.show()

#
#============================ basic02_parser ===========================
