#!/usr/bin/python3
# ============================ basic03_pca ===========================
#
# @brief    Test script for the most basic functionality of pca. Create
#           two puzzles (rotate 1 for 90 degree) and compare them by moments
#           pca.
#
# ============================ basic03_pca ===========================

#
# @file     basic03_pca.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/03  [created]
#
# ============================ basic03_pca ===========================


# ==[0] Prep environment
import numpy as np

from puzzle.piece.pca import PCA
from puzzle.piece.template import Template

# ==[1] Create raw puzzle piece data.
#
theMask = np.full((20, 20), False, dtype=bool)
theMask[4:14, 7:12] = True
theImage = np.zeros((20, 20, 3), dtype='uint8')
theImage[4:14, 7:12, :] = np.full((1, 1, 3), [0, 200, 200])

thePiece_1 = Template.buildFromMaskAndImage(theMask, theImage)
thePiece_1.setPlacement(np.array([10, 10]))

theMask = np.full((20, 20), False, dtype=bool)
theMask[7:12, 4:14] = True
theImage = np.zeros((20, 20, 3), dtype='uint8')
theImage[7:12, 4:14, :] = np.full((1, 1, 3), [0, 200, 200])

thePiece_2 = Template.buildFromMaskAndImage(theMask, theImage)
thePiece_2.setPlacement(np.array([50, 50]))

# ==[2] Test creation
#
thePiece_1.display()
thePiece_2.display()

# ==[3] Create a PCA instance and compare puzzle 1 and 2. Should see -90.
#
thePCA = PCA(5)

ret = thePCA.score(thePiece_1, thePiece_2)
print('Create a PCA instance and compare puzzle 1 and 2. Should see -90.')
print(ret)

#
# ============================ basic02_moments ===========================
