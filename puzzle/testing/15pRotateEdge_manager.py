#!/usr/bin/python3
# ============================= 15pRotateEdge_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (15p img + random rotation)
#
#
# ============================= 15pRotateEdge_manager =============================
#
# @file     15pRotateEdge_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/30 [created]
#
# ============================= 15pRotateEdge_manager =============================

import os

import cv2
import improcessor.basic as improcessor
# ==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.manager import manager, managerParms
from puzzle.parser.fromSketch import fromSketch
from puzzle.piece.edge import edge
from puzzle.piece.regular import regular
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/data/balloon.png')
# theImageSol = cv2.imread(cpath + '/data/cocacola.jpg')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

# theMaskSol_src = cv2.imread(cpath + '/data/puzzle_60p_AdSt408534841.png')

theMaskSol_src = cv2.imread(cpath + '/data/puzzle_15p_123rf.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcesser to obtain the mask.
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

theGrid_src = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                             theParams=paramGrid(areaThreshold=5000, pieceConstructor=regular,
                                                                 reorder=True))

# ==[2.1] Explode it into a new board.
#
epImage, epBoard = theGrid_src.explodedPuzzle(dx=200, dy=200)

# ==[2.2] Randomly swap the puzzle pieces.
#
theGrid_new = gridded(epBoard, paramGrid(reorder=True))

_, epBoard = theGrid_new.swapPuzzle()

# ==[2.3] Randomly rotate the puzzle pieces.
#

gt_rotation = []
for i in range(epBoard.size()):
    gt_rotation.append(np.random.randint(0, 20))
    epBoard.pieces[i] = epBoard.pieces[i].rotatePiece(gt_rotation[-1])

epImage = epBoard.toImage(CONTOUR_DISPLAY=False)
# plt.imshow(epImage)
# plt.show()

# ==[2.4] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(epImage.copy())
theMaskSol_new = theDet.getState().x

# plt.imshow(theMaskSol_new)
# plt.show()

theGrid_new = gridded.buildFrom_ImageAndMask(epImage, theMaskSol_new,
                                             theParams=paramGrid(areaThreshold=1000, pieceConstructor=regular,
                                                                 reorder=True))

# ==[3] Create a manager
#

theManager = manager(theGrid_src.solution, managerParms(matcher=edge()))
theManager.process(theGrid_new.solution)

# ==[4] Display. Should see some ids on the puzzle pieces
# while the ids in the assignment board refer to the ids in the solution board.
#
bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)
bsolImage = theManager.solution.toImage(ID_DISPLAY=True)

f, axarr = plt.subplots(1, 2)
axarr[0].imshow(bMeasImage)
axarr[0].title.set_text('Measurement')
axarr[1].imshow(bsolImage)
axarr[1].title.set_text('Solution')

# Show assignment
print('The first index refers to the measured board while the second one refers to the solution board. Note that '
      'the index in different boards may refer to different puzzle pieces.')
print(theManager.pAssignments)

print('The computed rotation angles(degree):')
print('Note that the order of angles do not correspond to the pieces')
print(np.sort(np.array(theManager.pAssignments_rotation).astype('int')))
print('The gt rotation angles(degree):')
print(np.sort(np.array(gt_rotation).astype('int')))

plt.show()
#
# ============================= 15pRotateEdge_manager =============================
