#!/usr/bin/python3
#============================ real01_template ===========================
#
# @brief    Test script for the most basic functionality of template
#           puzzle piece class for a real puzzle piece input.
#
# 09/15: BROKEN. NEED TO FIX.
# 11/15: HAS REALLY WEIRD preprocess_real_puzzle FUNCTION THAT IS
#        HORRIBLE.  FIRST IT IS HARD CODED. SECOND IT DOES NOT USE
#        THE PERCEIVEER/DETECTOR FRAMEWORK FOR PUZZLE EXTRACTION.
#        THIRD, IT DOESN'T EVEN RUN.  WHAT DOES RUN SHOWS REALLY
#        ATROCIOUS PROCESSING.  NEEDS TOTAL REDO. WHAT IN THE WORLD
#        INSPIRED THIS CODE?
# 11/15: AFFFECTS ALL realXX_YY SCRIPTS.  THEY ALL NEED TO BE REDONE.
#        EITHER DELETE OR FIGURE OUT HOW TO REUSE EXISTING IMAGES.
#        MOST LIKELY DELETE SINCE IMAGING CONDITIONS HAVE CHANGED.
#
#============================ real01_template ===========================

#
# @file     real01_template.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/09  [created]
#
#============================ real01_template ===========================

#==[0] Prep environment

import os

import cv2
import matplotlib.pyplot as plt

from puzzle.piece import Template
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
theImageSol = cv2.imread('../../../testing/data/puzzle_real_sample_black/SinglePiece_mea_1.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

#==[1.1] Create an improcessor to obtain the mask.
#
theMaskSol = preprocess_real_puzzle(theImageSol)

#==[1.2] Create raw puzzle piece data.
#
thePiece = Template.buildFromMaskAndImage(theMaskSol, theImageSol)

#==[1.3] Display.
#
theImage = thePiece.toImage()
plt.imshow(theImage)

plt.show()
#
#============================ real01_template ===========================