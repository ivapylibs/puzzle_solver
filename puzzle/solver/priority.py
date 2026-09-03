#============================ puzzle.solver.priority ===========================
#
# @package  puzzle.solver.priority
# @brief    Priority based solving. 

# Puzzlebot estimates the scene every k actions (sort, place, direct place).
# After scene estimation, performs a decision about which action to perform based on
# priorities.  After performing action, repeat the process.  Uses the look rate 
# to determine how often to re-assess priorities and switch actions.  Assumes 
# continuous solving with human, no tending.
#         
#
# @note The could might be wrong.  Priority tending was wrong in terms of how
#       the counter oeprated.  That means Priority is probably wrong unless it
#       was fixed.  Not sure taht happened.  Needs review. 2026/08/28 - PAV.
#
#============================ puzzle.solver.priority ===========================

import numpy as np
from dataclasses import dataclass

import rospy

from camera.base import ImageRGBD
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from puzzle.piece import PieceStatus

from puzzle.solver.base_v2 import Base, Action , CfgSolver, Mode

@dataclass
class Priority_State:
    """!
    @ingroup    Puzzle_Solving
    """
    DIRECT_PLACE = 0
    PLACE = 1
    SORT = 2
    END = 4
    operation: int
    num_pieces: int
    pc_list: any
    needs_look: bool = True

#============================ Priority_Solver ============================
#
class Priority_Solver(Base):
    """!
    @brief      Priority-driven approach to puzzle solving.
    @ingroup    Puzzle_Solving

    Each action type is assigned a score with the highest score winning.
    The scores are established from an action priority specification.
    The action types are: sort, place, direct place, and look at scene.
    The look at scene action includes a request for the human worker to
    move their hand out of the scene.
    """


    #============================= __init___ =============================
    #
    def __init__(self, cfgSolver: CfgSolver):
        """!
        @brief  Constructor for Priority Solver instance.

        @param[in]  cfgSolver   Configuration for the solver, including reference board and parameters.
        """
        super().__init__(cfgSolver)
        self.updatePriorities()
        self.zones_to_estimate = [Base.SOL, Base.UNORGANIZED] + [i for i in range(1, Base.NUM_ZONES + 1)]
    
    #============================ reset_solver ===========================
    #
    def reset_solver(self):
        """!
        @brief  Reset the solver state and mode.
        """
        super().reset_solver()
        self.state = Priority_State(
            operation=-1, num_pieces=0, pc_list=None, needs_look=True
        )
        self.mode = Mode.PERCEIVE
    
    #========================== updatePriorities =========================
    #
    def updatePriorities(self):
        """!
        @brief  Update priorities by snagging from ROS1 dynamic parameter server.
        """

        if rospy.has_param('sort_priority') and rospy.has_param('place_priority') \
                                            and rospy.has_param('direct_place_priority'):
            self.sort_pty           = rospy.get_param('sort_priority')
            self.place_pty          = rospy.get_param('place_priority')
            self.dir_place_pty      = rospy.get_param('direct_place_priority')
        else:
            rospy.logwarn('The priority paramaters are not set. Check ROS params.')
            self.sort_pty      = 0.33
            self.place_pty     = 0.33
            self.dir_place_pty = 0.33

        if rospy.has_param('look_rate'):
            self.PIECES_BEFORE_LOOK = rospy.get_param('look_rate')
        else:
            rospy.logerror('The look paramaters are not set. Check ROS params.')
            self.PIECES_BEFORE_LOOK = 5

    #========================== computePlacePlan =========================
    #
    def computePlacePlan(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """!
        @brief  Computes a custom place plan. 

        Starts by filling in pieces from most populated zones to least populated zones.
        """
        
        pieces_left = self.PIECES_BEFORE_LOOK
        plan        = []

        # Create set of measured boards that are based on zone placement of pieces.
        # There may be errors in the actual pieces placed within the zone, thus it
        # does nto serve as a strong prior.  Usually yes, but not if the worker
        # is mistaken or intentionally adversarial.  We need a scheme to correct.
        #
        all_zones = list(range(1, Base.NUM_ZONES + 1))
        for zone in all_zones:
            measured_board  = self.createMeasuredBoard(rgbd, scene, [zone])

            # Match against the reference board to reveal each observed
            # piece's intended zone without trusting its physical sort zone.
            zone_matches = self.performZoneMatch(measured_board)
            match_zones  = list(dict.fromkeys(zone_matches.values()))

            # This is the board used for planning: it includes only the
            # destination zones associated with pieces in measured_board.
            solution_board = self.createSolutionBoard(match_zones)
            plan.append((len(measured_board.pieces), measured_board, solution_board))

            # @note Looks like only attempts to solve measured_board elements.  What is
            #       going on here.  The code is weird.  Why did Nihit not document the
            #       workflow?? 2026/09/03 - PAV.
        
        # Sort most to least pieces
        plan.sort(key=lambda x: x[0], reverse=True)
        i = 0
        pieces = []
        while pieces_left > 0 and i < Base.NUM_ZONES:
            num_pieces, measured_board, solution_board = plan[i]
            if len(solution_board.pieces) == 0 or len(measured_board.pieces) == 0:
                # No pieces to place in this zone, skip
                i += 1
                continue
            self.performMatching(measured_board, solution_board)
            zone_pieces = self.getSequentialPlan(measured_board, solution_board, pieces_left)
            if len(zone_pieces) != 0:
                pieces.extend(zone_pieces)
                pieces_left -= len(zone_pieces)
            i += 1
        
        return pieces
            
            
    #========================== getNextOperation =========================
    #
    def getNextOperation(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """!
        @brief  Compute the composite priority of each operation and
                return the operation with highest composite priority.

        @param[in]  rgbd    RGBD image for the current scene.
        @param[in]  scene   Current scene state.
        
        @return     Tuple: List of pieces, Next operation state
        """

        # Retreive the priorities and relevant rates.
        self.updatePriorities()

        scores = []
        # Sort score
        # Number of pieces in unorganized zone
        # Create a measured board for unorganized region
        unorganized_measured_board = self.createMeasuredBoard(rgbd, scene, [Base.UNORGANIZED])
        unorganized_zone_pieces = len(unorganized_measured_board.pieces)
        sort_score = unorganized_zone_pieces * self.sort_pty
        scores.append(sort_score)
        
        # Place priority
        # Number of pieces in organized zone
        zones = [i for i in range(1, Base.NUM_ZONES + 1)]
        organized_measured_board = self.createMeasuredBoard(rgbd, scene, zones)
        organized_zone_pieces = len(organized_measured_board.pieces)
        
        place_score = organized_zone_pieces * self.place_pty
        scores.append(place_score)
        
        # Direct Place priority
        # Update solution estimate
        self.updateSolutionRegEstimate(scene)
        solution_board = self.createSolutionBoard(Base.UNORGANIZED)
        empty_spots = len(solution_board.pieces)

        direct_place_score = unorganized_zone_pieces * self.dir_place_pty
        scores.append(direct_place_score)
        
        # Pre-emptively finish if no empty spots in solution board
        if empty_spots == 0:
            return [], Priority_State.END
        # Pick the highest priority score
        print("Pieces in organized zones: ", organized_zone_pieces, " and in unorganized zone: ", unorganized_zone_pieces, " with empty spots in solution board: ", empty_spots)
        print("Scores: Sort: ", sort_score, " Place: ", place_score, " Direct Place: ", direct_place_score)
        i = np.argmax(scores)

        if scores[i] == 0:
            # No piece to perform highest priority task, keep looking
            return [], -1
        if i == 0:
            # Sort
            self.performMatching(unorganized_measured_board, solution_board)
            pieces = self.getSequentialPlan(unorganized_measured_board, solution_board, self.PIECES_BEFORE_LOOK)
            return pieces, Priority_State.SORT
        elif i == 1:
            # Place
            pieces = self.computePlacePlan(scene, rgbd)
            return pieces, Priority_State.PLACE
        else:
            # Direct Place
            self.performMatching(unorganized_measured_board, solution_board)
            pieces = self.getSequentialPlan(unorganized_measured_board, solution_board, self.PIECES_BEFORE_LOOK)
            return pieces, Priority_State.DIRECT_PLACE
            
    
    #=========================== getNextAction ===========================
    #
    def getNextAction(self, rgbd:ImageRGBD=None, scene:StatePuzzleScene=None):
        """!
        @brief  Return the next action to execute from current solver state.

        @param[in]  rgbd    RGBD image for the current scene.
        @param[in]  scene   Current scene state.
        
        @return     Action to take.

        @note  Uses a two-mode state machine:
          PERCEIVE - handles looking (scene estimation) and priority planning.
          ACT      - executes sort / place / direct-place operations.
                     When the piece list is exhausted, mode switches back to PERCEIVE.
        """

        # First ever call: initialize state and request a look.
        if self.state is None:
            action      = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            self.state  = Priority_State(
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

                # Scene received — compute priorities and plan.
                pc_list, operation = self.getNextOperation(scene, rgbd)
                print("Next operation: ", operation, " with pieces: ", len(pc_list))

                if operation == Priority_State.END:
                    print("Ending operations")
                    return Action(type=Action.END)

                if len(pc_list) == 0:
                    # No actionable pieces — re-look.
                    return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)

                # Plan ready — transition to ACT.
                self.state.needs_look  = False
                self.state.operation   = operation
                self.state.pc_list     = pc_list
                self.state.num_pieces  = 0
                self.mode              = Mode.ACT
                return Action(type=Action.NULL)

        # -----------------------------------------------------------------
        #  ACT mode: execute sort / place / direct-place from pc_list.
        # -----------------------------------------------------------------
        if self.mode == Mode.ACT:

            # Check exit condition: pieces exhausted.
            if self.state.num_pieces >= len(self.state.pc_list):
                self.mode               = Mode.PERCEIVE
                self.state.needs_look   = True
                return Action(type=Action.NULL)

            # Execute the next piece in the plan.
            if self.state.operation == Priority_State.SORT:
                meaPiece, solPiece, rot, tgt_zone = self.state.pc_list[self.state.num_pieces]
                self.state.num_pieces += 1

                if not self.isPieceThere(meaPiece, scene):
                    return Action(type=Action.NULL)

                return Action(type=Action.SORT,
                              measured_pc=meaPiece,
                              solution_pc=solPiece, rotation=rot,
                              tgt_zone=tgt_zone)
            else:
                # DIRECT_PLACE or PLACE
                meaPiece, solPiece, rot, _ = self.state.pc_list[self.state.num_pieces]
                self.state.num_pieces += 1

                if not self.isPieceThere(meaPiece, scene):
                    return Action(type=Action.NULL)

                return Action(type=Action.PICKPLACE,
                              measured_pc=meaPiece,
                              solution_pc=solPiece, rotation=rot)

        # Fallback — should not be reached.
        print("WARNING: getNextAction fell through. Requesting estimation.")
        self.mode = Mode.PERCEIVE
        self.state.needs_look = True
        return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            

#
#============================ puzzle.solver.priority ===========================
