#!/usr/bin/python3
# ============================ 15p_simTime ===========================
#
# @brief    The test script for the basic time-aware simulator.
#
# ============================ 15p_simTime ===========================

#
# @file     15p_simTime.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/11/25  [created]
#
# ============================ 15p_simTime ===========================

# ==[0] Prep environment
import os

import cv2
import improcessor.basic as improcessor

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.parser.fromSketch import FromSketch
from puzzle.piece.template import Template
from puzzle.simulator.hand import Hand
from puzzle.simulator.simTime import SimTime
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

# ==[3] Read the source image to create a hand.
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

# ==[4] Create a simulator and display.
#

simulator = SimTime(epBoard, theHand)

simulator.display()

#
# ============================ 15p_simTime ===========================
