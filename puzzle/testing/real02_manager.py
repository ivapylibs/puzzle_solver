#!/usr/bin/python3
# ============================= real02_manager =============================
#
# @brief    Tests the core functionality of the puzzle.manager class. The manager
#           will have access to measurement and solution images & masks to generate
#           associations between them. (a series of real imgs)
#
#
# ============================= real02_manager =============================
#
# @file     real02_manager.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/02/15 [created]
#
# ============================= real02_manager =============================


# ==[0] Prep environment
import copy
import os
import cv2
import time
import matplotlib.pyplot as plt

from puzzle.builder.arrangement import Arrangement, ParamArrange
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#


theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample_black_new/test_yunzhi_mea_000.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)
theMaskSol = preprocess_real_puzzle(theImageSol)
theGrid_Sol = Arrangement.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                             theParams=ParamArrange(areaThresholdLower=1000, areaThresholdUpper=13000))

f, axarr = plt.subplots(2, 1)
plt.ion()
for i in range(1,13):

    print(f'Frame {i}')

    time_start = time.time()
    theImageMea = cv2.imread(cpath + f'/data/puzzle_real_sample_black_new2/test_yunzhi_mea_{str(i).zfill(3)}.png')
    theImageMea = cv2.cvtColor(theImageMea, cv2.COLOR_BGR2RGB)

    # ==[1.1] Create an improcessor to obtain the mask.
    #
    theMaskMea = preprocess_real_puzzle(theImageMea, verbose=False)

    # ==[2] Create a Grid instance.
    #
    print('Running through test cases. Will take a bit.')

    # cv2.imshow('debug', theMaskMea)
    # cv2.waitKey()

    theGrid_Mea = Arrangement.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                                 theParams=ParamArrange(areaThresholdLower=1000, areaThresholdUpper=13000))

    # ==[3] Create a manager
    #
    try:
        theManager = Manager(copy.deepcopy(theGrid_Sol), ManagerParms(matcher=Sift()))
        theManager.process(theGrid_Mea)

        time_end = time.time() - time_start
        print(f'Time usage: {time_end}s')


    # ==[4] Display. Should see some ids on the puzzle pieces
    # while the ids in the assignment board refer to the ids in the solution board.
    #

        bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)
    except:
        print(f'Problem with {i}')
    bSolImage = theManager.solution.toImage(ID_DISPLAY=True)


    axarr[0].imshow(bMeasImage)
    axarr[0].title.set_text('Measurement_1')
    axarr[1].imshow(bSolImage)
    axarr[1].title.set_text('Measurement_2')

    # Show assignment
    print('The first index refers to the measured board while the second one refers to the solution board.')
    print(theManager.pAssignments)

    plt.pause(1)

plt.ioff()
plt.show()
#
# ============================= real02_manager =============================
