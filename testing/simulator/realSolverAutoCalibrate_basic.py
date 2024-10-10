#!/usr/bin/python3
# ============================ realSolverAutoCalibrate_basic ===========================
#
# @brief    Test script with command from the solver & with automatic calibration process (put exploded pieces together according to rough distance). (real img)
#
# ============================ realSolverAutoCalibrate_basic ===========================

#
# @file     realSolverAutoCalibrate_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/16  [created]
#
# ============================ realSolverAutoCalibrate_basic ===========================

# ==[0] Prep environment
import glob
import os

import cv2
import imageio
import matplotlib.pyplot as plt
import numpy as np

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
# theImageMea = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/ExplodedWithRotationAndExchange_mea_0.png')

# Case 2
theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_hard/GTSolBoard_mea_3.png')
theImageMea = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_hard/MeaBoard_5.png')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)
theImageMea = cv2.cvtColor(theImageMea, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#
theMaskSol = preprocess_real_puzzle(theImageSol)
theMaskMea = preprocess_real_puzzle(theImageMea, verbose=False)

# ==[2] Create Grid instance to build up solution board & measured board.
#

theGridSol_src = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                                theParams=ParamGrid(areaThresholdLower=1000, reorder=True,
                                                                    pieceConstructor=Regular))
theBoard = Board()
theRegular_0 = theGridSol_src.pieces[0]
theRegular_0 = theRegular_0.rotatePiece(theta=theRegular_0.theta)
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

theGridMea = Gridded.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                            theParams=ParamGrid(areaThresholdLower=1000, reorder=True,
                                                                pieceConstructor=Regular))
fhSol, fhMea = plt.figure(), plt.figure()
theGridSol.display(fh=fhSol)
theGridMea.display(fh=fhMea)
plt.show()

# ==[3] Create a manager
#

theManager = Manager(theGridSol, ManagerParms(matcher=Sift()))
theManager.process(theGridMea)

# ==[4] Create simple solver and set up the match
#
theSolver = Simple(theGridSol, theGridMea)

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
    filename_list = glob.glob(cpath + f'/data/realSolverAutoCalibrate_step*.png')
    for filename in filename_list:
        os.remove(filename)

finishFlag = False
i = 0

while 1:

    # Since we use the same instance in the simulator and the solver,
    # it will update automatically
    theSim.display(ID_DISPLAY=True)

    theSim.fig.suptitle(f'Step {i}', fontsize=20)
    plt.pause(1)

    if finishFlag:
        break
    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    if saveMe:
        theSim.fig.savefig(cpath + f'/data/realSolverAutoCalibrate_step{str(i).zfill(2)}.png')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='order', COMPLETE_PLAN=False, SAVED_PLAN=False)

    finishFlag = theSim.takeAction(plan)

    i = i + 1

plt.ioff()
# plt.draw()

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/realSolverAutoCalibrate.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/realSolverAutoCalibrate_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)

#
# ============================ realSolverAutoCalibrate_basic ===========================
