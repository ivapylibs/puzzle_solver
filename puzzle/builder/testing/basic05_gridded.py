#============================ basic05_gridded ===========================
#
# @brief    Test script for the most basic functionality of Grid class.
#           Build a gridded instance from different sources.
#           (6 shapes img)
#
#============================ basic05_gridded ===========================

#
# @file     basic05_gridded.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/08  [created]
#
#============================ basic05_gridded ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import pickle
from dataclasses import dataclass
from puzzle.parser.fromLayer import fromLayer
from puzzle.builder.gridded import gridded

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
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png')

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

#==[2] Create an Grid instance
#

#==[2.1] Test buildFromFile_Puzzle
#

theGrid_1 = gridded.buildFromFile_Puzzle(cpath + '/data/board_6p.obj')

bsolGrid_1 = theGrid_1.solution.toImage(ID_DISPLAY=True)
axarr[0, 1].imshow(bsolGrid_1)
axarr[0, 1].title.set_text('Solution board from Grid 1')

#==[2.2] Test buildFromFile_ImageAndMask
#

theGrid_2 = gridded.buildFromFile_ImageAndMask(cpath + '/data/image_6p.obj')

bsolGrid_2 = theGrid_2.solution.toImage(ID_DISPLAY=True)
axarr[0, 2].imshow(bsolGrid_2)
axarr[0, 2].title.set_text('Solution board from Grid 2')

#==[2.3] Test buildFromFiles_ImageAndMask
#

theGrid_3 = gridded.buildFromFiles_ImageAndMask(
cpath + '/../../testing/data/shapes_color_six_image_solution.png',
cpath + '/../../testing/data/shapes_color_six_image_solution.png'
)

bsolGrid_3 = theGrid_1.solution.toImage(ID_DISPLAY=True)
axarr[1, 0].imshow(bsolGrid_3)
axarr[1, 0].title.set_text('Solution board from Grid 3')


#==[2.4] Test buildFrom_ImageAndMask
#

theGrid_4 = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol)

bsolGrid_4 = theGrid_1.solution.toImage(ID_DISPLAY=True)
axarr[1, 1].imshow(bsolGrid_4)
axarr[1, 1].title.set_text('Solution board from Grid 4')

#==[2.5] Test buildFrom_ImageProcessing
#

theGrid_5 = gridded.buildFrom_ImageProcessing(theImageSol)

bsolGrid_5 = theGrid_1.solution.toImage(ID_DISPLAY=True)
axarr[1, 2].imshow(bsolGrid_5)
axarr[1, 2].title.set_text('Solution board from Grid 5')

# Should see 6 same boards
plt.show()

#==[3] Display the Interlocking matrix. Should see an identity matrix.
#
print('Interlocking matrix: \n', theGrid_1.ilMat)
print('Grid coordinates: \n', theGrid_1.gc)

#
#============================ basic05_gridded ===========================
