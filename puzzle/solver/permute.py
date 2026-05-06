#=============== puzzle.solver.permute.py =====================
#
# @class    puzzle.solver.permute.py
# @brief    Permute receives a sequence of operations
#           it iterates through them and attempts to create
#           a plan accordingly till it hits look_rate.
#           then , it continues from there. Also wraps around.
#
#           
#
#
#
#=============== puzzle.solver.permute.py =====================

import rospy
from puzzle.solver.base_v2 import Base, Action , CfgSolver
from puzzle.solver.priority import Priority_Solver
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from camera.base import ImageRGBD
import numpy as np
from puzzle.piece import PieceStatus
from dataclasses import dataclass


@dataclass
class Permute_State:
    DIRECT_PLACE = 0
    PLACE = 1
    SORT = 2
    OUTRIGHT = 3
    END = 4
    ASKHELP = 5
    operation: int
    op_list: any # List of next operations
    num_pieces: int
    tend_counter: int
    pc_list: any # List of next pieces
    operation_index: int  # index within the larger order


'''
Core Tasks:
2. Have a counter that iterates through these once the operation is carried out.
3. getNextOperation will simply gauge how far ahead we can go from counter and com
press into a single plan- min of left operations in the plan, and look rate.
'''
class Permute_Solver(Priority_Solver):
    def __init__(self, cfgSolver: CfgSolver, permutation=[]):
        super().__init__(cfgSolver)
        self.PIECES_BEFORE_TEND = rospy.get_param('tend_rate')

        # Logically, the robot can estimate when in ask for help state
        # so, the pices before look is the minimum of (look_rate, tend_rate)
        self.PIECES_BEFORE_LOOK = min(self.PIECES_BEFORE_LOOK, self.PIECES_BEFORE_TEND)

        self.order = permutation
        
        
    def getNextOperation(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """
        @brief  Compute the composite priority of each operation and
                return the operation with highest composite priority.
        Args:
            rgbd:  RGBD image for the current scene.
            scene:  current scene state.
        
        Returns: 
            List of pieces, List of OPERATIONS
        
        """
        # Retreive the priorities and relevant rates.
        self.updatePriorities()
        self.PIECES_BEFORE_TEND = rospy.get_param('tend_rate')
        self.PIECES_BEFORE_LOOK = min(self.PIECES_BEFORE_LOOK, self.PIECES_BEFORE_TEND)

        # Extract next list of operations
        operations = []
        i = self.state.operation_index
        count = 0
        numSort = 0
        numPlace = 0
        numDPlace = 0
        while count < self.PIECES_BEFORE_LOOK:
            op = self.order[i]
            if op == Permute_State.PLACE:
                operations.append(op)
                numPlace += 1
            elif op == Permute_State.DIRECT_PLACE:
                operations.append(op)
                numDPlace += 1
            elif op == Permute_State.SORT:
                operations.append(op)
                numSort += 1
            else:
                raise ValueError("Invalid operation in order")
            count += 1
            i = (i + 1) % len(self.order)
        self.state.operation_index = i
        
        # Generate the piece list for unorg <-> soln
        unorganized_measured_board = self.createMeasuredBoard(rgbd, scene, [Base.UNORGANIZED])
        #---- Update solution estimate
        self.updateSolutionRegEstimate(scene)
        solution_board = self.createSolutionBoard(Base.UNORGANIZED)
        empty_spots = len(solution_board.pieces)
        if empty_spots == 0:
            return None, [] # Short circuit if no empty spots
        self.performMatching(unorganized_measured_board, solution_board)
        pieces_sort_dplace = self.getSequentialPlan(unorganized_measured_board,\
                                                     solution_board, numSort + numDPlace)
        
        # Generate the piece list for org <-> soln
        zones = [i for i in range(1, Base.NUM_ZONES + 1)]
        organized_measured_board = self.createMeasuredBoard(rgbd, scene, zones)
        self.performMatching(organized_measured_board, solution_board)
        pieces_place = self.computePlacePlan(scene, rgbd)

        # Create the final list of pieces and operations
        pieces = []
        op_list = []
        i = 0
        j = 0
        for op in operations:
            if op == Permute_State.SORT or op == Permute_State.DIRECT_PLACE:
                if i < len(pieces_sort_dplace):
                    pieces.append(pieces_sort_dplace[i])
                    i += 1
                    op_list.append(op)
            elif op == Permute_State.PLACE:
                if j < len(pieces_place):
                    pieces.append(pieces_place[j])
                    j += 1
                    op_list.append(op)
        
        return pieces, op_list
        
            
            
            
        
        
    
    def getNextAction(self, rgbd:ImageRGBD=None, scene:StatePuzzleScene=None):
        """
        @brief  Return the next action to execute from current solver state.

        Args:
            rgbd: Optional RGBD image for the current scene.
            scene: Optional current scene state.
        
        Returns:
            Action
        """
        
        '''
        Logic
        Assumption is that re-assessing
        priorities / switching actions requires the robot
        to measure again.
        
        Assess -> perform -> assess
        '''
        # Start of the solving logic
        
        if self.state is None:
            # Start by estimating scene and solving
            # for first k pieces
            action = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            self.state = Permute_State(operation=Permute_State.OUTRIGHT, num_pieces=0, \
                                       tend_counter=0, pc_list=None, operation_index=0, \
                                        op_list=None)
            return action
        
        previous = self.state
        nextOperation = -1
        nextNumPieces = -1
        nextPcList = None
        nextTendCounter = -1
        nextOpList = None
        
        if previous.operation == Permute_State.OUTRIGHT:
            # Action was asking for estimation
            if scene is None or rgbd is None:
                print("ERROR: Expected scene information")
                return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            # Compute the priorities and action plan
            nextPcList, nextOpList = self.getNextOperation(scene, rgbd)
            print("Next operations: ", nextOpList, " with pieces: ", len(nextPcList))

            # End if no operations available (e.g., solved)
            if not nextOpList:
                action  = Action(type=Action.END)
                nextOperation = Permute_State.END
                nextNumPieces = -1
            else:
                nextNumPieces = 0
                nextOperation = nextOpList[nextNumPieces]
                # Move to next state if direct place / sort, but if place, then go to left.
                if nextOperation == Permute_State.PLACE:
                    action = Action(type=Action.OUTLEFT, estimate_zone=[])
                else:
                    action = Action(type=Action.NULL)
                
            nextTendCounter = previous.tend_counter
        elif previous.operation == Permute_State.DIRECT_PLACE or previous.operation == Permute_State.PLACE:
            # previous action was an estimation followed with a place
            # this one is going to be a place / or go back to estimation

            if previous.tend_counter == self.PIECES_BEFORE_TEND:
                # Ask for help
                action = Action(type=Action.HELP, help="Fix the solution")
                nextOperation = Permute_State.ASKHELP
                nextNumPieces = -1
                nextTendCounter = -1
            elif previous.num_pieces == len(previous.pc_list):
                # Re-estimate
                action = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
                nextOperation = Permute_State.OUTRIGHT
                nextNumPieces = -1
                nextTendCounter = previous.tend_counter
            else:
                meaPiece, solPiece, rot, _ = previous.pc_list[previous.num_pieces]
                action = Action(type=Action.PICKPLACE, \
                                measured_pc=meaPiece,\
                                solution_pc=solPiece, rotation=rot)
                nextNumPieces = previous.num_pieces + 1
                if nextNumPieces == len(previous.pc_list):
                    nextOperation = previous.operation
                else:
                    nextOperation = previous.op_list[nextNumPieces]
                nextTendCounter = previous.tend_counter + 1
        elif previous.operation == Permute_State.SORT:
            if previous.tend_counter == self.PIECES_BEFORE_TEND:
                # Ask for help
                action = Action(type=Action.HELP, help="Fix the solution")
                nextOperation = Permute_State.ASKHELP
                nextNumPieces = -1
                nextTendCounter = -1
            elif previous.num_pieces == len(previous.pc_list):
                # Re-estimate
                action = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
                nextOperation = Permute_State.OUTRIGHT
                nextNumPieces = -1
                nextTendCounter = previous.tend_counter
            else:
                meaPiece, solPiece, rot, tgt_zone = previous.pc_list[previous.num_pieces]
                action = Action(type=Action.SORT, \
                                measured_pc=meaPiece,\
                                solution_pc=solPiece, rotation=rot,
                                tgt_zone=tgt_zone)
                nextNumPieces = previous.num_pieces + 1
                if nextNumPieces == len(previous.pc_list):
                    nextOperation = previous.operation
                else:
                    nextOperation = previous.op_list[nextNumPieces]
                nextTendCounter = previous.tend_counter + 1
        elif previous.operation == Permute_State.ASKHELP:
            # last step was to ask help, 
            # Next: estimate board again
            action = Action(type=Action.NULL)
            nextOperation = Permute_State.OUTRIGHT
            nextTendCounter = 0
        
        # Update state
        self.state.operation = nextOperation
        self.state.num_pieces = nextNumPieces
        self.state.tend_counter = nextTendCounter
        if nextPcList is not None:
            self.state.pc_list = nextPcList
        if nextOpList is not None:
            self.state.op_list = nextOpList
        # Send action
        return action
            
    






#=============== puzzle.solver.permute.py =====================
