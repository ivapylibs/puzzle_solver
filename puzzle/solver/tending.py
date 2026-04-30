#=============== puzzle.solver.tending.py =======================
#
# @class    puzzle.solver.tending
#
# @brief    Tending puzzle solving strategy. Robot goes right, 
#           estimates scene, performs k direct
#           places, asks for human help. Then repeats.
# 
# ========================= puzzle.solver.tending ========================


import rospy
from puzzle.solver.base_v2 import Base, Action , CfgSolver
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from camera.base import ImageRGBD
import numpy as np
from puzzle.piece import PieceStatus
from dataclasses import dataclass


@dataclass
class Tending_State:
    DIRECT_PLACE = 0
    OUTRIGHT = 1
    ASKHELP = 2
    operation: int
    num_pieces: int
    pc_list: any

class Tending_Solve(Base):
    def __init__(self, cfgSolver: CfgSolver):
        super().__init__(cfgSolver)
        self.PIECES_BEFORE_TEND = rospy.get_param('tend_rate')
    

    def getNextPieces(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """
        @brief  Returns list of pieces to pick drop. Gives them in 
                order of ids as it will be top left to bottom right
                which in general always satisfies constraint of
                piece placement.
        Args:
            scene
            rgbd
        """
        # Update solution estimate
        self.updateSolutionRegEstimate(scene)
        # Create a measured board for unorganized region
        measured_board = self.createMeasuredBoard(rgbd, scene, [Base.UNORGANIZED])
        # Create a solution board based on estimate for unorganized zone matching
        solution_board = self.createSolutionBoard(Base.UNORGANIZED)
        # Pre-emptively end if solution board is filled
        if len(solution_board.pieces) == 0:
            return []
        # Peform correspondence tracking to find a piece to direct place
        self.performMatching(measured_board, solution_board)

        # Get the sequential (id-wise) piece placement plan
        pieces = self.getSequentialPlan(measured_board, solution_board, self.PIECES_BEFORE_TEND)
        
        return pieces



    def getNextAction(self, rgbd:ImageRGBD=None, scene:StatePuzzleScene=None):
        """
        @brief  Return the next action to execute from current solver state.

        Args:
            rgbd: Optional RGBD image for the current scene.
            scene: Optional current scene state.
        """

        # Start of the solving logic
        if self.state == None:
            # Start by estimating scene and solving
            # for first k pieces
            action = Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])
            self.state = Tending_State(operation=Tending_State.OUTRIGHT, num_pieces=0, pc_list=None)
            return action


        # State transitions
        #OUTRIGHT -> DIRECT_PLACE -> ASKHELP ->  OUTRIGHT ...

        previous = self.state
        nextOperation = -1
        nextNumPieces = -1
        nextPcList = None

        if previous.operation == Tending_State.OUTRIGHT:
            # action was asking robot to estimate unorganized
            # zone and solution zone
            if scene is None or rgbd is None:
                print("ERROR: Expected scene information")
                return Action(type=Action.OUTRIGHT, estimate_zone=[Base.SOL, Base.UNORGANIZED])

            nextPcList = self.getNextPieces(scene, rgbd)


            # End if empty
            if len(nextPcList) == 0:
                action  = Action(type=Action.END)
            else:
                # Simply move to next state
                action = Action(type=Action.NULL)
                nextOperation = Tending_State.DIRECT_PLACE
                nextNumPieces = 0
        elif previous.operation == Tending_State.DIRECT_PLACE:
            # previous action was an estimation followed with a place
            # this one is going to be a place / or go back to estimation
            if previous.num_pieces == len(previous.pc_list):
                # Ask for help
                action = Action(type=Action.HELP, help="Fix the solution")
                nextOperation = Tending_State.ASKHELP
                nextNumPieces = -1
            else:
                meaPiece, solPiece, rot, _ = previous.pc_list[previous.num_pieces]
                action = Action(type=Action.PICKPLACE, \
                                measured_pc=meaPiece,\
                                solution_pc=solPiece, rotation=rot)
                nextOperation = Tending_State.DIRECT_PLACE
                nextNumPieces = previous.num_pieces + 1
        elif previous.operation == Tending_State.ASKHELP:
            # last step was to ask help, 
            # Next: estimate board again
            action = Action(type=Action.NULL)
            nextOperation = Tending_State.OUTRIGHT
        
        # Update state
        self.state.operation = nextOperation
        self.state.num_pieces = nextNumPieces
        if nextPcList is not None:
            self.state.pc_list = nextPcList
        # Send action
        return action



                

   














# ========================= puzzle.solver.tending ========================