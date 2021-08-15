#!/usr/bin/python3
#============================ explode01_gridded ===========================
#
# @brief    Test script for explodedPuzzle function. (6 shapes img)
#
#
#============================ explode01_gridded ===========================

#
# @file     explode01_gridded.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/15  [created]
#
#============================ explode01_gridded ===========================


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
f, axarr = plt.subplots(1,2)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0].imshow(bSource)
axarr[0].title.set_text('Source Board')

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

#==[2] Create an Grid instance and explode it
#

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol)

epImage = theGrid.explodedPuzzle()

axarr[1].imshow(epImage)
axarr[1].title.set_text('Exploded view')

plt.show()


#
#============================ explode01_gridded ===========================
