#!/usr/bin/python3
#================================= real05sift ================================
##@file
# @brief    Testing SIFT on more involved puzzle piece comparison.
#           Pieces are not in same place in both boards, but differ.
#
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Patricio A. Vela        pvela@gatech.edu
#
# @date     2024/11/01  [created from real04sift]
#
# @quitf
#================================= real05sift ================================
#
# NOTE
#   100 columns. Indent 4 spaces.
#
#================================= real05sift ================================

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
theImageSol_B = cv2.imread(prefix + 'puzzle_real_sample_black/ExplodedWithRotationAndExchange_mea_0.png')
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
        thePiece_C.setPlacement(theGridSol.pieces[j].rLoc)
        theBoard.addPiece(thePiece_C)
    
  print(np.any(matchMat[i,::]))
  if not np.any(matchMat[i,::]):
    thePiece_C = theGridMea.pieces[i].rotatePiece(theta=0)
    thePiece_C.setPlacement(np.array([-250,-250]), isOffset=True)
    theBoard.addPiece(thePiece_C)

theGridMea.display_mp()
theBoard.display_mp()
theGridSol.display_mp()
print('--------------')
print(matchMat)
print("Pieces that failed to match are above and left-ish of the main set.")
print("The other visualized board is the solution board.")
plt.show()
#
# ============================ real05sift ===========================
