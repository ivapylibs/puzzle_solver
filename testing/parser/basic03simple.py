#!/usr/bin/python3
#============================= basic03simple =============================
#
# @brief    Augmenting basic setup by packaging into a simple board
#           perceiver. 
#
#============================= basic03simple =============================

#
# @file     basic03_simple.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @author   Patricio A. Vela,       pvela@gatech.edu
#
# @date     2021/08/02  [created]
#
# NOTES:
#   80 columns or more.
#
#   2023/09/08:     Class changes tested. Require some adjustment. Works.
#
#============================= basic03simple =============================


#==[0] Prep environment (dependencies)
#
import os

import cv2
import detector.inImage as detector
import improcessor.basic as improcessor
import matplotlib.pyplot as plt

import puzzle.parse.simple as perceiver
from puzzle.parser import boardMeasure, CfgBoardMeasure

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Build the perceiver.
#--[1.1] Create the detector and tracker instances.
#
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((90, 255, cv2.THRESH_BINARY),))
binDet = detector.inImage(improc)

theLayer = boardMeasure()

#--[1.2] Package up into a perceiver.
#
boardPer = perceiver.Simple(None, binDet, theLayer)

#==[2] Load image
#      Extract info from the image
#
theImage = cv2.imread('../data/shapes_color_six_image.png')
boardPer.process(theImage)

#==[4] Display the state
#
plt.imshow(theImage)
boardPer.displayState()
plt.show()

#
#============================= basic03simple =============================
