#!/usr/bin/python3
# ============================ real06_template ===========================
#
# @brief    Test script for the most basic functionality of template
#           puzzle piece class for a real puzzle piece input.
#
# ============================ real06_template ===========================

#
# @file     real06_template.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/25  [created]
#
# ============================ real06_template ===========================

# ==[0] Prep environment

import os
import cv2
import matplotlib.pyplot as plt

from puzzle.builder.arrangement import arrangement, paramArrange
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.utils.imageProcessing import preprocess_real_puzzle

from puzzle.piece.template import template


fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
# theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_hard/GTSolBoard_mea_1.png')
theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_hard/4.png')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol = preprocess_real_puzzle(theImageSol, verbose=True)
cv2.imshow('debug',theMaskSol)
cv2.waitKey()
# ==[1.2] Create raw puzzle piece data.
#

theArrange = arrangement.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                                theParams=paramArrange(areaThreshold=1000))
# ==[1.3] Display.
#
theImage = theArrange.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY=True, COLOR=(0,255,0))
plt.imshow(theImage)

plt.show()
#
# ============================ real06_template ===========================
