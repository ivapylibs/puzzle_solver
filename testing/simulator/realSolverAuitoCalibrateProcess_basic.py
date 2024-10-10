#!/usr/bin/python3
# ============================ realSolverAuitoCalibrateProcess_basic ===========================
#
# @brief    Test script with command from the solver & for calibration process
#           We simulate the real image sequences of automatic calibration. (real img)
#
# ============================ realSolverAuitoCalibrateProcess_basic ===========================

#
# @file     realSolverAuitoCalibrateProcess_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/23  [created]
#
# ============================ realSolverAuitoCalibrateProcess_basic ===========================

# ==[0] Prep environment

import copy
import glob
import os

import cv2
import imageio
import improcessor.basic as improcessor
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.arrangement import Arrangement, ParamPuzzle
from puzzle.builder.board import Board
from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.regular import Regular
from puzzle.piece.sift import Sift
from puzzle.simulator.basic import Basic
from puzzle.solver.simple import Simple
from puzzle.utils.imageProcessing import preprocess_real_puzzle, find_nonzero_mask

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#

# Case 1
# theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/Exploded_mea_0.png')

# Case 2
theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_hard/GTSolBoard_mea_3.png')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#
theMaskSol = preprocess_real_puzzle(theImageSol, verbose=False)
# cv2.imshow('debug', theMaskSol)
# cv2.waitKey()

# ==[2] Create Grid instance to build up solution board & measured board.
#

theGridSol_src = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                                theParams=ParamGrid(areaThresholdLower=1000, reorder=True,
                                                                    pieceConstructor=Regular))
theBoard = Board()
theRegular_0 = theGridSol_src.pieces[0]
theRegular_0 = theRegular_0.rotatePiece(theta=theRegular_0.theta)
theRegular_0.setPlacement(np.array([-200, -200]), offset=True)

theBoard.addPiece(theRegular_0)

for i in range(1, theGridSol_src.size()):

    theRegular_0 = theBoard.pieces[i - 1]

    theRegular_1 = theGridSol_src.pieces[i]
    theRegular_1 = theRegular_1.rotatePiece(theta=theRegular_1.theta)

    # Todo: Adhoc way, will update in the future
    if i == theGridSol_src.gc.shape[1] / theGridSol_src.gc.shape[0]:
        theRegular_0 = theBoard.pieces[0]
        piece_A_coord = find_nonzero_mask(theRegular_0.edge[3].mask) + np.array(theRegular_0.rLoc).reshape(-1, 1)
        piece_B_coord = find_nonzero_mask(theRegular_1.edge[2].mask) + np.array(theRegular_1.rLoc).reshape(-1, 1)
    else:
        piece_A_coord = find_nonzero_mask(theRegular_0.edge[1].mask) + np.array(theRegular_0.rLoc).reshape(-1, 1)
        piece_B_coord = find_nonzero_mask(theRegular_1.edge[0].mask) + np.array(theRegular_1.rLoc).reshape(-1, 1)

    x_relative = np.max(piece_B_coord[0, :]) - np.max(piece_A_coord[0, :])
    y_relative = np.max(piece_B_coord[1, :]) - np.max(piece_A_coord[1, :])

    theRegular_1.setPlacement([int(-x_relative), int(-y_relative)], offset=True)
    theBoard.addPiece(theRegular_1)

theGridSol = Gridded(theBoard)

# ==[3] Create a manager
#

theManager = Manager(theGridSol, ManagerParms(matcher=Sift()))
theManager.process(theGridSol_src)

# ==[4] Create simple solver and set up the match
#
theSolver = Simple(theGridSol, copy.deepcopy(theGridSol_src))

theSolver.setMatch(theManager.pAssignments, theManager.pAssignments_rotation)

# ==[5] Create a simulator for display
#
theSim = Basic(theSolver.current)

# ==[6] Start the solver to take turns, execute the plan, and display the updated board.
#

plt.ion()

# saveMe = True
saveMe = False

if saveMe:
    filename_list = glob.glob(cpath + f'/data/realSolverCalibrate_step*.png')
    for filename in filename_list:
        os.remove(filename)

finishFlag = False
# To demonstrate assembly process
i = 0
# To save calibration process
j = 0

theCalibrated = Board()
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_RGB2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                           )

while 1:

    # Since we use the same instance in the simulator and the solver,
    # it will update automatically
    theSim.display(ID_DISPLAY=True)

    theSim.fig.suptitle(f'Step {i}', fontsize=20)
    plt.pause(1)

    thePrevImage = theSim.toImage(theImage=np.zeros_like(theImageSol).astype('uint8'), CONTOUR_DISPLAY=False,
                                  BOUNDING_BOX=False)

    if finishFlag:
        break
    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='order', STEP_WISE=False)

    finishFlag = theSim.takeAction(plan)

    theCurImage = theSim.toImage(theImage=np.zeros_like(theImageSol).astype('uint8'), CONTOUR_DISPLAY=False,
                                 BOUNDING_BOX=False)

    # Todo: We may have to use other strategies with real data input
    diff = cv2.absdiff(theCurImage, thePrevImage)
    mask = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

    th = 1
    imask = mask > th

    canvas = np.ones_like(theCurImage, np.uint8)
    canvas[imask] = theCurImage[imask]

    if finishFlag is False:

        theMaskMea = improc.apply(canvas)
        # cv2.imshow('debug', theMaskMea)
        # cv2.waitKey()
        theBoard_single = Arrangement.buildFrom_ImageAndMask(canvas, theMaskMea,
                                                             theParams=ParamPuzzle(areaThresholdLower=1000))

        # theCalibrated.addPiece(theBoard_single.pieces[0])

        # Debug only
        try:
            theCalibrated.addPiece(theBoard_single.pieces[0])
        except:
            cv2.imshow('theMaskMea', theMaskMea)
            cv2.imshow('thePrevImage', thePrevImage)
            cv2.imshow('theCurImage', theCurImage)
            cv2.imshow('canvas', canvas)
            cv2.waitKey()

        if saveMe:
            theCalibratedImage = theCalibrated.toImage(ID_DISPLAY=True)
            cv2.imwrite(cpath + f'/data/realSolverCalibrate_step{str(j).zfill(2)}.png',
                        cv2.cvtColor(thePrevImage, cv2.COLOR_RGB2BGR)
                        )
            j = j + 1
            cv2.imwrite(cpath + f'/data/realSolverCalibrate_step{str(j).zfill(2)}.png',
                        cv2.cvtColor(theCurImage, cv2.COLOR_RGB2BGR)
                        )
            j = j + 1
            cv2.imwrite(cpath + f'/data/realSolverCalibrate_step{str(j).zfill(2)}.png',
                        cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
                        )
            j = j + 1
            cv2.imwrite(cpath + f'/data/realSolverCalibrate_step{str(j).zfill(2)}.png',
                        cv2.cvtColor(theCalibratedImage, cv2.COLOR_RGB2BGR)
                        )
            j = j + 1

    i = i + 1

plt.ioff()

theCalibrated.display(ID_DISPLAY=True)

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/realSolverCalibrate.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/realSolverCalibrate_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)
plt.show()
#
# ============================ realSolverAuitoCalibrateProcess_basic ===========================
