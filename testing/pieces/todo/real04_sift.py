#!/usr/bin/python3
# ============================ real04_sift ===========================
#
# @brief    Test script for the most basic functionality of sift features
#           for puzzle pieces. (well-separated pieces + connected solution from real images)
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

import cv2
import matplotlib.pyplot as plt
import numpy as np

# from puzzle.builder.arrangement import Arrangement, ParamArrange
from puzzle.builder.gridded import Gridded, CfgGridded
# from puzzle.builder.board import Board
from puzzle.board import Board
# from puzzle.piece.sift import Sift
from puzzle.pieces.matchSimilar import SIFTCV
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol_A = cv2.imread(cpath + '/../../data/puzzle_real_sample_black/Exploded_mea_0.png')
# theImageSol_A = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/SinglePiece_mea_2.png')
theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

theImageSol_B = cv2.imread(cpath + '/../../data/puzzle_real_sample_black/GTSolBoard_mea_0.png')
theImageSol_B = cv2.cvtColor(theImageSol_B, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False)
theMaskSol_B = preprocess_real_puzzle(theImageSol_B)

# ==[1.2] Create raw puzzle piece data.
#

theParams = CfgGridded()
theParams.update(dict(areaThresholdLower=1000))

theGridSol = Gridded.buildFrom_ImageAndMask(theImageSol_B, theMaskSol_B, theParams=theParams)
theGridMea = Gridded.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A, theParams=theParams)

# theGridSol = Arrangement.buildFrom_ImageAndMask(theImageSol_B, theMaskSol_B,
#                                                 theParams=ParamArrange(areaThresholdLower=1000))
# theGridMea = Arrangement.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A,
#                                                 theParams=ParamArrange(areaThresholdLower=1000))

# ==[3] Create a sift matcher and display the match
#

print('Should see the match pieces one by one. Some fail to match.')

for i in range(theGridMea.size()):
    theMatcher = SIFTCV()

    ret = theMatcher.compare(theGridMea.pieces[i], theGridSol.pieces[0])
    if ret[0]:
        theBoard = Board()
        thePiece_C = theGridMea.pieces[i].rotatePiece(theta=-ret[1])

        # Method 1: without knowing thePiece_B's rLoc
        # The most important part is to recompute the relative position from the
        # transformed top-left to new top-left for a specific piece
        trans = np.eye(3)
        trans[0:2] = ret[2][0:2]
        rLoc_new = trans @ np.array([theGridMea.pieces[i].rLoc[0], theGridMea.pieces[i].rLoc[1], 1]).reshape(-1, 1)
        rLoc_new = rLoc_new.flatten()[:2]
        rLoc_relative = rLoc_new - theGridMea.pieces[i].rLoc - thePiece_C.rLoc_relative
        thePiece_C.setPlacement(r=rLoc_relative.astype('int'), offset=True)

        theBoard.addPiece(theGridSol.pieces[0])
        theBoard.addPiece(thePiece_C)

        theBoard.display(ID_DISPLAY=True)

        plt.show()
#
# ============================ real04_sift ===========================
