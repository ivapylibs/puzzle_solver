#!/usr/bin/python3
# ============================ realSolverNoCalibrate_basic ===========================
#
# @brief    Test script with command from the solver & with no calibration process. (real img)
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
import os

import cv2
import improcessor.basic as improcessor
import matplotlib.pyplot as plt

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.parser.fromSketch import FromSketch
from puzzle.piece.template import Template
from puzzle.simulator.agent_yunzhi import Agent
from puzzle.simulator.simTimeless_yunzhi import SimTimeLess
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

# ==[1] Read the source image and template.
#
fsize = 1
theImageSol = cv2.imread(cpath + '/../../testing/data/hand.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)
theImageSol = cv2.resize(theImageSol, (0, 0), fx=fsize, fy=fsize)

# ==[1.1] Create an improcessor to obtain the mask.
#

theMaskSol = preprocess_real_puzzle(theImageSol, cannyThresh=(50, 400))

theHand = Template.buildFromMaskAndImage(theMaskSol, theImageSol)

# ==[1.3] Display.
#
theImage = theHand.toImage()
# plt.imshow(theImage)
#
# plt.show()

init_agent_loc = [600, 50]
# agent = Agent.buildSphereAgent(100, (0, 0, 255), rLoc=init_agent_loc)

thePiece = Template.buildFromMaskAndImage(theMaskSol, theImageSol)
thePiece.setPlacement(r=init_agent_loc)
agent = Agent(thePiece)

# prepare the simulator
# param_sim = ParamST(
#     canvas_H=2000,
#     canvas_W=200
# )
simulator = SimTimeLess(epBoard, agent)

simulator.display()
plt.show()
#
# ============================ realSolverNoCalibrate_basic ===========================
