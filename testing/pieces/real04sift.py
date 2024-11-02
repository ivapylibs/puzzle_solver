#!/usr/bin/python3
# ============================ real04_sift ===========================
#
# @brief    Test script for the most basic functionality of sift features
#           for puzzle pieces. (well-separated pieces + connected solution from
#           real images)
#
# ============================ real04_sift ===========================

#
# @file     real04_sift.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/17  [created]
#
# ============================ real04_sift ===========================

# ==[0] Prep environment

import os
import pkg_resources

import cv2
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.arrangement import Arrangement, CfgArrangement
from puzzle.board import Board
from puzzle.pieces.matchSimilar import SIFTCV
from puzzle.utils.imageProcessing import preprocess_real_puzzle

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
theImageSol_B = cv2.imread(prefix + 'puzzle_real_sample_black/ExplodedWithRotation_mea_0.png')
theImageSol_B = cv2.cvtColor(theImageSol_B, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False)
theMaskSol_B = preprocess_real_puzzle(theImageSol_B, verbose=False)

# DEBUG VISUAL
#plt.imshow(theMaskSol_A)
#plt.imshow(theMaskSol_B)

# ==[1.2] Create raw puzzle piece data.
#

theParams = CfgArrangement()
theParams.update(dict(minArea=400))

theGridSol = Arrangement.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A, theParams=theParams)
theGridMea = Arrangement.buildFrom_ImageAndMask(theImageSol_B, theMaskSol_B, theParams=theParams)

# ==[3] Create a sift matcher and display the match
#

print('Matched pieces in new board for comparison to solution board. Some fail to match.')
print('This is where assignment strategy might work, with lower bound on acceptable.')

# DEBUG VISUAL
#theGridSol.display_mp(ID_DISPLAY=True)
#theGridMea.display_mp(ID_DISPLAY=True)
#plt.show()

matchMat = np.full((theGridMea.size(), theGridSol.size()), False)

theMatcher = SIFTCV()
theBoard = Board()

for i in range(theGridMea.size()):
  print('--------------')

  for j in range(theGridSol.size()):

    ret = theMatcher.compare(theGridMea.pieces[i], theGridSol.pieces[j])
    matchMat[i,j] = ret[0]

    if ret[0]:
        thePiece_C = theGridMea.pieces[i].rotatePiece(theta=-ret[1])
        theBoard.addPiece(thePiece_C)

theBoard.display_mp()
theGridSol.display_mp()
print('--------------')
print(matchMat)
plt.show()
#
# ============================ real04_sift ===========================
