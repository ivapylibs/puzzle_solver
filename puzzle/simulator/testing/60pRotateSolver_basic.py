#!/usr/bin/python3
# ============================ 60pRotateSolver_basic ===========================
#
# @brief    Test script with command from the solver. (60p img)
#
# ============================ 60pRotateSolver_basic ===========================

#
# @file     60pRotateSolver_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/30  [created]
#
# ============================ 60pRotateSolver_basic ===========================


import glob
import os

import cv2
import imageio
import improcessor.basic as improcessor
# ==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.manager import manager, managerParms
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
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

# ==[1.1] Create an improcesser to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000))
theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[1.3] Create a Grid instance to reorder the puzzle board
#

theGrid_src = gridded(theBoardSol, paramGrid(reorder=True))

# ==[2] Create a Grid instance and explode it into a new board
#

print('Running through test cases. Will take a bit.')

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=paramGrid(areaThreshold=5000))

# ==[2.1] Create a new Grid instance from the images
#

_, epBoard = theGrid.explodedPuzzle(dx=100, dy=100)

# ==[2.2] Randomly swap the puzzle pieces.
#
theGrid_new = gridded(epBoard, paramGrid(reorder=True))

_, epBoard = theGrid_new.swapPuzzle()

# ==[2.3] Randomly rotate the puzzle pieces.
#

gt_rotation = []
for i in range(epBoard.size()):
    # gt_rotation.append(60)
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
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(epImage.copy())
theMaskSol_new = theDet.getState().x

# temp_demo = cv2.resize(theMaskSol_new, (int(theMaskSol_new.shape[1] / 2), int(theMaskSol_new.shape[0] / 2)), interpolation=cv2.INTER_AREA)
# cv2.imshow('debug',temp_demo)
# cv2.waitKey()
theGrid_new = gridded.buildFrom_ImageAndMask(epImage, theMaskSol_new,
                                             theParams=paramGrid(areaThreshold=1000, reorder=True))

# ==[3] Create a manager
#

theManager = manager(theGrid_src.solution, managerParms(matcher=sift()))
theManager.process(theGrid_new.solution)

# # Debug only
# bMeasImage = theManager.bMeas.toImage(ID_DISPLAY = True)
# bsolImage = theManager.solution.toImage(ID_DISPLAY = True)
#
# f, axarr = plt.subplots(1,2)
# axarr[0].imshow(bMeasImage)
# axarr[0].title.set_text('Measurement')
# axarr[1].imshow(bsolImage)
# axarr[1].title.set_text('Solution')
#
# # Show assignment
# print('The first index refers to the measured board while the second one refers to the solution board. Note that '
#       'the index in different boards may refer to different puzzle pieces.')
# print(theManager.pAssignments)
#
# plt.show()

# ==[4] Create simple sovler and set up the match
#
theSolver = simple(theGrid_src.solution, theGrid_new.solution)

theSolver.setMatch(theManager.pAssignments, theManager.pAssignments_rotation)

# ==[5] Create a simulator for display
#
theSim = basic(theGrid_new.solution)

# ==[6] Start the solver to take turns, display the updated board.
#

plt.ion()

# saveMe = True
saveMe = False

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
        theSim.fig.savefig(cpath + f'/data/60pRotateSolver_step{str(i).zfill(3)}.png')

    print(f'Step {i + 1}:')
    FINISHED = theSolver.takeTurn(defaultPlan='order')

    i = i + 1

plt.ioff()
# plt.draw()

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/60pRotateSolver_step.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/60pRotateSolver_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)

#
# ============================ 60pRotateSolver_basic ===========================