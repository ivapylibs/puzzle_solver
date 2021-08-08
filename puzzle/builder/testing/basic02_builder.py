#============================ basic02_builder ===========================
#
# @brief    Test script for the most basic functionality of arrangement class.
#           Build an arrangement instance from different sources
#
#============================ basic02_builder ===========================

#
# @file     basic02_builder.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/08  [created]
#
#============================ basic02_builder ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import pickle
from dataclasses import dataclass
from puzzle.parser.fromLayer import fromLayer
from puzzle.builder.arrangement import arrangement

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

theMaskSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png', cv2.IMREAD_GRAYSCALE)
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


#==[1.3] Save theBoardSol
#
theData_save = dataBoard(theBoardSol)

with open(cpath + '/data/board.obj', 'wb') as fp:
  pickle.dump(theData_save, fp)

del theData_save

#==[1.4] Save theImageSol & theMaskSol
#
theData_save = dataImage(theImageSol, theMaskSol)

with open(cpath + '/data/image.obj', 'wb') as fp:
  pickle.dump(theData_save, fp)

del theData_save

#==[2] Create an arrangement instance
#

#==[2.1] Test buildFromFile_Puzzle
#

theArrangement_1 = arrangement.buildFromFile_Puzzle(cpath + '/data/board.obj')

bsolArrangement_1 = theArrangement_1.solution.toImage(ID_DISPLAY=True)
axarr[0, 1].imshow(bsolArrangement_1)
axarr[0, 1].title.set_text('Solution board from arrangement 1')

#==[2.2] Test buildFromFile_ImageAndMask
#

theArrangement_2 = arrangement.buildFromFile_ImageAndMask(cpath + '/data/image.obj')

bsolArrangement_2 = theArrangement_2.solution.toImage(ID_DISPLAY=True)
axarr[0, 2].imshow(bsolArrangement_2)
axarr[0, 2].title.set_text('Solution board from arrangement 2')

#==[2.3] Test buildFromFiles_ImageAndMask
#

theArrangement_3 = arrangement.buildFromFiles_ImageAndMask(
cpath + '/../../testing/data/shapes_color_six_image_solution.png',
cpath + '/../../testing/data/shapes_color_six_image_solution.png'
)

bsolArrangement_3 = theArrangement_1.solution.toImage(ID_DISPLAY=True)
axarr[1, 0].imshow(bsolArrangement_3)
axarr[1, 0].title.set_text('Solution board from arrangement 3')


#==[2.4] Test buildFrom_ImageAndMask
#

theArrangement_4 = arrangement.buildFrom_ImageAndMask(theImageSol, theMaskSol)

bsolArrangement_4 = theArrangement_1.solution.toImage(ID_DISPLAY=True)
axarr[1, 1].imshow(bsolArrangement_4)
axarr[1, 1].title.set_text('Solution board from arrangement 4')

#==[2.5] Test buildFrom_ImageProcessing
#

theArrangement_5 = arrangement.buildFrom_ImageProcessing(theImageSol)

bsolArrangement_5 = theArrangement_1.solution.toImage(ID_DISPLAY=True)
axarr[1, 2].imshow(bsolArrangement_5)
axarr[1, 2].title.set_text('Solution board from arrangement 5')

# Should see 6 same boards
plt.show()

#
#============================ basic02_builder ===========================
