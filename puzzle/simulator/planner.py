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
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift

@dataclass
class ParamPlanner(ParamGrid):
    hand_radius: int = 120
    tracking_life_thresh: int = 15

class Planner:
    def __init__(self, solver, manager, theParams=ParamPlanner):
        """
        @brief Work like a wrapper of solver & manager in the test script.

        Args:
            solver: The solver instance.
            manager: The manager instance.
            theParams: The params.
        """

        self.solver = solver
        self.manager = manager
        self.param = theParams

        # match: id to sol_id
        # It is always the updated one
        self.record = {'meaBoard': None, 'match': {}, 'rLoc_hand': None}

        # For saving the tracked board with solution board ID
        self.displayBoard = None

        # For saving the status history
        self.status_history = None

        # For saving the puzzle piece's location history
        self.loc_history = None

    def measure(self, img):
        """
        @brief Process the input image to get the measured board.

        Args:
            img: The input image.

        Returns:
            meaBoard: The measured board instance.
        """

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

    def adapt(self, meaBoard, visibleMask, rLoc_hand=None, COMPLETE_PLAN=True, SAVED_PLAN=True, RUN_SOLVER=True):
        """
        @brief Update the tracked board/history and generate the action plan for the robot.

        Args:
            meaBoard: The measured board for the current view.
            visibleMask: The mask image for the visible area.
            rLoc_hand: The location of the hand.
            COMPLETE_PLAN: Whether to generate the complete plan.
            SAVED_PLAN: Use the saved plan (self.plan) or not.
            RUN_SOLVER: Run solver or not.

        Returns:
            plan: The action plan.
        """
        # Todo: Not sure if this hard threshold is a good idea or not.
        # Remove the measured pieces if they are too close to the hand.
        # Only meaningful when we can see a hand.
        if rLoc_hand is not None:
            meaBoard_filtered = Board()
            for piece in meaBoard.pieces.values():
                if np.linalg.norm(piece.rLoc.reshape(2, -1) - rLoc_hand.reshape(2, -1)) > self.param.hand_radius+50:
                    meaBoard_filtered.addPiece(piece)

            meaBoard = meaBoard_filtered

        # manager processes the measured board to establish the association
        self.manager.process(meaBoard)

        record_board_temp = Board()
        record_match_temp = {}

        # For tracking

        # Note: The matching with the last frame may help when pieces look different from the one in the solution board (due to light)
        # But it may also hurt for a while when a piece has been falsely associated with one in the solution board

        match_intra = {}
        if self.record['meaBoard'] is not None:
            # Create a new manager for association between last frame and the current frame
            theManager_intra = Manager(self.record['meaBoard'], ManagerParms(matcher=Sift()))
            theManager_intra.process(meaBoard)

            for match in theManager_intra.pAssignments.items():
                # We only care about the ones which do not move
                # if np.linalg.norm(meaBoard.pieces[match[0]].rLoc.reshape(2, -1) - self.record['meaBoard'].pieces[match[1]].rLoc.reshape(2, -1)) < 50:
                match_intra[match[0]]=match[1]


        for record_match in self.record['match'].items():
            findFlag = False

            for match in self.manager.pAssignments.items():
                if record_match[1] == match[1]:
                    # 1) If some pieces are available on both boards, those pieces will have an updated status

                    # If only the piece can be matched to the same one in the tracking board.
                    if match[0] in match_intra:
                        if match_intra[match[0]]==record_match[0]:
                            # All three associations agree, then update

                            del match_intra[match[0]]
                            # The new meaBoard will always have pieces of tracking_life as 0
                            record_board_temp.addPiece(meaBoard.pieces[match[0]])
                            record_match_temp[record_board_temp.id_count-1] = record_match[1]
                            findFlag = True
                            break

            if findFlag == False:
                findFlag_2 = False
                # e,g, ID 1 (meaBoard)->4 (tracked)->4 (solBoard)
                if record_match[0] in match_intra.values():
                    key_new = list(match_intra.values()).index(record_match[0])

                    # We only care about the cases where pieces do not move
                    if np.linalg.norm(meaBoard.pieces[key_new].rLoc.reshape(2,-1) - self.record['meaBoard'].pieces[record_match[0]].rLoc.reshape(2,-1)) < 50:

                        # The new meaBoard will always have pieces of tracking_life as 0
                        record_board_temp.addPiece(meaBoard.pieces[key_new])
                        record_match_temp[record_board_temp.id_count - 1] = record_match[1]
                        findFlag_2 = True
                        del match_intra[key_new]

                if findFlag_2 == False:
                    # 2) If some pieces are only available on the record board, their status will be marked as TRACKED

                    # self.record['meaBoard'].pieces[record_match[0]].tracking_life += 1

                    # # For puzzle piece state change idea
                    # Check if most of the piece's part is visible in the current visibleMask
                    mask_temp = np.zeros(visibleMask.shape,dtype='uint8')
                    mask_temp[self.record['meaBoard'].pieces[record_match[0]].rLoc[1]:self.record['meaBoard'].pieces[record_match[0]].rLoc[1]+self.record['meaBoard'].pieces[record_match[0]].y.size[1], \
                                self.record['meaBoard'].pieces[record_match[0]].rLoc[0]:self.record['meaBoard'].pieces[record_match[0]].rLoc[0]+self.record['meaBoard'].pieces[record_match[0]].y.size[0]] \
                               = (self.record['meaBoard'].pieces[record_match[0]].y.mask/255).astype('uint8')
                    ratio_visible = (visibleMask.astype('uint8') + mask_temp == 2).sum()/mask_temp.sum()
                    # print('RATIO:', ratio_visible)

                    # Todo: Not sure how to set up the threshold
                    if ratio_visible > 0.99:
                        self.record['meaBoard'].pieces[record_match[0]].status = PieceStatus.GONE
                    else:
                        self.record['meaBoard'].pieces[record_match[0]].status = PieceStatus.INVISIBLE

                    # If their status has been TRACKED for a while but no update. They will be deleted from the record board
                    if self.record['meaBoard'].pieces[record_match[0]].tracking_life < self.param.tracking_life_thresh:
                        record_board_temp.addPiece(self.record['meaBoard'].pieces[record_match[0]])
                        record_match_temp[record_board_temp.id_count-1] = record_match[1]


        for new_match in self.manager.pAssignments.items():
            findFlag = False
            for match in record_match_temp.items():
                if new_match[1] == match[1]:
                    # Some that have the false associations will be filtered out here
                    findFlag = True
                    break

            if findFlag == False:
                # 3) If some pieces are only available on the new board, they will be added to the record board

                if new_match[0] in match_intra:
                    # 4) If some pieces can only be associated to the one in the record board, throw it away
                    pass
                else:
                    record_board_temp.addPiece(meaBoard.pieces[new_match[0]])
                    record_match_temp[record_board_temp.id_count-1] = new_match[1]

        # Update
        self.record['meaBoard'] = record_board_temp
        self.record['match'] = record_match_temp
        self.record['rLoc_hand'] = rLoc_hand

        # For puzzle piece state change idea
        # We want to print the ID from the solution board.
        self.displayBoard = Board()
        for match in self.record['match'].items():
            # Save for analysis
            self.status_history[match[1]].append(self.record['meaBoard'].pieces[match[1]].status)
            self.loc_history[match[1]].append(self.record['meaBoard'].pieces[match[1]].rLoc)

            # Save for demo
            self.displayBoard.addPiece(self.record['meaBoard'].pieces[match[1]], ORIGINAL_ID=True)

        # # Debug only
        # if self.record['rLoc_hand'] is not None:
        #     print('Current hand location:', self.record['rLoc_hand'])
        # # Current id to solution id
        # print('Match in the new measured board:', self.manager.pAssignments)

        # # Note that the printed tracking id is not the one used in meaBoard, or the one used in DisplayBoard (simulator), or the one used in SolBoard.
        # print('Match in the tracking record:', self.record['match'])
        # for match in self.record['match'].items():
        #     print(f"ID{match[0]}: {self.record['meaBoard'].pieces[match[0]].status}")

        # Debug only
        # We want to print the ID from the solution board.
        for match in self.record['match'].items():
            print(f"ID{match[1]}: {self.record['meaBoard'].pieces[match[1]].status}")

        if RUN_SOLVER:
            # Solver plans for the measured board
            self.solver.setCurrBoard(meaBoard)
            self.solver.setMatch(self.manager.pAssignments, self.manager.pAssignments_rotation)

            """
            Right now, can only work when puzzle board is not re-processed. 
            Otherwise, the connected ones will not be considered in the list. 
            As a result, same effect, so it is fine.
            """

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

    def process(self, input, rLoc_hand=None, visibleMask=None, COMPLETE_PLAN=True, SAVED_PLAN=True, RUN_SOLVER=True):
        """
        @brief  Draft the action plan given the measured board.

        @note In principle, the process is not triggered by key but should be called every processing time

        Args:
            input: A measured board or RGB image.
            rLoc_hand: The location of the hand.
            visibleMask: The mask of the visible area on the table (puzzle included).
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

        # We have the option to not plan anything but just update tracked board
        plan = self.adapt(meaBoard, rLoc_hand=rLoc_hand, visibleMask=visibleMask, COMPLETE_PLAN=COMPLETE_PLAN, SAVED_PLAN=SAVED_PLAN, RUN_SOLVER=RUN_SOLVER)

        return plan
