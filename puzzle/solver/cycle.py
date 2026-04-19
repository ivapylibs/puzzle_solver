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

from puzzle.solver.base_v2 import Base, Action, CfgSolver
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from camera.base import ImageRGBD
import numpy as np
from puzzle.piece import PieceStatus

@dataclass
class Cycle_State:
    DIRECT_PLACE = 0
    PLACE = 1
    OUTRIGHT = 2
    OUTLEFT = 3
    operation: int
    zone: int



class Cycle_Place(Base):

    def __init__(self, cfgSolver: CfgSolver):
        super().__init__(cfgSolver)
     
    def getNextPiece(self, zone: int, scene: StatePuzzleScene, rgbd: ImageRGBD):
        """
        @brief  Get the next piece to place from the given zone.

        Args:
            zone: The zone from which to get the next piece.
            scene: The current state of the puzzle scene.
            rgbd: The RGBD image of the current scene.
        """
        # Update solution estimate
        self.updateSolutionRegEstimate(scene)
        # Create a measured board for unorganized region
        measured_board = self.createMeasuredBoard(rgbd, scene, zone)
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
        """
        @brief  Return the next action to execute from current solver state.

        Args:
            rgbd: Optional RGBD image for the current scene.
            scene: Optional current scene state.
        """
        # Start of the cycling place logic
        if self.state == None:
            # Start by asking it to estimate solution region
            action = Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])
            self.state = Cycle_State(operation=Cycle_State.OUTRIGHT, zone=-1)
            return action
        
        # State transitions
        # OUTRIGHT -> DIRECT place, -> outleft -> place -> outleft -> place -> ...
        
        previous = self.state
        nextZone = -1
        nextOperation = -1
           
        if previous.operation == Cycle_State.OUTRIGHT:
            #  action was asking robot to move out and get an estimate
            # of the solution region and unorganized region
            # NEXT: Do a direct place
            if scene is None:
                print("ERROR: Expected scene information after robot out of way in right.")
                return Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])
            
            meaPiece, solPiece, rot, complete = self.getNextPiece(Base.UNORGANIZED, scene, rgbd)

            # If no piece found in unorganized zone,
            # cycle to next state.
            if complete:
                print("Board is full.")
                action = Action(type=Action.END)
            elif meaPiece is None:
                print(f"No placeable piece in zone {Base.UNORGANIZED}")
                action = Action(type=Action.NULL)
            else:
                action = Action(type=Action.PICKPLACE, \
                                            measured_pc=meaPiece,\
                                                solution_pc=solPiece, rotation=rot)
            nextOperation = Cycle_State.DIRECT_PLACE
            nextZone = Base.UNORGANIZED   
        elif previous.operation == Cycle_State.DIRECT_PLACE:
            #  action was a direct place,
            # NEXT: we ask to go out left and get an estimate of the
            # solution region and zone to place from next.
            nextZone = 1
            action = Action(type=Action.OUTLEFT, estimate_zone=[Base.SOL, nextZone])
            nextOperation = Cycle_State.OUTLEFT
        elif previous.operation == Cycle_State.OUTLEFT:
            #  action was asking robot to move out left and get an estimate
            # of the solution region and current zone to place from
            # NEXT: Do a place from the current zone
            if scene is None:
                print("ERROR: Expected scene information after robot out of way in left.")
                return Action(type=Action.OUTLEFT, estimate_zone=[Base.SOL, previous.zone])
            
            meaPiece, solPiece, rot, complete = self.getNextPiece(previous.zone, scene, rgbd)
            # if no piece in current zone
            # cycle to next state
            if complete:
                print("Board is full")
                action = Action(type=Action.END)
            elif meaPiece is None:
                print(f"No placeable piece in zone {previous.zone}")
                action = Action(type=Action.NULL)
            else:
                action = Action(type=Action.PICKPLACE,\
                                                  measured_pc=meaPiece,\
                                                    solution_pc=solPiece, rotation=rot)
            nextOperation = Cycle_State.PLACE
            nextZone = previous.zone

        elif previous.operation == Cycle_State.PLACE:
            # action was a place from a zone, we want to continue placing from zones until all zones are done
            # NEXT: we ask to go out left and get an estimate of the solution region and zone to place from next, until all zones are done, then we ask for final estimate and place
            # else, we go to estimate unorganized zone.
            nextZone = previous.zone + 1
            if nextZone > Base.NUM_ZONES:
                action = Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])
                nextOperation = Cycle_State.OUTRIGHT
                nextZone = -1
            else:
                action = Action(type=Action.OUTLEFT, estimate_zone=[Base.SOL, previous.zone])
                nextOperation = Cycle_State.OUTLEFT
            
            
            
        # Update state
        self.state.operation = nextOperation
        self.state.zone = nextZone
        # Send action
        return action

