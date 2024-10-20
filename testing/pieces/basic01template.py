#!/usr/bin/python3
#============================ basic01_template ===========================
##@file
# @brief    Test script for the most basic functionality of template
#           puzzle piece class.
#
# Creates a few very basic instances of puzzle pieces, then visualizes them
# in a virtual puzzle board.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2024/10/20  [aligned with Perceiver updates and documented]
# @date     2021/07/31  [modified]
# @date     2021/07/28  [created]
#
# @quitf
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

cLoc = np.array([0,0])
thePiece = Template.buildFromMaskAndImage(theMask, theImage, cLoc)

#==[2] Test creation
#
thePiece.display()
print("Testing out piece extraction.  Should see puzzle piece and mask.")
print("First image displays a single puzzle piece in a small image.")
print("Correct the messages.")

#==[3] Test insertion into image data.
#
bigImage = np.zeros((200, 200, 3))

thePiece.placeInImage(bigImage)
thePiece.setPlacement(np.array([50, 50]))
thePiece.placeInImage(bigImage)
thePiece.placeInImageAt(bigImage, np.array([70, 30]))

print("First image displays a three puzzle pieces in a big image.")

# Display the resulting image. Should have three puzzle pieces in it.
plt.figure()
plt.imshow(bigImage)
plt.title("Test puzzle piece placement in image.")
#plt.show()     # Uncomment to pause here; close windows to continue.

#==[4] Test the builder of the basic puzzle piece
squarePiece = Template.buildSquare(20, color=(255, 0, 0), rLoc=(80, 40))
spherePiece = Template.buildSphere(10, color=(0, 255, 0), rLoc=(80, 140))
bigImage = np.zeros((200, 200, 3))
# @todo DOES NOT USE rLoc BUT IT PROBABLY SHOULD!!!! NEED TO CORRECT.
#       APPEARS TO RELY ON pcorner. WHY IS THAT?  NEED TO DOCUMENT BETTER!
#       CHECK HOW DISPLAY WORKS!! WHY ISN'T pcorner ALWAYS SIMPLY [0,0]??
squarePiece.placeInImage(bigImage)
spherePiece.placeInImage(bigImage)
plt.figure()
plt.title("Test builder of basic-shape puzzle pieces: red square and green sphere")
plt.imshow(bigImage)
print("Third displays to different puzzle pieces in an image.")

plt.show()
print("Close all windows to end test.")


#
#============================ basic01_template ===========================
