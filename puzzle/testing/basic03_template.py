#============================ basic02_moments ===========================
#
# @brief    Test script for the most basic functionality of template
#           puzzle piece class.
#
#============================ basic02_moments ===========================

#
# @file     basic01_template.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2017/07/28  [created]
#           2021/07/31  [modified]
#
#============================ basic02_moments ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.piece.template import template
from puzzle.board import board

#==[1] Create raw puzzle piece data.
#
theMask = np.full((20,20), False, dtype=bool)
theMask[4:14,7:12] = True
theImage = np.zeros((20,20,3),dtype='uint8')
theImage[4:14,7:12,:] = np.full((1,1,3), [0,200,200])

thePiece_1 = template.buildFromMaskAndImage(theMask, theImage)
thePiece_1.setPlacement(np.array([10,10]))

theMask = np.full((20,20), False, dtype=bool)
theMask[4:14,7:12] = True
theImage = np.zeros((20,20,3),dtype='uint8')
theImage[4:14,7:12,:] = np.full((1,1,3), [0,200,200])

thePiece_2 = template.buildFromMaskAndImage(theMask, theImage)
thePiece_2.setPlacement(np.array([50,50]))

#==[2] Test creation
#
thePiece_1.display()
thePiece_2.display()




#==[3] Create a solution board and add thePiece_1
#
theBoard_gt = board()
theBoard_gt.addPiece(thePiece_1)

#==[4] Create a measured board and add thePiece_2
#
theBoard_measured = board()
theBoard_measured.addPiece(thePiece_2)







#
#============================ basic02_moments ===========================
