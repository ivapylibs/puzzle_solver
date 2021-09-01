#!/usr/bin/python3
#============================= explode01_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (15p img)
#
#
#============================= explode01_manager =============================

#
# @file     explode01_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/28 [created]
#
#============================= explode01_manager =============================

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

from puzzle.piece.regular import regular
from puzzle.piece.edge import edge
from puzzle.piece.moments import moments

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/data/puzzle_15p_123rf.png')


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
theLayer = fromLayer(paramPuzzle(areaThreshold=5000, pieceConstructor=regular))

theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()


#==[2] Create an Grid instance and explode it into two new boards
#

print('Running through test cases. Will take a bit.')

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=paramGrid(areaThreshold=5000, pieceConstructor=regular))


_, epBoard = theGrid.explodedPuzzle(dx=100,dy=100)


#==[3] Create a manager
#
theManager = manager(theBoardSol, managerParms(matcher=edge(20)))

theManager.process(epBoard)

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
print('The first index refers to the measured board while the second one refers to the solution board.')
print(theManager.pAssignments)

plt.show()
#
#============================= explode01_manager =============================
