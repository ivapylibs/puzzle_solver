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
from tkinter import Grid
import cv2
import time
import matplotlib.pyplot as plt
import numpy as np
import glob

from puzzle.builder.board import Board
from puzzle.builder.arrangement import Arrangement
from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift
from puzzle.utils.dataProcessing import closestNumber
from puzzle.utils.imageProcessing import preprocess_real_puzzle
from puzzle.utils.puzzleProcessing import calibrate_real_puzzle
from puzzle.solver.simple import Simple
from puzzle.simulator.planner import Planner, ParamPlanner
from puzzle.piece.template import Template, PieceStatus


# ===== Helper Elements
#

@dataclass
class ParamRunner(ParamPlanner):
    areaThresholdLower: int = 1000
    areaThresholdUpper: int = 10000
    lengthThresholdLower: int = 1000
    BoudingboxThresh: tuple = (10, 200)
    pieceConstructor: any = Template
    pieceStatus: int = PieceStatus.MEASURED
    tauDist: int = 100
    hand_radius: int = 200
    tracking_life_thresh: int = 15
    solution_area: np.array = np.array([0,0,0,0])
    solution_area_center: np.array = np.array([0,0])
    solution_area_size: np.array = np.array([0,0])

class RealSolver:
    def __init__(self, theParams=ParamRunner):

        # Todo: will decide later what other parameters needs to be figured out.
        self.params = theParams

        # Create empty manager & empty solver -> empty planner
        self.theManager = Manager(None, ManagerParms(matcher=Sift()))
        self.theSolver = Simple(None)
        self.thePlanner = Planner(self.theSolver, self.theManager, self.params)

        # Current measure board
        self.meaBoard = None

        # Mainly for debug
        self.bMeasImage = None
        self.bTrackImage = None
        self.bTrackImage_SolID = None

        # Mainly for calibration of the solution board
        self.theCalibrated = Board()

        # For solution board calibration & solution area
        self.thePrevImage = None

    def calibrate(self, theImageMea, visibleMask, hTracker_BEV, option=1, verbose=False):
        """
        @brief  To obtain the solution board from a rosbag for calibration.

        Args:
            theImageMea: The input image (from the surveillance system).
            visibleMask: The mask image of the visible area (no hand/robot)(from the surveillance system).
            hTracker_BEV: The location of the hand in the BEV.
            option: The option 0 is to assemble the puzzle while option 1 is to disassemble the puzzle

        """

        # Only work when hand is not present
        if hTracker_BEV is None:
            self.thePrevImage, self.theCalibrated = calibrate_real_puzzle(theImageMea, self.thePrevImage, self.theCalibrated, params=self.params, option=option)

    def setSolBoard(self, img_input, input=None):
        """
        @brief Set up the solution board.

        Args:
            input: A board/path/raw image.
        """
        solParams = ParamGrid(
            gcMethod="rectangle"
        )

        if issubclass(type(input), Board):
            theArrangeSol = Gridded(input, solParams)
        elif isinstance(input, str):
            theArrangeSol = Gridded.buildFromFile_Puzzle(input, solParams)
            # Currently, we only change the solution area if we have already calibrated it

            self.params.solution_area = [closestNumber(theArrangeSol.boundingBox()[0][0], 30), closestNumber(theArrangeSol.boundingBox()[0][1],30), \
                                         closestNumber(theArrangeSol.boundingBox()[1][0], 30, lower=False), closestNumber(theArrangeSol.boundingBox()[1][1], 30, lower=False)]

            self.params.solution_area_center = np.array([(self.params.solution_area[0] + self.params.solution_area[2]) / 2, (self.params.solution_area[1] + self.params.solution_area[3]) / 2])
            self.params.solution_area_size = np.linalg.norm(self.params.solution_area_center-np.array([self.params.solution_area[0],self.params.solution_area[1]]))
        else:
            # Read the input image and template to build up the solution board.
            theMaskSol = preprocess_real_puzzle(img_input, areaThresholdLower=self.params.areaThresholdLower,
                                                areaThresholdUpper=self.params.areaThresholdUpper,
                                                BoudingboxThresh=self.params.BoudingboxThresh, WITH_AREA_THRESH=True,
                                                verbose=False)

            theArrangeSol = Gridded.buildFrom_ImageAndMask(img_input, theMaskSol, self.params)

        # For theManager & theSolver
        self.theManager.solution = theArrangeSol

        # # Debug only
        # cv2.imshow('Debug', self.theManager.solution.toImage())
        # cv2.waitKey()

        self.theSolver.desired = theArrangeSol

        self.bSolImage = self.theManager.solution.toImage(theImage=np.zeros_like(img_input), BOUNDING_BOX=False,
                                                          ID_DISPLAY=True)

        # For saving the status history
        self.thePlanner.status_history = dict()
        self.thePlanner.loc_history = dict()
        for i in range(self.theManager.solution.size()):
            self.thePlanner.status_history[i] = []
            self.thePlanner.loc_history[i] = []

    def progress(self, USE_MEASURED=True):
        """
        @brief Check the status of the progress. (Return the ratio of the completed puzzle pieces)

        Note:
        It is different from the one we used for the simulator case. There is less information we have for this progress.
        It is not always true when the matching is wrong/rotation is not correct. So there are some false positives.

        Args:
            USE_MEASURED: Use the measured board or use the tracked board.

        Returns:
            thePercentage: The progress.
        """

        if USE_MEASURED:
            manager = self.thePlanner.manager
            # Check the measured board to get all the pieces location
            pLocs = manager.bMeas.pieceLocations()

            # Get match between measured board and the solution board, it may be incomplete
            # Then we have some matched pieces id: location
            pLocs_sol = {}
            for match in manager.pAssignments.items():
                pLocs_sol[match[1]] = pLocs[match[0]]

            # Check all the matched pieces
            # inPlace is just checking the top left corner for now. It is not 100% accurate.
            # Todo: We may add a solution board to the simulator to make it more concise
            inPlace = manager.solution.piecesInPlace(pLocs_sol, tauDist=self.params.tauDist)

            val_list = [val for _, val in inPlace.items()]

            # # Debug only
            # print(val_list)

            thePercentage = '{:.1%}'.format(np.count_nonzero(val_list) / len(manager.solution.pieces))

        else:
            pLocs = self.thePlanner.record['meaBoard'].pieceLocations()

            # Get match between measured board and the solution board, it may be incomplete
            # Then we have some matched pieces id: location
            pLocs_sol = {}
            for match in self.thePlanner.record['match'].items():
                pLocs_sol[match[1]] = pLocs[match[0]]

            # Check all the matched pieces
            # inPlace is just checking the top left corner for now. It is not 100% accurate.
            # Todo: We may add a solution board to the simulator to make it more concise
            inPlace = self.thePlanner.manager.solution.piecesInPlace(pLocs_sol, tauDist=self.params.tauDist)

            val_list = [val for _, val in inPlace.items()]

            # # Debug only
            # print(val_list)

            thePercentage = '{:.1%}'.format(np.count_nonzero(val_list) / len(self.thePlanner.manager.solution.pieces))

        return thePercentage

    def process(self, theImageMea, visibleMask, hTracker_BEV, run_solver=True, verbose=False, debug=False, planOnTrack=False):
        """
        @brief Process the input from the surveillance system.
                It first obtain the measured pieces, which is categorized into the solution area pieces and the working area pieces.
                Then the solving plan is obtained.

        Args:
            theImageMea: The input image (from the surveillance system).
            visibleMask: The mask image of the visible area (no hand/robot)(from the surveillance system).
            hTracker_BEV: The location of the hand in the BEV.
            debug: If True, will display the detected measured pieces, from working or solution area.

        Returns:
            plan: The action plan.
        """

        # Todo: Move to somewhere else
        # We will adopt the frame difference idea in the solution area
        mask_working = np.ones(theImageMea.shape[:2],dtype='uint8')
        mask_working[self.params.solution_area[1]:self.params.solution_area[3], self.params.solution_area[0]:self.params.solution_area[2]] = 0
        mask_solution = 1 - mask_working

        theImageMea_solutionArea = cv2.bitwise_and(theImageMea, theImageMea, mask=mask_solution)


        theImageMea = cv2.bitwise_and(theImageMea, theImageMea, mask=mask_working)


        # Create an improcessor to obtain the mask.
        theMaskMea = preprocess_real_puzzle(theImageMea, areaThresholdLower=self.params.areaThresholdLower,
                                                areaThresholdUpper=self.params.areaThresholdUpper,
                                            BoudingboxThresh=self.params.BoudingboxThresh, WITH_AREA_THRESH=True,
                                            verbose=False)

        # Create an arrangement instance.
        theArrangeMea = Gridded.buildFrom_ImageAndMask(theImageMea, theMaskMea, self.params)
        theArrangeMea_work_img = theArrangeMea.toImage()

        # Only update when the hand is far away or not visible
        if hTracker_BEV is None or \
                np.linalg.norm(hTracker_BEV.reshape(2, -1) - self.params.solution_area_center.reshape(2, -1)) > self.params.hand_radius + self.params.solution_area_size + 50:

            self.thePrevImage, self.theCalibrated = calibrate_real_puzzle(theImageMea_solutionArea, self.thePrevImage, self.theCalibrated,
                                                                       params=self.params,
                                                                       option=0, verbose=verbose)

            # Combination of the pieces from the solution area and other working area
            for piece in self.theCalibrated.pieces.values():
                theArrangeMea.addPiece(piece)
        theArrangeMea_all_img = theArrangeMea.toImage()
        
        # visualize
        if debug:
            print("Showing the debug info of the puzzle solver before the planning. Press any key on the last window to continue...")
            cv2.imshow("THe work space measured pieces", theImageMea[:,:,::-1])
            cv2.imshow("THe solution space measured pieces", theImageMea_solutionArea[:,:,::-1])
            cv2.imshow("The work space puzzle mask", theMaskMea)
            cv2.imshow("The work space board", theArrangeMea_work_img[:,:,::-1])
            cv2.imshow("The all space board", theArrangeMea_all_img[:,:,::-1])
            cv2.waitKey()
            cv2.destroyAllWindows()


        # Note that hTracker_BEV is (2,1) while our rLoc is (2, ). They have to be consistent.
        self.meaBoard = theArrangeMea
        plan = self.thePlanner.process(theArrangeMea, rLoc_hand=hTracker_BEV, visibleMask=visibleMask,
                                       COMPLETE_PLAN=True, SAVED_PLAN=False, RUN_SOLVER=run_solver, planOnTrack=planOnTrack)

        # with full size view
        self.bMeasImage = self.thePlanner.manager.bMeas.toImage(theImage=np.zeros_like(theImageMea), BOUNDING_BOX=False,
                                                                ID_DISPLAY=True)
        self.bTrackImage = self.thePlanner.record['meaBoard'].toImage(theImage=np.zeros_like(theImageMea),
                                                                      BOUNDING_BOX=False, ID_DISPLAY=True)
        self.bTrackImage_SolID = self.thePlanner.displayBoard.toImage(theImage=np.zeros_like(theImageMea),
                                                                      BOUNDING_BOX=False, ID_DISPLAY=True)

        # Return action plan
        return plan

    def getMeaBoard(self)->Gridded:
        return self.meaBoard
    
    def getSolBoard(self)->Gridded:
        return self.thePlanner.manager.solution
    
    def getTrackBoard(self)->Gridded:
        return self.thePlanner.record['meaBoard']


#
# ========================== puzzle.runner =========================


if __name__ == "__main__":

    # Reproduce the results on the rosbag for debug purpose

    # Basic Settings

    # target_folder = '../../Surveillance/Surveillance/deployment/ROS/activity_multi_free_4'
    # puzzle_solver_mode = 0

    # target_folder = '../../Surveillance/Surveillance/deployment/ROS/tangled_1_sol'
    # puzzle_solver_mode = 1

    target_folder = '../../Surveillance/Surveillance/deployment/ROS/tangled_1_work'
    puzzle_solver_SolBoard = '../../Surveillance/Surveillance/deployment/ROS/caliSolBoard.obj'
    puzzle_solver_mode = 2

    # verbose = True
    verbose = False

    # Build up the puzzle solver
    configs_puzzleSolver = ParamRunner(
        areaThresholdLower=1000,
        areaThresholdUpper=8000,
        pieceConstructor=Template,
        lengthThresholdLower=1000,
        BoudingboxThresh=(20, 100),
        tauDist=100,  # @< The radius distance determining if one piece is at the right position.
        hand_radius=200,  # @< The radius distance to the hand center determining the near-by pieces.
        tracking_life_thresh=15  # @< Tracking life for the pieces, it should be set according to the processing speed.
    )

    puzzleSolver = RealSolver(configs_puzzleSolver)

    npy_file_list = glob.glob(os.path.join(target_folder, '*.npy'))
    npy_file_list.sort()

    for npy_file in npy_file_list:

        call_back_id = int(os.path.basename(npy_file)[:4])

        # if call_back_id == 81:
        #     print('Debug on the specific frame!')
        #     verbose=True

        # Read
        postImg = cv2.imread(os.path.join(target_folder, f'{str(call_back_id).zfill(4)}_puzzle.png'))
        postImg = cv2.cvtColor(postImg, cv2.COLOR_BGR2RGB)
        visibleMask = cv2.imread(os.path.join(target_folder, f'{str(call_back_id).zfill(4)}_visibleMask.png'), -1)
        with open(os.path.join(target_folder, f'{str(call_back_id).zfill(4)}_hTracker.npy'), 'rb') as f:
            hTracker_BEV = np.load(f, allow_pickle=True)
            if hTracker_BEV.size == 1:
                hTracker_BEV = None

        if puzzle_solver_mode == 0:
            if call_back_id == 0:
                puzzleSolver.setSolBoard(postImg)
                print(
                    f'Number of puzzle pieces registered in the solution board: {len(puzzleSolver.theManager.solution.pieces)}')
            # Plan not used yet
            plan = puzzleSolver.process(postImg, visibleMask, hTracker_BEV)
        elif puzzle_solver_mode == 1:
            plan = puzzleSolver.calibrate(postImg, visibleMask, hTracker_BEV, verbose=verbose)
        elif puzzle_solver_mode == 2:
            if call_back_id == 0:
                puzzleSolver.setSolBoard(postImg, puzzle_solver_SolBoard)
                print(
                    f'Number of puzzle pieces registered in the solution board: {len(puzzleSolver.theManager.solution.pieces)}')

            # Plan not used yet
            plan = puzzleSolver.process(postImg, visibleMask, hTracker_BEV, verbose=verbose)

        if puzzle_solver_mode!=1:
            # Compute progress
            # Note that the solution board should be correct, otherwise it will fail.
            try:
                thePercent = puzzleSolver.progress(USE_MEASURED=False)
                print(f"Progress: {thePercent}")
            except:
                print('Double check the solution board to make it right.')

        print(f"The processed test frame id: {call_back_id} ")
        print('\n\n')

        # Display
        if puzzle_solver_mode != 1:
            cv2.imshow('bMeaImage', puzzleSolver.bMeasImage[:, :, ::-1])
            cv2.imshow('bTrackImage', puzzleSolver.bTrackImage[:, :, ::-1])
            cv2.imshow('bTrackImage_SolID', puzzleSolver.bTrackImage_SolID[:, :, ::-1])
            cv2.imshow('bSolImage', puzzleSolver.bSolImage[:, :, ::-1])
            cv2.waitKey(1)

    if puzzle_solver_mode == 1:
        cv2.imshow('debug_solBoard', puzzleSolver.theCalibrated.toImage(ID_DISPLAY=True, COLOR=[0,255,0])[:, :, ::-1])

    # Stop here for double-check
    cv2.waitKey()
