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
from dataclasses import dataclass
import copy
import os
import cv2
import time
import matplotlib.pyplot as plt
import numpy as np
import glob

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.builder.board import Board
from puzzle.builder.arrangement import Arrangement
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift
from puzzle.utils.imageProcessing import preprocess_real_puzzle
from puzzle.solver.simple import Simple
from puzzle.simulator.planner import Planner, ParamPlanner
from puzzle.piece.template import Template, PieceStatus
# from puzzle.utils.puzzleProcessing import get_near_hand_puzzles

# ===== Helper Elements
#

@dataclass
class ParamRunner(ParamPlanner):
    areaThresholdLower: int = 1000
    areaThresholdUpper: int = 10000
    lengthThresholdLower: int = 1000
    areaThresh: int = 10
    BoudingboxThresh: tuple = (10,200)
    pieceConstructor: any  = Template
    pieceStatus: int = PieceStatus.MEASURED
    tauDist: int = 100
    hand_radius: int = 200
    tracking_life_thresh: int = 15

class RealSolver:
    def __init__(self, theParams=ParamRunner):

        # Todo: will decide later what other parameters needs to be figured out.
        self.params = theParams

        # Create empty manager & empty solver -> empty planner
        self.theManager = Manager(None, ManagerParms(matcher=Sift()))
        self.theSolver = Simple(None)
        self.thePlanner = Planner(self.theSolver, self.theManager, self.params)

        # Mainly for debug
        self.bMeasImage = None
        self.bTrackImage = None
        self.bTrackImage_SolID = None

    def setSolBoard(self, input):
        # Assuming the input is already in RGB

        if issubclass(type(input), Board):
            theArrangeSol = Arrangement(input)
        else:
            # Read the input image and template to build up the solution board.
            theMaskSol = preprocess_real_puzzle(input, areaThresh=self.params.areaThresh, BoudingboxThresh = self.params.BoudingboxThresh, WITH_AREA_THRESH=True, verbose=False)

            theArrangeSol = Arrangement.buildFrom_ImageAndMask(input, theMaskSol, self.params)

        # For theManager & theSolver
        self.theManager.solution = theArrangeSol

        # # Debug only
        # cv2.imshow('Debug', self.theManager.solution.toImage())
        # cv2.waitKey()

        self.theSolver.desired = theArrangeSol

        self.bSolImage = self.theManager.solution.toImage(theImage=np.zeros_like(input), BOUNDING_BOX=False, ID_DISPLAY=True)

        # For saving the status history
        self.thePlanner.status_history = dict()
        self.thePlanner.loc_history = dict()
        for i in range(self.theManager.solution.size()):
            self.thePlanner.status_history[i] = []
            self.thePlanner.loc_history[i] = []

    def progress(self):
        """
        @brief Check the status of the progress. (Return the ratio of the completed puzzle pieces)

        @note
        It is different from the one we used for the simulator case. There is less information we have for this progress.

        It is not always true when the matching is wrong/rotation is not correct. So there are some false positives.

        Returns:
            thePercentage: The progress.
        """

        # Check the measured board to get all the pieces location
        pLocs = self.thePlanner.manager.bMeas.pieceLocations()

        # Get match between measured board and the solution board, it may be incomplete
        # Then we have some matched pieces id: location
        pLocs_sol = {}
        for match in self.thePlanner.manager.pAssignments.items():
            pLocs_sol[match[1]] = pLocs[match[0]]

        # Check all the matched pieces
        # inPlace is just checking the top left corner for now. It is not 100% accurate.
        # Todo: We may add a solution board to the simulator to make it easier
        inPlace = self.thePlanner.manager.solution.piecesInPlace(pLocs_sol, tauDist=self.params.tauDist)

        val_list = [val for _, val in inPlace.items()]

        # # Debug only
        # print(val_list)

        thePercentage = '{:.1%}'.format(np.count_nonzero(val_list) / len(self.thePlanner.manager.solution.pieces))

        return thePercentage

    def process(self, theImageMea, visibleMask, hTracker_BEV):

        # Create an improcessor to obtain the mask.
        theMaskMea = preprocess_real_puzzle(theImageMea, areaThresh=self.params.areaThresh, BoudingboxThresh = self.params.BoudingboxThresh, WITH_AREA_THRESH=True, verbose=False)

        # Create an arrangement instance.
        theArrangeMea = Arrangement.buildFrom_ImageAndMask(theImageMea, theMaskMea,self.params)

        # Note that hTracker_BEV is (2,1) while our rLoc is (2, ). They have to be consistent.
        plan = self.thePlanner.process(theArrangeMea, rLoc_hand=hTracker_BEV, visibleMask=visibleMask, COMPLETE_PLAN=True, SAVED_PLAN=False, RUN_SOLVER=False)

        # with full size view
        self.bMeasImage = self.thePlanner.manager.bMeas.toImage(theImage=np.zeros_like(theImageMea), BOUNDING_BOX=False, ID_DISPLAY=True)
        self.bTrackImage = self.thePlanner.record['meaBoard'].toImage(theImage=np.zeros_like(theImageMea), BOUNDING_BOX=False, ID_DISPLAY=True)
        self.bTrackImage_SolID = self.thePlanner.displayBoard.toImage(theImage=np.zeros_like(theImageMea), BOUNDING_BOX=False, ID_DISPLAY=True)

        # # Note: It seems that this process is unnecessary to us as we have integrated the nearHand into pick & place interpretation
        # # hTracker_BEV is the trackpointer of the hand, (2, 1)
        # id_dict = get_near_hand_puzzles(hTracker_BEV, self.thePlanner.manager.bMeas.pieceLocations(), hand_radius=self.params.hand_radius)

        # Return action plan, the id number near hand (We assign it as None since we do not need it now), hand_activity
        return plan, None, self.thePlanner.hand_activity

#
# ========================== puzzle.runner =========================


if __name__ == "__main__":

    # Reproduce the results on the rosbag for debug purpose
    target_folder = '../../Surveillance/Surveillance/deployment/ROS/activity_multi_free_4'

    # Build up the puzzle solver
    configs_puzzleSolver = ParamRunner(
        areaThresholdLower=2000,
        areaThresholdUpper=8000,
        pieceConstructor=Template,
        lengthThresholdLower=1000,
        areaThresh=1000,
        BoudingboxThresh=(20, 100),
        tauDist=100,  # @< The radius distance determining if one piece is at the right position.
        hand_radius=200,  # @< The radius distance to the hand center determining the near-by pieces.
        tracking_life_thresh=15  # @< Tracking life for the pieces, it should be set according to the processing speed.
    )

    puzzleSolver = RealSolver(configs_puzzleSolver)

    for call_back_id in range(len(glob.glob(os.path.join(target_folder,'*.npy')))):

        if call_back_id ==33:
            print('Debug on the specific frame!')

        # Read
        postImg = cv2.imread(os.path.join(target_folder,f'{str(call_back_id).zfill(4)}_puzzle.png'))
        postImg = cv2.cvtColor(postImg, cv2.COLOR_BGR2RGB)
        visibleMask = cv2.imread(os.path.join(target_folder,f'{str(call_back_id).zfill(4)}_visibleMask.png'), -1)
        with open(os.path.join(target_folder,f'{str(call_back_id).zfill(4)}_hTracker.npy'),'rb') as f:
            hTracker_BEV = np.load(f, allow_pickle=True)
            if hTracker_BEV.size==1:
                hTracker_BEV = None

        # Todo: Currently, initialize the SolBoard with the very first frame.
        # We assume SolBoard is perfect (all the pieces have been recognized successfully)
        # We can hack it with something outside
        if call_back_id == 0:
            puzzleSolver.setSolBoard(postImg)
            print(f'Number of puzzle pieces registered in the solution board: {len(puzzleSolver.theManager.solution.pieces)}')

        # Plan not used yet
        plan, id_dict, hand_activity = puzzleSolver.process(postImg, visibleMask, hTracker_BEV)

        # # Note: It seems that this process is unnecessary to us as we have integrated the nearHand into pick & place interpretation
        # # @note there may be false negatives
        # print('ID from puzzle solver:', id_dict)
        print('Hand activity:', hand_activity)

        # Compute progress
        # Note that the solution board should be correct, otherwise it will fail.
        try:
            thePercent = puzzleSolver.progress()
            print(f"Progress: {thePercent}")
        except:
            print('Double check the solution board to make it right.')

        print(f"The processed test frame id: {call_back_id} ")
        print('\n\n')

        # Display
        cv2.imshow('bTrackImage_SolID', puzzleSolver.bTrackImage_SolID[:, :, ::-1])
        cv2.waitKey(1)