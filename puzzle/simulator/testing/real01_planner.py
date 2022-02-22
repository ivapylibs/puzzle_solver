#!/usr/bin/python3
# ============================= real01_planner =============================
#
# @brief    Tests the tracking function with the planner (a sequence of real imgs)
#
#
# ============================= real01_planner =============================
#
# @file     real01_planner.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/02/16 [created]
#
# ============================= real01_planner =============================


# ==[0] Prep environment
import copy
import os
import cv2
import time
import matplotlib.pyplot as plt
import numpy as np
import glob

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.builder.arrangement import Arrangement, ParamArrange
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift
from puzzle.utils.imageProcessing import preprocess_real_puzzle
from puzzle.solver.simple import Simple
from puzzle.simulator.planner import Planner

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template to build up the solution board.
#

# VIDEO_DIR = 'puzzle_real_sample_black_paper'
# VIDEO_DIR = 'puzzle_real_sample_black_hand'
VIDEO_DIR = 'puzzle_real_sample_black_hand_2'
# VIDEO_DIR = 'puzzle_real_sample_black_hand_robot'

theImageSol = cv2.imread(cpath + f'/../../testing/data/{VIDEO_DIR}/test_yunzhi_mea_000.png')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)
theMaskSol = preprocess_real_puzzle(theImageSol)

theArrangeSol = Arrangement.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                                   theParams=ParamArrange(areaThresholdLower=1000, areaThresholdUpper=13000))

#  ==[2] Create a manager & an empty planner

theManager = Manager(copy.deepcopy(theArrangeSol), ManagerParms(matcher=Sift()))
bSolImage = theManager.solution.toImage(ID_DISPLAY=True)

thePlanner = None

f, axarr = plt.subplots(3, 1)
plt.ion()

file_list = glob.glob(cpath + f'/../../testing/data/{VIDEO_DIR}/*.png')

for i in range(0,len(file_list)):

    print(f'Frame {i}')

    time_start = time.time()
    theImageMea = cv2.imread(cpath + f'/../../testing/data/{VIDEO_DIR}/test_yunzhi_mea_{str(i).zfill(3)}.png')


    theImageMea = cv2.cvtColor(theImageMea, cv2.COLOR_BGR2RGB)

    # ==[3] Create an improcessor to obtain the mask.
    #
    theMaskMea = preprocess_real_puzzle(theImageMea, verbose=False)

    # # Debug only
    # cv2.imshow('debug', theMaskMea)
    # cv2.waitKey()

    # ==[4] Create an arrangement instance.
    #

    theArrangeMea = Arrangement.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                                       theParams=ParamArrange(areaThresholdLower=1000, areaThresholdUpper=13000 ))

    # ==[5] Manager processing
    #
    try:
        theManager.process(theArrangeMea)

        if thePlanner is None:
            theSolver = Simple(theArrangeSol, theArrangeMea)
            thePlanner = Planner(theSolver, theManager, ParamArrange(areaThresholdLower=1000))

        plan = thePlanner.process(theArrangeMea, COMPLETE_PLAN=True, SAVED_PLAN=False, RUN_SOLVER=False)

        time_end = np.round(time.time() - time_start, 2)
        print(f'Time usage: {time_end}s')

        # ==[6] Display. Should see some ids on the puzzle pieces
        # while the ids in the assignment board refer to the ids in the solution board.
        #

        bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)

        bTrackImage = thePlanner.record['meaBoard'].toImage(ID_DISPLAY=True)
    except:
        print(f'Problem with {i}')
        # plt.waitforbuttonpress()

    axarr[0].imshow(bMeasImage)
    axarr[0].title.set_text(f'Measured board {i}')
    axarr[1].imshow(bTrackImage)
    axarr[1].title.set_text('Tracking board')
    axarr[2].imshow(bSolImage)
    axarr[2].title.set_text('Solution board')
    plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[])

    # # Debug only
    # plt.waitforbuttonpress()

    plt.pause(0.01)

plt.ioff()
plt.show()
#
# ============================= real01_planner =============================
