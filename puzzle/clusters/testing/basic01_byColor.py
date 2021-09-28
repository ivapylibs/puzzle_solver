#!/usr/bin/python3
# ============================ basic01_byColor ===========================
#
# @brief    Test script for basic functionality of byColor
#
# ============================ basic01_byColor ===========================

#
# @file     basic01_byColor.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/29  [created]
#
# ============================ basic01_byColor ===========================


# ==[0] Prep environment
import os

import cv2
import improcessor.basic as improcessor

from puzzle.clusters.byColor import byColor
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.parser.fromSketch import fromSketch
from puzzle.piece.regular import regular

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')

# ==[1.1] Create an improcesser to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000, pieceConstructor=regular))

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# plt.show()

# ==[2] Create a cluster instance and process the puzzle board.
#

theColorCluster = byColor(theBoardSol)
theColorCluster.process()

# ==[3] Display the extracted features.
#

print('Should see 15 pieces, each of them will have 4 features.')
print('The number of pieces:', len(theColorCluster.feature))
print('The number of features for each piece:', len(theColorCluster.feature[0]))

#
# ============================ basic01_byColor ===========================
