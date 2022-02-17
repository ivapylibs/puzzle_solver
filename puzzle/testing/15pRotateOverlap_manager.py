#!/usr/bin/python3
# ============================= 15pRotateOverlap_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (15p img + random rotation & overlapping)
#
#
# ============================= 15pRotateOverlap_manager =============================
#
# @file     15pRotateOverlap_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/11/2 [created]
#
# ============================= 15pRotateOverlap_manager =============================

# ==[0] Prep environment
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np

import improcessor.basic as improcessor

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.parser.fromSketch import FromSketch
from puzzle.piece.sift import Sift
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

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[2] Create a Grid instance.
#

print('Running through test cases. Will take a bit.')

theGridSol = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                            theParams=ParamGrid(areaThresholdLower=5000, reorder=True))

# ==[2.1] Explode it into a new board.
#
_, epBoard = theGridSol.explodedPuzzle(dx=150, dy=150)

# ==[2.2] Randomly swap the puzzle pieces.
#
theGridMea = Gridded(epBoard, ParamGrid(reorder=True))

_, epBoard, _ = theGridMea.swapPuzzle()

# ==[2.3] Randomly rotate & move the puzzle pieces.
#

gt_rotation = []
for key in epBoard.pieces:
    gt_rotation.append(np.random.randint(0, 70))
    epBoard.pieces[key] = epBoard.pieces[key].rotatePiece(gt_rotation[-1])

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

theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea,
                                            theParams=ParamGrid(areaThresholdLower=1000, areaThresholdUpper=80000))

# Debug only
# epImage=theGridMea.toImage(ID_DISPLAY=True,CONTOUR_DISPLAY=True,COLOR=(0,255,0))
# plt.imshow(epImage)
# plt.show()

# ==[3] Create a manager
#

theManager = Manager(theGridSol, ManagerParms(matcher=Sift()))
theManager.process(theGridMea)

# ==[4] Display. Should see some ids on the puzzle pieces
# while the ids in the assignment board refer to the ids in the solution board.
#
bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)
bSolImage = theManager.solution.toImage(ID_DISPLAY=True)

f, axarr = plt.subplots(1, 3)
axarr[0].imshow(bPerImage)
axarr[0].title.set_text('Display')
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
# ============================= 15pRotate_manager =============================
