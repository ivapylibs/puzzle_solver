#!/usr/bin/python3
# ============================= 15pEdge_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (15p img)
#
#
# ============================= 15pEdge_manager =============================
#
# @file     15pEdge_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/28 [created]
#
# ============================= 15pEdge_manager =============================

# ==[0] Prep environment
import os

import cv2
import improcessor.basic as improcessor
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.manager import manager, managerParms
from puzzle.parser.fromSketch import fromSketch
from puzzle.piece.edge import edge
from puzzle.piece.regular import regular

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/data/puzzle_15p_123rf.png')

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[2] Create a Grid instance and explode it into a new board
#

print('Running through test cases. Will take a bit.')

theGrid_src = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                             theParams=paramGrid(areaThresholdLower=5000, pieceConstructor=regular,
                                                                 reorder=True))

epImage, _ = theGrid_src.explodedPuzzle(dx=100, dy=100)

# ==[2.1] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                           cv2.dilate, (np.ones((3, 3), np.uint8),)
                           )
theMaskSol_new = improc.apply(epImage)

# cv2.imshow('debug', theMaskSol_new)
# cv2.waitKey()


theGrid_new = gridded.buildFrom_ImageAndMask(epImage, theMaskSol_new,
                                             theParams=paramGrid(areaThresholdLower=1000, pieceConstructor=regular,
                                                                 reorder=True))

# ==[3] Create a manager
#

theManager = manager(theGrid_src, managerParms(matcher=edge()))
theManager.process(theGrid_new)

# ==[4] Display. Should see some ids on the puzzle pieces
# while the ids in the assignment board refer to the ids in the solution board.
#
bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)
bSolImage = theManager.solution.toImage(ID_DISPLAY=True)

f, axarr = plt.subplots(1, 2)
axarr[0].imshow(bMeasImage)
axarr[0].title.set_text('Measurement')
axarr[1].imshow(bSolImage)
axarr[1].title.set_text('Solution')

# Show assignment
print('The first index refers to the measured board while the second one refers to the solution board.')
print(theManager.pAssignments)

num_failure = 0
for pair in theManager.pAssignments:
    if pair[0] != pair[1]:
        num_failure = num_failure + 1

# Add the unmatched pairs
num_failure = num_failure + theManager.bMeas.size() - len(theManager.pAssignments)
print('Num. of failure cases:', num_failure)

plt.show()

#
# ============================= 15pEdge_manager =============================
