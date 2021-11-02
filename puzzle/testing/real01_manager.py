#!/usr/bin/python3
# ============================= real01_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (real img)
#
#
# ============================= real01_manager =============================
#
# @file     real01_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/12 [created]
#
# ============================= real01_manager =============================

import os

import cv2
# ==[0] Prep environment
import matplotlib.pyplot as plt

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.manager import manager, managerParms
from puzzle.piece.sift import sift
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample_black/Exploded_mea_0.png')

theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample_black/ExplodedWithRotationAndExchange_mea_0.png')
# theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample_black/ExplodedWithRotation_mea_0.png')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)
theImageMea = cv2.cvtColor(theImageMea, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#
theMaskSol = preprocess_real_puzzle(theImageSol)
theMaskMea = preprocess_real_puzzle(theImageMea, verbose=False)

# ==[2] Create a Grid instance.
#
print('Running through test cases. Will take a bit.')

# cv2.imshow('debug', theMaskMea)
# cv2.waitKey()
theGrid_Sol = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                             theParams=paramGrid(areaThresholdLower=1000, reorder=True))
theGrid_Mea = gridded.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                             theParams=paramGrid(areaThresholdLower=1000, reorder=True))

# ==[3] Create a manager
#
# theManager = manager(theGrid_src, managerParms(matcher=edge()))

theManager = manager(theGrid_Sol, managerParms(matcher=sift()))
theManager.process(theGrid_Mea)

# ==[4] Display. Should see some ids on the puzzle pieces
# while the ids in the assignment board refer to the ids in the solution board.
#
bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)
bSolImage = theManager.solution.toImage(ID_DISPLAY=True)

f, axarr = plt.subplots(1, 2)
axarr[0].imshow(bMeasImage)
axarr[0].title.set_text('Measurement')
axarr[1].imshow(bSolImage)
axarr[1].title.set_text('Solution')

# Show assignment
print('The first index refers to the measured board while the second one refers to the solution board.')
print(theManager.pAssignments)

num_failure = 0
for pair in theManager.pAssignments:
    if pair[0] != pair[1]:
        num_failure = num_failure + 1

# Add the unmatched pairs
num_failure = num_failure + theManager.bMeas.size() - len(theManager.pAssignments)
print('Num. of failure cases:', num_failure)

plt.show()
#
# ============================= real01_manager =============================
