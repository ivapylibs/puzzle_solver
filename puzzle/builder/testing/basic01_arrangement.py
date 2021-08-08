#============================ basic01_arrangement ===========================
#
# @brief    Test script for the most basic functionality of arrangement class.
#
#============================ basic01_arrangement ===========================

#
# @file     basic01_arrangement.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/08  [created]
#
#============================ basic01_arrangement ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2

from puzzle.parser.fromLayer import fromLayer
from puzzle.builder.arrangement import arrangement

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

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
theBoardSol.display(ID_DISPLAY=True)
plt.show()

#==[2] Create an arrangement instance & simulate the pLoc
#

theArrange = arrangement(theBoardSol)

pLoc ={
  0: [30,200],
  1: [130,200],
  2: [230,200],
  3: [330,200],
  4: [430,200],
  5: [530,200],
}

#==[2.1] Test distances. Should see a dict of id & distance.
#
print('The distances of each puzzle piece:',theArrange.distances(pLoc))

#==[2.2] Test scoreByLocation. Should see a large score number.
#
print('The sum score of the puzzle pieces given the location:', theArrange.scoreByLocation(pLoc))

#==[2.3] Test scoreBoard. Should see 0 for theBoardSol.
#
print('The score of the estimated board:', theArrange.scoreBoard(theBoardSol))

#==[2.4] Test piecesInPlace. Should see a dict of id & boolean value.
#
print('The checklist of each puzzle piece given the location:', theArrange.piecesInPlace(pLoc))

#==[2.5] Test progress. Should see 1.
#
print('The current progress:', theArrange.progress(theBoardSol))

#
#============================ basic01_arrangement ===========================
