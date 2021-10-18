#!/usr/bin/python3
# ============================ real04_sift ===========================
#
# @brief    Test script for the most basic functionality of sift features
#           for puzzle pieces. (separate multiple pieces + connected solution from real images)
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

from puzzle.builder.arrangement import arrangement, paramArrange
from puzzle.builder.board import board
from puzzle.piece.sift import sift
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol_A = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/Exploded_mea_0.png')
# theImageSol_A = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/SinglePiece_mea_2.png')
theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

theImageSol_B = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/GTSolBoard_mea_1.png')
theImageSol_B = cv2.cvtColor(theImageSol_B, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False)
theMaskSol_B = preprocess_real_puzzle(theImageSol_B)

# ==[1.2] Create raw puzzle piece data.
#

theGrid_Sol = arrangement.buildFrom_ImageAndMask(theImageSol_B, theMaskSol_B,
                                                 theParams=paramArrange(areaThreshold=1000))
theGrid_Mea = arrangement.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A,
                                                 theParams=paramArrange(areaThreshold=1000))

# ==[3] Create a sift matcher
#


for i in range(theGrid_Mea.size()):
    theMatcher = sift()

    ret = theMatcher.compare(theGrid_Mea.pieces[i], theGrid_Sol.pieces[0])
    if ret[0]:
        theBoard = board()
        thePiece_C = theGrid_Mea.pieces[i].rotatePiece(theta=-ret[1])

        # Method 1: without knowing thePiece_B's rLoc
        # The most important part is to recompute the relative position from the
        # transformed top-left to new top-left for a specific piece
        trans = np.eye(3)
        trans[0:2] = ret[2][0:2]
        rLoc_new = trans @ np.array([theGrid_Mea.pieces[i].rLoc[0], theGrid_Mea.pieces[i].rLoc[1], 1]).reshape(-1, 1)
        rLoc_new = rLoc_new.flatten()[:2]
        rLoc_relative = rLoc_new - theGrid_Mea.pieces[i].rLoc - thePiece_C.rLoc_relative
        thePiece_C.setPlacement(r=rLoc_relative.astype('int'), offset=True)

        # thePiece_C.setPlacement(r=theGrid_Sol.pieces[0].rLoc - theGrid_Mea.pieces[i].rLoc, offset=True)
        theBoard.addPiece(theGrid_Sol.pieces[0])
        theBoard.addPiece(thePiece_C)

        theBoard.display(ID_DISPLAY=True)

        plt.show()
#
# ============================ real04_sift ===========================
