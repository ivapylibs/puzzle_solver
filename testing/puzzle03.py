#!/usr/bin/python3
#=============================== puzzle03 ==============================
#
# @brief    Code to create a puzzle detector and working on well-separated puzzles
#           (numpy), output movement instruction. Integrated in the perceiver.
#
#
#=============================== puzzle03 ==============================

#
# @file     puzzle03.py
#
# @author   Yunzhi Lin,         yunzhi.lin@gatech.edu
# @date     2021/07/20 [created]

#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
# @quit
#=============================== puzzle03 ==============================


#==[0] Prep environment.
#
import operator
import numpy as np
import cv2
import os

import matplotlib.pyplot as plt

import puzzle.detector_puzzle as detector_puzzle

import improcessor.basic as improcessor
import trackpointer.centroidMulti as tracker
import perceiver.simple as perceiver

#==[1] Build up a puzzle solver

#--[1.1] Create the detector instance.

improc = improcessor.basic(
                  operator.lt, (127,),
                  improcessor.basic.to_uint8,())

puzzleDet = detector_puzzle.detector_puzzle(improc)

#--[1.2] and the track pointer instance.

trackptr = tracker.centroidMulti()

#--[1.3] Package up into a perceiver.

ptsPer=perceiver.simple(theDetector=puzzleDet , theTracker=trackptr, trackFilter=None, theParams=None)


#==[2] Apply puzzle solver to simple image.

#--[2.1] Read an image from the online source

src_img = np.ones((100,100)) *255
# Create two boxes, 20*10
src_img[5:25, 5:15] = 0
src_img[70:80, 60:80] = 0

#--[2.2] Apply to simple image and visualize the output

print('Should see one segmented puzzle piece and one segmented template, \n'
      'as well as their final match \n'
      '(red: original puzzle piece; green: template; blue: rotated puzzle piece) \n'
      'The movement instruction is also displayed.\n')

ptsPer.process(src_img)

#--[2.3] Visualize the tracking output.

tstate = ptsPer.tracker.getstate()
ptsPer.tracker.setstate(tstate.tpt)

print("\nShould see two boxes with red X in the center.\n")
plt.imshow(src_img,cmap='Greys')
ptsPer.tracker.displayState()
plt.show()


#
#=============================== puzzle03 ==============================
