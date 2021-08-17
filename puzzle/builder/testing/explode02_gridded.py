#!/usr/bin/python3
#============================ explode02_gridded ===========================
#
# @brief    Test script for explodedPuzzle function.
#           (15 one with touching case)
#
#============================ explode02_gridded ===========================

#
# @file     explode02_gridded.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/15  [created]
#
#============================ explode02_gridded ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import pickle
from dataclasses import dataclass

import improcessor.basic as improcessor
from puzzle.parser.fromSketch import fromSketch
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.builder.gridded import gridded, paramGrid

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

#==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')


#==[1.1] Create an improcesser to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                  cv2.GaussianBlur, ((3, 3), 0,),
                  cv2.Canny, (30, 200,),
                  improcessor.basic.thresh, ((10,255,cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

cv2.imwrite(cpath+'/data/balloon_15_img.png', theImageSol)
cv2.imwrite(cpath+'/data/balloon_15_mask.png', theMaskSol)

#==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000))

theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()

#==[1.3] Display the solution board
#
f, axarr = plt.subplots(1,2)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0].imshow(bSource)
axarr[0].title.set_text('Source solution board')


#==[1.4] Save theBoardSol
#
if not os.path.exists(cpath + '/data/board_15p.obj'):
  theData_save = dataBoard(theBoardSol)

  with open(cpath + '/data/board_15p.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

  del theData_save

#==[1.5] Save theImageSol & theMaskSol
#
if not os.path.exists(cpath + '/data/image_15p.obj'):
  theData_save = dataImage(theImageSol, theMaskSol)

  with open(cpath + '/data/image_15p.obj', 'wb') as fp:
    pickle.dump(theData_save, fp)

  del theData_save

#==[2] Create an Grid instance and explode it
#

print('Running through test cases. Will take a bit.')

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=paramGrid(areaThreshold=5000))

epImage, _ = theGrid.explodedPuzzle(dx=100,dy=100)

axarr[1].imshow(epImage)
axarr[1].title.set_text('Exploded view')

plt.show()
#
#============================ explode02_gridded ===========================
