#============================ basic02_parser ===========================
#
# @brief    Test script for the most basic functionality of parser
#           class. (Shape data)
#
#============================ basic02_parser ===========================

#
# @file     basic02_parser.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2017/08/01  [created]
#
#============================ basic02_parser ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
from puzzle.parser.fromLayer import fromLayer

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Create image
#
theImage = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image.png')
#==[2] Create mask
#
theMask = cv2.imread(cpath + '/../../testing/data/shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

#==[3] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.measure(theImage,theMask)

theBoard = theLayer.bMeas

#==[4] Display the original image. Should see some puzzle pieces.
#
plt.imshow(theImage)
plt.show()

#==[5] Display the resulting image. Should have some puzzle pieces in a cropped region.
#
fh = theBoard.display()
plt.show()

#
#============================ basic01_parser ===========================
