#============================ puzzle.solver.base_v2 ============================
##
# @package  puzzle.solver.base_v2
# @brief    Abstract base puzzle solver interface with explicit solver
#           state/action modes.
#
# @ingroup  Puzzle_Solving
#
# @author   Nihit Agarwal,         nagarwal90@gatech.edu
# @date     2026/04/13 [created]
#           2026/04/13 [modified]
#
#============================ puzzle.solver.base_v2 ============================

#===== Environment / Dependencies
#
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import cv2
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
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


#===== Helper Elements
#


@dataclass
class Action:
    """!
    @brief      Action instance for puzzle solver.
    @ingroup    Puzzle_Solving
    """
    PICKPLACE = 0       #< Perform a puzzle piece pick and place .
    OUTLEFT = 1         #< Go left and estimate
    OUTRIGHT = 2        #< Go right and estimate
    HELP = 3            #< Request help (with what? tending?)
    SORT = 4            #< Sort action.
    END = 5             #< Puzzle solving ended.
    NULL = -1           #< Unknown.
    
    type:           int                 #< Action type.
    help:           str = ""            #< Help string.
    tgt_zone:       int = -1            #< Target zone of action.
    estimate_zone:  List[int] = None    #< Unsure. List of estimated pieces in the zone?
    measured_pc:    Template = None     #< The measured pieces in the zone.
    solution_pc:    Template = None     #< Solution pieces (in the zone?).
    rotation:       float = None        #< Orientation to align measured w/solution. (??)


@dataclass
class CfgSolver:
    """!
    @brief      Configuration instance for puzzle solver.
    @ingroup    Puzzle_Solving
    """
    reference_board:    SolutionBoard               #< Reference board.
    display:            bool = False                #< Display approach.
    cfgMatching:        CfgCorrespondences = None   #< Correspondences.
    imRegions:          np.ndarray = None           #< Image regions specification (zones).
    puzzle_params:      CfgArrangement = None       #< Puzzle board parameters.

#
#============================ puzzle.solver.base_v2 ============================
#

class Base(ABC):
    """!
    @brief      Abstract base class for puzzle solver.
    @ingroup    Puzzle_Solving

    This class collects all of the functional parts needed to solve a
    puzzle.  A reference (solution) board specification, a matching strategy,
    a description of the piece sort zones, an estimate of the current board,
    and other gluing elements.  All together, these permit an agent to get
    a sense for the state of progress and plan out how to complete the puzzle.

    Naturally, there can be mistaked in the automation.
    """

    NUM_ZONES = 4
    UNORGANIZED = 6
    SOL = 5

    #============================= __init___ =============================
    #
    def __init__(self, cfgSolver: CfgSolver):
        """
        @brief  Constructor for the abstract base puzzle solver.

        @param[in]  cfgSolver   Configuration for the solver, including reference board and parameters.
        """
        self.display = cfgSolver.display                    #< Debug display
        self.reference_board = cfgSolver.reference_board    #< Solution reference 
        self.cfgMatching = cfgSolver.cfgMatching            #< Correspondences configs
        self.imRegions = cfgSolver.imRegions                #< Region definitions for puzzle zones
        self.puzzle_params = cfgSolver.puzzle_params        #< Puzzle-specific parameters for arrangement building
        
        self.state = None                                   #< Internal state.
        self.board_estimate = None                          #< Board estimate from state history.
        self.correspondence_tracker = None                  #< Puzzle piece correspondence tracker.

        self.correspondence_tracker = Correspondences(self.cfgMatching)

        self.verbose = 1                                    #< Verbosity level.
        
        # Initialize the estimate board to all pieces unsolved
        self.reset_estimate_board()

    #======================== reset_estimate_board =======================
    #
    # @todo Changing to reset_board_estimate reads better.
    #
    def reset_estimate_board(self):
        """!
        @brief: Sets the estimate board to all pieces unsolved,
                based on the solution board.
        """
        self.board_estimate = copy.deepcopy(self.reference_board)
        for key in self.board_estimate.pieces:
            self.board_estimate.pieces[key].setStatus(PieceStatus.GONE)
           
    #============================ reset_solver ===========================
    #
    def reset_solver(self):
        """!
        @brief: Rests the solver to begin with new puzzle (or start). 
                
        Resets the board estimate to all pieces unsolved, based on 
        the solution board.  Also resets the state.
        """
        self.reset_estimate_board()
        self.state = None

    #===================== updateSolutionRegEstimate =====================
    #
    def updateSolutionRegEstimate(self, scene:StatePuzzleScene):
        """!
        @brief  Review pieces in solution region and update estimate.

        @param[in]  scene   Puzzle scene state.
        """

        segIm       = scene.segIm
        soln_mask   = (self.imRegions == Base.SOL).astype(np.uint8)
        solutionReg = segIm * soln_mask

        # @todo Switch to generic ivapy display.  Not a fan of matplotlib for this. - 2026/08/02 - PAV.
        # DEBUG: Verify mask
        # plt.imshow(solutionReg)
        # plt.title("solution region mask")
        # plt.show()

        self.board_estimate.setPieceStatus(solutionReg)

        empty_spots = [piece.id for key, piece in self.board_estimate.pieces.items() if piece.status == PieceStatus.GONE]

        # DEBUG
        # print the empty spot ids
        if self.verbose:
          print(f"Empty spots: {empty_spots}")
    
    #======================== createMeasuredBoard ========================
    #
    def createMeasuredBoard(self, rgbd:ImageRGBD, scene:StatePuzzleScene, zones: List[int]):
        """!
        @brief  Take in raw inputs and create (generic) board measurement.

        @param[in]  rgbd    RGBD image.
        @param[in]  scene   Puzzle scene state.
        @param[in]  zones   Zone listing for assignment during board measurement.
        """

        segIm       = scene.segIm
        zone_mask   = np.isin(self.imRegions, zones)
        zoneReg     = segIm * zone_mask

        measured_board = Arrangement.buildFrom_ImageAndMask(rgbd.color,
                                                        zoneReg, 
                                                        theParams=self.puzzle_params)

        # DEBUG
        # plt.imshow(zoneReg)
        # plt.title(f"Measured region mask for zones {zones}")
        # plt.show()
        # print(f"Created measured board with {len(measured_board.pieces)} pieces")

        return measured_board
    
    #=========================== isBoardSolved ===========================
    #
    def isBoardSolved(self):
        """!
        @brief  Check if all puzzle pieces are in place.

        This check may not be a hard-core matching based check.  

        @return Boolean flag indicating all pieces placed or at least one missing.
        """

        all_placed = True       # Assume true.  If any missing, then false.
        for key in self.board_estimate.pieces:
            if self.board_estimate.pieces[key].status == PieceStatus.GONE:
                all_placed = False
                break
        return all_placed
    
    #======================== createSolutionBoard ========================
    #
    def createSolutionBoard(self, zone_to_match: int):
        """!
        @brief  Create a solution board based on the zone we want to match against
        """

        solution_board = board.SolutionBoard()
        if zone_to_match == Base.UNORGANIZED:
            solution_board.createBoardByStatus(self.board_estimate, PieceStatus.GONE)
        else:
            solution_board.createBoardByZone(self.board_estimate, zone_to_match, PieceStatus.GONE)

        # DEBUG
        # print(f"Created solution board with {len(solution_board.pieces)} pieces")

        return solution_board

    #========================== performMatching ==========================
    #
    def performMatching(self, measured_board:Arrangement, solution_board:SolutionBoard):
        """!
        @brief  Perform correspondence tracking to find a piece to direct place


        @param[in]  measured_board  Latest measured board.
        @param[in]  solution_board  Known solution board.
        """

        # @todo Why does this look like it gets instantiated each time?  Might be bad idea
        #       as it is a strong assumption on how correspondences work. 2026/08/02 - PAV.
        self.correspondence_tracker.setBoard(solution_board)
        self.correspondence_tracker.process(measured_board)

    #======================== checkIDplaceability =======================
    #
    def checkIDplaceability(self, solID):
        """!
        @brief  Checks if piece with solID can be placed must have an adjacent 
                placed piece, or should be on an edge/corner.

        @param[in]  solID   ID of piece to check for visibility / graspability.
        """

        # @note Looks like gridding is hard-coded to be #rows x 10 columns.  Oops
        #       Need to fix eventually. 2026/08/02 - PAV.
        up      = solID - 10
        down    = solID + 10
        right   = solID + 1
        left    = solID - 1

        neighbor_ids    = [up , down , right , left ]
        potential_ids   = [pc.id for pc in self.board_estimate.pieces.values()]

        # Find the id to key mapping for the estimate board
        id_to_key = {pc.id: key for key, pc in self.board_estimate.pieces.items()}
        found = False
        for neighbor in neighbor_ids:
            # Check for edge piece
            if solID % 10 == 0 or solID % 10 == 1 or solID <= 10 or solID >= 61:
                if self.verbose:
                    print("Edge piece detected, allowing placement")
                found = True
                break
            # Check if neighbor even exists in board estimate, if not , it is an edge piece
            if neighbor not in potential_ids:
                if self.verbose:
                    print("Neighbor not found, treating as edge piece")
                found = True
                break

            if self.board_estimate.pieces[id_to_key[neighbor]].status == PieceStatus.MEASURED:
                if self.verbose:
                    print(f"Found adjacent placed piece with ID {neighbor}, allowing placement")
                found = True
                break

        return found  
    
    #============================ isPieceThere ===========================
    #
    def isPieceThere(self, meaPiece, scene:StatePuzzleScene):
        """
        @brief  Check if the measured piece is actually present in the scene by analyzing the segmentation mask.

        @param[in]  meaPiece    Measured piece whose presence we want to verify.
        @param[in]  scene       Current puzzle scene containing the segmentation mask.
            
        @return True if the piece is likely present based on the segmentation mask, False otherwise.
        """
        segIm = scene.segIm
        tooHigh = scene.tooHighMat
        occlusion_mask = np.logical_or((segIm == 150), ( tooHigh > 0))
        mask = (segIm == 75).astype(np.float32)

        piece_rows, piece_cols = np.nonzero(meaPiece.y.mask)
        if piece_rows.size == 0:
            return False

        row_offset = meaPiece.y.pcorner[1]
        col_offset = meaPiece.y.pcorner[0]
        rows = piece_rows + row_offset
        cols = piece_cols + col_offset

        valid = (
            (rows >= 0)
            & (rows < mask.shape[0])
            & (cols >= 0)
            & (cols < mask.shape[1])
        )
        if not np.any(valid):
            return False

        rows = rows[valid]
        cols = cols[valid]

        pad = 2
        points = np.column_stack((cols, rows)).astype(np.int32)
        x, y, w, h = cv2.boundingRect(points)

        x0 = max(x - pad, 0)
        y0 = max(y - pad, 0)
        x1 = min(x + w + pad, mask.shape[1])
        y1 = min(y + h + pad, mask.shape[0])

        mask_crop = mask[y0:y1, x0:x1]
        kernel = np.ones((5, 5), dtype=np.float32) / 25.0
        filtered = cv2.filter2D(mask_crop, -1, kernel, borderType=cv2.BORDER_CONSTANT)

        score = np.mean(filtered[rows - y0, cols - x0])

        is_occluded = np.any(occlusion_mask[rows, cols])
        is_visible  = score > 0.5
        if self.verbose:
            print(f"Pieces | visible = {is_visible} ; vi-score {score} ; occlusion {is_occluded}")

        return is_visible and not is_occluded  # Assuming a threshold of 0.5 for presence
    
    #========================= getSequentialPlan =========================
    #
    def getSequentialPlan(self, measured_board, solution_board, numPieces):
        """
        @brief  Generate a sequential placement plan by sorting matched pieces by solution ID.
        
        @param[in]  measured_board  The board with measured/detected pieces.
        @param[in]  solution_board  The reference solution board to match against.
        @param[in]  numPieces       Number of pieces to include in the plan.
        
        @return List of tuples containing (measured_piece, solution_piece, rotation).
        """

        #print("===SSSS===")
        #print(self.correspondence_tracker.pAssignments)
        
        plan = []
        for key in list(measured_board.pieces):
            if key not in self.correspondence_tracker.pAssignments:
                continue
                # This condition will be hit if an unknown puzzle piece is forced
                # to be associated and there are more pieces than there should
                # be in the measured board (say 13 pieces to 12 pieces in solution).
                # Happens when in correct piece is taken out from puzzle.
                # 2026/08/06 - PAV.
            solKey = self.correspondence_tracker.pAssignments[key]
            solID = solution_board.pieces[solKey].id 
            plan.append((key, solID))

        # Sort by the ID
        plan.sort(key=lambda x: x[-1])
        pieces = []

        # Ensure that the first id is placeable and plan is non empty
        if len(plan) == 0:
            if self.verbose:
                print("Measured board is empty, skipping sequential plan")
            return pieces
        elif not self.checkIDplaceability(plan[0][1]):
            if self.verbose:
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
            
    #=========================== getNextAction ===========================
    #
    @abstractmethod
    def getNextAction(self):
        """
        @brief  Return the next action to execute from current solver state.

        @param[in]  thePlan     Optional desired action plan.
        """

        raise NotImplementedError()

#
#========================= puzzle.solver.base_v2 =========================
