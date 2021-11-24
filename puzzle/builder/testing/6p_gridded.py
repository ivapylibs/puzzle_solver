#!/usr/bin/python3
# ============================ 6p_gridded ===========================
#
# @brief    Test script for the most basic functionality of Grid class.
#           Build a gridded instance from different sources.
#           (6 shapes img)
#
# ============================ 6p_gridded ===========================

#
# @file     6p_gridded.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/08  [created]
#
# ============================ 6p_gridded ===========================


import os
import pickle
from dataclasses import dataclass

import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.gridded import Gridded
from puzzle.parser.fromLayer import FromLayer

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]


@dataclass
class dataBoard:
    Board: any = None
    tauDist: float = None


@dataclass
class dataImage:
    I: np.ndarray = None
    M: np.ndarray = None


# ==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2GRAY)
_, theMaskSol = cv2.threshold(theMaskSol, 10, 255, cv2.THRESH_BINARY)

# ==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer()
theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[1.2] Display the solution board
#
f, axarr = plt.subplots(2, 3)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0, 0].imshow(bSource)
axarr[0, 0].title.set_text('Source Board')

# ==[1.3] Save theBoardSol
#
theData_save = dataBoard(theBoardSol)

with open(cpath + '/data/board_6p.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

del theData_save

# ==[1.4] Save theImageSol & theMaskSol
#
theData_save = dataImage(theImageSol, theMaskSol)

with open(cpath + '/data/image_6p.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

del theData_save

# ==[2] Create an Grid instance
#

# ==[2.1] Test buildFromFile_Puzzle
#

theGrid_1 = Gridded.buildFromFile_Puzzle(cpath + '/data/board_6p.obj')

bsolGrid_1 = theGrid_1.toImage(ID_DISPLAY=True)
axarr[0, 1].imshow(bsolGrid_1)
axarr[0, 1].title.set_text('Board 1')

# ==[2.2] Test buildFromFile_ImageAndMask
#

theGrid_2 = Gridded.buildFromFile_ImageAndMask(cpath + '/data/image_6p.obj')

bsolGrid_2 = theGrid_2.toImage(ID_DISPLAY=True)
axarr[0, 2].imshow(bsolGrid_2)
axarr[0, 2].title.set_text('Board 2')

# ==[2.3] Test buildFromFiles_ImageAndMask
#

theGrid_3 = Gridded.buildFromFiles_ImageAndMask(
    cpath + '/../../testing/data/shapes_color_six_image_solution.png',
    cpath + '/../../testing/data/shapes_color_six_image_solution.png'
)

bsolGrid_3 = theGrid_3.toImage(ID_DISPLAY=True)
axarr[1, 0].imshow(bsolGrid_3)
axarr[1, 0].title.set_text('Board 3')

# ==[2.4] Test buildFrom_ImageAndMask
#

theGrid_4 = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol)

bsolGrid_4 = theGrid_4.toImage(ID_DISPLAY=True)
axarr[1, 1].imshow(bsolGrid_4)
axarr[1, 1].title.set_text('Board 4')

# ==[2.5] Test buildFrom_ImageProcessing
#

theGrid_5 = Gridded.buildFrom_ImageProcessing(theImageSol)

bsolGrid_5 = theGrid_5.toImage(ID_DISPLAY=True)
axarr[1, 2].imshow(bsolGrid_5)
axarr[1, 2].title.set_text('Board 5')

# ==[3] Display the Interlocking matrix. Should see an identity matrix.
#
print('Should see the same board 6 times.')

print('Interlocking matrix: \n', theGrid_1.ilMat)
print('Grid coordinates: \n', theGrid_1.gc)

plt.show()

#
# ============================ 6p_gridded ===========================
