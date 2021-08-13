#!/usr/bin/python3
#============================ basic06_gridded ===========================
#
# @brief    Test script for the most basic functionality of Grid class.
#           Build a gridded instance from different sources.
#           (4 touching box puzzle pieces)
#
#============================ basic06_gridded ===========================

#
# @file     basic06_gridded.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/10  [created]
#
#============================ basic06_gridded ===========================


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

theImageSol = np.zeros((100,100,3),dtype='uint8')
cv2.rectangle(theImageSol,(20,20),(20+30,20+30),(0,255,0),2)
cv2.rectangle(theImageSol,(20+30,20),(20+30+30,20+30),(0,255,0),2)
cv2.rectangle(theImageSol,(20,20+30),(20+30,20+30+30),(0,255,0),2)
cv2.rectangle(theImageSol,(20+30,20+30),(20+30+30,20+30+30),(0,255,0),2)

theMaskSol = cv2.cvtColor(theImageSol,cv2.COLOR_BGR2GRAY)
_ , theMaskSol = cv2.threshold(theMaskSol,10,255,cv2.THRESH_BINARY)

cv2.imwrite(cpath+'/data/touchbox_img.png',theImageSol)
cv2.imwrite(cpath+'/data/touchbox_mask.png',theMaskSol)

#==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()

theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()

#==[1.2] Display the solution board
#
f, axarr = plt.subplots(2,3)
bSource = theBoardSol.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY = False)
axarr[0, 0].imshow(bSource)
axarr[0, 0].title.set_text('Source Board')

#==[1.3] Save theBoardSol
#
if not os.path.exists(cpath + '/data/board_4touch.obj'):

  theData_save = dataBoard(theBoardSol)

  with open(cpath + '/data/board_4touch.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

  del theData_save

#==[1.4] Save theImageSol & theMaskSol
#
if not os.path.exists(cpath + '/data/image_4touch.obj'):

  theData_save = dataImage(theImageSol, theMaskSol)

  with open(cpath + '/data/image_4touch.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

  del theData_save

#==[2] Create an Grid instance
#

#==[2.1] Test buildFromFile_Puzzle
#

theGrid_1 = gridded.buildFromFile_Puzzle(cpath + '/data/board_4touch.obj')

bsolGrid_1 = theGrid_1.solution.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY = False)
axarr[0, 1].imshow(bsolGrid_1)
axarr[0, 1].title.set_text('Board 1')

#==[2.2] Test buildFromFile_ImageAndMask
#

theGrid_2 = gridded.buildFromFile_ImageAndMask(cpath + '/data/image_4touch.obj')

bsolGrid_2 = theGrid_2.solution.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY = False)
axarr[0, 2].imshow(bsolGrid_2)
axarr[0, 2].title.set_text('Board 2')

#==[2.3] Test buildFromFiles_ImageAndMask
#

theGrid_3 = gridded.buildFromFiles_ImageAndMask(
cpath + '/data/touchbox_img.png',
cpath + '/data/touchbox_mask.png'
)

bsolGrid_3 = theGrid_3.solution.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY = False)
axarr[1, 0].imshow(bsolGrid_3)
axarr[1, 0].title.set_text('Board 3')


#==[2.4] Test buildFrom_ImageAndMask
#

theGrid_4 = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol)

bsolGrid_4 = theGrid_4.solution.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY = False)
axarr[1, 1].imshow(bsolGrid_4)
axarr[1, 1].title.set_text('Board 4')

#==[2.5] Test buildFrom_ImageProcessing
#

theGrid_5 = gridded.buildFrom_ImageProcessing(theImageSol)

bsolGrid_5 = theGrid_5.solution.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY = False)
axarr[1, 2].imshow(bsolGrid_5)
axarr[1, 2].title.set_text('Board 5')

#==[3] Display the Interlocking matrix. Should see a matrix full of True.
#
print('Should see the same board 6 times.')

print('Interlocking matrix: \n', theGrid_1.ilMat)
print('Should see a matrix full of True.')
print('All pieces are sufficiently close to each other in this 2x2 board.')
print('Grid coordinates: \n', theGrid_1.gc)

plt.show()

#
#============================ basic06_gridded ===========================
