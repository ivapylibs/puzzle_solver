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

from puzzle.builder.arrangement import arrangement
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

        self.plan = None

    def setMatch(self, match, rotation_match=None):
        """
        @brief  Set up the match.

        Args:
          match: The match between the index in the measured board and the solution board.
          rotation_match: The rotation for each piece in the measured board to the one in the solution board.
        """
        self.match = np.array(match)
        if rotation_match is not None:
            # The command should be minus rotation_match
            # The computed angle is following counter-clockwise order
            # while our rotation function is with clockwise order
            self.rotation_match = -np.array(rotation_match)

    # ============================== takeTurn =============================
    #
    # @brief  Perform a single puzzle solving action, which move a piece
    #         to its correct location.
    #
    def takeTurn(self, thePlan=None, defaultPlan='score'):

        if self.plan is None:
            if thePlan is None:
                if defaultPlan == 'score':
                    FINISHED = self.planByScore()
                elif defaultPlan == 'order':
                    FINISHED = self.planOrdered()
                else:
                    print('No default plan has been correctly initlized.')

            else:
                """
                @todo Get and apply move from thePlan
                Plans not figured out yet, so ignore for now.
                """
                pass
        else:
            """
            @todo Get and apply move from self.plan
            Plans not figured out yet, so ignore for now.
            """
            pass

        return FINISHED

    # ============================ planByScore ============================
    #
    # @brief      Plan is to solve in the order of lowest score.
    #             Will display the plan and update the puzzle piece.
    #
    def planByScore(self):
        """
        @brief      Plan is to solve in the order of lowest score
        Will display the plan and update the puzzle piece.

        """

        # @note
        # Check current puzzle against desired for correct placement boolean
        # Find lowest false instance
        # Establish were it must be placed to be correct.
        # Move to that location.

        # Upgrade to a builder instance to have more functions
        theArrange = arrangement(self.desired)

        # the pLoc of current ones
        pLoc_cur = self.current.pieceLocations()

        # Obtain the id in the solution board according to match
        pLoc_sol = {}
        for i in self.match:
            pLoc_sol[i[1]] = pLoc_cur[i[0]]

        theScores = theArrange.piecesInPlace(pLoc_sol)
        theDists = theArrange.distances(pLoc_sol)

        # Filter the result by piecesInPlace, only take the False into consideration
        theDists_filtered = {}
        for key in theScores:
            if theScores[key] == False:
                theDists_filtered[key] = theDists[key]

        if len(theDists_filtered) > 0:
            # Note that the key refers to the index in the solution board.
            best_index_sol = min(theDists_filtered, key=theDists_filtered.get)

            # Obtain the correction plan for all the matched pieces
            theCorrect = theArrange.corrections(pLoc_sol)

            index = np.where(self.match[:, 1] == best_index_sol)[0]

            if index.size > 0:
                # Obtain the corresponding index in the measured board
                best_index_mea = self.match[:, 0][index][0]

                # Display the plan
                print(f'Move piece {best_index_mea} by', theCorrect[best_index_sol])

                # Execute the plan and update the current board
                self.current.pieces[best_index_mea].setPlacement(theCorrect[best_index_sol], offset=True)
            else:
                print('No assignment found')
        else:
            print('All the puzzle pices have been in position. No move.')
            return True

        return False

    def planOrdered(self):
        """
        @brief  Plan is to just solve in order (col-wise).
        """

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

        # Rearrange the piece according to match in the solution board
        pLoc_sol = {}
        for i in self.match:
            pLoc_sol[i[1]] = pLoc_cur[i[0]]

        # Obtain the correction plan for all the matched pieces
        # with id
        theCorrect = self.desired.corrections(pLoc_sol)

        # with id
        theScores = self.desired.piecesInPlace(pLoc_sol)

        if all(value == True for value in theScores.values()):

            if self.rotation_match is None or np.isnan(self.rotation_match).all():
                print('All the matched puzzle pieces have been in position. No move.')
                return True


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
                # Display the plan
                print(f'Rotate piece {best_id_mea} by {int(self.rotation_match[index])} degree')
                self.current.pieces[best_index_mea] = self.current.pieces[best_index_mea].rotatePiece(
                    self.rotation_match[index])
                self.rotation_match[index] = None
                break

            # Display the plan
            print(f'Move piece {best_id_mea} by {theCorrect[best_index_sol]}')

            # Execute the plan and update the current board
            self.current.pieces[best_index_mea].setPlacement(theCorrect[best_index_sol], offset=True)
            break

        return False

    def planGreedyTSP(self):
        """
        @brief      Generate a greedy plan based on TS-like problem.
        The travelling salesman problem is to visit a set of cities in a
        path optimal manner.  This version applies the same idea in a greed
        manner. That involves finding the piece closest to the true
        solution, then placing it.  After that it seearches for a piece that
        minimizes to distance to pick and to place (e.g., distance to the
        next piece + distance to its true location).  That piece is added to
        the plan, and the process repeats until all pieces are planned.

        """

        self.plan = None  # EVENTUALLY NEED TO CODE. IGNORE FOR NOW.

#
# ========================== puzzle.solver.simple =========================
