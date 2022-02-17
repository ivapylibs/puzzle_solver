#!/usr/bin/python3
# ============================ real_arrangement ===========================
#
# @brief    Test script for building up an arrangement board.
#           (pieces close to each other from real images)
#
# ============================ real_arrangement ===========================

#
# @file     real_arrangement.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/11/1  [created]
#
# ============================ real_arrangement ===========================

# ==[0] Prep environment

import os

import cv2
import matplotlib.pyplot as plt

from puzzle.builder.arrangement import Arrangement, ParamArrange
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
# theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_hard/GTSolBoard_mea_3.png')
# theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_hard/MeaBoard_5.png')
# theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/Exploded_mea_0.png')
# theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_paper/test_yunzhi_mea_000.png')
theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_paper/test_yunzhi_mea_008.png')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#
print('Press any key to proceed.')
theMaskSol = preprocess_real_puzzle(theImageSol, verbose=True)
# cv2.imshow('debug',theMaskSol)
# cv2.waitKey()

# ==[1.2] Create raw puzzle piece data.
#

theArrange = Arrangement.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                                theParams=ParamArrange(areaThresholdLower=1000))
# ==[1.3] Display.
#
theImage = theArrange.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY=True, COLOR=(0,255,0))
plt.imshow(theImage)

plt.show()
#
# ============================ real_arrangement ===========================
