#!/usr/bin/python3
# ============================ 60pRotateSolverNewPlan_basic ===========================
#
# @brief    Test script with command from the solver (new strategy). (60p img)
#
# ============================ 60pRotateSolverNewPlan_basic ===========================

#
# @file     60pRotateSolverNewPlan_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/11/3  [created]
#
# ============================ 60pRotateSolverNewPlan_basic ===========================

# Todo: You can change the flag here

ROTATION_ENABLED = True
# ROTATION_ENABLED = False


# ==[0] Prep environment
import glob
import os
import shutil

import cv2
import imageio
import improcessor.basic as improcessor
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.manager import manager, managerParms
from puzzle.parser.fromSketch import fromSketch
from puzzle.piece.sift import sift
from puzzle.simulator.basic import basic
from puzzle.solver.simple import simple
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
# theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
# theImageSol = cv2.imread(cpath + '/../../testing/data/church.jpg')
theImageSol = cv2.imread(cpath + '/../../testing/data/cocacola.jpg')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_60p_AdSt408534841.png')
# theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[2] Create a Grid instance and explode it into a new board
#

print('Running through test cases. Will take a bit.')

theGridSol = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=paramGrid(areaThresholdLower=5000))

# ==[2.1] Create a new Grid instance from the images
#

_, epBoard = theGridSol.explodedPuzzle(dx=125, dy=125)

# ==[2.2] Randomly swap the puzzle pieces.
#
theGridMea = gridded(epBoard, paramGrid(reorder=True))

_, epBoard = theGridMea.swapPuzzle()

# ==[2.3] Randomly rotate the puzzle pieces.
#

if ROTATION_ENABLED:
    gt_rotation = []
    for i in range(epBoard.size()):
        gt_rotation.append(np.random.randint(0, 70))
        epBoard.pieces[i] = epBoard.pieces[i].rotatePiece(gt_rotation[-1])

epImage = epBoard.toImage(CONTOUR_DISPLAY=False)

# ==[2.4] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                           cv2.dilate, (np.ones((3, 3), np.uint8),)
                           )
theMaskMea = improc.apply(epImage)

theGridMea = gridded.buildFrom_ImageAndMask(epImage, theMaskMea,
                                            theParams=paramGrid(areaThresholdLower=1000, reorder=True))

# ==[3] Create a manager
#

theManager = manager(theGridSol, managerParms(matcher=sift()))
theManager.process(theGridMea)

# ==[4] Create simple solver and set up the match
#
theSolver = simple(theGridSol, theGridMea)

if ROTATION_ENABLED:
    theSolver.setMatch(theManager.pAssignments, theManager.pAssignments_rotation)
else:
    theSolver.setMatch(theManager.pAssignments)

# ==[5] Create a simulator for display
#
theSim = basic(theSolver.current)

# ==[6] Start the solver to take turns, execute the plan, and display the updated board.
#

plt.ion()

# saveMe = True
saveMe = False

if saveMe:
    filename_list = glob.glob(cpath + f'/data/60pRotateSolverNewPlan_step*.png')
    for filename in filename_list:
        shutil.rmtree(filename)

FINISHED = False
i = 0

while 1:

    # Since we use the same instance in the simulator and the solver,
    # it will update automatically.
    theSim.display(ID_DISPLAY=True)

    theSim.fig.suptitle(f'Step {i}', fontsize=20)
    plt.pause(1)

    if FINISHED:
        break
    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    if saveMe:
        theSim.fig.savefig(cpath + f'/data/60pRotateSolverNewPlan_step{str(i).zfill(3)}.png')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='new')

    FINISHED = theSim.takeAction(plan)

    i = i + 1

plt.ioff()
# plt.draw()

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/60pRotateSolverNewPlan.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/60pRotateSolverNewPlan_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)

#
# ============================ 60pRotateSolverNewPlan_basic ===========================
