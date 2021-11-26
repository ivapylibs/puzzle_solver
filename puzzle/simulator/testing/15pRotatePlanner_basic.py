#!/usr/bin/python3
# ============================ 15pRotatePlanner_basic ===========================
#
# @brief    Test script with command from the planner. (15p img)
#
# ============================ 15pRotatePlanner_basic ===========================

#
# @file     15pRotatePlanner_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/11/25  [created]
#
# ============================ 15pRotatePlanner_basic ===========================

# ==[0] Prep environment
import glob
import os

import cv2
import imageio
import improcessor.basic as improcessor
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.parser.fromSketch import FromSketch
from puzzle.piece.sift import Sift
from puzzle.simulator.basic import Basic
from puzzle.simulator.planner import Planner
from puzzle.solver.simple import Simple
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
# theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.imread(cpath + '/../../testing/data/cocacola.jpg')
# theImageSol = cv2.imread(cpath + '/../../testing/data/church.jpg')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[2] Create a Grid instance and explode it into a new board
#

print('Running through test cases. Will take a bit.')

theGridSol = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=ParamGrid(areaThresholdLower=5000))

# ==[2.1] Create a new Grid instance from the images
#

_, epBoard = theGridSol.explodedPuzzle(dx=400, dy=400)

# ==[2.2] Randomly swap the puzzle pieces.
#
theGridMea = Gridded(epBoard, ParamGrid(reorder=True))

_, epBoard = theGridMea.swapPuzzle()

# ==[2.3] Randomly rotate the puzzle pieces.
#

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

# cv2.imshow('debug', theMaskMea)
# cv2.waitKey()

theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea,
                                            theParams=ParamGrid(areaThresholdLower=1000, reorder=True))

# ==[3] Create a manager & simple solver and integrate them into planner
#

theManager = Manager(theGridSol, ManagerParms(matcher=Sift()))
theSolver = Simple(theGridSol, theGridMea)
thePlanner = Planner(theSolver, theManager)

# ==[4] Create a simulator for display
#
theSim = Basic(theSolver.current)

# ==[5] Start the solver to take turns, execute the plan, and display the updated board.
#

plt.ion()

# saveMe = True
saveMe = False

if saveMe:
    filename_list = glob.glob(cpath + f'/data/15pRotatePlanner_step*.png')
    for filename in filename_list:
        os.remove(filename)

FINISHED = False
i = 0

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
        theSim.fig.savefig(cpath + f'/data/15pRotatePlanner_step{str(i).zfill(2)}.png')

    print(f'Step {i + 1}:')

    # Re-plan for every iteration
    plan = thePlanner.process(meaBoard=theSim.puzzle, COMPLETE_PLAN=False)

    FINISHED = theSim.takeAction(plan)

    i = i + 1

plt.ioff()
# plt.draw()

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/15pRotatePlanner.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/15pRotatePlanner_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)

#
# ============================ 15pRotatePlanner_basic ===========================
