#=============================== puzzle02 ==============================
#
# @brief    Code to create a puzzle detector and working on well-separated puzzles
#           (online resource), output movement instruction.
#
#
#=============================== puzzle02 ==============================

#
# @file     puzzle02.py
#
# @author   Yunzhi Lin,         yunzhi.lin@gatech.edu
# @date     2021/07/20 [created]

#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
# @quit
#=============================== puzzle02 ==============================


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

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                  operator.lt, (127,),
                  improcessor.basic.to_uint8,())

puzzleDet = detector_puzzle.detector_puzzle(improc)

#==[2] Apply puzzle solver to simple image.

#--[2.1] Read an image from the online source

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# src_img = cv2.imread(cpath + '/data/image_1.jpg')
src_img = cv2.imread(cpath + '/data/image_2.png')

#--[2.2] Apply to simple image and visualize the output

print('Should see one segmented puzzle piece and one segmented template, \n'
      'as well as their final match \n'
      '(red: original puzzle piece; green: template; blue: rotated puzzle piece) \n'
      'The movement instruction is also displayed.\n')

puzzleDet.process(src_img)

#
#=============================== puzzle02 ==============================