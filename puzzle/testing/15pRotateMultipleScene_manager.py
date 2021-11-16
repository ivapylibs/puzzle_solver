#!/usr/bin/python3
# ============================= 15pRotateMultipleScene_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (15p img + random rotation & overlapping)
#
#
# ============================= 15pRotateMultipleScene_manager =============================
#
# @file     15pRotateMultipleScene_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/11/15 [created]
#
# ============================= 15pRotateMultipleScene_manager =============================

# ==[0] Prep environment
import os

import cv2
import improcessor.basic as improcessor
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.manager import manager, managerParms
from puzzle.parser.fromSketch import fromSketch
from puzzle.piece.sift import sift
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
# theImageSol = cv2.imread(cpath + '/data/balloon.png')
theImageSol = cv2.imread(cpath + '/data/cocacola.jpg')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/data/puzzle_15p_123rf.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[2] Create a Grid instance.
#

print('Running through test cases. Will take a bit.')

theGridSol = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                            theParams=paramGrid(areaThresholdLower=5000, reorder=True))

# ==[2.1] Explode it into a new board.
#
_, epBoard = theGridSol.explodedPuzzle(dx=150, dy=150)

# ==[2.2] Randomly swap the puzzle pieces.
#
theGridMea = gridded(epBoard, paramGrid(reorder=True))

_, epBoard = theGridMea.swapPuzzle()

# ==[2.3] Randomly rotate & move the puzzle pieces.
#

gt_rotation = []
for i in range(epBoard.size()):
    gt_rotation.append(np.random.randint(0, 70))
    epBoard.pieces[i] = epBoard.pieces[i].rotatePiece(gt_rotation[-1])

for i in range(epBoard.size()):
    epBoard.pieces[i].setPlacement(r=[np.random.randint(-100, 100), np.random.randint(-100, 100)], offset=True)

epImage = epBoard.toImage(CONTOUR_DISPLAY=False)

bPerImage = epBoard.toImage(CONTOUR_DISPLAY=True)

# # Debug only
# epImage = epBoard.toImage(ID_DISPLAY=True,CONTOUR_DISPLAY=True,COLOR=(0,255,0))
# plt.imshow(epImage)
# plt.show()

# ==[2.4] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                           cv2.dilate, (np.ones((3, 3), np.uint8),)
                           )
theMaskMea = improc.apply(epImage)

# Debug only
# cv2.imshow('debug', theMaskMea)
# cv2.waitKey()

theGridMea = gridded.buildFrom_ImageAndMask(epImage, theMaskMea,
                                            theParams=paramGrid(areaThresholdLower=1000, areaThresholdUpper=55000))

# Debug only
# epImage=theGridMea.toImage(ID_DISPLAY=True,CONTOUR_DISPLAY=True,COLOR=(0,255,0))
# plt.imshow(epImage)
# plt.show()

# ==[3] Create a manager
#

theManager = manager(theGridSol, managerParms(matcher=sift()))
theManager.process(theGridMea)

# ==[4] Display. Should see some ids on the puzzle pieces
# while the ids in the assignment board refer to the ids in the solution board.
#
bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)
bSolImage = theManager.solution.toImage(ID_DISPLAY=True)

f, axarr = plt.subplots(1, 3)
axarr[0].imshow(bPerImage)
axarr[0].title.set_text('Perceived')
axarr[1].imshow(bMeasImage)
axarr[1].title.set_text('Measured')
axarr[2].imshow(bSolImage)
axarr[2].title.set_text('Solution')

text = f'The first index refers to the measured board while the second one refers to the solution board. \n ' \
       f'Note that the index in different boards may refer to different puzzle pieces. \n' \
       f'{theManager.pAssignments}'

plt.gcf().text(0.1, 0.7, text, fontsize=14)

# Show assignment
print('The first index refers to the measured board while the second one refers to the solution board. Note that '
      'the index in different boards may refer to different puzzle pieces.')
print(theManager.pAssignments)

plt.show()
#
# ============================= 15pRotateMultipleScene_manager =============================
