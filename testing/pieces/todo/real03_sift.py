#!/usr/bin/python3
#================================ real03_sift ================================
# YOU NEED TO DOCUMENT JUST LIKE THE OTHER CODE IN THE PARENT FOLDER.
# BELOW IS NOT ENTIRELY CORRECT. DO THE SAME FOR THE OTHER FILES.
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
#================================ real03_sift ================================

#==[0] Prep environment

import os

import cv2
import numpy as np
import matplotlib.pyplot as plt

from puzzle.builder.arrangement import Arrangement, CfgArrangement
from puzzle.board import Board
from puzzle.pieces.matchSimilar import SIFTCV, CfgSIFTCV
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
# THIS CODE IS NOT UP TO DATE.  SEE HOW WE USE PYTHON PACKAGE INFO TO
# SNAG THE FOLDER WITHOUT USING CURRENT PATH IN CODE FROM PARENT FOLDER.  
# SUCH AN APPROACH PROTECTS AGAINST CHANGES TO FOLDER LOCATION OF THE SCRIPT
# WITHOUT REQUIRING CODE CHANGES.  THE DATA LOCATION IS INTENDED TO BE PERMANENT.
# PLEASE REVIEW CODE IN PARENT FOLDE TO LEARN HOW TO FOLLOW BEST PRACTICE.
# IN GENERAL UPDATING CODE IS MORE THAN JUST GETTING TO RUN, BUT REVIEWING
# THE OVERALL STYLE OF RELATED CODE AND CONFORMING TO IT.
#
theImageSol_A = cv2.imread(cpath + '/../../data/puzzle_real_sample_black/SinglePiece_mea_2.png')
theImageSol_A = cv2.cvtColor(theImageSol_A, cv2.COLOR_BGR2RGB)

theImageSol_B = cv2.imread(cpath + '/../../data/puzzle_real_sample_black/SinglePiece_mea_1.png')
theImageSol_B = cv2.cvtColor(theImageSol_B, cv2.COLOR_BGR2RGB)

#==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol_A = preprocess_real_puzzle(theImageSol_A, verbose=False)
theMaskSol_B = preprocess_real_puzzle(theImageSol_B)

#==[1.2] Create raw puzzle piece data.
#
theParams = CfgArrangement()
theParams.update(dict(minArea=100))

# DEBUG VISUAL
#plt.imshow(theMaskSol_A)
#plt.figure()
#plt.imshow(theMaskSol_B)
#print("Review Masks. Hit q on windows to close them")
#plt.show()

theGridSol = Arrangement.buildFrom_ImageAndMask(theImageSol_B, theMaskSol_B, theParams)
theGridMea = Arrangement.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A, theParams)

# DEBUG VISUAL
#theGridSol.display_mp()
#theGridMea.display_mp()
#print("Review boards. Hit q on windows to close them")
#plt.show()

## == OLD STUFF
# USING AN ARRANGEMENT WAS CORRECT.  DID YOU LOOK AT THE IMAGE?
# IT WAS A SINGLE PUZZLE PIECE.  THERE IS NO NEED TO USE A GRIDDED BOARD
# TO LOAD THE INFORMATION. I ADDED THE VISUALIZATION CODE ABOVE TO SEE
# THE PUZZLE BOARDS AND THE PIECES ON THE BOARD.  IN THIS CASE THERE WAS 
# JUST ONE PIECE. IN FUTURE, YOU CAN DO THE SAME AND SHOULD SEE SUCH DEBUGGING
# CODE IN THE FILES. WHEN USED AND CONFIRMED, IT IS BEST TO COMMENT OUT
# SO THAT THE DISPLAY DOES NOT OCCUR.  LEAVING THE CODE PROVIDES A WAY FOR PEOPLE
# TO KNOW WHAT ARE GOOD DEBUG OPTIONS AT THAT CODE POINT. THEY CAN UNCOMMMENT
# IN CASE IT HELPS THEIR OWN DEBUGGING.
#
# DELETE THIS NOTE AFTER READING. DELETE THIS OLD STUFF TOO. IT IS CORRECT ABOVE.
#
# theGridMea = Arrangement.buildFrom_ImageAndMask(theImageSol_A, theMaskSol_A,
#                                                 theParams=ParamArrange(areaThresholdLower=1000))
# theGridSol = Arrangement.buildFrom_ImageAndMask(theImageSol_B, theMaskSol_B,
#                                                 theParams=ParamArrange(areaThresholdLower=1000))
## == OLD STUFF

#==[2] Create a new board
#
theBoard = Board()
thePiece_A = theGridMea.pieces[0]
thePiece_B = theGridSol.pieces[0]

#==[3] Create a sift matcher
#

SIFTParams = CfgSIFTCV()
theMatcher = SIFTCV(SIFTParams)
theMatcher = SIFTCV()

#==[4] Display the new board and the comparison result.
#
print('Should see True')

# ABOVE CODE SNAGGED THE FIRST ITEM FROM EACH BOARD ALREADY AS THE VARIABLES
# thePiece_A and thePiece_B. JUST NEED TO SEND ALONG BELOW.  DO NOT RE-INDEX.
# I CHANGED THE CODE TO USE thePiece_X RATHER THAN theGridYYY.pieces[0].
# DELETE WHEN REVIEWED.
# 
ret = theMatcher.compare(thePiece_A, thePiece_B)
print('\nSIFT Matching information:')
print(ret)
print('\n\n')

#==[5] Manipulate the pieces following sift result.
#
print('Should see two 100% overlapped pieces (or nearly so).')

if ret[0]:
    thePiece_C = thePiece_A.rotatePiece(theta=-ret[1])
    thePiece_C.setPlacement(r=thePiece_B.rLoc - thePiece_A.rLoc, isOffset=True)

    theBoard.addPiece(thePiece_B)
    theBoard.addPiece(thePiece_C)

    theBoard.display_mp(ID_DISPLAY=True)
    plt.show()
    print('Pieces do match.  Piece 2 on top of Piece 1.')
else:
    print('Pieces do not match')
#
#================================ real03_sift ================================
