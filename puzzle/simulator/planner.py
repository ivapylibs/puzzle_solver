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

class Planner:
    def __init__(self, solver, manager, theParams=ParamGrid):
        self.solver = solver
        self.manager = manager
        self.param = theParams

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

        return meaBoard

    def adapt(self, meaBoard, COMPLETE_PLAN=True):

        # manager process the measured board to establish the association
        self.manager.process(meaBoard)

        # Solver use the association to plan which next puzzle to move to where
        self.solver.setCurrBoard(meaBoard)

        self.solver.setMatch(self.manager.pAssignments, self.manager.pAssignments_rotation)


        # plan = self.solver.takeTurn(defaultPlan='order', COMPLETE_PLAN=COMPLETE_PLAN)



        # Get the index of the pieces with the occlusion and skip them
        meaBoard.processAdjacency()
        occlusionList = []
        for index in range(meaBoard.adjMat.shape[0]):
            if sum(meaBoard.adjMat[index,:])>1:
                occlusionList.append(index)
        print(occlusionList)

        # Plan is for the measured piece
        plan = self.solver.takeTurn(defaultPlan='order', occlusionList=occlusionList, COMPLETE_PLAN=COMPLETE_PLAN)
        # print(plan)
        return plan


    def process(self, input, COMPLETE_PLAN=True):
        """
        @brief  Draft the action plan given the measured board.

        Args:
            input: A measured board or RGB image.
            COMPLETE_PLAN: Whether to plan the whole sequence.

        Returns:
            plan(The action plan for the simulator to perform)
        """

        if issubclass(type(input),Board):
            meaBoard = input
        else:
            meaBoard = self.measure(input)

        plan = self.adapt(meaBoard, COMPLETE_PLAN=COMPLETE_PLAN)

        return plan
