#!/usr/bin/python3
# ============================ basic02_arrangement ===========================
#
# @brief    Test script for the most basic functionality of arrangement class.
#           Build an arrangement instance from different sources. (6 shapes img)
#
# ============================ basic02_arrangement ===========================

#
# @file     basic02_arrangement.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/08  [created]
#
# ============================ basic02_arrangement ===========================


import os
import pickle
from dataclasses import dataclass

import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.arrangement import Arrangement
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
theBoardSol.display(ID_DISPLAY=True)
plt.show()

# ==[2] Create an arrangement instance & simulate the pLoc
#

theArrange = Arrangement(theBoardSol)

pLoc = {
    0: [30, 200],
    1: [130, 200],
    2: [230, 200],
    3: [330, 200],
    4: [430, 200],
    5: [530, 200],
}

# ==[2.1] Test distances. Should see a dict of id & distance.
#
print('The distances of each puzzle piece:', theArrange.distances(pLoc))

# ==[2.2] Test scoreByLocation. Should see a large score number.
#
print('The sum score of the puzzle pieces given the location:', theArrange.scoreByLocation(pLoc))

# ==[2.3] Test scoreBoard. Should see 0 for theBoardSol.
#
print('The score of the estimated board:', theArrange.scoreBoard(theBoardSol))

# ==[2.4] Test piecesInPlace. Should see a dict of id & boolean value.
#
print('The checklist of each puzzle piece given the location:', theArrange.piecesInPlace(pLoc))

# ==[2.5] Test progress. Should see 100%.
#
print('The current progress:', theArrange.progress(theBoardSol))

# ==[3] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2GRAY)
_, theMaskSol = cv2.threshold(theMaskSol, 10, 255, cv2.THRESH_BINARY)

# ==[3.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer()
theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[3.2] Display the solution board
#
f, axarr = plt.subplots(2, 3)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0, 0].imshow(bSource)
axarr[0, 0].title.set_text('Source Board')

# ==[3.3] Save theBoardSol
#
theData_save = dataBoard(theBoardSol)

with open(cpath + '/data/board_6p.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

del theData_save

# ==[3.4] Save theImageSol & theMaskSol
#
theData_save = dataImage(theImageSol, theMaskSol)

with open(cpath + '/data/image_6p.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

del theData_save

# ==[4] Create an arrangement instance
#

# ==[4.1] Test buildFromFile_Puzzle
#

theArrangement_1 = Arrangement.buildFromFile_Puzzle(cpath + '/data/board_6p.obj')

bsolArrangement_1 = theArrangement_1.toImage(ID_DISPLAY=True)
axarr[0, 1].imshow(bsolArrangement_1)
axarr[0, 1].title.set_text('Board 1')

# ==[4.2] Test buildFromFile_ImageAndMask
#

theArrangement_2 = Arrangement.buildFromFile_ImageAndMask(cpath + '/data/image_6p.obj')

bsolArrangement_2 = theArrangement_2.toImage(ID_DISPLAY=True)
axarr[0, 2].imshow(bsolArrangement_2)
axarr[0, 2].title.set_text('Board 2')

# ==[4.3] Test buildFromFiles_ImageAndMask
#

theArrangement_3 = Arrangement.buildFromFiles_ImageAndMask(
    cpath + '/../../testing/data/shapes_color_six_image_solution.png',
    cpath + '/../../testing/data/shapes_color_six_image_solution.png'
)

bsolArrangement_3 = theArrangement_3.toImage(ID_DISPLAY=True)
axarr[1, 0].imshow(bsolArrangement_3)
axarr[1, 0].title.set_text('Board 3')

# ==[4.4] Test buildFrom_ImageAndMask
#

theArrangement_4 = Arrangement.buildFrom_ImageAndMask(theImageSol, theMaskSol)

bsolArrangement_4 = theArrangement_4.toImage(ID_DISPLAY=True)
axarr[1, 1].imshow(bsolArrangement_4)
axarr[1, 1].title.set_text('Board 4')

# ==[4.5] Test buildFrom_ImageProcessing
#

theArrangement_5 = Arrangement.buildFrom_ImageProcessing(theImageSol)

bsolArrangement_5 = theArrangement_5.toImage(ID_DISPLAY=True)
axarr[1, 2].imshow(bsolArrangement_5)
axarr[1, 2].title.set_text('Board 5')

# Should see 6 same boards
print('Test build-related functions:')
print('Should see the same board 6 times.')
print('All are loaded from different sources.')
plt.show()

#
# ============================ basic02_arrangement ===========================
