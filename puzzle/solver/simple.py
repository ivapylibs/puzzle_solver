# ========================== puzzle.solver.simple =========================
#
# @class    puzzle.solver.simple
#
# @brief    A basic puzzle solver that just puts puzzle pieces where they
#           belong based on sequential ordering.
#
# @file     simple.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/06 [created]
#           2021/08/12 [modified]
#
#
# ========================== puzzle.solver.simple =========================

import itertools
from copy import deepcopy

# ===== Environment / Dependencies
#
import numpy as np
from puzzleSolver import PuzzlePieces, PuzzleSolver

from puzzle.solver.base import Base


# ===== Helper Elements
#


#
# ========================== puzzle.solver.simple =========================
#

class Simple(Base):

    def __init__(self, theSol, thePuzzle):
        """
        @brief  Constructor for the simple puzzle solver. Assume existence
        of solution state and current puzzle state, the match is built up by
        the manager.

        Args:
          theSol: The solution board.
          thePuzzle: The estimated board.
        """

        super(Simple, self).__init__(theSol, thePuzzle)

        self.match = None  # @< Mapping from current to desired.
        self.rotation_match = None  # @< Mapping from current to desired.

        # We assume it has followed the plan structure:
        # [(piece_id, piece_index, action_type, action), ...]
        self.plan = None

    def setCurrBoard(self, theBoard):
        """
        @brief Set up the current board.

        Args:
            theBoard (Board): A board instance.
        """
        self.current = theBoard

        # Since the current board is updated, the original plan is useless
        self.plan = None

    def setMatch(self, match, rotation_match=None):
        """
        @brief  Set up the match.

        Args:
          match: The match between the index in the measured board and the solution board.
          rotation_match: The rotation angle for each piece in the match.
        """

        self.match = match
        if rotation_match is not None:
            # The command should be minus rotation_match
            # The computed angle is following counter-clockwise order
            # while our rotation function is with clockwise order
            self.rotation_match = {}
            for key in rotation_match.keys():
                self.rotation_match[key] = -rotation_match[key]

            # self.rotation_match = -np.array(rotation_match)

    def takeTurn(self, thePlan=None, defaultPlan='order', occlusionList=[], STEP_WISE=True, COMPLETE_PLAN=False,
                 SAVED_PLAN=True):
        """
        @brief  Create a plan.

        Args:
            thePlan: A specific desired action plan. We assume it only knows (piece_id, action_type, action).
            defaultPlan: The default plan strategy.
            occlusionList: Skip the pieces in the occlusionList.
            STEP_WISE: Perform STEP_WISE(rotation & movement together) action or not.
            COMPLETE_PLAN: Create a complete plan or just a single step action.
            SAVED_PLAN: Use the saved plan (self.plan) or not

        Returns:
            plan: Processed plan list.
        """

        if SAVED_PLAN is True:
            COMPLETE_PLAN = True
        else:
            self.plan = None

        # Mandatory check on STEP_WISE. Only if rotation does not exist, the option is valid.
        if self.rotation_match is None:
            STEP_WISE = True

        # FixMe: If we implement all the actions directly, but not from self.plan, then there will be a bug

        if self.plan is None:
            if thePlan is None:
                if defaultPlan == 'order':
                    plan = self.planOrdered(occlusionList=occlusionList, STEP_WISE=STEP_WISE,
                                            COMPLETE_PLAN=COMPLETE_PLAN)
                elif defaultPlan == 'new':
                    plan = self.planNew()
                else:
                    raise RuntimeError('No default plan has been correctly initialized.')

                if SAVED_PLAN == True:
                    # Save the complete plan and keep executing it
                    self.plan = plan
                elif COMPLETE_PLAN == True:
                    plan.append(None)

            else:
                piece_id = thePlan[0]
                action_type = thePlan[1]
                action = thePlan[2]

                for key in self.current.pieces:
                    if piece_id ==key:
                        plan = [(piece_id, piece_id, action_type, action)]
                        break
                    else:
                        raise RuntimeError('Cannot find this id!')

        # If we have to re-process the image every time, then the saved plan does not make much sense
        if SAVED_PLAN and self.plan is not None:
            # Pop out the first action
            if len(self.plan) > 0:
                plan = [self.plan[0]]
                self.plan.pop(0)
                if STEP_WISE == False and len(self.plan) > 0:
                    plan.append(self.plan[0])
                    self.plan.pop(0)
            else:
                # Reset self.plan
                self.plan = None
                plan = [None]
        return plan

    def planOrdered(self, occlusionList=[], STEP_WISE=True, COMPLETE_PLAN=False):
        """
        @brief  Plan is to solve puzzle pieces in order (col-wise).

        Args:
            STEP_WISE: If disabled, we will put the puzzle piece's rotation & location
                        in a single step.
            COMPLETE_PLAN:  If enabled, we will create the complete plan instead a single step.

        Returns:
            plan: The plan list.
        """

        # The plan list
        plan = []

        # With rotation action
        if self.rotation_match is not None:
            # Create a copy of the current board
            current_corrected = deepcopy(self.current)

            for key, angle in self.rotation_match.items():
                if not np.isnan(angle):
                    current_corrected.pieces[key] = current_corrected.pieces[key].rotatePiece(angle)

            pLoc_cur = current_corrected.pieceLocations()
        else:
            # the pLoc of current ones
            pLoc_cur = self.current.pieceLocations()

        # Rearrange the piece according to the match in the solution board
        pLoc_sol = {}
        for match in self.match.items():
            # i represents id
            pLoc_sol[match[1]] = pLoc_cur[self.current.pieces[match[0]].id]

        # Obtain the correction plan for all the matched pieces
        # with id
        # may be incomplete
        theCorrect = self.desired.corrections(pLoc_sol)

        # with id
        theScores = self.desired.piecesInPlace(pLoc_sol)

        if all(value == True for value in theScores.values()):

            # if rotation_match not available or all of them have been corrected or all of them have a tiny error
            if self.rotation_match is None \
                    or np.isnan(list(self.rotation_match.values())).all() \
                    or (np.abs(list(self.rotation_match.values())) < 0.5).all():
                # print('All the matched puzzle pieces have been in position. No move.')

                plan.append(None)
                return plan

        x_max, y_max = np.max(self.desired.gc, axis=1)

        for i, j in itertools.product(range(int(x_max + 1)), range(int(y_max + 1))):

            # best_index_sol is just the next target, no matter if the assignment is ready or not
            best_index_sol = np.argwhere((self.desired.gc.T == [i, j]).all(axis=1)).flatten()[0]

            # In sol, id and index share the same value
            best_id_sol = best_index_sol

            # Check if can find the match for best_id_sol
            if best_id_sol not in theScores:
                # print(f'No assignment found')
                continue

            for match in self.match.items():
                if match[1] == best_id_sol:
                    best_id_mea = match[0]

            # Skip pieces with occlusion
            if best_id_mea in occlusionList:
                continue

            # Skip if theScore is False
            if theScores[best_id_sol] == True:
                if self.rotation_match is None:
                    # No rotation option
                    continue
                else:
                    # With rotation option
                    if np.isnan(self.rotation_match[best_id_mea]) or abs(self.rotation_match[best_id_mea]) < 0.5:
                        continue

            skipFlag = False

            # Valid rotation
            if self.rotation_match is not None and not np.isnan(self.rotation_match[best_id_mea]) and abs(
                    self.rotation_match[best_id_mea]) > 0.5:
                # # Display the plan
                # print(f'Rotate piece {best_id_mea} by {int(self.rotation_match[best_id_mea])} degree')

                plan.append((best_id_mea, best_id_mea, 'rotate', self.rotation_match[best_id_mea]))

                self.rotation_match[best_id_mea] = np.nan

                if STEP_WISE == False:
                    # # Display the plan
                    # print(f'Move piece {best_id_mea} by {theCorrect[best_id_mea]}')

                    plan.append((best_id_mea, best_id_mea, 'move', theCorrect[best_id_sol]))
                    skipFlag = True

                if COMPLETE_PLAN == False:
                    break

            # # Display the plan
            # print(f'Move piece {best_id_mea} by {theCorrect[best_id_sol]}')

            # In some rare cases, we have to skip re-append move action
            if skipFlag == True:
                continue

            plan.append((best_id_mea, best_id_mea, 'move', theCorrect[best_id_sol]))

            if COMPLETE_PLAN == False:
                break

        return plan

    def planNew(self):
        """
        @brief Implement Dr. Adan Vela's algorithm

        Returns:
            plan: The plan list.
        """

        # The plan list
        plan = []

        # With rotation action
        if self.rotation_match is not None:
            # Create a copy of the current board
            current_corrected = deepcopy(self.current)

            for key, angle in self.rotation_match.items():
                if not np.isnan(angle):
                    current_corrected.pieces[key] = current_corrected.pieces[key].rotatePiece(angle)

            pLoc_cur = current_corrected.pieceLocations()
        else:
            # the pLoc of current ones: {id_1: location_1, id_2: location_2 ...}
            pLoc_cur = self.current.pieceLocations()

        # Rearrange the piece according to the match in the solution board
        pLoc_sol = {}
        for match in self.match.items():
            pLoc_sol[match[1]] = pLoc_cur[self.current.pieces[match[0]].id]

        theCorrect = self.desired.corrections(pLoc_sol)

        # ==========================
        # @note
        # theCorrect: saves displacement from x_0 (initial x,y position) to x_d (desired x,y position)
        # like {piece_id_1: displacement_1, piece_id_2: displacement_2, ...}
        #
        # pLoc_sol: saves x_0 (initial x,y position)
        # like {piece_id_1: location_1, piece_id_2: location_2, ...}
        #
        # self.desired.pieceLocations(): saves x_d (initial x,y position)
        # like {piece_id_1: location_1, piece_id_2: location_2, ...}
        #
        # New Strategy implementation here, You can output a list of piece_id or a single piece_id
        #
        # Assume you save them to a list called piece_id_list like
        # piece_id_list = list(range(0,60))
        #
        # ==========================

        # ==========================
        # Adapted from Prof. Adan Vela's code
        xy_0 = []
        xy_d = []
        uid_list = []
        for key in pLoc_sol:
            xy_0.append(pLoc_sol[key])
            xy_d.append(self.desired.pieceLocations()[key])
            uid_list.append(key)
        pps = PuzzlePieces()
        pps.addPuzzlePieceXYs(xy_0, xy_d, uid_list=uid_list)
        mySolver = PuzzleSolver(pps, useMethod='local')
        mySolver.optimize()

        # Our id starts from 0
        piece_id_list = np.array(mySolver.solution) - 1

        # ==========================

        #
        # # Todo: Comment this line when New Strategy implementation is ready
        # piece_id_list = list(range(0, 60))

        # Generate the action plan following the piece_id_list
        for piece_id_sol in piece_id_list:
            # piece_id_sol is the one in the solution board

            for key, value in self.match.items():
                if value == piece_id_sol:
                    piece_id_mea = self.current.pieces[key].id
                    break

            if self.rotation_match is not None:
                plan.append((piece_id_mea, piece_id_mea, 'rotate', self.rotation_match[piece_id_mea]))

            plan.append((piece_id_mea, piece_id_mea, 'move', theCorrect[piece_id_sol]))

        plan.append(None)
        return plan

    def planGreedyTSP(self):
        """
        @brief      Generate a greedy plan based on TS-like problem.
        The travelling salesman problem is to visit a set of cities in a
        path optimal manner.  This version applies the same idea in a greed
        manner. That involves finding the piece closest to the true
        solution, then placing it.  After that it searches for a piece that
        minimizes to distance to pick and to place (e.g., distance to the
        next piece + distance to its true location).  That piece is added to
        the plan, and the process repeats until all pieces are planned.

        """

        pass
#
# ========================== puzzle.solver.simple =========================
