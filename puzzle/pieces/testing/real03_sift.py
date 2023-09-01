#!/usr/bin/python3
# ============================ real03_sift ===========================
#
# @brief    Test script for the most basic functionality of sift features
#           for puzzle pieces. (well-separated pieces from real images)
#
# ============================ real03_sift ===========================

#
# @file     real03_sift.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/16  [created]
#
# ============================ real03_sift ===========================

# ==[0] Prep environment

import os

import cv2
import matplotlib.pyplot as plt

from puzzle.builder.arrangement import Arrangement, ParamArrange
from puzzle.builder.board import Board
from puzzle.piece.sift import Sift
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol_A = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/SinglePiece_mea_2.png')
theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

theImageSol_B = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/SinglePiece_mea_1.png')
# theImageSol_B = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/GTSolBoard_mea_0.png')

theImageSol_B = cv2.cvtColor(theImageSol_B, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False)
theMaskSol_B = preprocess_real_puzzle(theImageSol_B)

# ==[1.2] Create raw puzzle piece data.
#

theGridMea = Arrangement.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A,
                                                theParams=ParamArrange(areaThresholdLower=1000))
theGridSol = Arrangement.buildFrom_ImageAndMask(theImageSol_B, theMaskSol_B,
                                                theParams=ParamArrange(areaThresholdLower=1000))

# ==[2] Create a new board
#
theBoard = Board()
thePiece_A = theGridMea.pieces[0]
thePiece_B = theGridSol.pieces[0]

# ==[3] Create a sift matcher
#
theMatcher = Sift()

# ==[4] Display the new board and the comparison result.
#
print('Should see True')

ret = theMatcher.compare(theGridMea.pieces[0], theGridSol.pieces[0])
print(ret)

# ==[5] Manipulate the pieces following sift result.
#
print('Should see two 100% overlapped pieces')

thePiece_C = thePiece_A.rotatePiece(theta=-ret[1])

# # Method 1: without knowing thePiece_B's rLoc
# # The most important part is to recompute the relative position from the
# # transformed top-left to new top-left for a specific piece
# trans = np.eye(3)
# trans[0:2]= ret[2][0:2]
# rLoc_new = trans @ np.array([thePiece_A.rLoc[0],thePiece_A.rLoc[1],1]).reshape(-1,1)
# rLoc_new = rLoc_new.flatten()[:2]
# rLoc_relative = rLoc_new -thePiece_A.rLoc - thePiece_C.rLoc_relative
# thePiece_C.setPlacement(r=rLoc_relative.astype('int'), offset=True)

# Method 2:
thePiece_C.setPlacement(r=thePiece_B.rLoc - thePiece_A.rLoc, offset=True)

theBoard.addPiece(thePiece_B)
theBoard.addPiece(thePiece_C)

theBoard.display(ID_DISPLAY=True)

plt.show()
#
# ============================ real03_sift ===========================
