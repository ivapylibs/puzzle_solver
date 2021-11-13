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
# @date     2021/11/12  [created]
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
import numpy as np

from puzzle.builder.arrangement import arrangement, paramPuzzle
from puzzle.builder.board import board
from puzzle.builder.gridded import gridded, paramGrid
from puzzle.manager import manager, managerParms
from puzzle.piece.regular import regular
from puzzle.piece.sift import sift
from puzzle.simulator.basic import basic
from puzzle.solver.simple import simple
from puzzle.utils.imageProcessing import preprocess_real_puzzle, find_nonzero_mask

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image.
#


# ==[2] Read the source images and reconstruct the solution board.
#
# Number of pieces
N = 15

theCalibrated = board()

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),),
                           )

for i in range(1,N+1):
    if i==1:
        thePrevImage = cv2.imread(cpath + f'/../../testing/data/puzzle_real_sample_black_cali/sol_cali_mea_{i-1}.png')
        thePrevImage = cv2.cvtColor(thePrevImage, cv2.COLOR_BGR2RGB)

    else:
        thePrevImage = theCurImage

    theCurImage = cv2.imread(cpath + f'/../../testing/data/puzzle_real_sample_black_cali/sol_cali_mea_{i}.png')
    theCurImage = cv2.cvtColor(theCurImage, cv2.COLOR_BGR2RGB)

    # Todo: We may have to use other strategies with real data input
    diff = cv2.absdiff(theCurImage, thePrevImage)
    # cv2.imshow('diff', diff)
    # cv2.waitKey()
    mask = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

    th = 50
    imask = mask > th

    canvas = np.ones_like(theCurImage, np.uint8)
    canvas[imask] = theCurImage[imask]

    theMaskMea = improc.apply(canvas)
    cv2.imshow('debug', theMaskMea)
    cv2.waitKey()
    # theBoard_single = arrangement.buildFrom_ImageAndMask(canvas, theMaskMea,
    #                                                      theParams=paramPuzzle(areaThresholdLower=1000))
    #
    # theCalibrated.addPiece(theBoard_single.pieces[0])

theCalibrated.display(ID_DISPLAY=True, CONTOUR_DISPLAY=False)
plt.show()


# ==[3] Create Grid instance to build up solution board.
#

theGridSol = gridded(theCalibrated,theParams=paramGrid(areaThresholdLower=1000, reorder=True,
                                                                pieceConstructor=regular))

theImageMea = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black_hard2/sol_cali_mea_23.png')
theImageMea = cv2.cvtColor(theImageMea, cv2.COLOR_BGR2RGB)

theMaskMea = preprocess_real_puzzle(theImageMea, verbose=False)
theGridMea = gridded.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                            theParams=paramGrid(areaThresholdLower=1000, reorder=True,
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
    filename_list = glob.glob(cpath + f'/data/realSolverCalibrate_step*.png')
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
        theSim.fig.savefig(cpath + f'/data/realSolver_step{str(i).zfill(2)}.png')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='order')

    FINISHED = theSim.takeAction(plan)

    i = i + 1

plt.ioff()
# plt.draw()

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
# ============================ realSolverManualCalibrate_basic ===========================
