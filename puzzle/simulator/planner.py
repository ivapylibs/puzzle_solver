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
    tracking_life_thresh: int = 15

class Planner:
    def __init__(self, solver, manager, theParams=ParamPlanner):
        self.solver = solver
        self.manager = manager
        self.param = theParams

        # match: id to sol_id
        # It is always the updated one
        self.record = {'meaBoard': None, 'match': {}, 'rLoc_hand': None}

        # For recording hand_activity, where 0: nothing; 1: pick; 2: place.
        self.hand_activity = 0

        # For saving the tracked board with solution board ID
        self.displayBoard = None

        # For saving the status history
        self.status_history = None

        # For saving the puzzle piece's location history
        self.loc_history = None

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

    def adapt(self, meaBoard, visibleMask, rLoc_hand=None, COMPLETE_PLAN=True, SAVED_PLAN=True, RUN_SOLVER=True):

        # manager processes the measured board to establish the association
        self.manager.process(meaBoard)

        record_board_temp = Board()
        record_match_temp = {}

        # # ROI-based idea (stop for now)
        #
        # # 0: nothing; 1: pick; 2: place.
        # self.hand_activity = 0
        #
        # # For both pick and place, we assume the change of location of one puzzle piece near Hand is only caused by hand
        # # For place
        # if self.record['meaBoard'] is not None and self.record['rLoc_hand'] is not None:
        #
        #     # 0: Check if the hand moves or not visible now
        #     if rLoc_hand is None or (np.linalg.norm(rLoc_hand.reshape(2,-1)- self.record['rLoc_hand'].reshape(2,-1))>30):
        #         print('*****CHECK PLACE START*****')
        #         print('PREVIOUS HAND LOC:', self.record['rLoc_hand'].reshape(2, -1))
        #
        #         # Check how many puzzle pieces in the tracked board (no matter measured or tracked) before in the hand region (last saved)
        #         # We need the non-updated tracked board. Otherwise, we will see the piece can be found there
        #         num_before = 0
        #         for piece in self.record['meaBoard'].pieces.values():
        #             if piece.status == PieceStatus.TRACKED or piece.status == PieceStatus.MEASURED:
        #
        #                 # 1: Check if there was piece appearing in the hand region (last saved)
        #                 if np.linalg.norm(piece.rLoc.reshape(2,-1) - self.record['rLoc_hand'].reshape(2,-1))< self.param.hand_radius:
        #                     print('Piece in the record board:', piece.rLoc.reshape(2, -1), 'Status:', piece.status)
        #
        #                     num_before +=1
        #
        #         # Check how many puzzle pieces in the current measured board (no matter measured or tracked) before in the hand region (last saved)
        #         num_now = 0
        #         for piece in meaBoard.pieces.values():
        #
        #             if piece.status == PieceStatus.TRACKED or piece.status == PieceStatus.MEASURED:
        #                 if np.linalg.norm(piece.rLoc.reshape(2, -1) - self.record['rLoc_hand'].reshape(2,-1)) < self.param.hand_radius:
        #                     # 2:  Check if most of the appeared piece's part is visible in the current visibleMask
        #                     mask_temp = np.zeros(visibleMask.shape, dtype='uint8')
        #                     mask_temp[piece.rLoc[1]:piece.rLoc[1] + piece.y.size[1],
        #                     piece.rLoc[0]:piece.rLoc[0] + piece.y.size[0]] = (piece.y.mask / 255).astype('uint8')
        #                     ratio_visible = (visibleMask.astype('uint8') + mask_temp == 2).sum() / mask_temp.sum()
        #                     print('RATIO:', ratio_visible)
        #
        #                     if ratio_visible > 0.85:
        #                         # 3: Check if the appeared piece is visible in the current measured board
        #                         print('Piece in the current measured board:', piece.rLoc.reshape(2, -1),'Status:', piece.status)
        #
        #                             # Place is different, the placed piece may not have the same rotation? Seems not matter.
        #                         num_now +=1
        #                         # print('Piece in the current measured board:', piece_2.rLoc.reshape(2, -1))
        #
        #         if num_now>num_before:
        #             self.hand_activity = 2
        #
        #         # Corner case: if one puzzle piece is moved from a place to another place not far away (both in the hand region), our assumption of caclulating num diff does not hold
        #         if num_now>0 and num_now==num_before:
        #             # Piece in the record board: [[978]
        #             #  [589]] Status: PieceStatus.MEASURED
        #             # Piece in the record board: [[924]
        #             #  [575]] Status: PieceStatus.TRACKED
        #             # Piece in the record board: [[1085]
        #             #  [ 562]] Status: PieceStatus.TRACKED
        #             # Piece in the current measured board: [[978]
        #             #  [589]] Status: PieceStatus.MEASURED
        #             # Piece in the current measured board: [[924]
        #             #  [574]] Status: PieceStatus.MEASURED
        #             # Piece in the current measured board: [[963]
        #             #  [527]] Status: PieceStatus.MEASURED
        #
        #             # Re-check if one piece moved
        #             for piece in self.record['meaBoard'].pieces.values():
        #
        #                 if piece.status == PieceStatus.TRACKED or piece.status == PieceStatus.MEASURED:
        #                     flagFound_place = False
        #                     if np.linalg.norm(piece.rLoc.reshape(2,-1) - self.record['rLoc_hand'].reshape(2,-1))< self.param.hand_radius:
        #                         for piece_2 in meaBoard.pieces.values():
        #                             if piece_2.status == PieceStatus.TRACKED or piece_2.status == PieceStatus.MEASURED:
        #                                 if np.linalg.norm(piece_2.rLoc.reshape(2, -1) - self.record['rLoc_hand'].reshape(2, -1)) < self.param.hand_radius:
        #                                     if np.linalg.norm(piece.rLoc.reshape(2, -1) - piece_2.rLoc.reshape(2, -1)) < 50:
        #                                         flagFound_place = True
        #
        #                         # Cannot find one without move
        #                         if flagFound_place == False:
        #                             if piece.status==PieceStatus.TRACKED:
        #                                 self.hand_activity = 2
        #
        #         print('*****CHECK PLACE END*****')
        #

        # For tracking
        for record_match in self.record['match'].items():
            findFlag = False
            for match in self.manager.pAssignments.items():
                if record_match[1] == match[1]:
                    # 1) If some pieces are available on both boards, those pieces will have an updated status

                    # The new meaBoard will always have pieces of tracking_life as 0
                    record_board_temp.addPiece(meaBoard.pieces[match[0]])
                    record_match_temp[record_board_temp.id_count-1] = match[1]
                    findFlag = True
                    break

            if findFlag == False:
                # 2) If some pieces are only available on the record board, their status will be marked as TRACKED
                # Do not update INHAND ones (it could be considered as a special state)
                # if self.record['meaBoard'].pieces[record_match[0]].status!=PieceStatus.INHAND:

                # # ROI-based idea (stop for now)
                # # Todo: Seems not working.
                # if self.record['meaBoard'].pieces[record_match[0]].status != PieceStatus.INHAND:
                #     self.record['meaBoard'].pieces[record_match[0]].status = PieceStatus.TRACKED
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
                    findFlag = True
                    break

            if findFlag == False:
                # 3) If some pieces are only available on the new board, they will be added to the record board
                record_board_temp.addPiece(meaBoard.pieces[new_match[0]])
                record_match_temp[record_board_temp.id_count-1] = new_match[1]

        # Update
        self.record['meaBoard'] = record_board_temp
        self.record['match'] = record_match_temp

        # # ROI-based idea (stop for now)
        # #
        # if self.hand_activity == 0:
        #     # For pick
        #     if self.record['meaBoard'] is not None and self.record['rLoc_hand'] is not None:
        #
        #         # 0: Check if the hand moves or not visible now
        #         if rLoc_hand is None or (np.linalg.norm(rLoc_hand.reshape(2,-1)- self.record['rLoc_hand'].reshape(2,-1))>30):
        #             print('*****CHECK PICK START*****')
        #             print('PREVIOUS HAND LOC:', self.record['rLoc_hand'].reshape(2,-1))
        #
        #             # We need an updated tracked board here
        #             for key, piece in self.record['meaBoard'].pieces.items():
        #
        #                 # Corner case: if a piece has been picked up but not placed yet, it will be re-checked falsely
        #                 if piece.status == PieceStatus.TRACKED:
        #                     # 1: Check if there was piece disappearing in the hand region (last saved),
        #                     # which means not in the hand region (last saved) right now
        #
        #                     # Todo: Corner case: if a piece is not visible in the previous timestamp but shows up in the next timestep, we will believe there is a pick action.
        #                     # However, if the pieces are close to the hand, chances are that, it is unluckily not detected before but luckily detected again.
        #
        #                     # Be careful about the distance thresh (It should be large enough),
        #                     # when picked up the piece, the hand may be far from piece rLoc.
        #                     if np.linalg.norm(piece.rLoc.reshape(2,-1) - self.record['rLoc_hand'].reshape(2,-1)) < self.param.hand_radius:
        #                         print('Piece in the record board:', piece.rLoc.reshape(2, -1))
        #
        #                         # 2:  Check if most of the disappearing piece's part is visible in the current visibleMask
        #                         mask_temp = np.zeros(visibleMask.shape,dtype='uint8')
        #                         mask_temp[piece.rLoc[1]:piece.rLoc[1]+piece.y.size[1],piece.rLoc[0]:piece.rLoc[0]+piece.y.size[0]] = (piece.y.mask/255).astype('uint8')
        #                         ratio_visible = (visibleMask.astype('uint8') + mask_temp == 2).sum()/mask_temp.sum()
        #                         print('RATIO:', ratio_visible)
        #
        #                         # if ratio_visible>0.01:
        #                         #     cv2.imshow('debug_visible', mask_temp*255)
        #                         #     cv2.waitKey()
        #
        #
        #                         if ratio_visible > 0.95:
        #                             # 3: Check if the disappeared piece is visible in the current measured board, we want it to be not
        #                             flagFound_pick = False
        #                             for piece_2 in meaBoard.pieces.values():
        #                                 if np.linalg.norm(piece.rLoc.reshape(2, -1) - piece_2.rLoc.reshape(2,-1)) < 50:
        #                                     print('Piece in the current measured board:', piece_2.rLoc.reshape(2,-1))
        #                                     flagFound_pick = True
        #
        #                             if flagFound_pick is False:
        #                                 self.hand_activity = 1
        #                                 self.record['meaBoard'].pieces[key].status = PieceStatus.INHAND
        #                                 break
        #             print('*****CHECK PICK END*****')

        # Update the rLoc_hand in the end
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
