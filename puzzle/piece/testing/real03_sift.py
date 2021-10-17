#!/usr/bin/python3
# ============================ real03_sift ===========================
#
# @brief    Test script for the most basic functionality of sift features
#           for puzzle pieces. (real images)
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
import numpy as np

from puzzle.builder.board import board
from puzzle.piece.sift import sift
from puzzle.piece.template import template
from puzzle.utils.imageProcessing import preprocess_real_puzzle

from puzzle.builder.arrangement import arrangement, paramArrange


fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
# theImageSol_A = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample/SinglePiece5_meaBoard.png')
theImageSol_A = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/SinglePiece_mea_1.png')
theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

# theImageSol_B = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample/SinglePiece2_meaBoard.png')
theImageSol_B = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/SinglePiece_mea_2.png')
# theImageSol_B = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/GTSolBoard_mea_0.png')

theImageSol_B = cv2.cvtColor(theImageSol_B, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False)
theMaskSol_B = preprocess_real_puzzle(theImageSol_B)

# ==[1.2] Create raw puzzle piece data.
#

theGrid_Sol = arrangement.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A,
                                             theParams=paramArrange(areaThreshold=1000))
theGrid_Mea = arrangement.buildFrom_ImageAndMask(theImageSol_B, theMaskSol_B,
                                             theParams=paramArrange(areaThreshold=1000))

# ==[2] Create a new board
#
theBoard = board()
thePiece_A = theGrid_Mea.pieces[0]
thePiece_B = theGrid_Sol.pieces[0]

# ==[3] Create a sift matcher
#
theMatcher = sift()

# ==[4] Display the new board and the comparison result.
#
print('Should see True')

ret = theMatcher.compare(theGrid_Mea.pieces[0], theGrid_Sol.pieces[0])
print(ret)

# ==[5] Manipulate the pieces following sift result.
#
print('Should see two 100% overlapped pieces')

thePiece_C = thePiece_A.rotatePiece(theta= -ret[1])
thePiece_C.setPlacement(r=thePiece_B.rLoc-thePiece_A.rLoc, offset=True)
theBoard.addPiece(thePiece_B)
theBoard.addPiece(thePiece_C)

theBoard.display(ID_DISPLAY=True)

plt.show()
#
# ============================ real03_sift ===========================
