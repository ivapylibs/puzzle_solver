#!/usr/bin/python3
# ============================ basic03_simple ===========================
#
# @brief    Test script for the most basic functionality of parser
#           class. Packaged into simple.
#
# ============================ basic03_simple ===========================

#
# @file     basic03_simple.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/02  [created]
#
# ============================ basic03_simple ===========================


import os
import pkg_resources

import cv2
import detector.inImage as detector
import improcessor.basic as improcessor
# ==[0] Prep environment
import matplotlib.pyplot as plt

import puzzle.parser as puzzle
from puzzle.parse.fromLayer import FromLayer

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Build the perceiver.

# --[1.1] Create the detector instance.

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((27, 255, cv2.THRESH_BINARY),))

binDet = detector.inImage(improc)

#--[1.2] and the tracker instance.

theLayer = FromLayer()

#--[1.3] Package up into a perceiver.

boardPer = puzzle.boardPerceive(theDetector=binDet, theTracker=theLayer, theParams=None)

#==[2] Create image
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')
theImage = cv2.imread(prefix + 'shapes_color_six_image.png')

# ==[3] Extract info from theImage
#
boardPer.process(theImage.copy())
quit()

# ==[4] Display the state
#
plt.imshow(theImage)
plt.figure()
boardPer.displayState()
plt.show()

#
# ============================ basic03_simple ===========================
