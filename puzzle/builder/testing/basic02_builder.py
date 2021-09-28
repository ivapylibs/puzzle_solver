#!/usr/bin/python3
# ============================ basic02_builder ===========================
#
# @brief    Test script for the most basic functionality of arrangement class.
#           Build an arrangement instance from different sources. (6 shapes img)
#
# ============================ basic02_builder ===========================

#
# @file     basic02_builder.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/08  [created]
#
# ============================ basic02_builder ===========================


import os
import pickle
from dataclasses import dataclass

import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.arrangement import arrangement
from puzzle.parser.fromLayer import fromLayer

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


# ==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2GRAY)
_, theMaskSol = cv2.threshold(theMaskSol, 10, 255, cv2.THRESH_BINARY)

# ==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
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
if not os.path.exists(cpath + '/data/board_6p.obj'):
    theData_save = dataBoard(theBoardSol)

    with open(cpath + '/data/board_6p.obj', 'wb') as fp:
        pickle.dump(theData_save, fp)

    del theData_save

# ==[1.4] Save theImageSol & theMaskSol
#
if not os.path.exists(cpath + '/data/image_6p.obj'):
    theData_save = dataImage(theImageSol, theMaskSol)

    with open(cpath + '/data/image_6p.obj', 'wb') as fp:
        pickle.dump(theData_save, fp)

    del theData_save

# ==[2] Create an arrangement instance
#

# ==[2.1] Test buildFromFile_Puzzle
#

theArrangement_1 = arrangement.buildFromFile_Puzzle(cpath + '/data/board_6p.obj')

bsolArrangement_1 = theArrangement_1.solution.toImage(ID_DISPLAY=True)
axarr[0, 1].imshow(bsolArrangement_1)
axarr[0, 1].title.set_text('Board 1')

# ==[2.2] Test buildFromFile_ImageAndMask
#

theArrangement_2 = arrangement.buildFromFile_ImageAndMask(cpath + '/data/image_6p.obj')

bsolArrangement_2 = theArrangement_2.solution.toImage(ID_DISPLAY=True)
axarr[0, 2].imshow(bsolArrangement_2)
axarr[0, 2].title.set_text('Board 2')

# ==[2.3] Test buildFromFiles_ImageAndMask
#

theArrangement_3 = arrangement.buildFromFiles_ImageAndMask(
    cpath + '/../../testing/data/shapes_color_six_image_solution.png',
    cpath + '/../../testing/data/shapes_color_six_image_solution.png'
)

bsolArrangement_3 = theArrangement_3.solution.toImage(ID_DISPLAY=True)
axarr[1, 0].imshow(bsolArrangement_3)
axarr[1, 0].title.set_text('Board 3')

# ==[2.4] Test buildFrom_ImageAndMask
#

theArrangement_4 = arrangement.buildFrom_ImageAndMask(theImageSol, theMaskSol)

bsolArrangement_4 = theArrangement_4.solution.toImage(ID_DISPLAY=True)
axarr[1, 1].imshow(bsolArrangement_4)
axarr[1, 1].title.set_text('Board 4')

# ==[2.5] Test buildFrom_ImageProcessing
#

theArrangement_5 = arrangement.buildFrom_ImageProcessing(theImageSol)

bsolArrangement_5 = theArrangement_5.solution.toImage(ID_DISPLAY=True)
axarr[1, 2].imshow(bsolArrangement_5)
axarr[1, 2].title.set_text('Board 5')

# Should see 6 same boards
print('Should see the same board 6 times.')
print('All are loaded from different sources.')
plt.show()

#
# ============================ basic02_builder ===========================
