#!/usr/bin/python3
#============================= basic03simple =============================
#
# @brief    Augmenting basic setup by packaging into a simple board
#           perceiver. Detector gets pieces only within a certain
#           intensity range (after conversion to gray scale).  Not all
#           pieces will be snagged.  The ones grabbed will have corner
#           markers.
#
# Basic test of recovering puzzle pieces from a given color image, based on
# a detection mask.  The detector is based on a gray level range.
# Setting the lower threshold to 90 will get three of the objects.  Lowering
# to 70 will get five of the objects.  Too low and it crashes, maybe due to
# grabbing the entire image. Has not been debugged.
#
#============================= basic03simple =============================

#
# @file     basic03_simple.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
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
import matplotlib.pyplot as plt
import pkg_resources

import detector.inImage as detector
import improcessor.basic as improcessor
import puzzle.parse.simple as perceiver
from puzzle.parser import boardMeasure, CfgBoardMeasure


#==[1] Build the perceiver.
#--[1.1] Create the detector and tracker instances.  This is what does the
#        gary level detection part.
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
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImage = cv2.imread(prefix + 'shapes_color_six_image.png')
boardPer.process(theImage)

#==[4] Display the state
#
plt.imshow(theImage)
boardPer.displayState()
plt.show()

#
#============================= basic03simple =============================
