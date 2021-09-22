#!/usr/bin/python3
#============================= 15pRotate_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (15p img + random rotation)
#
#
#============================= 15pRotate_manager =============================

#
# @file     15pRotate_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/21 [created]
#
#============================= 15pRotate_manager =============================

#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2

from puzzle.manager import manager, managerParms

import improcessor.basic as improcessor
from puzzle.parser.fromSketch import fromSketch
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.builder.gridded import gridded, paramGrid

from puzzle.utils.imageProcessing import cropImage

from puzzle.piece.regular import regular
from puzzle.piece.edge import edge
from puzzle.piece.sift import sift
from puzzle.piece.moments import moments

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
# theImageSol = cv2.imread(cpath + '/data/balloon.png')
theImageSol = cv2.imread(cpath + '/data/cocacola.jpg')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/data/puzzle_15p_123rf.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

#==[1.1] Create an improcesser to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                  cv2.GaussianBlur, ((3, 3), 0,),
                  cv2.Canny, (30, 200,),
                  improcessor.basic.thresh, ((10,255,cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000))
theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()

#==[1.3] Create a Grid instance to reorder the puzzle board
#

theGrid_src = gridded(theBoardSol,paramGrid(reorder=True))

#==[2] Create a Grid instance.
#

print('Running through test cases. Will take a bit.')

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=paramGrid(areaThreshold=5000))

#==[2.1] Explode it into a new board.
#
_, epBoard = theGrid.explodedPuzzle(dx=400,dy=400)

#==[2.2] Randomly swap the puzzle pieces.
#
theGrid_src = gridded(epBoard,paramGrid(reorder=True))

_, epBoard  = theGrid_src.swapPuzzle()

#==[2.2] Randomly rotate the puzzle pieces.
#
for i in range(epBoard.size()):
    epBoard.pieces[i] = epBoard.pieces[i].rotatePiece(np.random.randint(0,360))

epImage = epBoard.toImage(CONTOUR_DISPLAY=False)
# plt.imshow(epImage)
# plt.show()

#==[2.3] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                  improcessor.basic.thresh, ((5,255,cv2.THRESH_BINARY),),
                  cv2.GaussianBlur, ((3, 3), 0,),
                  cv2.Canny, (30, 200,),
                  improcessor.basic.thresh, ((10,255,cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(epImage.copy())
theMaskSol_new = theDet.getState().x

theGrid_new = gridded.buildFrom_ImageAndMask(epImage, theMaskSol_new, theParams=paramGrid(areaThreshold=1000,reorder=True))

#==[3] Create a manager
#

theManager = manager(theGrid_src.solution, managerParms(matcher=sift()))
theManager.process(theGrid_new.solution)

#==[4] Display. Should see some ids on the puzzle pieces
# while the ids in the assignment board refer to the ids in the solution board.
#
bMeasImage = theManager.bMeas.toImage(ID_DISPLAY = True)
bsolImage = theManager.solution.toImage(ID_DISPLAY = True)

f, axarr = plt.subplots(1,2)
axarr[0].imshow(bMeasImage)
axarr[0].title.set_text('Measurement')
axarr[1].imshow(bsolImage)
axarr[1].title.set_text('Solution')

# Show assignment
print('The first index refers to the measured board while the second one refers to the solution board. Note that '
      'the index in different boards may refer to different puzzle pieces.')
print(theManager.pAssignments)

plt.show()
#
#============================= 15pRotate_manager =============================
