#!/usr/bin/python3
# ============================ 15pRotateSolverCalibrate_basic ===========================
#
# @brief    Test script with command from the solver & for calibration process. (15p img)
#
# ============================ 15pRotateSolverCalibrate_basic ===========================

#
# @file     15pRotateSolverCalibrate_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/23  [created]
#
# ============================ 15pRotateSolverCalibrate_basic ===========================

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
from puzzle.parser.fromSketch import FromSketch
from puzzle.piece.sift import Sift
from puzzle.simulator.basic import Basic
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

# theGridSol is unknown to the calibrated board but we will use it for simulator
theGridSol = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                            theParams=ParamGrid(areaThresholdLower=5000, reorder=True))

# ==[2.1] Create a new Grid instance from the images
#

_, epBoard = theGridSol.explodedPuzzle(dx=400, dy=400)

# ==[2.2] Randomly change the locations of the puzzle pieces.
#

for i in range(epBoard.size()):
    epBoard.pieces[i].setPlacement(r=np.array([500, 500]) + np.random.randint(-30, 30), offset=True)

# ==[2.3] Randomly rotate the puzzle pieces.
#

gt_rotation = []
for i in range(epBoard.size()):
    gt_rotation.append(np.random.randint(0, 20))
    epBoard.pieces[i] = epBoard.pieces[i].rotatePiece(gt_rotation[-1])

epImage = epBoard.toImage(CONTOUR_DISPLAY=False, BOUNDING_BOX=False)

# cv2.imshow('debug',epImage)
# cv2.waitKey()

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

theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea,
                                            theParams=ParamGrid(areaThresholdLower=1000, reorder=True))

# We will simulate the hand movement
theGridMea_src = copy.deepcopy(theGridMea)

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
    filename_list = glob.glob(cpath + f'/data/15pRotateSolverCalibrate_step*.png')
    for filename in filename_list:
        os.remove(filename)

finishFlag = False

# To demonstrate assembly process
i = 0
# To save calibration process
j = 0

theCalibrated = Board()

while 1:

    # Since we use the same instance in the simulator and the solver,
    # it will update automatically

    theSim.display(ID_DISPLAY=True)
    theSim.fig.suptitle(f'Step {i}', fontsize=20)
    plt.pause(1)

    thePrevImage = theSim.toImage(theImage=np.zeros_like(epImage).astype('uint8'), CONTOUR_DISPLAY=False,
                                  BOUNDING_BOX=False)
    if finishFlag:
        break
    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='order', STEP_WISE=False)

    finishFlag = theSim.takeAction(plan)

    theCurImage = theSim.toImage(theImage=np.zeros_like(epImage).astype('uint8'), CONTOUR_DISPLAY=False,
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
        theBoard_single = Arrangement.buildFrom_ImageAndMask(canvas, theMaskMea,
                                                             theParams=ParamPuzzle(areaThresholdLower=1000))
        theCalibrated.addPiece(theBoard_single.pieces[0])

        if saveMe:
            theCalibratedImage = theCalibrated.toImage(ID_DISPLAY=True)
            cv2.imwrite(cpath + f'/data/15pRotateSolverCalibrate_step{str(j).zfill(2)}.png',
                        cv2.cvtColor(thePrevImage, cv2.COLOR_RGB2BGR)
                        )
            j = j + 1
            cv2.imwrite(cpath + f'/data/15pRotateSolverCalibrate_step{str(j).zfill(2)}.png',
                        cv2.cvtColor(theCurImage, cv2.COLOR_RGB2BGR)
                        )
            j = j + 1
            cv2.imwrite(cpath + f'/data/15pRotateSolverCalibrate_step{str(j).zfill(2)}.png',
                        cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
                        )
            j = j + 1
            cv2.imwrite(cpath + f'/data/15pRotateSolverCalibrate_step{str(j).zfill(2)}.png',
                        cv2.cvtColor(theCalibratedImage, cv2.COLOR_RGB2BGR)
                        )
            j = j + 1

    i = i + 1

plt.ioff()
# plt.draw()

theCalibrated.display(ID_DISPLAY=True)

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/15pRotateSolverCalibrate.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/15pRotateSolverCalibrate_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)
plt.show()
#
# ============================ 15pRotateSolverCalibrate_basic ===========================
