#!/usr/bin/python3
# ============================ basic04_fromSketch ============================
#
# @brief    Code to test out the simple image detector for a fairly
#           contrived scenario: threshold a grayscale image.
#
# Upgrades earlier test scripts to use a depth image plus upper and lower
# depth limits to establish a detection depth zone. The "depth image" here
# is simply fictitious data placed into an array (same as fake data in
# earlier test scripts).
#
# ============================ basic04_fromSketch ============================

#
# @file     basic04_fromSketch.m
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/10  [created]
#

#
# @quitf
# ============================ basic04_fromSketch ============================

# ==[0] Prep the environment. From most basic to current implementation.
#

import os
import cv2
import numpy as np

import improcessor.basic as improcessor
import camera.utils.display as display

from puzzle.parse.fromSketch import FromSketch

#fpath = os.path.realpath(__file__)
#cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read a sketch image that needs to be processed.
#

theImage = cv2.imread('../data/puzzle_15p_123rf.png')

# ==[2] Instantiate inImage detector with an image processor that does
#      the thresholding.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (100, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)

# Why is this approach taken and not one based on region labels?
# Seems really weird. Region props gives the full pixel listing of the regions.
# Ignoring for now, but may need to revisit.

# ==[3] Apply and visualize.
#
theDet.process(theImage)

# ==[4] Visualize the output
#
print("Creating window: should see a processed mask.")
display.rgb_cv(theImage,window_name='Input')
display.binary_cv(theDet.getState().x, window_name='Output')
display.wait_cv()

print("This test script is suspect.  It uses edge detection when thresholding");
print("of the image is a better choice for getting a mask image.");

#
# ============================ basic04_fromSketch ============================
