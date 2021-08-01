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
# @author   WHO ELSE?
# @date     2017/07/28  [created]
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

theImage = np.zeros((20,20,3))
theImage[4:14,7:12,:] = np.full((1,1,3), [200,100,100])
  # Or should it be an OpenCV image instance?


thePiece = template.buildFromMaskAndImage(theMask, theImage)


#==[2] Test creation
#
thePiece.display()

#==[3] Test insertion into image data.
#
bigImage = np.zeros((200,200,3))

thePiece.placeInImage(bigImage)
thePiece.setPlacement(np.array([50,50]))
thePiece.placeInImage(bigImage)
thePiece.placeInImageAt(bigImage, np.array([70,30]))

# Display the resulting image. Should have three puzzle pieces in it.
plt.figure()
plt.imshow(bigImage, extent = [0, 1, 0, 1])
plt.show()

#
#============================ basic01_template ===========================
