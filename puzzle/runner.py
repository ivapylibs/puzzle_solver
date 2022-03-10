#!/usr/bin/python3
# ============================= puzzle.runner =============================
#
# @class    puzzle.runner
#
# @brief    A wrapper class for deployment in the real-world cases
#
# ============================= puzzle.runner =============================
#
# @file     runner.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/03/09 [created]
#
# ============================= puzzle.runner =============================


# ==[0] Prep environment
import copy
import os
import cv2
import time
import matplotlib.pyplot as plt
import numpy as np
import glob

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.builder.board import Board
from puzzle.builder.arrangement import Arrangement, ParamArrange
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift
from puzzle.utils.imageProcessing import preprocess_real_puzzle
from puzzle.solver.simple import Simple
from puzzle.simulator.planner import Planner

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

class RealSolver:
    def __init__(self, theParams=ParamArrange):

        # Todo: will decide later what other parameters needs to be figured out.
        self.params = theParams

        # Create empty manager & solver -> empty planner
        self.theManager = Manager(None, ManagerParms(matcher=Sift()))
        # bSolImage = theManager.solution.toImage(ID_DISPLAY=True)
        self.theSolver = Simple(None)
        self.thePlanner = Planner(self.theSolver, self.theManager, self.params)

        # Mainly for debug
        self.bMeasImage = None
        self.bTrackImage = None

    def setSolBoard(self, input):

        # Assuming the input is already in RGB

        if issubclass(type(input), Board):
            theArrangeSol = Arrangement(input)
        else:
            # Read the input image and template to build up the solution board.
            theMaskSol = preprocess_real_puzzle(input)
            theArrangeSol = Arrangement.buildFrom_ImageAndMask(input, theMaskSol,self.params)

        # For theManager & theSolver
        # Todo: Need double check
        self.theManager.solution = theArrangeSol
        self.theSolver.desired = theArrangeSol

    def process(self, theImageMea):

        # Create an improcessor to obtain the mask.
        theMaskMea = preprocess_real_puzzle(theImageMea, verbose=False)

        # Create an arrangement instance.
        theArrangeMea = Arrangement.buildFrom_ImageAndMask(theImageMea, theMaskMea,self.params)

        plan = self.thePlanner.process(theArrangeMea, COMPLETE_PLAN=True, SAVED_PLAN=False, RUN_SOLVER=False)

        # with full size view
        self.bMeasImage = self.thePlanner.manager.bMeas.toImage(theImage=np.zeros_like(theImageMea), BOUNDING_BOX=False, ID_DISPLAY=True)
        self.bTrackImage = self.thePlanner.record['meaBoard'].toImage(theImage=np.zeros_like(theImageMea), BOUNDING_BOX=False, ID_DISPLAY=True)

        return plan

#
# ========================== puzzle.runner =========================
