#!/usr/bin/python3
#================================= real06sift ================================
##@file
# @brief    Board Correspondences using SIFT.
#
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Devesh Nath        dnath7@gatech.edu
#
# @date     2024/11/09  [created from real05sift]
#
# @quitf
#================================= real06sift ================================
#
# NOTE
#   100 columns. Indent 4 spaces.
#
#================================= real06sift ================================

# ==[0] Prep environment

import os
import pkg_resources

import cv2
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.arrangement import Arrangement, CfgArrangement
from puzzle.utils.imageProcessing import preprocess_real_puzzle
import puzzle.board as board

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImageSol_A = cv2.imread(prefix + 'puzzle_real_sample_black/Exploded_mea_0.png')
theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

# Used to be '/../../data/puzzle_real_sample_black/GTSolBoard_mea_0.png' which doesn't make
# sense because the individual pieces cannot be extracted.  Why did this exist??  Changed
# to be two exploded pieces with intent to match.  Really this should use board to board
# data association, which is what the board manager does (right?).
#
theImageMea_B = cv2.imread(prefix + 'puzzle_real_sample_black/ExplodedWithRotationAndExchange_mea_0.png')
theImageMea_B = cv2.cvtColor(theImageMea_B, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False)
theMaskMea_B = preprocess_real_puzzle(theImageMea_B, verbose=False)

# DEBUG VISUAL
# plt.imshow(theMaskSol_A)
# plt.show()
# plt.imshow(theMaskSol_B)
# plt.show()

# ==[1.2] Create raw puzzle piece data.
#

theParams = CfgArrangement()
theParams.update(dict(minArea=400))

theGridSol = Arrangement.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A, theParams=theParams)
theGridMea = Arrangement.buildFrom_ImageAndMask(theImageMea_B, theMaskMea_B, theParams=theParams)

# DEBUG VISUAL
theGridSol.display_mp(ID_DISPLAY=True)
theGridMea.display_mp(ID_DISPLAY=True)
# plt.show()

#==[2] Board Correspondence with SIFTCV.
#

CfgTrack   = board.CfgCorrespondences()
CfgTrack.matcher = 'SIFTCV'  
CfgTrack.matchParams = None
theTracker = board.Correspondences(CfgTrack, theGridSol)

'''
   Here I was expecting to get the correspondences from the tracker and apply them to 
   theGridMea to show that this works. However theTracker.process makes changes to the GridMea.
   Visualized the changes later. The correspondences are 'mostly' correct but except for puzzle piece
   4 which gets mapped to 7?
'''
theTracker.process(theGridMea)

'''
   The puzzle pieces in the plots are labeled with index startiong at 1, pAssignments start at index 0.
   Not sure if thats a bug we need to solve. pAssignments_rotation is missing rotation for piece with index 1.
'''
print(theTracker.pAssignments)
print(theTracker.pAssignments_rotation)

theGridMea.display_mp(ID_DISPLAY=True)
plt.show()

# ============================ real06sift ===========================
