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
from copy import deepcopy
from dataclasses import  dataclass

# from puzzle.builder.arrangement import Arrangement
from puzzle.builder.interlocking import Interlocking
from puzzle.builder.gridded import ParamGrid, Gridded
from puzzle.builder.board import Board
from puzzle.piece.template import PieceStatus
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift

from puzzle.utils.shapeProcessing import bb_intersection_over_union

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

@dataclass
class ParamPlanner(ParamGrid):
    hand_radius: int = 120
    tracking_life_thresh: int = 15

class Planner:
    def __init__(self, solver, manager:Manager, theParams=ParamPlanner):
        """
        @brief Work like a wrapper of solver & manager in the test script.

        Args:
            solver: The solver instance.
            manager: The manager instance.
            theParams: The params.
        """

        self.solver = solver
        self.manager = manager
        self.params = theParams

        # match: id to sol_id
        # It is always the updated one
        # NOTE: meaboard - previous track board (trackBoard); match: previous calculated match
        self.record = {'meaBoard': None, 'match': {}, 'rLoc_hand': None}

        # For saving the tracked board with solution board ID
        self.displayBoard = None

        # For saving the status history
        self.status_history = None

        # For saving the puzzle piece's location history
        self.loc_history = None

        # A manager instance for association between last measured board and the current measured board
        self.theManager_intra = None

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

        # # Debug only
        # cv2.imshow('debug_theMaskMea', theMaskMea)
        # cv2.waitKey()

        meaBoard = Interlocking.buildFrom_ImageAndMask(img, theMaskMea,
                                                       theParams=self.params)
        # # Debug only
        # meaBoard.pieces[10].display()
        # import matplotlib.pyplot as plt
        # plt.plot()
        return meaBoard

    def adapt(self, meaBoard, visibleMask, theImageMea, rLoc_hand=None, COMPLETE_PLAN=True, SAVED_PLAN=True, RUN_SOLVER=True, PLAN_WITH_TRACKBOARD=True):
        """
        @brief Update the tracked board/history and generate the action plan for the robot.

        Args:
            meaBoard: The measured board for the current view. Contains pieces at all the working area (include solution area)
            visibleMask: The mask image for the visible area.
            theImageMea: The original processed RGB image from the surveillance system.
            rLoc_hand: The location of the hand.
            COMPLETE_PLAN: Whether to generate the complete plan.
            SAVED_PLAN: Use the saved plan (self.plan) or not.
            RUN_SOLVER: Run solver or not.

        Returns:
            plan: The action plan.
        """

        # The idea of checking the meaBoard_ori is obsolete
        # meaBoard_ori = deepcopy(meaBoard)

        # Todo: Not sure if this hard threshold is a good idea or not.
        # Remove the measured pieces if they are too close to the hand.
        # Only meaningful when we can see a hand.
        if rLoc_hand is not None:
            meaBoard_filtered = Board()
            for piece in meaBoard.pieces.values():
                if np.linalg.norm(piece.rLoc.reshape(2, -1) - rLoc_hand.reshape(2, -1)) > self.params.hand_radius+50:
                    meaBoard_filtered.addPiece(piece)

            # Yunzhi: with the new update, it does not matter much if it is simple Board instance or an Interlocking instance or more.
            meaBoard = Interlocking(meaBoard_filtered)

        # manager processes the measured board to establish the association
        # NOTE: it is now using the meaBoard to assemble the puzzle pieces

        self.manager.process(meaBoard)

        record_board_temp = Board()
        record_match_temp = {}

        # For tracking

        # Note: The matching with the last frame may help when pieces look different from the one in the solution board (due to light)
        # But it may also hurt for a while when a piece has been falsely associated with one in the solution board

        # ============== Detect the match between the current measured board and the trackBoard ========================
        match_intra = {}    # store the association between the current measured board and the trackBoard
        match_intra_copy = {}  # Debug only
        if self.record['meaBoard'] is not None:
            # Create a new manager for association between the current measured board and the trackBoard
            self.theManager_intra = Manager(self.record['meaBoard'], ManagerParms(matcher=Sift()))
            self.theManager_intra.process(meaBoard)

            for match in self.theManager_intra.pAssignments.items():
                # We only care about the ones which do not move
                # if np.linalg.norm(meaBoard.pieces[match[0]].rLoc.reshape(2, -1) - self.record['meaBoard'].pieces[match[1]].rLoc.reshape(2, -1)) < 50:
                match_intra[match[0]]=match[1]

            match_intra_copy = deepcopy(match_intra)  # For debug only
        # ============== Update the trackBoard(self.record["meaBoard"]) and tracked match(self.record["match"]) =====================
        # ============== i.e. Updates the tracked pieces in the trackBoard =====================

        # Yunzhi: This is not necessary (Yiye's previous udpate)
        # added_piece_ids = []         # A list of piece_ids in the current meaBoard that are already added to the updated tracking board

        for record_match in self.record['match'].items():
            findFlag = False

            # First check whether the current assignment match one of the previous assignment, 
            # in which case the two pieces are treated as the same one.
            for match in self.manager.pAssignments.items():
                if record_match[1] == match[1]:
                    # 1) If some pieces are available on both boards (measured & tracked), those pieces will have an updated status

                    # Note: If the piece is put into the solution area, then we do not care if it is well associated with the tracked board or not
                    # Since they should lie on the nearby area, light effect is not so big
                    if (hasattr(self.params, 'solution_area') and self.params.solution_area[0]< meaBoard.pieces[match[0]].rLoc[0]< self.params.solution_area[2] and \
                     self.params.solution_area[1]< meaBoard.pieces[match[0]].rLoc[1]< self.params.solution_area[3]):

                        if match[0] in match_intra:
                            del match_intra[match[0]]

                        # The new meaBoard will always have pieces of tracking_life as 0
                        record_board_temp.addPiece(meaBoard.pieces[match[0]])
                        record_match_temp[record_board_temp.id_count - 1] = record_match[1]
                        # added_piece_ids.append(match[0]) # Yunzhi: This is not necessary (Yiye's previous udpate)
                        findFlag = True
                        break

                    # Only if the piece can be matched to the same one in the tracked board.
                    if match[0] in match_intra:
                        if match_intra[match[0]]==record_match[0]:
                            # Note: Only if all three associations agree, then update
                            # i.e., record_match[0]: trackBoard ID, match[0]: current meaBoard ID
                            # match_intra[match[0]]: the computed trackBoard ID by theManager_intra

                            del match_intra[match[0]]
                            # The new meaBoard will always have pieces of tracking_life as 0
                            record_board_temp.addPiece(meaBoard.pieces[match[0]])
                            record_match_temp[record_board_temp.id_count-1] = record_match[1]
                            # added_piece_ids.append(match[0]) # Yunzhi: This is not necessary (Yiye's previous udpate)
                            findFlag = True
                            break

            # Deal with the pieces in the meaBoard that match one of the previously tracked pieces (trackBoard),
            # but are not assigned to the same solBoard piece as the tracked piece.
            if findFlag == False:
                findFlag_2 = False
                # e.g, ID 1 (meaBoard)-> ID 4 (trackBoard) by match_intra & ID 4 (trackBoard) -> ID 4 (solBoard) by record_match,
                # but ID 1 (meaBoard) is not assigned to ID 4 (solBoard) by match
                if record_match[0] in match_intra.values():

                    # Get the ID for pieces in meaBoard
                    key_new = list(match_intra.values()).index(record_match[0])

                    # We only care about the cases where pieces do not move, then update them with the one in the trackBoard
                    if np.linalg.norm(meaBoard.pieces[key_new].rLoc.reshape(2,-1) - self.record['meaBoard'].pieces[record_match[0]].rLoc.reshape(2,-1)) < 50:

                        # The new meaBoard will always have pieces of tracking_life as 0
                        record_board_temp.addPiece(meaBoard.pieces[key_new])
                        record_match_temp[record_board_temp.id_count - 1] = record_match[1]
                        # added_piece_ids.append(key_new) # Yunzhi: This is not necessary (Yiye's previous udpate)
                        findFlag_2 = True
                        del match_intra[key_new]

                if findFlag_2 == False:
                    # 2) If some pieces are only available on the tracked board, their statuses will be marked as GONE or INVISIBLE (both are considered as TRACKED)

                    # Updated tracking life
                    # Todo: we have not enabled it for now, may need more experiments to see if it is useful
                    # self.record['meaBoard'].pieces[record_match[0]].tracking_life += 1

                    # # For puzzle piece state change idea
                    # Check if most of the piece's region (we use a rough bounding box size for faster speed) is visible in the current visibleMask
                    # which means we can see the area
                    # Todo: A corner case is that the piece cannot be well associated to the solution board but can be measured
                    # However, if we enable it, we may have trouble when a blank region is mistakenly considered as a piece
                    mask_temp = np.zeros(visibleMask.shape,dtype='uint8')
                    mask_temp[self.record['meaBoard'].pieces[record_match[0]].rLoc[1]:self.record['meaBoard'].pieces[record_match[0]].rLoc[1]+self.record['meaBoard'].pieces[record_match[0]].y.size[1], \
                                self.record['meaBoard'].pieces[record_match[0]].rLoc[0]:self.record['meaBoard'].pieces[record_match[0]].rLoc[0]+self.record['meaBoard'].pieces[record_match[0]].y.size[0]] \
                               = (self.record['meaBoard'].pieces[record_match[0]].y.mask/255).astype('uint8')
                    ratio_visible = (visibleMask.astype('uint8') + mask_temp == 2).sum()/mask_temp.sum()
                    # print('RATIO:', ratio_visible)

                    # Check if we can see some piece inside the ROI
                    # Todo: This is a strong prior. May not work in other cases.
                    # 1) Check if the region is most black.
                    unknownPieceFlag = False

                    if cv2.countNonZero(cv2.threshold(
                        cv2.cvtColor(cv2.bitwise_and(theImageMea, theImageMea, mask=mask_temp).astype('float32'),
                                     cv2.COLOR_BGR2GRAY), 50, 255, cv2.THRESH_BINARY)[1])/mask_temp.sum() > 0.2:
                        unknownPieceFlag = True

                    # Debug only
                    # aa = cv2.bitwise_and(theImageMea, theImageMea, mask=mask_temp)
                    # bb = cv2.cvtColor(aa, cv2.COLOR_BGR2GRAY)
                    # cc = cv2.threshold(bb, 0, 255, cv2.THRESH_BINARY)[1]
                    #
                    # cv2.imshow('cc', cc)
                    # cv2.waitKey()

                    # # 2) Check the original measured board. There might be a piece that cannot be well associated to the solution board but can be measured
                    # A corner case is that if pieces are connected to each other, we will not be able to tell if there are pieces according to the measured board
                    # So this idea is not working
                    #
                    # unknownPieceFlag = False
                    # target_bb = [self.record['meaBoard'].pieces[record_match[0]].rLoc[0],
                    #              self.record['meaBoard'].pieces[record_match[0]].rLoc[1],
                    #              self.record['meaBoard'].pieces[record_match[0]].rLoc[0] +
                    #              self.record['meaBoard'].pieces[record_match[0]].y.size[0],
                    #              self.record['meaBoard'].pieces[record_match[0]].rLoc[1] +
                    #              self.record['meaBoard'].pieces[record_match[0]].y.size[1]]
                    # for piece in meaBoard_ori.pieces.values():
                    #     query_bb = [piece.rLoc[0], piece.rLoc[1], piece.rLoc[0] + piece.y.size[0],
                    #                 piece.rLoc[1] + piece.y.size[1]]
                    #
                    #     if bb_intersection_over_union(query_bb, target_bb) > 0.1:
                    #         unknownPieceFlag = True
                    #         break


                    # Todo: Not sure how to set up the threshold
                    # Currently, if the region of the piece in the tracked board is visible in the visibleMask and not too close to the hand, then we consider it as GONE,
                    # Otherwise, we consider it as INVISIBLE
                    if unknownPieceFlag is False and ratio_visible > 0.99 and \
                            (rLoc_hand is None or \
                             (rLoc_hand is not None and \
                            np.linalg.norm(self.record['meaBoard'].pieces[record_match[0]].rLoc.reshape(2, -1) - rLoc_hand.reshape(2, -1)) > self.params.hand_radius+50)):

                        self.record['meaBoard'].pieces[record_match[0]].status = PieceStatus.GONE
                    else:
                        self.record['meaBoard'].pieces[record_match[0]].status = PieceStatus.INVISIBLE

                    # If their status has been TRACKED for a while but no update. They will be deleted from the record board.
                    # Todo: we have not enabled it for now
                    if self.record['meaBoard'].pieces[record_match[0]].tracking_life < self.params.tracking_life_thresh:
                        record_board_temp.addPiece(self.record['meaBoard'].pieces[record_match[0]])
                        record_match_temp[record_board_temp.id_count-1] = record_match[1]
                        # added_piece_ids.append(record_match[0]) # Yunzhi: This is not necessary (Yiye's previous udpate)

        # ===================================== Now go through the newly detected pieces whose assignment are found ========================
        for new_match in self.manager.pAssignments.items():
            findFlag = False
            for match in record_match_temp.items():
                if new_match[1] == match[1]:
                    # Some that have been dealt with in the previous process will be filtered out here
                    findFlag = True
                    break

            # Yunzhi: We revert Yiye's logic here to be more strict about what pieces to be loaded
            # # NOTE: added by Yiye. Not sure whether it is a good idea
            # for added_piece in record_board_temp.pieces.values():
            #     if np.linalg.norm(meaBoard.pieces[new_match[0]].rLoc.reshape(2,-1) - added_piece.rLoc.reshape(2,-1)) < 75:
            #         findFlag = True

            if findFlag == False:
                # 3) If some pieces are only available on the new board, they will be added to the record board

                if new_match[0] in match_intra:
                    # 4) If some piece can be associated to the one in the record board, throw it away
                    pass
                else:
                    record_board_temp.addPiece(meaBoard.pieces[new_match[0]])
                    record_match_temp[record_board_temp.id_count-1] = new_match[1]
                    # added_piece_ids.append(new_match[0]) # Yunzhi: This is not necessary (Yiye's previous udpate)

        # Yunzhi: We revert Yiye's logic here to be more strict about what pieces to be loaded
        # # ===========================================================================================
        # # NOTE: added by Yiye. The above will omit the pieces whose match is not found.
        # # So add below to go through the pieces whose assignment are not FOUND.
        # # Will aim to pass the test of the testing/realRunner02_dynamic.py. Not sure if it will influence others
        # # ===========================================================================================
        # # go through all the measured pieces
        #
        # remain_mea_ids = [id for id in range(len(meaBoard.pieces)) if id not in added_piece_ids]
        # # print(f"{bcolors.WARNING}The missing pieces: {remain_mea_ids}{bcolors.ENDC}")
        # # print(f"{bcolors.WARNING}The pieces number before adding the missing pieces: {len(added_piece_ids)}{bcolors.ENDC}")
        #
        # for id in remain_mea_ids:
        #     # Make sure the remain piece does not overlap with the current piece,
        #     # It might be the case since the manager is not always reliable.
        #     overlap = False
        #     for added_piece in record_board_temp.pieces.values():
        #         if np.linalg.norm(meaBoard.pieces[id].rLoc.reshape(2,-1) - added_piece.rLoc.reshape(2,-1)) < 10:
        #             overlap = True
        #
        #     if not overlap:
        #         record_board_temp.addPiece(meaBoard.pieces[id])
        #     # NOTE: since the match is not detected, just don't update the match. Will this cause bugs?
        #     # record_match_temp[record_board_temp.id_count-1] = new_match[1]
        #
        # # Yiye Update ends here.
        # # ===========================================================================================

        # Debug only
        # The tracked board before the update
        record_match_copy = deepcopy(self.record['match'])

        # Update
        self.record['meaBoard'] = record_board_temp
        self.record['match'] = record_match_temp
        self.record['rLoc_hand'] = rLoc_hand

        # For puzzle piece state change idea
        # We want to print the ID from the solution board.
        self.displayBoard = Board()

        for match in self.record['match'].items():
            # Save for analysis
            self.status_history[match[1]].append(self.record['meaBoard'].pieces[match[0]].status)
            self.loc_history[match[1]].append(self.record['meaBoard'].pieces[match[0]].rLoc)

            # # Note that it just follows the connection at the very beginning
            # self.displayBoard.addPiece(self.record['meaBoard'].pieces[match[0]], ORIGINAL_ID=True)

            # # Save for demo
            piece = deepcopy(self.record['meaBoard'].pieces[match[0]])
            piece.id = match[1]
            self.displayBoard.addPiece(piece, ORIGINAL_ID=True)

        # # Debug only
        # # 1) Hand location
        # if self.record['rLoc_hand'] is not None:
        #     print('Current hand location:', self.record['rLoc_hand'])

        # 2) Association: Measured id to solution id
        print('Association between the measured board and the solution board:', self.manager.pAssignments)

        # Note that the printed tracking id is not the one used in meaBoard, or the one used in DisplayBoard (simulator), or the one used in SolBoard.
        # tracked id to solution id
        print('Association between the tracked board and the solution board (before update):', record_match_copy)

        # Measured id to tracked id
        print('Association between the measured board and the tracked board:', match_intra_copy)

        # tracked id to solution id
        print('Association between the tracked board and the solution board (after update):', self.record['match'])

        # # 3) Status info: ID from the tracked board
        # for match in self.record['match'].items():
        #     print(f"ID{match[0]}: {self.record['meaBoard'].pieces[match[0]].status}")

        # 4) Status info: ID from the solution board.
        for match in self.record['match'].items():
            print(f"ID{match[1]}: {self.record['meaBoard'].pieces[match[0]].status}")

            # Re-compute and print the ratio_visible
            # if self.record['meaBoard'].pieces[match[0]].status != PieceStatus.MEASURED:
            #
            #     mask_temp = np.zeros(visibleMask.shape, dtype='uint8')
            #     mask_temp[self.record['meaBoard'].pieces[match[0]].rLoc[1]:
            #               self.record['meaBoard'].pieces[match[0]].rLoc[1] +
            #               self.record['meaBoard'].pieces[match[0]].y.size[1], \
            #     self.record['meaBoard'].pieces[match[0]].rLoc[0]:
            #     self.record['meaBoard'].pieces[match[0]].rLoc[0] +
            #     self.record['meaBoard'].pieces[match[0]].y.size[0]] \
            #         = (self.record['meaBoard'].pieces[match[0]].y.mask / 255).astype('uint8')
            #     ratio_visible = (visibleMask.astype('uint8') + mask_temp == 2).sum() / mask_temp.sum()
            #     print("ratio_visible: ", ratio_visible)

        print('\n')


        if RUN_SOLVER:

            # Solver plans for the measured board
            if not PLAN_WITH_TRACKBOARD:
                self.solver.setCurrBoard(meaBoard)
                self.solver.setMatch(self.manager.pAssignments, self.manager.pAssignments_rotation)
            # solver plans for the tracking board
            else:
                self.manager.process(self.record['meaBoard'])
                self.solver.setCurrBoard(self.record['meaBoard'])
                self.solver.setMatch(self.manager.pAssignments, self.manager.pAssignments_rotation)

            plan = self.solver.takeTurn(defaultPlan='order', COMPLETE_PLAN=COMPLETE_PLAN, SAVED_PLAN=SAVED_PLAN)
            # print(plan)
            return plan
        else:
            return None

    def adapt_simulator(self, meaBoard, rLoc_hand=None, COMPLETE_PLAN=True, SAVED_PLAN=True, RUN_SOLVER=True):
        """
        @brief  Update the tracked board/history and generate the action plan for the robot.
                Still with the old pick & place idea (not working on the real cases).
                Todo: To be compatible with the old version. Maybe integrated later.

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

        # manager processes the measured board to establish the association
        self.manager.process(meaBoard)

        record_board_temp = Board()
        record_match_temp = {}

        # For place
        flagFound_place = False
        if self.record['meaBoard'] is not None and self.record['rLoc_hand'] is not None:

            if not np.array_equal(rLoc_hand, self.record['rLoc_hand']):
                # Check if there was no puzzle piece in the tracker board (no matter measured or tracked) before in the hand region (last saved)
                for piece in self.record['meaBoard'].pieces.values():

                    if (piece.status == PieceStatus.MEASURED or piece.status == PieceStatus.TRACKED):
                        if np.linalg.norm(piece.rLoc - self.record['rLoc_hand'])< self.params.hand_radius:
                            flagFound_place = True
                            break

                # Check if we can see a new piece in the hand region (last saved)
                if flagFound_place is False:
                    for piece in meaBoard.pieces.values():
                        if np.linalg.norm(piece.rLoc - self.record['rLoc_hand'])< self.params.hand_radius:
                            print('The hand just dropped a piece')
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
            if not np.array_equal(rLoc_hand, self.record['rLoc_hand']):
                # Check if there was a piece in the hand region (last saved)
                for piece in self.record['meaBoard'].pieces.values():

                    # Be careful about the distance thresh (It should be large enough),
                    # when picked up the piece, the hand may be far from the original piece rLoc,
                    if piece.status == PieceStatus.TRACKED:
                        if np.linalg.norm(piece.rLoc - self.record['rLoc_hand']) < self.params.hand_radius:
                            flagFound_pick = True
                            break

                # Check if there was no puzzle piece in the hand region (last saved)
                if flagFound_pick is True:
                    flagFound_pick_2 = False
                    for piece in meaBoard.pieces.values():
                        if np.linalg.norm(piece.rLoc - self.record['rLoc_hand']) < self.params.hand_radius:
                            flagFound_pick_2 = True
                            break

                    if flagFound_pick_2 is False:
                        print('The hand just picked up a piece')

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

            """
            Right now, this occlusion idea can only work when puzzle board is not re-processed. 
            Otherwise, the connected ones will not be considered in the list. 
            As a result, same effect, so it is fine.
            
            It may not be useful for the real cases, so we remove that there.
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

    def process(self, input, rLoc_hand=None, visibleMask=None, theImageMea=None, COMPLETE_PLAN=True, SAVED_PLAN=True, RUN_SOLVER=True, planOnTrack=False):
        """
        @brief  Draft the action plan given the measured board.

        @note In principle, the process is not triggered by key but should be called every processing time

        Args:
            input:          A measured board or RGB image.
            rLoc_hand:      The location of the hand.
            visibleMask:    The mask of the visible area on the table (puzzle included).
            theImageMea:    The original processed RGB image from the surveillance system.
            COMPLETE_PLAN:  Whether to plan the whole sequence.
            SAVED_PLAN:     Use the saved plan (self.plan) or not. NOTE: this option overwrite the COMPLETE_PLAN option. 
                            (i.e. If this is True, then the COMPLETE_PLAN will be set to true)
            RUN_SOLVER:     Whether to compute the solver to get the next action plan.
                            Otherwise, only the board will be recognized and updated.
        Returns:
            plan: The action plan for the simulator to perform
        """

        # Todo: Maybe good to incorporate the measure step here for the real case
        if issubclass(type(input), Board):
            meaBoard = input
        else:
            # Only used by the synthetic case
            meaBoard = self.measure(input)

        # Todo: May need double check the unit test
        if visibleMask is not None:
            # We have the option to not plan anything but just update tracked board
            plan = self.adapt(meaBoard, visibleMask, theImageMea=theImageMea, rLoc_hand=rLoc_hand, COMPLETE_PLAN=COMPLETE_PLAN, SAVED_PLAN=SAVED_PLAN, RUN_SOLVER=RUN_SOLVER, PLAN_WITH_TRACKBOARD=planOnTrack)
        else:
            # We have the option to not plan anything but just update tracked board
            plan = self.adapt_simulator(meaBoard, rLoc_hand=rLoc_hand, COMPLETE_PLAN=COMPLETE_PLAN, SAVED_PLAN=SAVED_PLAN, RUN_SOLVER=RUN_SOLVER)

        return plan
