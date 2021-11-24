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

import cv2
import detector.inImage as detector
import improcessor.basic as improcessor
# ==[0] Prep environment
import matplotlib.pyplot as plt

import puzzle.parser.simple as perceiver
from puzzle.parser.fromLayer import FromLayer

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Build the perceiver.

# --[1.1] Create the detector instance.

improc = improcessor.basic(improcessor.basic.thresh, ((127, 255, cv2.THRESH_BINARY),),
                           cv2.cvtColor, (cv2.COLOR_BGR2GRAY,))

binDet = detector.inImage(improc)

# --[1.2] and the tracker instance.

theLayer = FromLayer()

# --[1.3] Package up into a perceiver.

boardPer = perceiver.Simple(theDetector=binDet, theTracker=theLayer, theParams=None)

# ==[2] Create image
#
theImage = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image.png')

# ==[3] Extract info from theImage
#

boardPer.process(theImage)

# ==[4] Display the state
#
plt.imshow(theImage)
boardPer.displayState()
plt.show()

#
# ============================ basic03_simple ===========================
