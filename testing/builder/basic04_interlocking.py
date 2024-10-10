#!/usr/bin/python3
# ============================ basic04_interlocking ===========================
#
# @brief    Test script for the most basic functionality of Interlocking class.
#           Build an Interlocking instance from different sources.
#           (6 shapes img)
#
# ============================ basic04_interlocking ===========================

#
# @file     basic04_interlocking.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/08  [created]
#
# ============================ basic04_interlocking ===========================


import os
import pickle
from dataclasses import dataclass

import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.interlocking import Interlocking
from puzzle.parser.fromLayer import FromLayer

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

# ==[2] Create an Interlocking instance
#

# ==[2.1] Test buildFromFile_Puzzle
#

theInter_1 = Interlocking.buildFromFile_Puzzle(cpath + '/data/board_6p.obj')

bsolInterlocking_1 = theInter_1.toImage(ID_DISPLAY=True)
axarr[0, 1].imshow(bsolInterlocking_1)
axarr[0, 1].title.set_text('Board 1')

# ==[2.2] Test buildFromFile_ImageAndMask
#

theInter_2 = Interlocking.buildFromFile_ImageAndMask(cpath + '/data/image_6p.obj')

bsolInterlocking_2 = theInter_2.toImage(ID_DISPLAY=True)
axarr[0, 2].imshow(bsolInterlocking_2)
axarr[0, 2].title.set_text('Board 2')

# ==[2.3] Test buildFromFiles_ImageAndMask
#

theInter_3 = Interlocking.buildFromFiles_ImageAndMask(
    cpath + '/../../testing/data/shapes_color_six_image_solution.png',
    cpath + '/../../testing/data/shapes_color_six_image_solution.png'
)

bsolInterlocking_3 = theInter_3.toImage(ID_DISPLAY=True)
axarr[1, 0].imshow(bsolInterlocking_3)
axarr[1, 0].title.set_text('Board 3')

# ==[2.4] Test buildFrom_ImageAndMask
#

theInter_4 = Interlocking.buildFrom_ImageAndMask(theImageSol, theMaskSol)

bsolInterlocking_4 = theInter_4.toImage(ID_DISPLAY=True)
axarr[1, 1].imshow(bsolInterlocking_4)
axarr[1, 1].title.set_text('Board 4')

# ==[2.5] Test buildFrom_ImageProcessing
#

theInter_5 = Interlocking.buildFrom_ImageProcessing(theImageSol)

bsolInterlocking_5 = theInter_5.toImage(ID_DISPLAY=True)
axarr[1, 2].imshow(bsolInterlocking_5)
axarr[1, 2].title.set_text('Board 5')

# Should see 6 same boards
# ==[3] Display the interlocking matrix. Should see an identity matrix.
#
print('Should see the same board 6 times.')
print('All are loaded from different sources.')

print('Interlocking matrix: \n', theInter_1.ilMat)
print('Should see an identity matrix.')
print('That means none are interlocking')

plt.show()
#
# ============================ basic04_interlocking ===========================
