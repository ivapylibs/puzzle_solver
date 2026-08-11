#============================ puzzle.solver.tending ============================
#
# @package  puzzle.solver.tending
# @brief    Tending puzzle solving strategy. Robot goes right, 
#           estimates scene, performs k direct
#           places, asks for human help. Then repeats.
# 
# ========================= puzzle.solver.tending ========================

import numpy as np
from dataclasses import dataclass

import rospy


from camera.base import ImageRGBD
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from puzzle.piece import PieceStatus

from puzzle.solver.base_v2 import Base, Action , CfgSolver, Mode


@dataclass
class Tending_State:
    """!
    @brief      State for direct placement with periodic human tending.
    @ingroup    Puzzle_Solving
    """

    DIRECT_PLACE = 0
    END          = 3
    operation: int
    num_pieces: int
    tend_counter: int
    pc_list: any
    needs_look: bool = True
    needs_tend: bool = False
    last_action_was_tend: bool = False

class Tending_Solve(Base):
    """!
    @brief      Standard approach to puzzle solving w/periodic tending.
    @ingroup    Puzzle_Solving
    """

    #============================= __init___ =============================
    #
    def __init__(self, cfgSolver: CfgSolver):
        """!
        @brief  Constructor for Solver w/Tending instance.

        @param[in]  cfgSolver   Configuration for the solver, including reference board and parameters.
        """

        super().__init__(cfgSolver)

        self.PIECES_BEFORE_TEND = rospy.get_param('tend_rate')

    #============================ reset_solver ===========================
    #
    def reset_solver(self):
        """!
        @brief  Reset the solver state and mode.
        """
        super().reset_solver()
        self.state = Tending_State(
            operation=-1, num_pieces=0,
            tend_counter=self.PIECES_BEFORE_TEND,
            pc_list=None, needs_look=True, needs_tend=False,
            last_action_was_tend=False
        )
        self.mode = Mode.PERCEIVE
    

    #=========================== getNextPieces ===========================
    #
    def getNextPieces(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """!
        @brief  Returns list of pieces to pick drop. Gives them in 
                order of ids as it will be top left to bottom right
                which in general always satisfies constraint of
                piece placement.

        @param[in]  rgbd    RGBD image for the current scene.
        @param[in]  scene   Current scene state.
        
        @return     Pieces to solve as plan.
        """

        # Update solution estimate
        # Create a measured board for unorganized region
        # Create a solution board based on estimate for unorganized zone matching
        self.updateSolutionRegEstimate(scene)

        measured_board = self.createMeasuredBoard(rgbd, scene, [Base.UNORGANIZED])
        solution_board = self.createSolutionBoard(Base.UNORGANIZED)

        # Pre-emptively end if solution board is filled
        if len(solution_board.pieces) == 0:
            return []

        # Peform correspondence tracking to find a piece to direct place
        # Get the sequential (id-wise) piece placement plan up to next tend request.
        self.performMatching(measured_board, solution_board)
        pieces = self.getSequentialPlan(measured_board, solution_board, self.PIECES_BEFORE_TEND)
        
        return pieces


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
          ACT      - executes direct-place operations.
                     The tend counter decrements only after an actual action.
                     When it hits zero or the piece list is exhausted, mode
                     switches back to PERCEIVE.
        """

        # First ever call: initialize state and request a look.
        if self.state is None:
            action      = Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])
            self.state  = Tending_State(
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
            if self.state.operation == Tending_State.END:
                if self.state.needs_tend:
                    self.state.needs_tend = False
                    return Action(type=Action.HELP, help="Fix the solution")
                print("Ending operations")
                return Action(type=Action.END)

            # --- Sub-step 1: Tending (if triggered) ----------------------
            if self.state.needs_tend:
                # Request human help, then reset counter and clear flag.
                self.state.needs_tend   = False
                self.state.tend_counter = self.PIECES_BEFORE_TEND
                self.state.needs_look   = True   # Must re-look after tend.
                self.state.last_action_was_tend = True
                return Action(type=Action.HELP, help="Fix the solution")

            # --- Sub-step 2: Look / plan ---------------------------------
            if self.state.needs_look:
                if scene is None or rgbd is None:
                    # Scene data not yet available — request estimation.
                    return Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])

                # Scene received — compute next pieces.
                pc_list = self.getNextPieces(scene, rgbd)

                if len(pc_list) == 0:
                    if self.state.last_action_was_tend:
                        print("Puzzle solved and tend was already performed — ending operations.")
                        self.state.operation = Tending_State.END
                        return Action(type=Action.END)
                    else:
                        print("Puzzle solved — requesting final tend before ending.")
                        self.state.operation  = Tending_State.END
                        self.state.needs_tend = True
                        self.state.needs_look = False
                        return Action(type=Action.NULL)

                # Plan ready — transition to ACT.
                self.state.needs_look  = False
                self.state.operation   = Tending_State.DIRECT_PLACE
                self.state.pc_list     = pc_list
                self.state.num_pieces  = 0
                self.mode              = Mode.ACT
                return Action(type=Action.NULL)

        # -----------------------------------------------------------------
        #  ACT mode: execute direct-place from pc_list.
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
        return Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])

#
#============================ puzzle.solver.tending ============================
