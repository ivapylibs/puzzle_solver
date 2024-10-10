#!/usr/bin/python3
# ============================= 60p_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (60p img)
#
#
# ============================= 60p_manager =============================
#
# @file     60p_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/07 [created]
#
# ============================= 60p_manager =============================

# ==[0] Prep environment
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np

import improcessor.basic as improcessor

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.parser.fromSketch import FromSketch
from puzzle.piece.regular import Regular
from puzzle.piece.sift import Sift
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
# theImageSol = cv2.imread(cpath + '/data/balloon.png')
theImageSol = cv2.imread(cpath + '/data/cocacola.jpg')
# theImageSol = cv2.imread(cpath + '/data/church.jpg')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/data/puzzle_60p_AdSt408534841.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[2] Create a Grid instance and explode it into a new board
#

print('Running through test cases. Will take a bit.')

theGridSol = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                            theParams=ParamGrid(areaThresholdLower=5000, pieceConstructor=Regular,
                                                                reorder=True))

epImage, _ = theGridSol.explodedPuzzle(dx=100, dy=100)

# ==[2.1] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                           cv2.dilate, (np.ones((3, 3), np.uint8),)
                           )
theMaskMea = improc.apply(epImage)

# cv2.imshow('debug', theMaskMea)
# cv2.waitKey()

theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea,
                                            theParams=ParamGrid(areaThresholdLower=1000, pieceConstructor=Regular,
                                                                reorder=True))

# ==[3] Create a manager
#
# theManager = manager(theGridSol, managerParms(matcher=edge()))

theManager = Manager(theGridSol, ManagerParms(matcher=Sift()))
theManager.process(theGridMea)

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
for pair in theManager.pAssignments.items():
    if pair[0] != pair[1]:
        num_failure = num_failure + 1

# Add the unmatched pairs
num_failure = num_failure + theManager.bMeas.size() - len(theManager.pAssignments)
print('Num. of failure cases:', num_failure)

plt.show()
#
# ============================= 60p_manager =============================
