#!/usr/bin/python3
# ============================ real02_sift ===========================
#
# @brief    Test script for the most basic functionality of sift features
#           for puzzle pieces. (single piece from real images)
#
# ============================ real02_sift ===========================

#
# @file     real02_sift.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/10  [created]
#
# ============================ real02_sift ===========================

# ==[0] Prep environment

import os

import cv2
import matplotlib.pyplot as plt

from puzzle.builder.board import board
from puzzle.piece.sift import sift
from puzzle.piece.template import template
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
# theImageSol_A = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample/SinglePiece5_meaBoard.png')
theImageSol_A = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/SinglePiece_mea_1.png')

theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

# theImageSol_B = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample/SinglePiece2_meaBoard.png')
theImageSol_B = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/SinglePiece_mea_2.png')

theImageSol_B = cv2.cvtColor(theImageSol_B, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False)
theMaskSol_B = preprocess_real_puzzle(theImageSol_B)

# ==[1.2] Create raw puzzle piece data.
#

thePiece_A = template.buildFromMaskAndImage(theMaskSol_A, theImageSol_A)
thePiece_B = template.buildFromMaskAndImage(theMaskSol_B, theImageSol_B)

# ==[2] Create a new board
#
theBoard = board()
theBoard.addPiece(thePiece_A)
theBoard.addPiece(thePiece_B)

# ==[3] Create an edge matcher
#

theMatcher = sift()

# ==[4] Display the new board and the comparison result.
#
print('Should see True.')
print(theMatcher.compare(thePiece_A, thePiece_B))

# # Debug only
#
# ret = theMatcher.compare(thePiece_A, thePiece_B)
# dst = cv2.warpAffine(thePiece_A.y.image, ret[2][:2], (thePiece_A.y.size[0], thePiece_A.y.size[1]))
# cv2.imshow('B',thePiece_B.y.image)
# cv2.imshow('A_transformed',dst)
# cv2.waitKey()

theBoard.display()

plt.show()
#
# ============================ real02_sift ===========================
