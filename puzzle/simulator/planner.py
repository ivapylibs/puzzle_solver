# ========================= puzzle.simulator.planner ========================
#
# @class    puzzle.simulator.planner
#
# @brief    The planner for producing the action sequence to solve the puzzle.
#           This one is more general for most cases.
# @note     Yunzhi: more like a wrapper of solver & manager in the test script.
#
# ========================= puzzle.simulator.planner ========================
#
# @file     planner.py
#
# @author   Yiye Chen,               yychen2019@gatech.edu
#           Yunzhi Lin,              yunzhi.lin@gatech.edu
# @date     2021/09/02 [created]
#           2021/11/25 [modified]
#
#
# ========================= puzzle.simulator.planner ========================


import improcessor.basic as improcessor
import cv2
import numpy as np
from dataclasses import  dataclass

# from puzzle.builder.arrangement import Arrangement
from puzzle.builder.interlocking import Interlocking
from puzzle.builder.gridded import ParamGrid
from puzzle.builder.board import Board
from puzzle.piece.template import PieceStatus

@dataclass
class ParamPlanner(ParamGrid):
    hand_radius: int = 120

class Planner:
    def __init__(self, solver, manager, theParams=ParamPlanner):
        self.solver = solver
        self.manager = manager
        self.param = theParams

        # match: id to sol_id
        self.record = {'meaBoard': None, 'match': {}, 'rLoc_hand': None}

        # For recording hand_activity, where 0: nothing; 1: pick; 2: place.
        self.hand_activity = 0

    def measure(self, img):

        # Debug only
        # cv2.imshow('debug', cv2.cvtColor(img,cv2.COLOR_RGB2BGR))
        # cv2.waitKey()

        improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_RGB2GRAY,),
                                   improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                                   cv2.dilate, (np.ones((3, 3), np.uint8),)
                                   )
        theMaskMea = improc.apply(img)

        # Debug only
        # cv2.imshow('debug', theMaskMea)
        # cv2.waitKey()

        meaBoard = Interlocking.buildFrom_ImageAndMask(img, theMaskMea,
                                                       theParams=self.param)
        # # Debug only
        # meaBoard.pieces[10].display()
        # import matplotlib.pyplot as plt
        # plt.plot()
        return meaBoard

    def adapt(self, meaBoard, rLoc_hand=None, COMPLETE_PLAN=True, SAVED_PLAN=True, RUN_SOLVER=True):

        # manager processes the measured board to establish the association
        self.manager.process(meaBoard)

        record_board_temp = Board()
        record_match_temp = {}

        # 0: nothing; 1: pick; 2: place.
        self.hand_activity = 0

        # For both pick and place, we assume the change of the appearance of one puzzle piece near Hand is caused by hand
        # For place
        flagFound_place = False
        if self.record['meaBoard'] is not None and self.record['rLoc_hand'] is not None:

            # We only work on the cases where teh hand moves
            # Todo: May want to add some epsilon here
            if rLoc_hand is None or (not np.array_equal(rLoc_hand.reshape(2,-1), self.record['rLoc_hand'].reshape(2,-1))):
                # Check if there was no puzzle piece in the tracked board (no matter measured or tracked) before in the hand region (last saved)
                # We need the non-updated tracked board. Otherwise, we will see the piece can be found there.
                for piece in self.record['meaBoard'].pieces.values():

                    if (piece.status == PieceStatus.MEASURED or piece.status == PieceStatus.TRACKED):
                        if np.linalg.norm(piece.rLoc.reshape(2,-1) - self.record['rLoc_hand'].reshape(2,-1))< self.param.hand_radius:
                            flagFound_place = True
                            break

                # Check if we can see a new piece in the hand region (last saved)
                if flagFound_place is False:
                    # We need the current meaBoard
                    for piece in meaBoard.pieces.values():
                        if np.linalg.norm(piece.rLoc.reshape(2,-1) - self.record['rLoc_hand'].reshape(2,-1))< self.param.hand_radius:
                            self.hand_activity = 2
                            # print('The hand just dropped a piece')
                            break


        # For tracking
        for record_match in self.record['match'].items():
            findFlag = False
            for match in self.manager.pAssignments.items():
                if record_match[1] == match[1]:
                    # 1) If some pieces are available on both boards, those pieces will have an updated status.
                    record_board_temp.addPiece(meaBoard.pieces[match[0]])
                    record_match_temp[record_board_temp.id_count-1] = match[1]
                    findFlag = True
                    break

            if findFlag == False:
                # 2) If some pieces are only available on the record board, their status will be marked as TRACKED.
                # Todo: If their status has been TRACKED for a while. They will be deleted from the record board.
                self.record['meaBoard'].pieces[record_match[0]].status = PieceStatus.TRACKED
                record_board_temp.addPiece(self.record['meaBoard'].pieces[record_match[0]])
                record_match_temp[record_board_temp.id_count-1] = record_match[1]

        for new_match in self.manager.pAssignments.items():
            findFlag = False
            for match in record_match_temp.items():
                if new_match[1] == match[1]:
                    findFlag = True
                    break

            if findFlag == False:
                # 3) If some pieces are only available on the new board, they will be added to the record board.
                record_board_temp.addPiece(meaBoard.pieces[new_match[0]])
                record_match_temp[record_board_temp.id_count-1] = new_match[1]

        # Update
        self.record['meaBoard'] = record_board_temp
        self.record['match'] = record_match_temp

        # For pick
        flagFound_pick = False
        if self.record['meaBoard'] is not None and self.record['rLoc_hand'] is not None:

            # We only work on the cases where teh hand moves
            # Todo: May want to add some epsilon here
            if rLoc_hand is None or (not np.array_equal(rLoc_hand.reshape(2,-1), self.record['rLoc_hand'].reshape(2,-1))):
                # Check if there was a piece disappearing in the hand region (last saved)
                # We need an updated tracked board here
                for piece in self.record['meaBoard'].pieces.values():

                    # Be careful about the distance thresh (It should be large enough),
                    # when picked up the piece, the hand may be far from the original piece rLoc,
                    if piece.status == PieceStatus.TRACKED:
                        if np.linalg.norm(piece.rLoc.reshape(2,-1) - self.record['rLoc_hand'].reshape(2,-1)) < self.param.hand_radius:
                            flagFound_pick = True
                            break

                # Check if there is no puzzle piece in the hand region (last saved) right now
                if flagFound_pick is True:
                    flagFound_pick_2 = False
                    # We need teh current meaBoard
                    for piece in meaBoard.pieces.values():
                        if np.linalg.norm(piece.rLoc.reshape(2,-1) - self.record['rLoc_hand'].reshape(2,-1)) < self.param.hand_radius:
                            flagFound_pick_2 = True
                            break

                    if flagFound_pick_2 is False:
                        self.hand_activity = 1
                        # print('The hand just picked up a piece')

        # Update the rLoc_hand in the end
        self.record['rLoc_hand'] = rLoc_hand

        # # # Debug only
        # if self.record['rLoc_hand'] is not None:
        #     print('Current hand location:', self.record['rLoc_hand'])
        # # Current id to solution id
        # print('Match in the new measured board:', self.manager.pAssignments)
        # # Note that the printed tracking id is not the one used in meaBoard nor the one used in DisplayBoard (simulator)
        # print('Match in the tracking record:', self.record['match'])
        # for match in self.record['match'].items():
        #     print(f"ID{match[0]}: {self.record['meaBoard'].pieces[match[0]].status}")

        if RUN_SOLVER:
            # Solver plans for the measured board
            self.solver.setCurrBoard(meaBoard)
            self.solver.setMatch(self.manager.pAssignments, self.manager.pAssignments_rotation)

            # Right now, can only work when puzzle board is not re-processed.
            # Otherwise, the connected ones will not be considered in the list.
            # As a result, same effect.

            # Get the index of the pieces with the occlusion and skip them
            meaBoard.processAdjacency()
            occlusionList = []
            pieceKeysList = list(meaBoard.pieces.keys())
            for index in range(meaBoard.adjMat.shape[0]):
                if sum(meaBoard.adjMat[index, :]) > 1:
                    occlusionList.append(pieceKeysList[index])

            # print('Occlusion:', occlusionList)

            # Plan is for the measured piece
            plan = self.solver.takeTurn(defaultPlan='order', occlusionList=occlusionList, COMPLETE_PLAN=COMPLETE_PLAN, SAVED_PLAN=SAVED_PLAN)
            # print(plan)
            return plan
        else:
            return None

    def process(self, input, rLoc_hand=None, COMPLETE_PLAN=True, SAVED_PLAN=True, RUN_SOLVER=True):
        """
        @brief  Draft the action plan given the measured board.

        @note In principle, the process is not triggered by key but should be called every processing time

        Args:
            input: A measured board or RGB image.
            COMPLETE_PLAN: Whether to plan the whole sequence.
            SAVED_PLAN: Use the saved plan (self.plan) or not.
            RUN_SOLVER: Whether to compute the solver to get the next action plan.
                        Otherwise, only the board will be recognized and updated.
        Returns:
            plan: The action plan for the simulator to perform
        """

        if issubclass(type(input), Board):
            meaBoard = input
        else:
            meaBoard = self.measure(input)

        # We have the option to not plan anything
        plan = self.adapt(meaBoard, rLoc_hand=rLoc_hand, COMPLETE_PLAN=COMPLETE_PLAN, SAVED_PLAN=SAVED_PLAN, RUN_SOLVER=RUN_SOLVER)

        return plan
