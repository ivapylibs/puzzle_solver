#!/usr/bin/python3
#================================= real06sift ================================
##@file
# @brief    Board Correspondences using SIFT.
#
#
#  Since the two boards were captured under different visual settings, this
#  script can have a missed match.  Whether it will or not depends on whether
#  there is a further check to reject pooor matches.  That will involve the
#  forceMatches option.  If it is true, then the source pieces will be forced
#  to match when associated.  If it is false, then the association will be
#  tested against the matchers internal decision classifier to accept or reject
#  the match.  In essence it performs assignment verification.
#
#  Forcing matches operates independently of the garbage class option.  Both
#  can be enabled and have the parameters set such a non-garbage assignment can
#  be estimated but then the match check can fail and reject the assignment.
#  How they operate depends on the scoring thresholds for the garbage class and
#  for accepting a match.  Having properly differentiated treshold values can
#  lead to assignment verification.
#
#  > ./real06sift
#  > ./real06sift --withMatches=True
#  > ./real06sift --withMatches=False
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

#==[0] Prep environment

import os
import pkg_resources
import argparse

import cv2
import matplotlib.pyplot as plt
import numpy as np
from ivapy.Configuration import AlgConfig
import ivapy.display_cv as dcv
from ivapy.helper import strtobool

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
theGridSol.display_mp(ID_DISPLAY=True)
theGridMea.display_mp(ID_DISPLAY=True)
# plt.show()

#==[2] Board Correspondence with SIFTCV.
#

CfgTrack   = board.CfgCorrespondences()
CfgTrack.matcher = 'SIFTCV'  
CfgTrack.matchParams = None
CfgTrack.forceMatches = opt.forceMatches
theTracker = board.Correspondences(CfgTrack, theGridSol)

'''
   If forceMatches is True, then all pieces will be assigned to _best_ match in other board.
   If forceMatches if False, then one association fails the post-assignment
   matching test and triggers a failure to associate.  The piece is then given a new ID since
   doUpdate is True.
'''
theTracker.process(theGridMea)

'''
   The puzzle pieces in the plots are labeled with index startiong at 1,
   pAssignments start at index 0.  Not sure if thats a bug we need to solve.
   pAssignments_rotation is missing rotation for piece with index 1.
'''
print(theTracker.pAssignments)
print(theTracker.pAssignments_rotation)

theGridMea.display_mp(ID_DISPLAY=True)
plt.show()

# ============================ real06sift ===========================
