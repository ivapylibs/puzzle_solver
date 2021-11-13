#!/usr/bin/python3
# ============================ realSolverManualCalibrate_basic ===========================
#
# @brief    Test script with command from the solver & with manual calibration process. (real img)
#
# ============================ realSolverManualCalibrate_basic ===========================

#
# @file     realSolverManualCalibrate_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/11/13  [created]
#
# ============================ realSolverManualCalibrate_basic ===========================

# ==[0] Prep environment

import copy
import glob
import os

import cv2
import imageio
import improcessor.basic as improcessor
import matplotlib.pyplot as plt

from puzzle.builder.board import board
from puzzle.builder.gridded import gridded, paramGrid
from puzzle.manager import manager, managerParms
from puzzle.piece.regular import regular
from puzzle.piece.sift import sift
from puzzle.simulator.basic import basic
from puzzle.solver.simple import simple
from puzzle.utils.imageProcessing import preprocess_real_puzzle
from puzzle.utils.puzzleProcessing import calibrate_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image (exploded).
#

theImageMea = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_hard2/sol_cali_mea_16.png')
theImageMea = cv2.cvtColor(theImageMea, cv2.COLOR_BGR2RGB)

# ==[2] Read the source images and reconstruct the solution board.
#

# theCalibrated = calibrate_real_puzzle('data/puzzle_real_sample_black_cali_1', 0)
theCalibrated = calibrate_real_puzzle('data/puzzle_real_sample_black_cali_2', 1)

theCalibrated.display(ID_DISPLAY=True, CONTOUR_DISPLAY=False)
plt.show()

# ==[3] Create Grid instance to build up solution board & measured board.
#

theGridSol = gridded(theCalibrated, theParams=paramGrid(areaThresholdLower=1000, reorder=True,
                                                        pieceConstructor=regular, tauGrid=20))

theMaskMea = preprocess_real_puzzle(theImageMea, verbose=False)
theGridMea = gridded.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                            theParams=paramGrid(areaThresholdLower=1000,
                                                                pieceConstructor=regular))


# ==[4] Create a manager
#

theManager = manager(theGridSol, managerParms(matcher=sift()))
theManager.process(theGridMea)

bMeasImage = theManager.bMeas.toImage(ID_DISPLAY=True)
bSolImage = theManager.solution.toImage(ID_DISPLAY=True, CONTOUR_DISPLAY=False)

f, axarr = plt.subplots(1, 2)
axarr[0].imshow(bMeasImage)
axarr[0].title.set_text('Measurement')
axarr[1].imshow(bSolImage)
axarr[1].title.set_text('Solution')


# Show assignment
print('The first index refers to the measured board while the second one refers to the solution board. Note that '
      'the index in different boards may refer to different puzzle pieces.')
print(theManager.pAssignments)

plt.show()

# ==[4] Create simple solver and set up the match
#
theSolver = simple(theGridSol, copy.deepcopy(theGridMea))

theSolver.setMatch(theManager.pAssignments, theManager.pAssignments_rotation)

# ==[5] Create a simulator for display
#
theSim = basic(theSolver.current)

# ==[6] Start the solver to take turns, execute the plan, and display the updated board.
#

plt.ion()

# saveMe = True
saveMe = False

if saveMe:
    filename_list = glob.glob(cpath + f'/data/realSolverManualCalibrate_step*.png')
    for filename in filename_list:
        os.remove(filename)

FINISHED = False
# To demonstrate assembly process
i = 0
# To save calibration process
j = 0

theCalibrated = board()
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                           )

while 1:

    # Since we use the same instance in the simulator and the solver,
    # it will update automatically
    theSim.display(ID_DISPLAY=True)

    theSim.fig.suptitle(f'Step {i}', fontsize=20)
    plt.pause(1)

    if FINISHED:
        break
    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    if saveMe:
        theSim.fig.savefig(cpath + f'/data/realSolverManualCalibrate_step{str(i).zfill(2)}.png')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='order')

    FINISHED = theSim.takeAction(plan)

    i = i + 1

plt.ioff()
# plt.draw()

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/realSolverManualCalibrate.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/realSolverManualCalibrate_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)
plt.show()
#
# ============================ realSolverManualCalibrate_basic ===========================
