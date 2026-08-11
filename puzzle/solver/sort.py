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
from puzzle.solver.base_v2 import Base, Action , CfgSolver, Mode
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
    @brief      State for the sort-only solver.
    @ingroup    Puzzle_Solving
    """
    SORT = 0
    END = 2
    operation: int
    num_pieces: int
    pc_list: any
    needs_look: bool = True


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

    #============================ reset_solver ===========================
    #
    def reset_solver(self):
        """!
        @brief  Reset the solver state and mode.
        """
        super().reset_solver()
        self.state = Sort_State(
            operation=-1, num_pieces=0, pc_list=None, needs_look=True
        )
        self.mode = Mode.PERCEIVE

    #============================ getSortPlan ============================
    #
    def getSortPlan(self, rgbd: ImageRGBD=None, scene:StatePuzzleScene=None):
        """!
        @brief  Return the sort plan with correct piece ordering for robot
                to execute. Based on the policy set initially
        
        @param[in]  rgbd   RGBD image for the current scene.
        @param[in]  scene  Segmented puzzle scene state.

        @return  Sort plan for the current solver policy.
        """

        # Create unorganized region board
        unorganized_measured_board = self.createMeasuredBoard(rgbd, scene, [Base.UNORGANIZED])
        # Create solution region board
        self.updateSolutionRegEstimate(scene)
        solution_board = self.createSolutionBoard(Base.UNORGANIZED)
        # Perform matching
        self.performMatching(unorganized_measured_board, solution_board)

        #DEBUG show matches.
        #print("===MMMM===")
        #print(self.correspondence_tracker.pAssignments)

        # Sort plan based on the 4 policies
        if self.policy == Sort_Mode.STRUCTURED_ORDERED:
            plans = [[], [], [], []]

            for key in unorganized_measured_board.pieces:

                if key not in self.correspondence_tracker.pAssignments:
                  continue
                  # This condition will be hit if an unknown puzzle piece is forced
                  # to be associated and there are more pieces than there should
                  # be in the measured board (say 13 pieces to 12 pieces in solution).
                  # Happens when in correct piece is taken out from puzzle.
                  # 2026/08/06 - PAV.

                pieceMea = unorganized_measured_board.pieces[key]
                solKey   = self.correspondence_tracker.pAssignments[key]
                pieceSol = solution_board.pieces[solKey]
                rot      = self.correspondence_tracker.pAssignments_rotation[key]
                zone     = solution_board.zones[solKey]

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
        """!
        @brief  Return the next action to execute from current solver state.

        @param[in]  rgbd    RGBD image for the current scene.
        @param[in]  scene   Current scene state.
        
        @return     Action to take.

        @note  Uses a two-mode state machine:
          PERCEIVE - handles looking (scene estimation) and sort planning.
          ACT      - executes sort operations for pieces in the sort plan.
                     When all pieces are sorted, ends operations.
        """
        
        # First ever call: initialize state and request a look.
        if self.state is None:
            action      = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            self.state  = Sort_State(
                operation=-1, num_pieces=0, pc_list=None, needs_look=True
            )
            self.mode   = Mode.PERCEIVE
            return action

        # -----------------------------------------------------------------
        #  PERCEIVE mode: handle looking / planning.
        # -----------------------------------------------------------------
        if self.mode == Mode.PERCEIVE:
            if self.state.needs_look:
                if scene is None or rgbd is None:
                    # Scene data not yet available — request estimation.
                    return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)

                # Scene received — compute sort plan.
                pc_list = self.getSortPlan(rgbd, scene)
                print("Sort plan computed with pieces: ", len(pc_list))

                if len(pc_list) == 0:
                    # No pieces to sort — end operations.
                    print("No pieces to sort, ending operations.")
                    self.state.operation = Sort_State.END
                    return Action(type=Action.END)

                # Plan ready — transition to ACT.
                self.state.needs_look  = False
                self.state.operation   = Sort_State.SORT
                self.state.pc_list     = pc_list
                self.state.num_pieces  = 0
                self.mode              = Mode.ACT
                return Action(type=Action.NULL)

        # -----------------------------------------------------------------
        #  ACT mode: execute sort operations from pc_list.
        # -----------------------------------------------------------------
        if self.mode == Mode.ACT:

            # Check exit condition: all sorted.
            if self.state.num_pieces >= len(self.state.pc_list):
                print("Completed sort plan, ending operations.")
                self.state.operation = Sort_State.END
                return Action(type=Action.END)

            # Execute next sort action.
            meaPiece, solPiece, rot, tgt_zone = self.state.pc_list[self.state.num_pieces]
            self.state.num_pieces += 1

            return Action(type=Action.SORT,
                          measured_pc=meaPiece,
                          solution_pc=solPiece, rotation=rot,
                          tgt_zone=tgt_zone)

        # Fallback — should not be reached.
        print("WARNING: getNextAction fell through. Requesting estimation.")
        self.mode = Mode.PERCEIVE
        self.state.needs_look = True
        return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)


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
