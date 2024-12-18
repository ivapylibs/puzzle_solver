#!/usr/bin/python3
# ============================= puzzle.runner =============================
#
# @package    puzzle.runner
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

from puzzle.piece.template import Template, PieceStatus
from puzzle.piece.sift import Sift
from puzzle.builder.board import Board
from puzzle.builder.arrangement import Arrangement
from puzzle.builder.interlocking import Interlocking
from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.clusters.byColor import ByColor, ParamColorCluster
from puzzle.manager import Manager, ManagerParms
from puzzle.utils.dataProcessing import closestNumber, kmeans_id_2d, agglomerativeclustering_id_2d
from puzzle.utils.imageProcessing import preprocess_real_puzzle
from puzzle.utils.puzzleProcessing import calibrate_real_puzzle
from puzzle.solver.simple import Simple
from puzzle.simulator.planner import Planner, ParamPlanner


# ===== Helper Elements
#

@dataclass
class ParamRunner(ParamPlanner):
    # Params to filter out the pieces
    areaThresholdLower: int = 1000
    areaThresholdUpper: int = 10000
    lengthThresholdLower: int = 1000
    BoudingboxThresh: tuple = (10, 200)

    # Params for basic puzzle info
    pieceConstructor: any = Template
    pieceStatus: int = PieceStatus.MEASURED

    # Other params
    tauDist: int = 100 # For in-place check
    hand_radius: int = 200
    tracking_life_thresh: int = 15
    solution_area: np.array = np.array([0,0,0,0])
    solution_area_center: np.array = np.array([0,0])
    solution_area_size: float = 0.0

    # Params for clustering (currently all for byColor)
    cluster_mode: str = 'number' # 'number' or 'threshold'
    cluster_number: int = 3 # For number mode
    cluster_threshold: float = 0.5 # For threshold mode
    score_method: str = 'label' # 'label' or 'histogram' criteria for clustering

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
        self.bSolImage = None
        self.bClusterImage = None

        # Mainly for calibration of the solution board
        self.theCalibrated = Board()
        self.thePrevImage = None

        # Clustering
        self.theClusterBoard = None


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

        # @note For our old random test cases, the solution board does not have to be a grid board.
        # That's why we choose Arrangement class at first.

        if issubclass(type(input), Board):
            theGridSol = Gridded(input)
        elif isinstance(input, str):
            assert os.path.exists(input), 'The input path does not exist.'
            theGridSol = Gridded.buildFromFile_Puzzle(input)
            # Todo: Currently, we only change the solution area if we reads from a file of board instance. The other options may need updates.

            self.params.solution_area = [closestNumber(theGridSol.boundingBox()[0][0], 30),
                                         closestNumber(theGridSol.boundingBox()[0][1], 30),
                                         closestNumber(theGridSol.boundingBox()[1][0], 30, lower=False),
                                         closestNumber(theGridSol.boundingBox()[1][1], 30, lower=False)]

            self.params.solution_area_center = np.array([(self.params.solution_area[0] + self.params.solution_area[2]) / 2, (self.params.solution_area[1] + self.params.solution_area[3]) / 2])
            self.params.solution_area_size = np.linalg.norm(self.params.solution_area_center-np.array([self.params.solution_area[0],self.params.solution_area[1]]))
        else:
            # Read the input image and template to build up the solution board.
            theMaskSol = preprocess_real_puzzle(img_input, areaThresholdLower=self.params.areaThresholdLower,
                                                areaThresholdUpper=self.params.areaThresholdUpper,
                                                BoudingboxThresh=self.params.BoudingboxThresh, WITH_AREA_THRESH=True,
                                                verbose=False)

            theGridSol = Gridded.buildFrom_ImageAndMask(img_input, theMaskSol, self.params)

        # For theManager & theSolver
        self.theManager.solution = theGridSol
        self.theSolver.desired = theGridSol

        # # Debug only
        # cv2.imshow('Debug', self.theManager.solution.toImage())
        # cv2.waitKey()

        # For saving the status history
        self.thePlanner.status_history = dict()
        self.thePlanner.loc_history = dict()
        for i in range(self.theManager.solution.size()):
            self.thePlanner.status_history[i] = []
            self.thePlanner.loc_history[i] = []

        # For debug
        self.bSolImage = self.theManager.solution.toImage(theImage=np.zeros_like(img_input), BOUNDING_BOX=False,
                                                          ID_DISPLAY=True)


    def setClusterBoard(self, target_board=None, mode='solution'):
        """
        @brief Set up the cluster board.
               Two ways to support clustering stuff:
               1) Use the solution board as the cluster board. You can track the progress in this way.
               2) Use any board. But only give a one-time suggestion.

        Args:
            mode: 'solution' or 'arbitrary', default is 'solution'.
            target_board: the reference board for clustering. Can be any board at any time (does not have to be the solution one)

        Returns:

        """

        if mode == 'solution':
            target_board = self.theManager.solution
        elif mode == 'arbitrary':
            assert target_board is not None, 'Please provide a board for clustering.'
        else:
            raise ValueError('The mode should be "solution" or "arbitrary".')

        if self.params.cluster_mode == 'number':
            self.theClusterBoard = ByColor(target_board, theParams=ParamColorCluster(cluster_num=self.params.cluster_number,
                                                                           cluster_mode='number'))
        elif self.params.cluster_mode == 'threshold':
            self.theClusterBoard = ByColor(target_board, theParams=ParamColorCluster(tauDist=self.params.cluster_threshold,
                                                                           cluster_mode='threshold'))
        else:
            raise ValueError('Invalid cluster mode.')

        self.theClusterBoard.process()

        # Initialize the cluster id
        for k, v in self.theClusterBoard.feaLabel_dict.items():
            self.theClusterBoard.pieces[k].cluster_id = v

        self.bClusterImage = self.theClusterBoard.toImage(theImage=np.zeros_like(self.bSolImage), BOUNDING_BOX=False,
                                                                ID_DISPLAY=True, ID_DISPLAY_OPTION=1)

    def clusterScore(self):
        """
        @brief Compute the clustering score of the current tracked board.

        Returns:
            The clustering score.
        """
        assert self.theClusterBoard is not None, 'Please set up the cluster board first.'

        # We only consider the pieces whose statuses are not GONE
        piece_loc_dict = {}
        for piece_id, piece in self.thePlanner.record['meaBoard'].pieces.items():
            if piece.status != PieceStatus.GONE:
                piece_loc_dict[piece_id] = piece.rLoc

        # Maybe incomplete compared to the reference
        # Hierarchical clustering based on the 2d locations of the tracked board
        # current_cluster_dict = agglomerativeclustering_id_2d(piece_loc_dict, self.params.cluster_number)
        current_cluster_dict = kmeans_id_2d(piece_loc_dict, self.params.cluster_number)

        # Debug only
        print(f"Cluster info: {current_cluster_dict}")
        print(f"Reference info: {self.theClusterBoard.feaLabel_dict}")
        score = self.theClusterBoard.score(current_cluster_dict, method=self.params.score_method)

        return '{:.1%}'.format(score)

    def progress(self, USE_MEASURED=True):
        """
        @brief Check the status of the progress. (Return the ratio of the completed puzzle pieces)

        Note:
        It is different from the one we used for the simulator case. There is less information we have for this progress.
        It is not always true when the matching is wrong/rotation is not correct. So there are some false positives.

        Args:
            USE_MEASURED: Use the measured board, otherwise use the tracked board.

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

                # When we work on tracked board, we need to remove those pieces whose statuses are GONE
                if self.thePlanner.record['meaBoard'].pieces[match[0]].status != PieceStatus.GONE:
                    pLocs_sol[match[1]] = pLocs[match[0]]

            # Check all the matched pieces
            # inPlace is just checking the top left corner for now. It is not 100% accurate.
            # Todo: We may add a solution board to the simulator to make it more concise
            inPlace = self.thePlanner.manager.solution.piecesInPlace(pLocs_sol, tauDist=self.params.tauDist)


            val_list = [val for _, val in inPlace.items()]

            # Debug only
            print(f"piece in-place info: {inPlace}")
            # print(val_list)

            thePercentage = '{:.1%}'.format(np.count_nonzero(val_list) / len(self.thePlanner.manager.solution.pieces))

        return thePercentage

    def process(self, theImageMea, visibleMask, hTracker_BEV, run_solver=True, planOnTrack=False, verbose=False):
        """
        @brief Process the input from the surveillance system.
                It first obtain the measured pieces, which is categorized into the solution area pieces and the working area pieces.
                Then the solving plan is obtained.

        Args:
            theImageMea: The input image (from the surveillance system).
            visibleMask: The mask image of the visible area (no hand/robot)(from the surveillance system).
            hTracker_BEV: The location of the hand in the BEV.
            run_solver: Run the solver or not.
            planOnTrack: Plan on the tracked board or not.
            verbose: If True, will display the detected measured pieces, from working or solution area.

        Returns:
            plan: The action plan.
        """

        # Todo: Move to somewhere else
        # We will adopt the frame difference idea in the solution area to get the pieces later, here we crop the solution area out first
        mask_working = np.ones(theImageMea.shape[:2],dtype='uint8')
        mask_working[self.params.solution_area[1]:self.params.solution_area[3], self.params.solution_area[0]:self.params.solution_area[2]] = 0
        mask_solution = 1 - mask_working

        theImageMea_solutionArea = cv2.bitwise_and(theImageMea, theImageMea, mask=mask_solution)

        theImageMea_work = cv2.bitwise_and(theImageMea, theImageMea, mask=mask_working)


        # Create an improcessor to obtain the mask.
        theMaskMea_work = preprocess_real_puzzle(theImageMea_work, areaThresholdLower=self.params.areaThresholdLower,
                                                areaThresholdUpper=self.params.areaThresholdUpper,
                                            BoudingboxThresh=self.params.BoudingboxThresh, WITH_AREA_THRESH=True,
                                            verbose=False)

        # Create an Interlocking instance.
        theInterMea_work = Interlocking.buildFrom_ImageAndMask(theImageMea_work, theMaskMea_work, self.params)
        theInterMea_work_img = theInterMea_work.toImage(theImage=np.zeros_like(theImageMea))

        theInterMea_all = copy.deepcopy(theInterMea_work)
        # Only update when the hand is far away or not visible for the solution area
        if hTracker_BEV is None or \
                np.linalg.norm(hTracker_BEV.reshape(2, -1) - self.params.solution_area_center.reshape(2, -1)) > self.params.hand_radius + self.params.solution_area_size + 50:

            self.thePrevImage, self.theCalibrated = calibrate_real_puzzle(theImageMea_solutionArea, self.thePrevImage, self.theCalibrated,
                                                                       params=self.params,
                                                                       option=0, verbose=verbose)

            # Combination of the pieces from the solution area and other working area
            # In fact we usually have only one piece added here (frame difference idea)
            for piece in self.theCalibrated.pieces.values():
                theInterMea_all.addPiece(piece)

        theInterMea_all_img = theInterMea_all.toImage(theImage=np.zeros_like(theImageMea))
        
        # visualize
        if verbose:
            print("Showing the debug info of the puzzle solver before the planning. Press any key on the last window to continue...")
            cv2.imshow("The work space measured pieces", theImageMea_work[:,:,::-1])
            cv2.imshow("The solution space measured pieces", theImageMea_solutionArea[:,:,::-1])
            cv2.imshow("The work space puzzle mask", theMaskMea_work)
            cv2.imshow("The work space board", theInterMea_work_img[:,:,::-1])
            cv2.imshow("The all space board", theInterMea_all_img[:,:,::-1])
            cv2.waitKey()
            cv2.destroyAllWindows()


        # Note that hTracker_BEV is (2,1) while our rLoc is (2, ). They have to be consistent. We have forced to reshape them inside planner.
        self.meaBoard = theInterMea_all
        plan = self.thePlanner.process(theInterMea_all, rLoc_hand=hTracker_BEV, theImageMea=theImageMea, visibleMask=visibleMask,
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

    def getMeaBoard(self):
        return self.meaBoard
    
    def getSolBoard(self):
        return self.thePlanner.manager.solution
    
    def getTrackBoard(self):
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
