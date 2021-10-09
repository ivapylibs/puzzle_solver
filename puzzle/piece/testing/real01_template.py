#!/usr/bin/python3
# ============================ real01_template ===========================
#
# @brief    Test script for the most basic functionality of template
#           puzzle piece class for a real puzzle piece input.
#
# ============================ real01_template ===========================

#
# @file     real01_template.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/09  [created]
#
# ============================ real01_template ===========================

# ==[0] Prep environment

import os
import cv2
import matplotlib.pyplot as plt

from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.utils.imageProcessing import preprocess_real_puzzle

from puzzle.piece.template import template


fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol = preprocess_real_puzzle(theImageSol)

# ==[1.2] Create raw puzzle piece data.
#

thePiece = template.buildFromMaskAndImage(theMaskSol, theImageSol)

# ==[1.3] Display.
#
theImage = thePiece.toImage()
plt.imshow(theImage)

plt.show()
#
# ============================ real01_template ===========================
