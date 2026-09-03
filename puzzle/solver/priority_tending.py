#======================== puzzle.solver.priority_tending =======================
##
# @package  puzzle.solver.priority_tending
# @brief    Priority based solving with tending state. 
#
# The robot estimates the scene every k actions (sort, place, direct place).
# After scene estimation, the observed puzzle layout and priority weighting
# determines which (k-)action group to execute.  Repeats this plan and
# execute process until the k actions have been implemented.  A moved puzzle
# piece will trigger an action skip.  Uses the look rate to determine how
# often to re-assess priorities and switch actions.  
#
# @ingroup  Puzzle_Solving
#
#======================== puzzle.solver.priority_tending =======================

import numpy as np
from dataclasses import dataclass

import rospy

from camera.base import ImageRGBD
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from puzzle.piece import PieceStatus

from puzzle.solver.base_v2 import Base, Action , CfgSolver, Mode
from puzzle.solver.priority import Priority_Solver

STR_START           = "Let's start solving."
STR_LOOK            = "Please let me see"
STR_ARRANGE_PIECES  = "Please adjust the pieces"
STR_END             = "We are done solving."

@dataclass
class Priority_Tending_State:
    """!
    @brief      State for priority-driven solving with periodic tending.
    @ingroup    Puzzle_Solving
    """
    DIRECT_PLACE = 0
    PLACE = 1
    SORT = 2
    END = 4
    operation: int
    num_pieces: int
    tend_counter: int
    pc_list: any
    needs_look: bool = True
    needs_tend: bool = False
    last_action_was_tend: bool = False

class Priority_Tending_Solver(Priority_Solver):
    """!
    @brief      Priority-driven solver with human tending action/mode added.
    @ingroup    Puzzle_Solving

    Augment Priority_Solver with a worker tending mode.  Not much changes
    except for the fact that the robot provides an opportunity for the 
    human worker to fix the puzzle pieces to improve their arrangement
    (in the sort zones or in the solution proper) before proceeding.
    """


    #============================= __init___ =============================
    #
    def __init__(self, cfgSolver: CfgSolver):
        """!
        @brief  Constructor for Priority Tending Solver instance.

        @param[in]  cfgSolver   Configuration for the solver, including reference board and parameters.
        """

        super().__init__(cfgSolver)
        self.PIECES_BEFORE_TEND = rospy.get_param('tend_rate')
        self.PIECES_BEFORE_LOOK = min(rospy.get_param('look_rate') , self.PIECES_BEFORE_TEND)
        # The robot can estimate when before leaving tend state.
        # The pieces before look is the minimum of (look_rate, tend_rate).

        
    #============================ reset_solver ===========================
    #
    def reset_solver(self):
        """!
        @brief  Reset the solver to begin with a new puzzle or start.
                
        Resets the board estimate to all pieces unsolved, based on 
        the solution board.  Also resets the state and mode.
        """
        super().reset_solver()
        self.state = Priority_Tending_State(
            operation=-1, num_pieces=0,
            tend_counter=self.PIECES_BEFORE_TEND,
            pc_list=None, needs_look=True, needs_tend=False,
            last_action_was_tend=False
        )
        self.mode = Mode.PERCEIVE

    #========================== getNextOperation =========================
    #
    def getNextOperation(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """!
        @brief  Compute the composite priority of each operation and
                return the operation with highest composite priority.

        @param[in]  rgbd    RGBD image for the current scene.
        @param[in]  scene   Current scene state.
        
        @return     Tuple: List of pieces, Next operation state

        @note   This code essentially duplicates the same code in priority solver
                which causes problems when there are mistakes.  Common elements
                should go into a common member function.  It complicates understanding
                but simplifies gross changes.  That's more important when developing
                and iterating towards final implementation. 2026/08/02 - PAV.
        """

        # Retreive relevant rates and compute the priority scores. 
        #
        self.updatePriorities()
        self.PIECES_BEFORE_TEND = rospy.get_param('tend_rate')
        self.PIECES_BEFORE_LOOK = min(rospy.get_param('look_rate') , self.PIECES_BEFORE_TEND)
        # @todo Overload updatePriorities to include tending.  Above two line go elsewhere.
        #       2026/08/28 - PAV.

        scores = []         # Empty out to populate.

        # @note Looks like minimum of tend and look will dominate.  How does that actually
        #       implement what is specified?  Will not interleave.  These two actions
        #       are fundamentally different.  Web priority interface miscontrues the
        #       values. 2026/08/02 - PAV.
        # @note Code changes since previous note better align parameters with expected
        #       implementation.  The earlier note may not be so relevant.  Need more
        #       playing with design to determine if important or not.  If not, should
        #       remove the notes.  Recommending removal at 2026/10/02 if nothing changes.
        #       2026/08/28 - PAV.

        # @todo For sure the computations of the priority scores should be centralized.
        #       Makes absolutely no sense to replicate same code across classes.
        #       2026/08/28 - PAV.

        # [1] Sort score: Based on number of pieces in unorganized zone.
        #
        unorganized_measured_board  = self.createMeasuredBoard(rgbd, scene, [Base.UNORGANIZED])
        unorganized_zone_pieces     = len(unorganized_measured_board.pieces)
        sort_score                  = unorganized_zone_pieces * self.sort_pty

        scores.append(sort_score)
        
        # [2] Place score: Based on number of pieces in organized zone
        #
        zones = [i for i in range(1, Base.NUM_ZONES + 1)]
        organized_measured_board = self.createMeasuredBoard(rgbd, scene, zones)
        organized_zone_pieces    = len(organized_measured_board.pieces)
        
        place_score = organized_zone_pieces * self.place_pty
        scores.append(place_score)
        
        # [3] Direct Place score: Also based on number of pieces in unorganized zone.
        #     Originally based on empty solution pieces, but the robot placement is
        #     messy and solution estimate does not always match unorganized zone
        #     cardinality.  
        #
        #     Furthermore, using only unsolved pieces does not factor
        #     in the fact that the pieces could be all sorted.  Then the system might
        #     trigger a direct place, but then find no pieces in the unorganized area
        #     and bonk out, leading to odd behavior.  That is the main reason for
        #     removing the dependency on solution area.
        #
        #  Code immediately below is not used in new direct place score.
        #  Kept in case needed elsewhere.
        self.updateSolutionRegEstimate(scene)
        solution_board = self.createSolutionBoard(Base.UNORGANIZED)
        empty_spots    = len(solution_board.pieces)

        direct_place_score = unorganized_zone_pieces * self.dir_place_pty
        scores.append(direct_place_score)
        
        # If no empty spots in solution board, consider problem solved.
        if empty_spots == 0:
            return [], Priority_Tending_State.END

        # Otherwise, pick the highest priority score
        print("Pieces in organized zones: ", organized_zone_pieces, \
              " and in unorganized zone:  ", unorganized_zone_pieces, \
              " with empty spots in solution board: ", empty_spots)
        print("Scores: Sort: ", sort_score, \
                    " Place: ", place_score, \
             " Direct Place: ", direct_place_score)
        i = np.argmax(scores)

        if scores[i] == 0:
            # No piece to perform highest priority task, keep looking
            # Really, this should not be happening, but good to catch.
            return [], -1

        if i == 0:              # Sort Actions.

            self.performMatching(unorganized_measured_board, solution_board)
            pieces = self.getSequentialPlan(unorganized_measured_board, solution_board, self.PIECES_BEFORE_LOOK)
            return pieces, Priority_Tending_State.SORT

        elif i == 1:            # Place Actions.

            pieces = self.computePlacePlan(scene, rgbd)
            return pieces, Priority_Tending_State.PLACE

        else:                   # Direct Place Actions.

            self.performMatching(unorganized_measured_board, solution_board)
            pieces = self.getSequentialPlan(unorganized_measured_board, solution_board, self.PIECES_BEFORE_LOOK)
            return pieces, Priority_Tending_State.DIRECT_PLACE
            
    #=========================== getNextAction ===========================
    #
    def getNextAction(self, rgbd:ImageRGBD=None, scene:StatePuzzleScene=None):
        """!
        @brief  Return the next action to execute from current solver state.
       
        @param[in]  rgbd    RGBD image for the current scene.
        @param[in]  scene   Current scene state.
        
        @return     Action to take.
        
        @note  Uses a two-mode state machine:
          PERCEIVE - handles tending (human help) and looking (scene estimation).
                     Tending is requested first so the human can fix pieces
                     before the robot re-estimates the scene.
          ACT      - executes sort / place / direct-place operations.
                     The tend counter decrements only after an actual action.
                     When it hits zero or the piece list is exhausted, mode
                     switches back to PERCEIVE.
        """

        # First ever call: initialize state and request a look.
        if self.state is None:
            action      = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            self.state  = Priority_Tending_State(
                operation=-1, num_pieces=0,
                tend_counter=self.PIECES_BEFORE_TEND,
                pc_list=None, needs_look=True, needs_tend=False
            )
            self.mode   = Mode.PERCEIVE
            return action

        # -----------------------------------------------------------------
        #  PERCEIVE mode: handle tending, then looking / planning.
        # -----------------------------------------------------------------
        if self.mode == Mode.PERCEIVE:

            # --- Solved: request final tend, then end --------------------
            if self.state.operation == Priority_Tending_State.END:
                if self.state.needs_tend:
                    self.state.needs_tend = False
                    return Action(type=Action.HELP, help=STR_ARRANGE_PIECES)
                print("Ending operations")
                return Action(type=Action.END)

            # --- Sub-step 1: Tending (if triggered) ----------------------
            if self.state.needs_tend:
                # Request human help, then reset counter and clear flag.
                self.state.needs_tend   = False
                self.state.tend_counter = self.PIECES_BEFORE_TEND
                self.state.needs_look   = True   # Must re-look after tend.
                self.state.last_action_was_tend = True
                return Action(type=Action.HELP, help=STR_ARRANGE_PIECES)

            # --- Sub-step 2: Look / plan ---------------------------------
            if self.state.needs_look:
                if scene is None or rgbd is None:
                    # Scene data not yet available — request estimation.
                    return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)

                # Scene received — compute priorities and plan.
                pc_list, operation = self.getNextOperation(scene, rgbd)
                print("Next operation: ", operation, " with pieces: ", len(pc_list))

                if operation == -1:
                    # No valid robot operation: request tending.  On the
                    # following call, the existing needs_tend branch emits
                    # HELP and resets the tending counter before re-looking.
                    self.state.needs_tend = True
                    self.state.needs_look = False
                    return Action(type=Action.NULL)

                if operation == Priority_Tending_State.END:
                    if self.state.last_action_was_tend:
                        print("Puzzle solved and tend was already performed — ending operations.")
                        return Action(type=Action.END)
                    else:
                        print("Puzzle solved — requesting final tend before ending.")
                        self.state.operation   = Priority_Tending_State.END
                        self.state.needs_tend  = True
                        self.state.needs_look  = False
                        return Action(type=Action.NULL)

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

            # Check exit conditions: pieces exhausted or tend counter hit zero.
            if self.state.num_pieces >= len(self.state.pc_list) or \
               self.state.tend_counter <= 0:
                self.mode               = Mode.PERCEIVE
                self.state.needs_look   = True
                self.state.needs_tend   = (self.state.tend_counter <= 0)
                return Action(type=Action.NULL)

            # Execute the next piece in the plan.
            if self.state.operation == Priority_Tending_State.SORT:
                meaPiece, solPiece, rot, tgt_zone = self.state.pc_list[self.state.num_pieces]
                self.state.num_pieces += 1

                if not self.isPieceThere(meaPiece, scene):
                    return Action(type=Action.NULL)

                self.state.tend_counter -= 1
                self.state.last_action_was_tend = False
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

                self.state.tend_counter -= 1
                self.state.last_action_was_tend = False
                return Action(type=Action.PICKPLACE,
                              measured_pc=meaPiece,
                              solution_pc=solPiece, rotation=rot)

        # Fallback — should not be reached.
        print("WARNING: getNextAction fell through. Requesting estimation.")
        self.mode = Mode.PERCEIVE
        self.state.needs_look = True
        return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            

#
#======================== puzzle.solver.priority_tending =======================
