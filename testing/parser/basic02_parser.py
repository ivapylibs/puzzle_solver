#!/usr/bin/python3
# ============================ basic02_parser ===========================
#
# @brief    Test script for the most basic functionality of parser
#           class. (Shape data)
#
# ============================ basic02_parser ===========================

#
# @file     basic02_parser.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/01  [created]
#
# ============================ basic02_parser ===========================


import os

import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt

from puzzle.parser.fromLayer import FromLayer

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Create image
#
theImage = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image.png')
# ==[2] Create mask
#
theMask = cv2.imread(cpath + '/../../testing/data/shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

# ==[3] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer()
theLayer.measure(theImage, theMask)

theBoard = theLayer.bMeas

# ==[4] Display the original image. Should see some puzzle pieces.
#
print('Should see some puzzle pieces.')
plt.imshow(theImage)
plt.show()

# ==[5] Display the resulting image. Should see some puzzle pieces in a cropped region.
#
print('Should see some puzzle pieces in a cropped region.')
fh = theBoard.display()
plt.show()

#
# ============================ basic01_parser ===========================
