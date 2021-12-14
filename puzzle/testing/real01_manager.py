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


# ==[0] Prep environment
import os
import cv2
import matplotlib.pyplot as plt

from puzzle.builder.arrangement import Arrangement, ParamArrange
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#

# # Case 1:
# theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample_black/Exploded_mea_0.png')
# theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample_black/ExplodedWithRotationAndExchange_mea_0.png')

# Case 2
# theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample_black_hard3/sol_cali_mea_004.png')
# theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample_black_hard3/sol_cali_mea_003.png')

# Case 3
# theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample_black/Exploded_mea_0.png')
# theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample_black/ExplodedWithRotation_mea_0.png')

# # Case 4 (2 out of 18 missed)
# theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample_black_impossible/impossible_mea_000.png')
# theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample_black_impossible/impossible_mea_001.png')

# # Case 5 (2 out of 18 missed)
# theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample_black_impossible_noLight/impossible_noLight_mea_000.png')
# theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample_black_impossible_noLight/impossible_noLight_mea_001.png')

# Case 6 (7 out of 36 missed)
theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample_black_impossible_noLight/impossible_noLight_mea_006.png')
theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample_black_impossible_noLight/impossible_noLight_mea_005.png')

# # Case 7 (11 out of 34 missed)
# theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample_black_impossible_light/impossible_light_mea_000.png')
# theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample_black_impossible_light/impossible_light_mea_001.png')


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
theGrid_Sol = Arrangement.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                             theParams=ParamArrange(areaThresholdLower=1000, areaThresholdUpper=13000))
theGrid_Mea = Arrangement.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                             theParams=ParamArrange(areaThresholdLower=1000, areaThresholdUpper=13000))

# ==[3] Create a manager
#
# theManager = manager(theGridSol, managerParms(matcher=edge()))

theManager = Manager(theGrid_Sol, ManagerParms(matcher=Sift()))
theManager.process(theGrid_Mea)

# ==[4] Display. Should see some ids on the puzzle pieces
# while the ids in the assignment board refer to the ids in the solution board.
#
bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)
bSolImage = theManager.solution.toImage(ID_DISPLAY=True)

f, axarr = plt.subplots(2, 1)
axarr[0].imshow(bMeasImage)
axarr[0].title.set_text('Measurement_1')
axarr[1].imshow(bSolImage)
axarr[1].title.set_text('Measurement_2')

# Show assignment
print('The first index refers to the measured board while the second one refers to the solution board.')
print(theManager.pAssignments)

text = 'Match:' + str(theManager.pAssignments)
plt.gcf().text(0.1, 0.05, text, fontsize=8, wrap=True)

print('Num. of matched cases:', len(theManager.pAssignments))

plt.show()
#
# ============================= real01_manager =============================
