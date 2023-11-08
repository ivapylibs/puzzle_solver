#!/usr/bin/python3
#============================ basic01_template ===========================
#
# @brief    Test script for the most basic functionality of template
#           puzzle piece class.
#
# Creates a few very basic instances of puzzle pieces, then visualizes them
# in a virtual puzzle board.
#
#============================ basic01_template ===========================

#
# @file     basic01_template.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
#           Yiye Chen,              yychen2019@gatech.edu
# @date     2021/07/28  [created]
#           2021/07/31  [modified]
#
#============================ basic01_template ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.piece import Template

#==[1] Create raw puzzle piece data.
#
theMask = np.full((20, 20), False, dtype=bool)
theMask[4:14, 7:12] = True

theImage = np.zeros((20, 20, 3))
theImage[4:14, 7:12, :] = np.full((1, 1, 3), [1, 0, 1])

thePiece = Template.buildFromMaskAndImage(theMask, theImage)

#==[2] Test creation
#
thePiece.display()

#==[3] Test insertion into image data.
#
bigImage = np.zeros((200, 200, 3))

thePiece.placeInImage(bigImage)
thePiece.setPlacement(np.array([50, 50]))
thePiece.placeInImage(bigImage)
thePiece.placeInImageAt(bigImage, np.array([70, 30]))

# Display the resulting image. Should have three puzzle pieces in it.
plt.figure()
plt.imshow(bigImage)
plt.title("Test puzzle piece placement in image.")

#==[4] Test the builder of the basic puzzle piece
squarePiece = Template.buildSquare(20, color=(255, 0, 0), rLoc=(80, 40))
spherePiece = Template.buildSphere(10, color=(0, 255, 0), rLoc=(80, 140))
bigImage = np.zeros((200, 200, 3))
squarePiece.placeInImage(bigImage)
spherePiece.placeInImage(bigImage)
plt.figure()
plt.title("Test builder of basic-shape puzzle pieces: red square and green sphere")
plt.imshow(bigImage)

plt.show()

#
#============================ basic01_template ===========================
