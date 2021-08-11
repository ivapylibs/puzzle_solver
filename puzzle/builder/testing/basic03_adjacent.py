#============================ basic03_adjacent ===========================
#
# @brief    Test script for the most basic functionality of Adjacent class.
#           Build an Adjacent instance from different sources.
#           (6 shapes img adj)
#
#============================ basic03_adjacent ===========================

#
# @file     basic03_adjacent.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/08  [created]
#
#============================ basic03_adjacent ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import pickle
from dataclasses import dataclass
from puzzle.parser.fromLayer import fromLayer
from puzzle.builder.adjacent import adjacent

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

#==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_adjacent.png')

theMaskSol = cv2.cvtColor(theImageSol,cv2.COLOR_BGR2GRAY)
_ , theMaskSol = cv2.threshold(theMaskSol,10,255,cv2.THRESH_BINARY)

#==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()

#==[1.2] Display the solution board
#
f, axarr = plt.subplots(2,3)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0, 0].imshow(bSource)
axarr[0, 0].title.set_text('Source solution board')

# ==[1.3] Save theBoardSol
#
if not os.path.exists(cpath + '/data/board_6p_adj.obj'):
  theData_save = dataBoard(theBoardSol)

  with open(cpath + '/data/board_6p_adj.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

  del theData_save

# ==[1.4] Save theImageSol & theMaskSol
#
if not os.path.exists(cpath + '/data/image_6p_adj.obj'):
  theData_save = dataImage(theImageSol, theMaskSol)

  with open(cpath + '/data/image_6p_adj.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

  del theData_save

#==[2] Create an Adjacent instance
#

#==[2.1] Test buildFromFile_Puzzle
#

theAdj_1 = adjacent.buildFromFile_Puzzle(cpath + '/data/board_6p_adj.obj')

bsolAdjacent_1 = theAdj_1.solution.toImage(ID_DISPLAY=True)
axarr[0, 1].imshow(bsolAdjacent_1)
axarr[0, 1].title.set_text('Solution board from Adjacent 1')

#==[2.2] Test buildFromFile_ImageAndMask
#

theAdj_2 = adjacent.buildFromFile_ImageAndMask(cpath + '/data/image_6p_adj.obj')

bsolAdjacent_2 = theAdj_2.solution.toImage(ID_DISPLAY=True)
axarr[0, 2].imshow(bsolAdjacent_2)
axarr[0, 2].title.set_text('Solution board from Adjacent 2')

#==[2.3] Test buildFromFiles_ImageAndMask
#

theAdj_3 = adjacent.buildFromFiles_ImageAndMask(
cpath + '/../../testing/data/shapes_color_six_image_adjacent.png',
cpath + '/../../testing/data/shapes_color_six_image_adjacent.png'
)

bsolAdjacent_3 = theAdj_3.solution.toImage(ID_DISPLAY=True)
axarr[1, 0].imshow(bsolAdjacent_3)
axarr[1, 0].title.set_text('Solution board from Adjacent 3')


#==[2.4] Test buildFrom_ImageAndMask
#

theAdj_4 = adjacent.buildFrom_ImageAndMask(theImageSol, theMaskSol)

bsolAdjacent_4 = theAdj_4.solution.toImage(ID_DISPLAY=True)
axarr[1, 1].imshow(bsolAdjacent_4)
axarr[1, 1].title.set_text('Solution board from Adjacent 4')

#==[2.5] Test buildFrom_ImageProcessing
#

theAdj_5 = adjacent.buildFrom_ImageProcessing(theImageSol)

bsolAdjacent_5 = theAdj_5.solution.toImage(ID_DISPLAY=True)
axarr[1, 2].imshow(bsolAdjacent_5)
axarr[1, 2].title.set_text('Solution board from Adjacent 5')

# Should see 6 same boards
plt.show()
print('Should see 6 same boards.')

#==[3] Display the adjacent matrix. Should see 20 Trues (2*7+6).
#
print('Adjacent matrix: \n', theAdj_1.adjMat)
print('The number of Trues:', np.sum(theAdj_1.adjMat))
print('Should see 20 Trues (2*7+6).')
#
#============================ basic03_adjacent ===========================
