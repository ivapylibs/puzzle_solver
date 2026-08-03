#============================== puzzle.solver.sort =============================
#
# @package  puzzle.solver.sort
# @brief    Robot only performs sort according to a specified policy.
#
# There are different approaches to sorting that align with different instructions
# that can be provided to a human worker.  Here, the next action to take is
# determined by such a policy applied to the current puzzle scene state.
#
#============================== puzzle.solver.sort =============================

import rospy
from puzzle.solver.base_v2 import Base, Action , CfgSolver
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from camera.base import ImageRGBD
import numpy as np
from puzzle.piece import PieceStatus
from dataclasses import dataclass
import cv2
import ivapy.display_cv as display

@dataclass
class Sort_State:
    """!
    @ingroup    Puzzle_Solving
    """
    SORT = 0
    OUTRIGHT = 1
    END = 2
    operation: int
    num_pieces: int
    pc_list: any


class Sort_Mode(Base):
    """!
    @brief      Sort only puzzle solving implementation.
    @ingroup    Puzzle_Solving
    """

    STRUCTURED_ORDERED      = 0
    STRUCTURED_UNORDERED    = 1
    UNSTRUCTURED_ORDERED    = 2
    UNSTRUCTURED_UNORDERED  = 3


    #============================= __init___ =============================
    #
    def __init__(self, cfgSolver: CfgSolver, policy: int):
        """!
        @brief  Constructor for Sort Solver instance.

        @param[in]  cfgSolver   Configuration for the solver, including reference board and parameters.
        """

        super().__init__(cfgSolver)
        self.policy = policy
        
        self.zones_to_estimate = [Base.SOL, Base.UNORGANIZED] + [i for i in range(1, Base.NUM_ZONES + 1)]

    #============================ getSortPlan ============================
    #
    def getSortPlan(self, rgbd: ImageRGBD=None, scene:StatePuzzleScene=None):
        """
        @brief  Return the sort plan with correct piece ordering for robot
                to execute. Based on the policy set initially
        
        Args:
            rgbd: Image details
            scene: Segmented scene information
        """

        # Create unorganized region board
        unorganized_measured_board = self.createMeasuredBoard(rgbd, scene, [Base.UNORGANIZED])
        # Create solution region board
        self.updateSolutionRegEstimate(scene)
        solution_board = self.createSolutionBoard(Base.UNORGANIZED)
        # Perform matching
        self.performMatching(unorganized_measured_board, solution_board)

        # Sort plan based on the 4 policies
        if self.policy == Sort_Mode.STRUCTURED_ORDERED:
            plans = [[], [], [], []]
            for key in unorganized_measured_board.pieces:
                pieceMea = unorganized_measured_board.pieces[key]
                solKey = self.correspondence_tracker.pAssignments[key]
                pieceSol = solution_board.pieces[solKey]
                rot = self.correspondence_tracker.pAssignments_rotation[key]
                zone = solution_board.zones[solKey]
                if zone != 0:
                    plans[zone - 1].append((pieceMea, pieceSol, rot, zone))
            # Sort each plan
            for i in range(Base.NUM_ZONES):
                plans[i].sort(key= lambda x: x[1].id)
            # Create master plan by merging the lists
            plan = []
            for zone_plan in plans:
                plan.extend(zone_plan)
        elif self.policy == Sort_Mode.STRUCTURED_UNORDERED:
            plan = []
            for key in unorganized_measured_board.pieces:
                pieceMea = unorganized_measured_board.pieces[key]
                solKey = self.correspondence_tracker.pAssignments[key]
                pieceSol = solution_board.pieces[solKey]
                rot = self.correspondence_tracker.pAssignments_rotation[key]
                zone = solution_board.zones[solKey]
                if zone != 0:
                    plan.append((pieceMea, pieceSol, rot, zone))
            
            # Sort top left to bottom right
            plan.sort(key=lambda x: x[1].id)
        elif self.policy == Sort_Mode.UNSTRUCTURED_ORDERED:
            plans = [[], [], [], []]
            for key in unorganized_measured_board.pieces:
                pieceMea = unorganized_measured_board.pieces[key]
                solKey = self.correspondence_tracker.pAssignments[key]
                pieceSol = solution_board.pieces[solKey]
                rot = self.correspondence_tracker.pAssignments_rotation[key]
                zone = solution_board.zones[solKey]
                if zone != 0:
                    plans[zone - 1].append((pieceMea, pieceSol, rot, zone))
            
            # Create master plan by merging the lists
            plan = []
            for zone_plan in plans:
                plan.extend(zone_plan)
        elif self.policy == Sort_Mode.UNSTRUCTURED_UNORDERED:
            plan = []
            for key in unorganized_measured_board.pieces:
                pieceMea = unorganized_measured_board.pieces[key]
                solKey = self.correspondence_tracker.pAssignments[key]
                pieceSol = solution_board.pieces[solKey]
                rot = self.correspondence_tracker.pAssignments_rotation[key]
                zone = solution_board.zones[solKey]
                if zone != 0:
                    plan.append((pieceMea, pieceSol, rot, zone))
        
        return plan


    #=========================== getNextAction ===========================
    #
    def getNextAction(self, rgbd:ImageRGBD=None, scene:StatePuzzleScene=None):
        """
        @brief  Return the next action to execute from current solver state.

        @param[in]  rgbd    RGBD image for the current scene.
        @param[in]  scene   Current scene state.
        
        @return     Action to take.
        """
        
        # Start by estimation
        if self.state is None:
            action = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            self.state = Sort_State(operation=Sort_State.OUTRIGHT, num_pieces=0, pc_list=None)
            return action
        
        previous = self.state
        nextOperation = -1
        nextNumPieces = -1
        nextPcList = None

        if previous.operation == Sort_State.OUTRIGHT:
            # Action was asking for estimation
            if scene is None or rgbd is None:
                print("ERROR: Expected scene information")
                return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            # Compute the priorities and action plan
            nextPcList = self.getSortPlan(rgbd, scene)
            action = Action(type=Action.NULL)
            # Simply move to next state to start sorting
            nextOperation = Sort_State.SORT
            nextNumPieces = 0
        elif previous.operation == Sort_State.SORT:
            if previous.num_pieces == len(previous.pc_list):
                # End of Operations
                action  = Action(type=Action.END)
                nextOperation = Sort_State.END
                nextNumPieces = -1
            else:
                meaPiece, solPiece, rot, tgt_zone = previous.pc_list[previous.num_pieces]
                action = Action(type=Action.SORT, \
                                measured_pc=meaPiece,\
                                solution_pc=solPiece, rotation=rot,
                                tgt_zone=tgt_zone)
                nextOperation = previous.operation
                nextNumPieces = previous.num_pieces + 1
        
        # Update state
        self.state.operation = nextOperation
        self.state.num_pieces = nextNumPieces
        if nextPcList is not None:
            self.state.pc_list = nextPcList
        # Send action
        return action


    #============================= display_plan ============================
    #
    def display_plan(self, Imeas, sortPlan, window_name="Sort Plan", doRotate=False):
        """!
        @brief  Display the sort plan via sort zone overlay on puzzle piece.

        @param[in]  IMeas       The measured image.
        @param[in]  sortPlan    Recovered plan.
        @param[in]  window_name Optional window name (default:"Sort Plan")

        @note   Quick and dirty solution given that I don't know code well.
                2027/07/28 - PAV.
        """

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        char_size = cv2.getTextSize("0", font, 0.15, 2)[0]

        ID_COLOR=(255, 255, 255)
        MK_COLOR=(255, 0, 0)

        I = Imeas.copy()
        for pplan in sortPlan:
            pmeas  = pplan[0]
            pmatch = pplan[1]
            ptxt = (int(pmeas.centroidLoc[0] - 3*char_size[0]) ,
                    int(pmeas.centroidLoc[1] + 2*char_size[1]) )
            pcnt = (int(pmatch.centroidLoc[0]),int(pmatch.centroidLoc[1]))

            zoneStr = str(pplan[3])
            cv2.putText(I, zoneStr, ptxt, font, font_scale, ID_COLOR, 2, cv2.LINE_AA)
            #cv2.drawMarker(I, pcnt, MK_COLOR, cv2.MARKER_CROSS, 10, 2)

        lenPlan = len(sortPlan)
        lenMeas = len(self.correspondence_tracker.boardMeasurement.pieces)
        lenSol  = len(self.correspondence_tracker.boardEstimate.pieces)
        cv2.putText(I, f"{lenPlan} of {lenMeas} / {lenSol}", (10, 15), 
                    font, font_scale, ID_COLOR, 1, cv2.LINE_AA)

        if doRotate:
          I = cv2.rotate(I, cv2.ROTATE_180)

        display.rgb(I, window_name=window_name)

    #============================= display_solution_hint ============================
    #
    def display_solution_hint(self, Imeas, sortPlan, window_name="Solution Match", doRotate=False):
        """!
        @brief  Display the solution as pick/place vector hints.  

        Can be messy if applied to too many puzzle pieces.  Either pieces should be
        organized in some manner, or fewer used (can be problematic).  For many
        piece, it is better to synthesize a virtual solve puzzle image and check
        that it looks good.

        @note   Unsure where virtual solve image creation is.  We used to have it
                but code has changed a lot. 2027/07/29 - PAV.

        @param[in]  IMeas       The measured image.
        @param[in]  sortPlan    Recovered plan.
        @param[in]  window_name Optional window name (default:"Solution Match")

        @note   Quick and dirty solution given that I don't know code well.
                2027/07/28 - PAV.
        """

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        char_size = cv2.getTextSize("0", font, 0.15, 2)[0]

        ID_COLOR=(255, 255, 255)
        MK_COLOR=(255, 0, 0)

        I = Imeas.copy()
        for pplan in sortPlan:
            pmeas  = pplan[0]       # Measured piece.
            pmatch = pplan[1]       # Estimated matched solution piece.

            mPos = ( int( pmeas.centroidLoc[0]) , int( pmeas.centroidLoc[1]) )
            sPos = ( int(pmatch.centroidLoc[0]) , int(pmatch.centroidLoc[1]) )

            zoneStr = str(pplan[3])
            cv2.arrowedLine(I, mPos, sPos, (0, 255, 0), 1, tipLength=0.03)

        if doRotate:
          I = cv2.rotate(I, cv2.ROTATE_180)

        display.rgb(I, window_name=window_name)
