#============================ basic01_template ===========================
#
# @brief    Test script for the most basic functionality of template
#           puzzle piece class.
#
#============================ basic01_template ===========================

#
# @file     basic01_template.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2017/07/28  [created]
#           2021/07/31  [modified]
#
#============================ basic01_template ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.piece.template import template

#==[1] Create raw puzzle piece data.
#
theMask = np.full((20,20), False, dtype=bool)
theMask[4:14,7:12] = True

# Or should it be an OpenCV image instance?
theImage = np.zeros((20,20,3))
theImage[4:14,7:12,:] = np.full((1,1,3), [1,0,1])

thePiece = template.buildFromMaskAndImage(theMask, theImage)

#==[2] Test creation
#
thePiece.display()

#==[3] Test insertion into image data.
#
bigImage = np.zeros((200,200,3))

thePiece.placeInImage(bigImage)
# OpenCV style
thePiece.setPlacement(np.array([50,50]))
thePiece.placeInImage(bigImage)
# OpenCV style
thePiece.placeInImageAt(bigImage, np.array([70,30]))

# Display the resulting image. Should have three puzzle pieces in it.
plt.figure()
# plt.imshow(bigImage, extent = [0, 1, 0, 1])
plt.imshow(bigImage)
plt.show()

#
#============================ basic01_template ===========================
