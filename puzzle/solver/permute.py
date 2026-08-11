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
from puzzle.solver.base_v2 import Base, Action , CfgSolver, Mode
from puzzle.solver.priority import Priority_Solver
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from camera.base import ImageRGBD
import numpy as np
from puzzle.piece import PieceStatus
from dataclasses import dataclass


@dataclass
class Permute_State:
    """!
    @brief      State for the permutation-driven solver.
    @ingroup    Puzzle_Solving
    """
    DIRECT_PLACE = 0
    PLACE = 1
    SORT = 2
    END = 4
    operation: int
    op_list: any # List of next operations
    num_pieces: int
    tend_counter: int
    pc_list: any # List of next pieces
    operation_index: int  # index within the larger order
    needs_look: bool = True
    needs_tend: bool = False
    last_action_was_tend: bool = False


'''
Core Tasks:
2. Have a counter that iterates through these once the operation is carried out.
3. getNextOperation will simply gauge how far ahead we can go from counter and com
press into a single plan- min of left operations in the plan, and look rate.
'''
class Permute_Solver(Priority_Solver):
    """!
    @brief      Execute a configured permutation of puzzle operations.
    @ingroup    Puzzle_Solving
    """

    def __init__(self, cfgSolver: CfgSolver, permutation=[]):
        """!
        @brief  Construct a permutation-driven solver.

        @param[in]  cfgSolver    Configuration for the solver.
        @param[in]  permutation  Ordered sequence of solver operations.
        """
        super().__init__(cfgSolver)
        self.PIECES_BEFORE_TEND = rospy.get_param('tend_rate')

        # Logically, the robot can estimate when in ask for help state
        # so, the pices before look is the minimum of (look_rate, tend_rate)
        self.PIECES_BEFORE_LOOK = min(self.PIECES_BEFORE_LOOK, self.PIECES_BEFORE_TEND)

        self.order = permutation

    #============================ reset_solver ===========================
    #
    def reset_solver(self):
        """!
        @brief  Reset the solver state and mode.
        """
        super().reset_solver()
        self.state = Permute_State(
            operation=-1, op_list=None, num_pieces=0,
            tend_counter=self.PIECES_BEFORE_TEND,
            pc_list=None, operation_index=0,
            needs_look=True, needs_tend=False,
            last_action_was_tend=False
        )
        self.mode = Mode.PERCEIVE
        
        
    def getNextOperation(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """!
        @brief  Compute the composite priority of each operation and
                return the operation with highest composite priority.

        @param[in]  rgbd   RGBD image for the current scene.
        @param[in]  scene  Current puzzle scene state.
        
        @return  Tuple containing the piece list and operation list.
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
        """!
        @brief  Return the next action to execute from current solver state.

        @param[in]  rgbd   Optional RGBD image for the current scene.
        @param[in]  scene  Optional current puzzle scene state.
        
        @return  Action to take.

        @note  Uses PERCEIVE mode to plan and request tending, then ACT mode
               to execute the planned operations.
        """
        
        # First ever call: initialize state and request a look.
        if self.state is None:
            action = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            self.state = Permute_State(
                operation=-1, op_list=None, num_pieces=0,
                tend_counter=self.PIECES_BEFORE_TEND,
                pc_list=None, operation_index=0,
                needs_look=True, needs_tend=False
            )
            self.mode = Mode.PERCEIVE
            return action

        # -----------------------------------------------------------------
        #  PERCEIVE mode: handle tending, then looking / planning.
        # -----------------------------------------------------------------
        if self.mode == Mode.PERCEIVE:

            # --- Solved: request final tend, then end --------------------
            if self.state.operation == Permute_State.END:
                if self.state.needs_tend:
                    self.state.needs_tend = False
                    return Action(type=Action.HELP, help="Fix the solution")
                print("Ending operations")
                return Action(type=Action.END)

            # --- Sub-step 1: Tending (if triggered) ----------------------
            if self.state.needs_tend:
                self.state.needs_tend   = False
                self.state.tend_counter = self.PIECES_BEFORE_TEND
                self.state.needs_look   = True
                self.state.last_action_was_tend = True
                return Action(type=Action.HELP, help="Fix the solution")

            # --- Sub-step 2: Look / plan ---------------------------------
            if self.state.needs_look:
                if scene is None or rgbd is None:
                    return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)

                pc_list, op_list = self.getNextOperation(scene, rgbd)
                if op_list is not None and pc_list is not None:
                    print("Next operations: ", op_list, " with pieces: ", len(pc_list))

                if pc_list is None or len(pc_list) == 0:
                    if self.state.last_action_was_tend:
                        print("Puzzle solved and tend was already performed — ending operations.")
                        self.state.operation = Permute_State.END
                        return Action(type=Action.END)
                    else:
                        print("Puzzle solved — requesting final tend before ending.")
                        self.state.operation  = Permute_State.END
                        self.state.needs_tend = True
                        self.state.needs_look = False
                        return Action(type=Action.NULL)

                # Plan ready — transition to ACT.
                self.state.needs_look = False
                self.state.operation  = op_list[0]
                self.state.pc_list    = pc_list
                self.state.op_list    = op_list
                self.state.num_pieces = 0
                self.mode             = Mode.ACT
                return Action(type=Action.NULL)

        # -----------------------------------------------------------------
        #  ACT mode: execute sequence of operations from pc_list & op_list.
        # -----------------------------------------------------------------
        if self.mode == Mode.ACT:

            # Check exit conditions: pieces exhausted or tend counter hit zero.
            if self.state.num_pieces >= len(self.state.pc_list) or \
               self.state.tend_counter <= 0:
                self.mode               = Mode.PERCEIVE
                self.state.needs_look   = True
                self.state.needs_tend   = (self.state.tend_counter <= 0)
                return Action(type=Action.NULL)

            op = self.state.op_list[self.state.num_pieces]
            self.state.operation = op

            if op == Permute_State.SORT:
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

        # Fallback
        print("WARNING: getNextAction fell through. Requesting estimation.")
        self.mode = Mode.PERCEIVE
        self.state.needs_look = True
        return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            
    






#=============== puzzle.solver.permute.py =====================
