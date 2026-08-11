# ========================= puzzle.solver.cycle ==========================
#
# @class    puzzle.solver.cycle
#
# @brief    Cycle-based puzzle solver strategies. Robot moves to right
#           , estimates the scene, performs direct place, then moves left
#           estimates scene, performs place, estimates scene, and then
#           performs place .... for all zones. Then cycle continues.
#
# ========================= puzzle.solver.cycle ==========================

from dataclasses import dataclass

from puzzle.solver.base_v2 import Base, Action, CfgSolver, Mode
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from camera.base import ImageRGBD
import numpy as np
from puzzle.piece import PieceStatus

@dataclass
class Cycle_State:
    """!
    @brief      State for the cyclic placement solver.
    @ingroup    Puzzle_Solving
    """
    DIRECT_PLACE = 0
    PLACE = 1
    END = 4
    operation: int
    zone: int
    needs_look: bool = True



class Cycle_Place(Base):
    """!
    @brief      Cycle through direct placement and organized-zone placement.
    @ingroup    Puzzle_Solving
    """

    def __init__(self, cfgSolver: CfgSolver):
        """!
        @brief  Construct a cyclic placement solver.

        @param[in]  cfgSolver  Configuration for the solver.
        """
        super().__init__(cfgSolver)
     
    #============================ reset_solver ===========================
    #
    def reset_solver(self):
        """!
        @brief  Reset the solver state and mode.
        """
        super().reset_solver()
        self.state = Cycle_State(operation=-1, zone=-1, needs_look=True)
        self.mode = Mode.PERCEIVE

    def getNextPiece(self, zone: int, scene: StatePuzzleScene, rgbd: ImageRGBD):
        """!
        @brief  Get the next piece to place from the given zone.

        @param[in]  zone   Zone from which to get the next piece.
        @param[in]  scene  Current puzzle scene state.
        @param[in]  rgbd   RGBD image of the current scene.
        """
        # Update solution estimate
        self.updateSolutionRegEstimate(scene)
        # Create a measured board for unorganized region
        measured_board = self.createMeasuredBoard(rgbd, scene, [zone])
        # Create a solution board based on estimate for unorganized zone matching
        solution_board = self.createSolutionBoard(zone)
        # Peform correspondence tracking to find a piece to direct place
        self.performMatching(measured_board, solution_board)
        # Iterate through pieces in solution and find piece that shares at least
        # one edge with a MEASURED piece
        measured_board_key = None
        for key in measured_board.pieces:
            solKey = self.correspondence_tracker.pAssignments[key]
            solID = solution_board.pieces[solKey].id 
            # Hard coded based on num of pieces in a row in puzzle solution
            found = self.checkIDplaceability(solID)
            if found:
                measured_board_key = key
                break
        if measured_board_key is not None:
            # Can proceed to place the match
            solKey = self.correspondence_tracker.pAssignments[measured_board_key]
            meaPiece = measured_board.pieces[measured_board_key]
            solPiece = solution_board.pieces[solKey]
            rot = self.correspondence_tracker.pAssignments_rotation[measured_board_key]
            # Convert to rad
            rot = np.deg2rad(-1*rot)
            if np.isnan(rot):
                rot = 0
        else:
            meaPiece = None
            solPiece = None
            rot = None

        solved = self.isBoardSolved()
        
        return meaPiece, solPiece, rot, solved

        
    def getNextAction(self, rgbd:ImageRGBD=None, scene:StatePuzzleScene=None):
        """!
        @brief  Return the next action to execute from current solver state.

        @param[in]  rgbd   Optional RGBD image for the current scene.
        @param[in]  scene  Optional current puzzle scene state.

        @note  Uses a two-mode state machine:
          PERCEIVE - requests scene estimation (OUTRIGHT or OUTLEFT depending on zone).
          ACT      - evaluates piece placement for the current zone, then advances zone.
        """
        # First ever call: initialize state and request estimation
        if self.state is None:
            action = Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])
            self.state = Cycle_State(operation=-1, zone=-1, needs_look=True)
            self.mode = Mode.PERCEIVE
            return action

        # -----------------------------------------------------------------
        #  PERCEIVE mode: request scene estimation (OUTRIGHT or OUTLEFT)
        # -----------------------------------------------------------------
        if self.mode == Mode.PERCEIVE:
            if self.state.needs_look:
                if scene is None:
                    # Scene data not yet available — request estimation
                    if self.state.operation == Cycle_State.PLACE and self.state.zone > 0:
                        return Action(type=Action.OUTLEFT, estimate_zone=[Base.SOL, self.state.zone])
                    else:
                        return Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])

                # Scene received — transition to ACT.
                self.state.needs_look = False
                self.mode = Mode.ACT
                return Action(type=Action.NULL)

        # -----------------------------------------------------------------
        #  ACT mode: perform placement from current zone, then advance zone
        # -----------------------------------------------------------------
        if self.mode == Mode.ACT:
            current_zone = Base.UNORGANIZED if self.state.zone == -1 else self.state.zone
            meaPiece, solPiece, rot, complete = self.getNextPiece(current_zone, scene, rgbd)

            if complete:
                print("Board is full.")
                self.state.operation = Cycle_State.END
                return Action(type=Action.END)

            if meaPiece is None:
                print(f"No placeable piece in zone {current_zone}")
                act = Action(type=Action.NULL)
            else:
                act = Action(type=Action.PICKPLACE,
                             measured_pc=meaPiece,
                             solution_pc=solPiece, rotation=rot)

            # Advance to next cycle stage and request next look in PERCEIVE mode
            self.mode = Mode.PERCEIVE
            self.state.needs_look = True

            if self.state.zone == -1:
                # After DIRECT_PLACE (unorganized), move to zone 1 with OUTLEFT
                self.state.zone = 1
                self.state.operation = Cycle_State.PLACE
            else:
                # After PLACE from zone N, move to N + 1
                next_zone = self.state.zone + 1
                if next_zone > Base.NUM_ZONES:
                    # Done with all zones, cycle back to UNORGANIZED (OUTRIGHT)
                    self.state.zone = -1
                    self.state.operation = Cycle_State.DIRECT_PLACE
                else:
                    self.state.zone = next_zone
                    self.state.operation = Cycle_State.PLACE

            return act

        # Fallback
        print("WARNING: getNextAction fell through. Requesting estimation.")
        self.mode = Mode.PERCEIVE
        self.state.needs_look = True
        return Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])
