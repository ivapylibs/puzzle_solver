# ========================= puzzle.solver.base_v2 ========================
#
# @class    puzzle.solver.base_v2
#
# @brief    Abstract base puzzle solver interface with explicit solver
#           state/action modes.
#
# ========================= puzzle.solver.base_v2 ========================
#
# @file     base_v2.py
#
# @author   Nihit Agarwal,         nagarwal90@gatech.edu
# @date     2026/04/13 [created]
#           2026/04/13 [modified]
#
# ========================= puzzle.solver.base_v2 ========================

# ===== Environment / Dependencies
#
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import numpy as np
import copy

from Surveillance.layers.PuzzleScene import StatePuzzleScene
from camera.base import ImageRGBD
from puzzle.board import SolutionBoard
from puzzle.board import CfgCorrespondences, Correspondences
from puzzle.builder.arrangement import Arrangement, CfgArrangement
from puzzle import board
from puzzle.piece import PieceStatus
from puzzle.piece import Template
import matplotlib.pyplot as plt

# ===== Helper Elements
#


@dataclass
class Action:
    PICKPLACE = 0
    OUTLEFT = 1 # Go left and estimate
    OUTRIGHT = 2 # Go right and estimate
    HELP = 3
    SORT = 4
    END = 5
    NULL = -1
    
    type: int
    help: str = ""
    tgt_zone: int = -1
    estimate_zone: List[int] = None
    measured_pc: Template = None
    solution_pc: Template = None
    rotation: float = None


@dataclass
class CfgSolver:
    reference_board: SolutionBoard
    display: bool = False
    cfgMatching: CfgCorrespondences = None
    imRegions: np.ndarray = None
    puzzle_params: CfgArrangement = None

#
# ========================= puzzle.solver.base_v2 ========================
#

class Base(ABC):
    NUM_ZONES = 4
    UNORGANIZED = 6
    SOL = 5

    def __init__(self, cfgSolver: CfgSolver):
        """
        @brief  Constructor for the abstract base puzzle solver.

        Args:
            cfgSolver: Configuration for the solver, including reference board and parameters.
        """
        # Debug display
        self.display = cfgSolver.display
        # Solution Reference to compare against
        self.reference_board = cfgSolver.reference_board
        # Correspondences configs
        self.cfgMatching = cfgSolver.cfgMatching
        # Image region definitions for zones
        self.imRegions = cfgSolver.imRegions
        # Puzzle-specific parameters for arrangement building
        self.puzzle_params = cfgSolver.puzzle_params
        
        # Internal state variables
        self.state = None
        self.board_estimate = None
        self.correspondence_tracker = None
        
        # Initialize the estimate board to all pieces unsolved
        self.reset_estimate_board()

    def reset_estimate_board(self):
        """!
        @brief: Sets the estimate board to all pieces unsolved,
                based on the solution board.
        """
        self.board_estimate = copy.deepcopy(self.reference_board)
        for key in self.board_estimate.pieces:
            self.board_estimate.pieces[key].setStatus(PieceStatus.GONE)
           
    def updateSolutionRegEstimate(self, scene:StatePuzzleScene):
        segIm = scene.segIm
        soln_mask = (self.imRegions == Base.SOL).astype(np.uint8)
        solutionReg = segIm * soln_mask
        # Verify mask
        # plt.imshow(solutionReg)
        # plt.title("solution region mask")
        # plt.show()
        self.board_estimate.setPieceStatus(solutionReg)
    
    def createMeasuredBoard(self, rgbd:ImageRGBD, scene:StatePuzzleScene, zones: List[int]):
        segIm = scene.segIm
        zone_mask = np.isin(self.imRegions, zones)
        zoneReg = segIm * zone_mask
        plt.imshow(zoneReg)
        plt.title(f"Measured region mask for zones {zones}")
        plt.show()
        measured_board = Arrangement.buildFrom_ImageAndMask(rgbd.color,
                                                        zoneReg, 
                                                        theParams=self.puzzle_params)
        # print(f"Created measured board with {len(measured_board.pieces)} pieces")
        return measured_board
    
    def isBoardSolved(self):
        # Check if all pieces are placed
        all_placed = True
        for key in self.board_estimate.pieces:
            if self.board_estimate.pieces[key].status == PieceStatus.GONE:
                all_placed = False
                break
        return all_placed
    
    def createSolutionBoard(self, zone_to_match: int):
        # Create a solution board based on the zone we want to match against
        solution_board = board.SolutionBoard()
        if zone_to_match == Base.UNORGANIZED:
            solution_board.createBoardByStatus(self.board_estimate, PieceStatus.GONE)
        else:
            solution_board.createBoardByZone(self.board_estimate, zone_to_match, PieceStatus.GONE)
        # print(f"Created solution board with {len(solution_board.pieces)} pieces")

        return solution_board

    def performMatching(self, measured_board:Arrangement, solution_board:SolutionBoard):
        # Perform correspondence tracking to find a piece to direct place
        self.correspondence_tracker = Correspondences(self.cfgMatching, solution_board)
        self.correspondence_tracker.process(measured_board)

    def checkIDplaceability(self, solID):
        # checks if piece with solID can be placed
        # must have an adjacent placed piece, or should
        # be on an edge/corner

        up = solID - 10
        down = solID + 10
        right = solID + 1
        left = solID - 1
        neighbors = [up - 1, down - 1, right - 1, left - 1]
        found = False
        for neighbor in neighbors:
            # Check for edge piece
            if solID % 10 == 0 or solID % 10 == 1 or solID <= 10 or solID >= 61:
                found = True
                break
            # Check if neighbor even exists in board estimate, if not , it is an edge piece
            if neighbor not in self.board_estimate.pieces:
                found = True
                break

            if self.board_estimate.pieces[neighbor].status == PieceStatus.MEASURED:
                found = True
                break

        return found  
    
    def getSequentialPlan(self, measured_board, solution_board, numPieces):
        """
        @brief  Generate a sequential placement plan by sorting matched pieces by solution ID.
        
        Args:
            measured_board: The board with measured/detected pieces.
            solution_board: The reference solution board to match against.
            numPieces: Number of pieces to include in the plan.
        
        Returns:
            List of tuples containing (measured_piece, solution_piece, rotation).
        """
        
        plan = []
        for key in list(measured_board.pieces):
            solKey = self.correspondence_tracker.pAssignments[key]
            solID = solution_board.pieces[solKey].id 
            plan.append((key, solID))
        # Sort by the ID
        plan.sort(key=lambda x: x[-1])
        pieces = []
        # Ensure that the first id is placeable and plan is non empty
        if len(plan) == 0 or not self.checkIDplaceability(plan[0][1]):
            print("First piece in plan not placeable, skipping sequential plan")
            return pieces
        
        for item in plan:
            meaKey, solID = item
            # Can proceed to place the match
            solKey = self.correspondence_tracker.pAssignments[meaKey]
            meaPiece = measured_board.pieces[meaKey]
            solPiece = solution_board.pieces[solKey]
            rot = self.correspondence_tracker.pAssignments_rotation[meaKey]
            tgt_zone = solution_board.zones[solKey]
            # Convert to rad
            rot = np.deg2rad(-1*rot)
            if np.isnan(rot):
                rot = 0
            pieces.append((meaPiece, solPiece, rot, tgt_zone))
        return pieces[:numPieces]
            
    @abstractmethod
    def getNextAction(self):
        """
        @brief  Return the next action to execute from current solver state.

        Args:
            thePlan: Optional desired action plan.
        """

        raise NotImplementedError()

#
# ========================= puzzle.solver.base_v2 ========================
