#!/usr/bin/python3
#================================= real08sift ================================
##@file
# @brief    Stress testing correspondences.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Devesh Nath        dnath7@gatech.edu
#
# @date     2024/11/24  [created from real06sift]
#
# @quitf
#================================= real08sift ================================
#
# NOTE
#   100 columns. Indent 4 spaces.
#
#================================= real08sift ================================

#==[0] Prep environment

import os
import pkg_resources
import argparse

import cv2
import matplotlib.pyplot as plt
import numpy as np
from ivapy.Configuration import AlgConfig
import ivapy.display_cv as dcv
from distutils.util import strtobool 

from puzzle.builder.arrangement import Arrangement, CfgArrangement
from puzzle.utils.imageProcessing import preprocess_real_puzzle
import puzzle.board as board

#====[0.1] Parse environment to figure out how to execute.

argparser = argparse.ArgumentParser()
argparser.add_argument('--forceMatches', type=strtobool, default='True', 
                       choices=[True, False],
                       help='Chooses whether to force matches or not.')

opt = argparser.parse_args()


#==[1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

# theImageSol_A = cv2.imread(prefix + 'puzzle_real_sample_black_big_hard3/sol_cali_mea_003.png')
theImageSol_A = cv2.imread(prefix + 'puzzle_real_sample_black_impossible/impossible_mea_001.png')
# theImageSol_A = cv2.imread(prefix + 'puzzle_real_sample_black_impossible_noLight/impossible_noLight_mea_006.png') # Fails maybe due to low light
# theImageSol_A = cv2.imread(prefix + 'puzzle_real_sample_black_small_cali_1/sol_cali_mea_000.png') # Fails maybe due to gridded puzzle
theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

# theImageMea_B = cv2.imread(prefix + 'puzzle_real_sample_black_big_hard3/sol_cali_mea_004.png')
theImageMea_B = cv2.imread(prefix + 'puzzle_real_sample_black_impossible/impossible_mea_002.png')
# theImageMea_B = cv2.imread(prefix + 'puzzle_real_sample_black_impossible_noLight/impossible_noLight_mea_007.png') # Fails maybe due to low light
# theImageMea_B = cv2.imread(prefix + 'puzzle_real_sample_black_small_cali_1/sol_cali_mea_015.png') # Fails maybe due to gridded puzzle
theImageMea_B = cv2.cvtColor(theImageMea_B, cv2.COLOR_BGR2RGB)

#====[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False, ret_thresh_mask=True)
theMaskMea_B = preprocess_real_puzzle(theImageMea_B, verbose=False, ret_thresh_mask=True)

# DEBUG VISUAL
# plt.imshow(theMaskSol_A)
# plt.show()
# plt.imshow(theMaskSol_B)
# plt.show()

#====[1.2] Create raw puzzle piece data.
#

theParams = CfgArrangement()
theParams.update(dict(minArea=400))

theGridSol = Arrangement.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A, theParams=theParams)
theGridMea = Arrangement.buildFrom_ImageAndMask(theImageMea_B, theMaskMea_B, theParams=theParams)

# DEBUG VISUAL
theGridSol.display_mp(ID_DISPLAY=True)
# theGridMea.display_mp(ID_DISPLAY=True)
# plt.show()

#==[2] Board Correspondence with SIFTCV.
#

CfgTrack   = board.CfgCorrespondences()
CfgTrack.matcher = 'SIFTCV'  
CfgTrack.matchParams = None
CfgTrack.forceMatches = opt.forceMatches
theTracker = board.Correspondences(CfgTrack, theGridSol)

theTracker.process(theGridMea)

print(theTracker.pAssignments)
print(theTracker.pAssignments_rotation)

theGridMea.display_mp(ID_DISPLAY=True)
plt.show()

# ============================ real06sift ===========================
