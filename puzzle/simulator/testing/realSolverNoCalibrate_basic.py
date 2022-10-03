#!/usr/bin/python3
# ============================ realSolverNoCalibrate_basic ===========================
#
# @brief    Test script with command from the solver & with no calibration process (we directly take as a exploded puzzle as the solution).
#           (real img)
#
# ============================ realSolverNoCalibrate_basic ===========================

#
# @file     realSolverNoCalibrate_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/16  [created]
#
# ============================ realSolverNoCalibrate_basic ===========================

# ==[0] Prep environment
import glob
import os

import cv2
import imageio
import matplotlib.pyplot as plt

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.regular import Regular
from puzzle.piece.sift import Sift
from puzzle.simulator.basic import Basic
from puzzle.solver.simple import Simple
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#

# Case 1
# theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/Exploded_mea_0.png')
# theImageMea = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/ExplodedWithRotationAndExchange_mea_0.png')

# # Case 2
fsize= 0.8
theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_big_hard3/sol_cali_mea_004.png')
theImageSol = cv2.resize(theImageSol, (0, 0), fx=fsize, fy=fsize)
theImageMea = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_big_hard3/sol_cali_mea_003.png')
theImageMea = cv2.resize(theImageMea, (0, 0), fx=fsize, fy=fsize)

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

theGridSol = theGridSol_src

theGridMea = Gridded.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                            theParams=ParamGrid(areaThresholdLower=1000, reorder=True,
                                                                pieceConstructor=Regular))

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
    filename_list = glob.glob(cpath + f'/data/realSolverNoCalibrate_step*.png')
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
        theSim.fig.savefig(cpath + f'/data/realSolverNoCalibrate_step{str(i).zfill(2)}.png')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='order')

    finishFlag = theSim.takeAction(plan)

    i = i + 1

plt.ioff()
# plt.draw()

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/realSolverNoCalibrate.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/realSolverNoCalibrate_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)

#
# ============================ realSolverNoCalibrate_basic ===========================
