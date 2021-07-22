#=============================== puzzle01 ==============================
#
# @brief    Code to create a puzzle detector and working on well-separated puzzles
#           (numpy), output movement instruction.
#
#=============================== puzzle01 ==============================

#
# @file     puzzle01.py
#
# @author   Yunzhi Lin,         yunzhi.lin@gatech.edu
# @date     2021/07/20 [created]

#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
# @quit
#=============================== puzzle01 ==============================


#==[0] Prep environment.
#
import operator
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt

import improcessor.basic as improcessor
import puzzle_solver.detector_puzzle as detector_puzzle

#==[1] Build up a puzzle solver

#--[1.1] Create the detector instance.

improc = improcessor.basic(
                  operator.lt, (127,),
                  improcessor.basic.to_uint8,())

puzzleDet = detector_puzzle.detector_puzzle(improc)

#==[2] Apply puzzle solver to simple image.

#--[2.1] Read an image from numpy

src_img = np.ones((100,100)) *255
# Create two boxes, 20*10
src_img[5:25, 5:15] = 0
src_img[70:80, 60:80] = 0

#--[2.2] Apply to simple image and visualize the output

print('Should see one segmented puzzle piece and one segmented template, \n'
      'as well as their final match \n'
      '(red: original puzzle piece; green: template; blue: rotated puzzle piece) \n'
      'The movement instruction is also displayed.\n')

puzzleDet.process(src_img)
#
#=============================== puzzle01 ==============================