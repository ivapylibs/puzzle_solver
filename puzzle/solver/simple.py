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

from puzzle.solver.base import base


# ===== Helper Elements
#


#
# ========================== puzzle.solver.simple =========================
#

class simple(base):

    def __init__(self, theSol, thePuzzle):
        """
        @brief  Constructor for the simple puzzle solver. Assume existence
        of solution state and current puzzle state, the match is built up by
        the manager.

        Args:
          theSol: The solution board.
          thePuzzle: The estimated board.
        """

        super(simple, self).__init__(theSol, thePuzzle)

        self.match = None  # @< Mapping from current to desired.
        self.rotation_match = None  # @< Mapping from current to desired.

        # We assume it has followed the plan structure:
        # [(piece_id, piece_index, action_type, action), ...]
        self.plan = None

    def setMatch(self, match, rotation_match=None):
        """
        @brief  Set up the match.

        Args:
          match: The match between the index in the measured board and the solution board.
          rotation_match: The rotation angle for each piece in the match.
        """

        self.match = np.array(match)
        if rotation_match is not None:
            # The command should be minus rotation_match
            # The computed angle is following counter-clockwise order
            # while our rotation function is with clockwise order
            self.rotation_match = -np.array(rotation_match)

    def takeTurn(self, thePlan=None, defaultPlan='order', STEP_WISE=True, COMPLETE_PLAN=False):
        """
        @brief  Create a plan.

        Args:
            thePlan: A specific desired action plan. We assume it only knows (piece_id, action_type, action).
            defaultPlan: The default plan strategy.
            STEP_WISE: Perform STEP_WISE(move & rotation together) action or not.

        Returns:
            plan(Processed plan list)
        """

        if self.plan is None:
            if thePlan is None:
                if defaultPlan == 'order':
                    plan = self.planOrdered(STEP_WISE=STEP_WISE, COMPLETE_PLAN=COMPLETE_PLAN)
                elif defaultPlan == 'new':
                    plan = self.planNew(STEP_WISE=STEP_WISE, COMPLETE_PLAN=COMPLETE_PLAN)
                else:
                    print('No default plan has been correctly initialized.')

            else:
                piece_id = thePlan[0]
                action_type = thePlan[1]
                action = thePlan[2]

                for i, piece in enumerate(self.current.pieces):
                    if piece_id == piece.id:
                        piece_index = i
                        plan = [(piece_id, piece_index, action_type, action)]
                        break
                    else:
                        raise RuntimeError('Cannot find this id!')

        else:
            # Pop out the first action
            plan = self.plan[0]
            self.plan.pop(0)

        return plan

    def planOrdered(self, STEP_WISE=True, COMPLETE_PLAN=False):
        """
        @brief  Plan is to solve puzzle pieces in order (col-wise).

        Args:
            STEP_WISE: If disabled, we will put the puzzle piece's rotation & location
                        in a single step.
            COMPLETE_PLAN:  If enabled, we will create the complete plan instead a single step.

        Returns:
            plan(The plan list)
        """

        # The plan list
        plan = []

        # With rotation action
        if self.rotation_match is not None:
            # Create a copy of the current board
            current_corrected = deepcopy(self.current)

            for idx, angle in enumerate(self.rotation_match):
                if not np.isnan(angle):
                    current_corrected.pieces[idx] = current_corrected.pieces[idx].rotatePiece(angle)

            pLoc_cur = current_corrected.pieceLocations()
        else:
            # the pLoc of current ones
            pLoc_cur = self.current.pieceLocations()

        # Rearrange the piece according to the match in the solution board
        pLoc_sol = {}
        for i in self.match:
            pLoc_sol[i[1]] = pLoc_cur[i[0]]

        # Obtain the correction plan for all the matched pieces
        # with id
        # may be incomplete
        theCorrect = self.desired.corrections(pLoc_sol)

        # with id
        theScores = self.desired.piecesInPlace(pLoc_sol)

        if all(value == True for value in theScores.values()):

            if self.rotation_match is None or np.isnan(self.rotation_match).all():
                # print('All the matched puzzle pieces have been in position. No move.')
                # return best_id_mea, True

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

            # Find the corresponding index in the match, also for best_index_cur
            index = np.where(self.match[:, 1] == best_index_sol)[0][0]

            # Obtain the corresponding index in the measured board
            best_index_mea = self.match[:, 0][index]

            # Skip if theScore is False
            if theScores[best_id_sol] == True:
                if self.rotation_match is None:
                    # No rotation option
                    continue
                else:
                    # With rotation option
                    if np.isnan(self.rotation_match[index]):
                        continue

            # Get the corresponding id
            best_id_mea = self.current.pieces[best_index_mea].id

            if self.rotation_match is not None and not np.isnan(self.rotation_match[index]):
                # # Display the plan
                # print(f'Rotate piece {best_id_mea} by {int(self.rotation_match[index])} degree')

                # self.current.pieces[best_index_mea] = self.current.pieces[best_index_mea].rotatePiece(
                #     self.rotation_match[index])

                plan.append((best_id_mea, best_index_mea, 'rotate', self.rotation_match[index]))

                self.rotation_match[index] = None

                if STEP_WISE == False:
                    # # Display the plan
                    # # In sol, id and index share the same value, so it is safe to use theCorrect[best_index_sol]
                    # print(f'Move piece {best_id_mea} by {theCorrect[best_index_sol]}')

                    # # Execute the plan and update the current board
                    # self.current.pieces[best_index_mea].setPlacement(theCorrect[best_index_sol], offset=True)

                    plan.append((best_id_mea, best_index_mea, 'move', theCorrect[best_index_sol]))

                if COMPLETE_PLAN == False:
                    break

            # # Display the plan
            # print(f'Move piece {best_id_mea} by {theCorrect[best_index_sol]}')

            # # Execute the plan and update the current board
            # self.current.pieces[best_index_mea].setPlacement(theCorrect[best_index_sol], offset=True)

            plan.append((best_id_mea, best_index_mea, 'move', theCorrect[best_index_sol]))

            if COMPLETE_PLAN == False:
                break

        # return best_id_mea,  False
        return plan

    def planNew(self, STEP_WISE=True, COMPLETE_PLAN=False):
        """
        @brief Not ready yet

        Args:
            STEP_WISE: If disabled, we will put the puzzle piece's rotation & location
                        in a single step.
            COMPLETE_PLAN:  If enabled, we will create the complete plan instead a single step.

        Returns:
            plan(The plan list)
        """

        # The plan list
        plan = []

        # With rotation action
        if self.rotation_match is not None:
            # Create a copy of the current board
            current_corrected = deepcopy(self.current)

            for idx, angle in enumerate(self.rotation_match):
                if not np.isnan(angle):
                    current_corrected.pieces[idx] = current_corrected.pieces[idx].rotatePiece(angle)

            pLoc_cur = current_corrected.pieceLocations()
        else:
            # the pLoc of current ones: {id_1: location_1, id_2: location_2 ...}
            pLoc_cur = self.current.pieceLocations()

        # Rearrange the piece according to the match in the solution board
        pLoc_sol = {}
        for i in self.match:
            pLoc_sol[i[1]] = pLoc_cur[i[0]]

        theCorrect = self.desired.corrections(pLoc_sol)

        # ==========================
        # @note
        # theCorrect: saves displacement from x_o (initial x,y position) to x_d (desired x,y position)
        # like {piece_id_1: displacement_1, piece_id_2: displacement_2, ...}
        #
        # pLoc_sol: saves x_o (initial x,y position)
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

        # Todo: Comment this line when New Strategy implementation is ready
        piece_id_list = list(range(0, 60))

        # Generate the action plan following the piece_id_list
        for piece_id_sol in piece_id_list:
            # piece_id_sol is the one in the solution board

            for i in self.match:
                if i[1] == piece_id_sol:
                    piece_index = i[0]
                    break

            piece_id = self.current.pieces[piece_index].id
            index = np.where(self.match[:, 1] == piece_id_sol)[0][0]

            if self.rotation_match is not None:
                plan.append((piece_id, piece_index, 'rotate', self.rotation_match[index]))

            plan.append((piece_id, piece_index, 'move', theCorrect[piece_id_sol]))

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
