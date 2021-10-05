#!/usr/bin/python3
# ============================ basic03_adjacent ===========================
#
# @brief    Test script for the most basic functionality of Adjacent class.
#           Build an Adjacent instance from different sources.
#           (6 shapes img adj)
#
# ============================ basic03_adjacent ===========================

#
# @file     basic03_adjacent.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/08  [created]
#
# ============================ basic03_adjacent ===========================


import os
import pickle
from dataclasses import dataclass

import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.adjacent import adjacent
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
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_adjacent.png')

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
theData_save = dataBoard(theBoardSol)

with open(cpath + '/data/board_6p_adj.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

del theData_save

# ==[1.4] Save theImageSol & theMaskSol
#
theData_save = dataImage(theImageSol, theMaskSol)

with open(cpath + '/data/image_6p_adj.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

del theData_save

# ==[2] Create an Adjacent instance
#

# ==[2.1] Test buildFromFile_Puzzle
#

theAdj_1 = adjacent.buildFromFile_Puzzle(cpath + '/data/board_6p_adj.obj')

bsolAdjacent_1 = theAdj_1.toImage(ID_DISPLAY=True)
axarr[0, 1].imshow(bsolAdjacent_1)
axarr[0, 1].title.set_text('Board 1')

# ==[2.2] Test buildFromFile_ImageAndMask
#

theAdj_2 = adjacent.buildFromFile_ImageAndMask(cpath + '/data/image_6p_adj.obj')

bsolAdjacent_2 = theAdj_2.toImage(ID_DISPLAY=True)
axarr[0, 2].imshow(bsolAdjacent_2)
axarr[0, 2].title.set_text('Board 2')

# ==[2.3] Test buildFromFiles_ImageAndMask
#

theAdj_3 = adjacent.buildFromFiles_ImageAndMask(
    cpath + '/../../testing/data/shapes_color_six_image_adjacent.png',
    cpath + '/../../testing/data/shapes_color_six_image_adjacent.png'
)

bsolAdjacent_3 = theAdj_3.toImage(ID_DISPLAY=True)
axarr[1, 0].imshow(bsolAdjacent_3)
axarr[1, 0].title.set_text('Board 3')

# ==[2.4] Test buildFrom_ImageAndMask
#

theAdj_4 = adjacent.buildFrom_ImageAndMask(theImageSol, theMaskSol)

bsolAdjacent_4 = theAdj_4.toImage(ID_DISPLAY=True)
axarr[1, 1].imshow(bsolAdjacent_4)
axarr[1, 1].title.set_text('Board 4')

# ==[2.5] Test buildFrom_ImageProcessing
#

theAdj_5 = adjacent.buildFrom_ImageProcessing(theImageSol)

bsolAdjacent_5 = theAdj_5.toImage(ID_DISPLAY=True)
axarr[1, 2].imshow(bsolAdjacent_5)
axarr[1, 2].title.set_text('Board 5')

# ==[3] Print expected outcomes, the adjacency matrix, and plot the
#      boards. Should see 20 Trues (2*7+6).
#
print('Should see the same board 6 times.')
print('All are loaded from different sources.')

print('Adjacency matrix: \n', theAdj_1.adjMat)
print('The number of Trues:', np.sum(theAdj_1.adjMat))
print('Should see 20 Trues (3*6+2).')
print('All 6 have at least 2 neighbors plus self-adjacent.')
print('2 have a third neighbor.')

plt.show()

#
# ============================ basic03_adjacent ===========================
