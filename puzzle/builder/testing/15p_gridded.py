#!/usr/bin/python3
# ============================ 15p_gridded ===========================
#
# @brief    Test script for the most basic functionality of Grid class.
#           Build a gridded instance from different sources.
#           (15p with touching case)
#
# ============================ 15p_gridded ===========================

#
# @file     15p_gridded.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/10  [created]
#
# ============================ 15p_gridded ===========================


import os
import pickle
from dataclasses import dataclass

import cv2
import improcessor.basic as improcessor
# ==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.parser.fromSketch import fromSketch
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]


@dataclass
class dataBoard:
    board: any = None
    tauDist: float = None


@dataclass
class dataImage:
    I: np.ndarray = None
    M: np.ndarray = None


# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')
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

cv2.imwrite(cpath + '/data/balloon_15_img.png', theImageSol)
cv2.imwrite(cpath + '/data/balloon_15_mask.png', theMaskSol)

# ==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000))

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[1.3] Display the solution board
#
f, axarr = plt.subplots(2, 3)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0, 0].imshow(bSource)
axarr[0, 0].title.set_text('Source solution board')

# ==[1.4] Save theBoardSol
#
if not os.path.exists(cpath + '/data/board_15p.obj'):
    theData_save = dataBoard(theBoardSol)

    with open(cpath + '/data/board_15p.obj', 'wb') as fp:
        pickle.dump(theData_save, fp)

    del theData_save

# ==[1.5] Save theImageSol & theMaskSol
#
if not os.path.exists(cpath + '/data/image_15p.obj'):
    theData_save = dataImage(theImageSol, theMaskSol)

    with open(cpath + '/data/image_15p.obj', 'wb') as fp:
        pickle.dump(theData_save, fp)

    del theData_save

# ==[2] Create an Grid instance
#

print('Running through test cases. Will take a bit.')

# ==[2.1] Test buildFromFile_Puzzle
#

theGrid_1 = gridded.buildFromFile_Puzzle(cpath + '/data/board_15p.obj')

bsolGrid_1 = theGrid_1.toImage(ID_DISPLAY=True)
axarr[0, 1].imshow(bsolGrid_1)
axarr[0, 1].title.set_text('Board 1')

# ==[2.2] Test buildFromFile_ImageAndMask
#

theGrid_2 = gridded.buildFromFile_ImageAndMask(cpath + '/data/image_15p.obj', theParams=paramGrid(areaThreshold=5000))

bsolGrid_2 = theGrid_2.toImage(ID_DISPLAY=True)
axarr[0, 2].imshow(bsolGrid_2)
axarr[0, 2].title.set_text('Board 2')

# ==[2.3] Test buildFromFiles_ImageAndMask
#

theGrid_3 = gridded.buildFromFiles_ImageAndMask(
    cpath + '/data/balloon_15_img.png',
    cpath + '/data/balloon_15_mask.png', theParams=paramGrid(areaThreshold=5000)
)

bsolGrid_3 = theGrid_3.toImage(ID_DISPLAY=True)
axarr[1, 0].imshow(bsolGrid_3)
axarr[1, 0].title.set_text('Board 3')

# ==[2.4] Test buildFrom_ImageAndMask
#

theGrid_4 = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=paramGrid(areaThreshold=5000))

bsolGrid_4 = theGrid_4.toImage(ID_DISPLAY=True)
axarr[1, 1].imshow(bsolGrid_4)
axarr[1, 1].title.set_text('Board 4')

# ==[2.5] Test buildFrom_Sketch
#

theGrid_5 = gridded.buildFrom_Sketch(theImageSol, theMaskSol_src, theDetector=theDet,
                                     theParams=paramGrid(areaThreshold=5000))

bsolGrid_5 = theGrid_5.toImage(ID_DISPLAY=True)
axarr[1, 2].imshow(bsolGrid_5)
axarr[1, 2].title.set_text('Board 5')

# ==[3] Display the Interlocking matrix. Should see a matrix filled with some Trues.
#
print('Should see the same board 6 times.')

print('Interlocking matrix: \n', theGrid_1.ilMat)
print('Grid coordinates: \n', theGrid_1.gc)

plt.show()

#
# ============================ 15p_gridded ===========================
