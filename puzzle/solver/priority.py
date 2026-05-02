#=============== puzzle.solver.priority.py =====================
#
# @class    puzzle.solver.priority.py
# @brief    Priority based solving. Involves estimating the
#           scene every k actions (sort, place, direct place)
#           robot. After scene estimation performs a decision about
#           which action to perform based on priorities.
#           After performing action, repeat the process.
#           Uses the look rate to determine how often
#           to re-assess priorities and switch actions.
#           Assumes continuous solving with human, so no tending.
#         
#
#
#
#=============== puzzle.solver.priority.py =====================

import rospy
from puzzle.solver.base_v2 import Base, Action , CfgSolver
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from camera.base import ImageRGBD
import numpy as np
from puzzle.piece import PieceStatus
from dataclasses import dataclass


@dataclass
class Priority_State:
    DIRECT_PLACE = 0
    PLACE = 1
    SORT = 2
    OUTRIGHT = 3
    END = 4
    operation: int
    num_pieces: int
    pc_list: any

class Priority_Solver(Base):
    def __init__(self, cfgSolver: CfgSolver):
        super().__init__(cfgSolver)
        self.updatePriorities()
        self.zones_to_estimate = [Base.SOL, Base.UNORGANIZED] + [i for i in range(1, Base.NUM_ZONES + 1)]
    
    def updatePriorities(self):
        self.sort_pty = rospy.get_param('sort_priority')
        self.place_pty = rospy.get_param('place_priority')
        self.dir_place_pty = rospy.get_param('direct_place_priority')
        self.PIECES_BEFORE_LOOK = rospy.get_param('look_rate')
    
    def computePlacePlan(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """
        @brief  Computes a custom place plan. Starts by filling in pieces from 
                most populated zones to least populated zones.
        """
        
        pieces_left = self.PIECES_BEFORE_LOOK
        plan = []
        for zone in range(1, Base.NUM_ZONES + 1):
            measured_board = self.createMeasuredBoard(rgbd, scene, [zone])
            solution_board = self.createSolutionBoard(zone)
            plan.append((len(measured_board.pieces), measured_board, solution_board))
        
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
            
            
        
        
        
    def getNextOperation(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """
        @brief  Compute the composite priority of each operation and
                return the operation with highest composite priority.
        Args:
            rgbd:  RGBD image for the current scene.
            scene:  current scene state.
        
        Returns: 
            List of pieces, Next operation state
        
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

        direct_place_score = empty_spots * self.dir_place_pty
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
            return [], Priority_State.OUTRIGHT
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
            self.state = Priority_State(operation=Priority_State.OUTRIGHT, num_pieces=0, pc_list=None)
            return action
        
        previous = self.state
        nextOperation = -1
        nextNumPieces = -1
        nextPcList = None
        
        if previous.operation == Priority_State.OUTRIGHT:
            # Action was asking for estimation
            if scene is None or rgbd is None:
                print("ERROR: Expected scene information")
                return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            # Compute the priorities and action plan
            nextPcList, nextOperation = self.getNextOperation(scene, rgbd)
            print("Next operation: ", nextOperation, " with pieces: ", len(nextPcList))

            # End if no empty spots in solution board
            if nextOperation == Priority_State.END:
                action  = Action(type=Action.END)
            elif nextOperation == Priority_State.OUTRIGHT:
                action = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            else:
                # Simply move to next state
                action = Action(type=Action.NULL)
                nextNumPieces = 0
        elif previous.operation == Priority_State.DIRECT_PLACE or previous.operation == Priority_State.PLACE:
            # previous action was an estimation followed with a place
            # this one is going to be a place / or go back to estimation
            if previous.num_pieces == len(previous.pc_list):
                # Re-estimate
                action = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
                nextOperation = Priority_State.OUTRIGHT
                nextNumPieces = -1
            else:
                meaPiece, solPiece, rot, _ = previous.pc_list[previous.num_pieces]
                # Add a check to see if the piece is already placed correctly, if so skip
                if not self.isPieceThere(meaPiece, scene):
                    action = Action(type=Action.NULL)
                    nextOperation = previous.operation
                    nextNumPieces = previous.num_pieces + 1
                else:
                    action = Action(type=Action.PICKPLACE, \
                                    measured_pc=meaPiece,\
                                    solution_pc=solPiece, rotation=rot)
                    nextOperation = previous.operation
                    nextNumPieces = previous.num_pieces + 1
        elif previous.operation == Priority_State.SORT:
            if previous.num_pieces == len(previous.pc_list):
                # Re-estimate
                action = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
                nextOperation = Priority_State.OUTRIGHT
                nextNumPieces = -1
            else:
                meaPiece, solPiece, rot, tgt_zone = previous.pc_list[previous.num_pieces]
                if not self.isPieceThere(meaPiece, scene):
                    action = Action(type=Action.NULL)
                    nextOperation = previous.operation
                    nextNumPieces = previous.num_pieces + 1
                else:
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
            
    






#=============== puzzle.solver.priority.py =====================
