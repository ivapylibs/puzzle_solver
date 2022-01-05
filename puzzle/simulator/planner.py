# ========================= puzzle.simulator.planner ========================
#
# @class    puzzle.simulator.planner
#
# @brief    The planner for producing the action sequence to solve the puzzle.
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

# from puzzle.builder.arrangement import Arrangement
from puzzle.builder.interlocking import Interlocking
from puzzle.builder.gridded import ParamGrid
from puzzle.builder.board import Board
from puzzle.piece.template import PieceStatus


class Planner:
    def __init__(self, solver, manager, theParams=ParamGrid):
        self.solver = solver
        self.manager = manager
        self.param = theParams

        self.record = {'meaBoard': None, 'match': {}}

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

    def adapt(self, meaBoard, COMPLETE_PLAN=True):

        # manager processes the measured board to establish the association
        self.manager.process(meaBoard)

        record_board_temp = Board()
        record_match_temp = {}

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
                # 2) If some pieces are only available on the record board, their status will be marked as unknown.
                # If their status has been unknown for a while. They will be deleted from the record board.
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

        self.record['meaBoard'] = record_board_temp
        self.record['match'] = record_match_temp

        # Debug only
        print('Match in the new measured board:', self.manager.pAssignments)
        print('Match in the tracking record:', self.record['match'])


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
                # occlusionList.append(index)
                occlusionList.append(pieceKeysList[index])

        print('Occlusion:', occlusionList)

        # Plan is for the measured piece
        plan = self.solver.takeTurn(defaultPlan='order', occlusionList=occlusionList, COMPLETE_PLAN=COMPLETE_PLAN)
        # print(plan)
        return plan

    def process(self, input, COMPLETE_PLAN=True):
        """
        @brief  Draft the action plan given the measured board.

        @note In principle, the process is not triggered by key but should be called every processing time

        Args:
            input: A measured board or RGB image.
            COMPLETE_PLAN: Whether to plan the whole sequence.

        Returns:
            plan: The action plan for the simulator to perform
        """

        if issubclass(type(input), Board):
            meaBoard = input
        else:
            meaBoard = self.measure(input)

        plan = self.adapt(meaBoard, COMPLETE_PLAN=COMPLETE_PLAN)

        return plan
