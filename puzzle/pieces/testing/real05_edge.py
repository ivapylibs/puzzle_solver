#!/usr/bin/python3
# ============================ real05_edge ===========================
#
# @brief    Test script for assembling the solution board from
#           well-separated puzzle pieces.
#
# ============================ real05_edge ===========================

#
# @file     real05_edge.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/19  [created]
#
# ============================ real05_edge ===========================

# ==[0] Prep environment

import os
import pkg_resources

import cv2
import matplotlib.pyplot as plt
import numpy as np

from puzzle.board import Board
from puzzle.builder.gridded import Gridded, CfgGridded
from puzzle.piece import Regular
from puzzle.utils.imageProcessing import preprocess_real_puzzle, find_nonzero_mask
import improcessor.basic as improcessor

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')
theImageSol_A = cv2.imread(prefix + 'puzzle_real_sample_black/Exploded_mea_0.png')
theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

#==[1.2] Create raw puzzle piece data from the source image.
#        Requires using an improcessor to generate a mask from the image.
#        Here this works because the puzzle pieces are sparsely placed
#        on a black mat.

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                    improcessor.basic.thresh, ((60, 255, cv2.THRESH_BINARY),))
theMaskSol_A = improc.apply(theImageSol_A)

#DEBUG VISUAL
#plt.imshow(theMaskSol_A)
#plt.show()

theParams  = CfgGridded();
print(theParams)
theParams.update(dict(minArea=1000, pieceBuilder='Regular', 
                                     gridding='arrangedbox',reorder=True))

theGridMea = Gridded.buildFrom_ImageAndMask(theImageSol_A, 
                                            theMaskSol_A , theParams)

theImage = theGridMea.toImage(COLOR=(0,100,0), ID_DISPLAY=True, CONTOUR_DISPLAY=True)

#DEBUG VISUAL
plt.imshow(theImage)
plt.show()

# ==[2] Assemble the puzzle according to grid pos
# (we assume the relative location has not been changed)
#

theBoard = Board()
theRegular_0 = theGridMea.pieces[0]
#theRegular_0 = theRegular_0.rotatePiece(theta=theRegular_0.theta)
theBoard.addPiece(theRegular_0)

#IAMHERE.
for i in range(1, theGridMea.size()):

    theRegular_0 = theBoard.pieces[i - 1]

    theRegular_1 = theGridMea.pieces[i]
    #theRegular_1 = theRegular_1.rotatePiece(theta=theRegular_1.theta)

    if i == 3:
        theRegular_0 = theBoard.pieces[0]
        piece_A_coord = find_nonzero_mask(theRegular_0.edge[3].mask) + np.array(theRegular_0.rLoc).reshape(-1, 1)
        piece_B_coord = find_nonzero_mask(theRegular_1.edge[2].mask) + np.array(theRegular_1.rLoc).reshape(-1, 1)
    else:
        piece_A_coord = find_nonzero_mask(theRegular_0.edge[1].mask) + np.array(theRegular_0.rLoc).reshape(-1, 1)
        piece_B_coord = find_nonzero_mask(theRegular_1.edge[0].mask) + np.array(theRegular_1.rLoc).reshape(-1, 1)

    y_relative = np.max(piece_B_coord[1, :]) - np.max(piece_A_coord[1, :])
    x_relative = np.max(piece_B_coord[0, :]) - np.max(piece_A_coord[0, :])

    #theRegular_1.setPlacement([int(-x_relative), int(-y_relative)], offset=True)
    theBoard.addPiece(theRegular_1)

# ==[3] Display
#

f, axarr = plt.subplots(1, 2)

axarr[0].imshow(theGridMea.toImage(ID_DISPLAY=True))
axarr[0].title.set_text('The original puzzle pieces')

axarr[1].imshow(theBoard.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY=False))
axarr[1].title.set_text('The assembled puzzle pieces')

plt.show()

# ============================ real05_edge ===========================
