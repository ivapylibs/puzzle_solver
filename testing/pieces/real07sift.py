#!/usr/bin/python3
#================================= real07sift ================================
##@file
# @brief    Floating Board Correspondences using SIFT.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Devesh Nath        dnath7@gatech.edu
#
# @date     2024/11/16  [created from real06sift]
#
# @quitf
#================================= real07sift ================================
#
# NOTE
#   100 columns. Indent 4 spaces.
#
#================================= real07sift ================================

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

theImageSol_A = cv2.imread(prefix + 'puzzle_real_sample_black/Exploded_mea_0.png')
theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

theImageMea_B = cv2.imread(prefix + 'puzzle_real_sample_black/ExplodedWithRotationAndExchange_mea_0.png')
theImageMea_B = cv2.cvtColor(theImageMea_B, cv2.COLOR_BGR2RGB)

#====[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False)
theMaskMea_B = preprocess_real_puzzle(theImageMea_B, verbose=False)

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
# theGridSol.display_mp(ID_DISPLAY=True)
# theGridMea.display_mp(ID_DISPLAY=True)
# plt.show()

#==[2] Board Correspondence with SIFTCV.
#

CfgTrack   = board.CfgCorrespondences()
CfgTrack.matcher = 'SIFTCV'  
CfgTrack.matchParams = None
CfgTrack.forceMatches = opt.forceMatches
theTracker = board.Correspondences(CfgTrack, theGridSol)


#==[3] Set up interactive plotting
plt.ion()  
fig, axs = plt.subplots(1, 3, figsize=(15, 5)) 

# Simulate measured board updates
shift_up = np.array([0, -5])
shift_left = np.array([-5, 0])
shift_diag = np.array([-5, -5])

theGridSol.display_mp(ID_DISPLAY=True, ax=axs[0])
axs[0].set_title("Solution Board")

theGridMea.display_mp(ID_DISPLAY=True, ax=axs[1])
axs[1].set_title("Original Measured Board")

plt.tight_layout()

for i in range(70):
    # Apply shifts to measured board pieces
    theGridMea.pieces[0].setPlacement(shift_up, True)
    theGridMea.pieces[1].setPlacement(shift_up, True)
    theGridMea.pieces[2].setPlacement(shift_up, True)
    theGridMea.pieces[3].setPlacement(shift_left, True)
    theGridMea.pieces[4].setPlacement(shift_left, True)
    theGridMea.pieces[5].setPlacement(shift_diag, True)

    # Correspondences
    theTracker.process(theGridMea)

    # Update Measured Board plot
    theGridMea.display_mp(ID_DISPLAY=True, ax=axs[2])
    axs[2].set_title("Current Measured Board")

    plt.pause(0.05)  

plt.ioff()  
plt.show()  

# ============================ real07sift ===========================
