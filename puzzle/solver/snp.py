#=============== puzzle.solver.snp.py =====================
#
# @class    puzzle.solver.snp.py
# @brief    Robot performs sort according to specified 
#           policies and then performs place
#           operations on the sorted pieces.
#
#
#
#=============== puzzle.solver.snp.py =====================

import rospy
from puzzle.solver.base_v2 import Base, Action , CfgSolver
from Surveillance.layers.PuzzleScene import StatePuzzleScene
from camera.base import ImageRGBD
import numpy as np
from puzzle.piece import PieceStatus
from dataclasses import dataclass

@dataclass
class SNP_State:
    SORT = 0
    OUTRIGHT = 1
    PLACE = 2
    OUTLEFT = 3
    END = 4
    operation: int
    num_pieces: int
    pc_list: any


class SNP(Base):
    STRUCTURED_ORDERED = 0
    STRUCTURED_UNORDERED = 1
    UNSTRUCTURED_ORDERED = 2
    UNSTRUCTURED_UNORDERED = 3
    def __init__(self, cfgSolver: CfgSolver, policy: int):
        super().__init__(cfgSolver)
        self.policy = policy
        
        self.zones_to_estimate = [Base.SOL, Base.UNORGANIZED] + [i for i in range(1, Base.NUM_ZONES + 1)]


    def computePlacePlan(self, scene:StatePuzzleScene, rgbd:ImageRGBD):
        """
        @brief  Computes a custom place plan. Starts by filling in pieces from 
                most populated zones to least populated zones.
        """
        
        plan = []
        for zone in range(1, Base.NUM_ZONES + 1):
            measured_board = self.createMeasuredBoard(rgbd, scene, [zone])
            solution_board = self.createSolutionBoard(zone)
            plan.append((len(measured_board.pieces), measured_board, solution_board))
        
        # Sort most to least pieces
        plan.sort(key=lambda x: x[0], reverse=True)
        i = 0
        pieces = []
        pieces_left = len(self.board_estimate.pieces)
        while i < Base.NUM_ZONES:
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
     
    def getSortPlan(self, rgbd: ImageRGBD=None, scene:StatePuzzleScene=None):
        """
        @brief  Return the sort plan with correct piece ordering for robot
                to execute. Based on the policy set initially
        
        Args:
            rgbd: Image details
            scene: Segmented scene information
        """

        # Create unorganized region board
        unorganized_measured_board = self.createMeasuredBoard(rgbd, scene, [Base.UNORGANIZED])
        # Create solution region board
        self.updateSolutionRegEstimate(scene)
        solution_board = self.createSolutionBoard(Base.UNORGANIZED)
        # Perform matching
        self.performMatching(unorganized_measured_board, solution_board)

        # Sort plan based on the 4 policies
        if self.policy == SNP.STRUCTURED_ORDERED:
            plans = [[], [], [], []]
            for key in unorganized_measured_board.pieces:
                pieceMea = unorganized_measured_board.pieces[key]
                solKey = self.correspondence_tracker.pAssignments[key]
                pieceSol = solution_board.pieces[solKey]
                rot = self.correspondence_tracker.pAssignments_rotation[key]
                zone = solution_board.zones[solKey]
                if zone != 0:
                    plans[zone - 1].append((pieceMea, pieceSol, rot, zone))
            # Sort each plan
            for i in range(Base.NUM_ZONES):
                plans[i].sort(key= lambda x: x[1].id)
            # Create master plan by merging the lists
            plan = []
            for zone_plan in plans:
                plan.extend(zone_plan)
        elif self.policy == SNP.STRUCTURED_UNORDERED:
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
        elif self.policy == SNP.UNSTRUCTURED_ORDERED:
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
        elif self.policy == SNP.UNSTRUCTURED_UNORDERED:
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


    def getNextAction(self, rgbd:ImageRGBD=None, scene:StatePuzzleScene=None):
        """
        @brief  Return the next action to execute from current solver state.

        Args:
            rgbd: Optional RGBD image for the current scene.
            scene: Optional current scene state.
        
        Returns:
            Action
        """
        
        # Start by estimation
        if self.state is None:
            action = Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            self.state = SNP_State(operation=SNP_State.OUTRIGHT, num_pieces=0, pc_list=None)
            return action
        
        previous = self.state
        nextOperation = -1
        nextNumPieces = -1
        nextPcList = None

        if previous.operation == SNP_State.OUTRIGHT:
            # Action was asking for estimation
            if scene is None or rgbd is None:
                print("ERROR: Expected scene information")
                return Action(type=Action.OUTRIGHT, estimate_zone=self.zones_to_estimate)
            # Compute the priorities and action plan
            nextPcList = self.getSortPlan(rgbd, scene)
            action = Action(type=Action.NULL)
            # Simply move to next state to start sorting
            nextOperation = SNP_State.SORT
            nextNumPieces = 0
        elif previous.operation == SNP_State.OUTLEFT:
            # Action was asking for estimation
            if scene is None or rgbd is None:
                print("ERROR: Expected scene information")
                zones_place_estimate = [i for i in range(1, Base.NUM_ZONES + 1)]
                return Action(type=Action.OUTLEFT, estimate_zone=zones_place_estimate)
            # Compute the priorities and action plan
            nextPcList = self.computePlacePlan(scene, rgbd)
            action = Action(type=Action.NULL)
            # Simply move to next state to start placing
            nextOperation = SNP_State.PLACE
            nextNumPieces = 0
        elif previous.operation == SNP_State.SORT:
            if previous.num_pieces == len(previous.pc_list):
                # End of sort, move to estimation for place
                zones_place_estimate = [i for i in range(1, Base.NUM_ZONES + 1)]
                action  = Action(type=Action.OUTLEFT, estimate_zone=zones_place_estimate)
                nextOperation = SNP_State.OUTLEFT
                nextNumPieces = -1
            else:
                meaPiece, solPiece, rot, tgt_zone = previous.pc_list[previous.num_pieces]
                action = Action(type=Action.SORT, \
                                measured_pc=meaPiece,\
                                solution_pc=solPiece, rotation=rot,
                                tgt_zone=tgt_zone)
                nextOperation = previous.operation
                nextNumPieces = previous.num_pieces + 1
        elif previous.operation == SNP_State.PLACE:
            if previous.num_pieces == len(previous.pc_list):
                # End of Operations
                action  = Action(type=Action.END)
                nextOperation = SNP_State.END
                nextNumPieces = -1
            else:
                meaPiece, solPiece, rot, tgt_zone = previous.pc_list[previous.num_pieces]
                action = Action(type=Action.PICKPLACE, \
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

#=============== puzzle.solver.snp.py =====================
