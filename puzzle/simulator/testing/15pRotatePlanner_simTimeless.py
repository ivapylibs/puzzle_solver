#!/usr/bin/python3
# ============================ 15pRotatePlanner_simTimeless ===========================
#
# @brief    Test script with command from the planner & simTimeless simulator. (15p img)
#
# ============================ 15pRotatePlanner_simTimeless ===========================

#
# @file     15pRotatePlanner_simTimeless.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/11/25  [created]
#
# ============================ 15pRotatePlanner_simTimeless ===========================

# ==[0] Prep environment
import os

import cv2
import improcessor.basic as improcessor
import numpy as np

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.parser.fromSketch import FromSketch
from puzzle.piece.sift import Sift
from puzzle.piece.template import Template
from puzzle.simulator.hand import Hand
from puzzle.simulator.planner import Planner
from puzzle.simulator.plannerHand import PlannerHand
from puzzle.simulator.simTimeless import SimTimeLess
from puzzle.solver.simple import Simple
from puzzle.utils.imageProcessing import cropImage
from puzzle.utils.imageProcessing import preprocess_real_puzzle

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

np.random.seed(100)

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
for key in epBoard.pieces:
    gt_rotation.append(np.random.randint(0, 70))
    epBoard.pieces[key] = epBoard.pieces[key].rotatePiece(gt_rotation[-1])

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

# Todo: May need another instance
thePlannerHand = PlannerHand(theSolver, theManager)

# ==[4] Read the source image to create a hand.
#
fsize = 1
theImageSol = cv2.imread(cpath + '/../../testing/data/hand.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)
theImageSol = cv2.resize(theImageSol, (0, 0), fx=fsize, fy=fsize)

theMaskSol = preprocess_real_puzzle(theImageSol, cannyThresh=(50, 400))
theHandApperance = Template.buildFromMaskAndImage(theMaskSol, theImageSol)
init_agent_loc = [600, 50]

theHandApperance.setPlacement(r=init_agent_loc)
theHand = Hand(theHandApperance)

# ==[5] Create a simulator and display.
#
theSim = SimTimeLess(theSolver.current, theHand, thePlanner, thePlannerHand)
theSim.display()

#
# ============================ 15pRotatePlanner_simTimeless ===========================
