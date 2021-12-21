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

from puzzle.builder.board import Board
from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.regular import Regular
from puzzle.piece.sift import Sift
from puzzle.simulator.basic import Basic
from puzzle.solver.simple import Simple
from puzzle.utils.imageProcessing import preprocess_real_puzzle
from puzzle.utils.puzzleProcessing import calibrate_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image for measurement.
#
fsize = 0.8
theImageMea = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_big_hard3/sol_cali_mea_001.png')
theImageMea = cv2.resize(theImageMea, (0, 0), fx=fsize, fy=fsize)
theImageMea = cv2.cvtColor(theImageMea, cv2.COLOR_BGR2RGB)

# ==[2] Read the source images and reconstruct the solution board.
#

# theCalibrated = calibrate_real_puzzle('data/puzzle_real_sample_black_cali_1', 0)
theCalibrated = calibrate_real_puzzle('data/puzzle_real_sample_black_big_cali_4', 1, fsize=fsize)

# Debug only
theCalibrated.display(ID_DISPLAY=True, CONTOUR_DISPLAY=False)
plt.show()

# theCalibrated.pieces[6].display()
# plt.show()

# # Debug only
# for piece in theCalibrated.pieces:
#     piece.display()
#     plt.show()

# ==[3] Create Grid instance to build up solution board & measured board.
#

theGridSol = Gridded(theCalibrated, theParams=ParamGrid(areaThresholdLower=1000, reorder=True,
                                                        pieceConstructor=Regular, tauGrid=20))

for i in range(len(theGridSol.pieces)):
    theGridSol.pieces[i].setPlacement(r=(-500,-500),offset=True)

# theGridSol = gridded(theCalibrated, theParams=paramGrid(areaThresholdLower=1000,
#                                                         pieceConstructor=regular, tauGrid=20, grid=(5,3)))

theMaskMea = preprocess_real_puzzle(theImageMea, verbose=False)
theGridMea = Gridded.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                            theParams=ParamGrid(areaThresholdLower=1000,
                                                                pieceConstructor=Regular))


# ==[4] Create a manager
#

theManager = Manager(theGridSol, ManagerParms(matcher=Sift(theThreshMatch=0.6)))
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
theSolver = Simple(theGridSol, copy.deepcopy(theGridMea))

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
    filename_list = glob.glob(cpath + f'/data/realSolverManualCalibrate_step*.png')
    for filename in filename_list:
        os.remove(filename)

finishFlag = False
# To demonstrate assembly process
i = 0
# To save calibration process
j = 0

theCalibrated = Board()
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                           )

while 1:

    # Since we use the same instance in the simulator and the solver,
    # it will update automatically
    theSim.display(ID_DISPLAY=True, CONTOUR_DISPLAY=False)

    theSim.fig.suptitle(f'Step {i}', fontsize=20)
    plt.pause(1)

    if finishFlag:
        break
    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    if saveMe:
        theSim.fig.savefig(cpath + f'/data/realSolverManualCalibrate_step{str(i).zfill(2)}.png')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='order')

    finishFlag = theSim.takeAction(plan)

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
