#!/usr/bin/python3
#============================= basic01_board =============================
#
# @brief    Tests the core functionality of the puzzle.board class.
#
#
#============================= basic01_board =============================

#
# @file     basic01_board.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/29 [created]
#           2021/08/01 [modified]
#
#============================= basic01_board =============================

#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.piece.template import template
from puzzle.board import board

#==[1] Create raw puzzle piece data.
#
theMask = np.full((20,20), False, dtype=bool)
theMask[4:14,7:12] = True
theImage = np.zeros((20,20,3))
theImage[4:14,7:12,:] = np.full((1,1,3), [1,0,1])

thePiece_1 = template.buildFromMaskAndImage(theMask, theImage)
thePiece_1.setPlacement(np.array([10,10]))

theMask = np.full((40,10), False, dtype=bool)
theMask[5:35, 2:8] = True
theImage = np.zeros((40,10,3))
theImage[5:35, 2:8,:] = np.full((1,1,3), [0,1,1])

thePiece_2 = template.buildFromMaskAndImage(theMask, theImage)
thePiece_2.setPlacement(np.array([50,50]))

#==[2] Test creation
#
thePiece_1.display()
thePiece_2.display()

#==[3] Create a board and add these two pieces to a board.
#
theBoard = board()
theBoard.addPiece(thePiece_1)
theBoard.addPiece(thePiece_2)

#==[4] Simple test of the board
#
#==[4.1] Test length, should see 2
#
print('Board size: ', theBoard.size())

#==[4.2] Test extents
#
print('Board extents: ',theBoard.extents())

#==[4.3] Test bounding box
#
print('Board bounding box: ', theBoard.boundingBox())

#==[4.4] Get piece locations.
#
print('Board piece locations: ', theBoard.pieceLocations())

#==[5] Obtain as image and display in window.
#
#==[5.1] Directly use the baord display function
fh = theBoard.display()

#==[5.2] Use the image insertion routine to synthesize an image
# 5.1 and 5.2 should see the same result.
plt.figure()
bigImage = np.zeros((90,60,3))
thePiece_1.placeInImage(bigImage)
thePiece_2.placeInImage(bigImage)

plt.imshow(bigImage)
plt.show()

#
#============================= basic01_board =============================
