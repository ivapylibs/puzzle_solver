# ========================= puzzle.simulator.hand ========================
#
# @class    puzzle.simulator.hand
#
# @brief    The agent simulates a subject to solve the puzzle task.
#           It takes the perceived board and the solution board,
#           and plan the next step
#
# ========================= puzzle.simulator.hand ========================
#
# @file     hand.py
#
# @author   Yiye Chen,               yychen2019@gatech.edu
#           Yunzhi Lin,              yunzhi.lin@gatech.edu
# @date     2021/08/29 [created]
#           2021/11/25 [modified]
#
# ========================= puzzle.simulator.hand ========================

import numpy as np

from puzzle.piece.template import Template


class Hand:

    def __init__(self, app: Template):
        """
        @brief  The Agent class equip the Base with the actions and the planning ability

        Args:
            app: A Template instance.
        """
        self.app = app

        self.cache_piece = None  # A piece instance in hand

    def move(self, param):

        if isinstance(param, tuple):
            targetLoc = param[0]
            offset = param[1]
        elif isinstance(param, list) or isinstance(param, np.ndarray):
            targetLoc = param
            offset = False

        self.app.setPlacement(targetLoc, offset=offset)

        if self.cache_piece is not None:
            self.cache_piece.setPlacement(targetLoc, offset=offset)

        return True

    def pieceInHand(self, rLoc):

        theDist = np.linalg.norm(np.array(rLoc) - np.array(self.app.rLoc))

        return theDist < 80

    def pick(self, puzzle, piece_id=None):
        """
        @brief Pick up a puzzle piece (can be specified).

        Args:
            puzzle: A puzzle instance.
            piece_index: The index of the puzzle.

        Returns:
            Whether have successfully performed the operation.

        """
        if piece_id is None:
            theDists = {}
            pLocTrue = puzzle.pieceLocations()

            for id in pLocTrue.keys():
                theDists[id] = np.linalg.norm(np.array(pLocTrue[id]) - np.array(self.app.rLoc))

            piece_id = min(theDists, key=theDists.get)

            # for i, piece in enumerate(puzzle.pieces):
            #     if piece_id == piece.id:
            #         piece_index = i
            #         break

        piece = puzzle.pieces[piece_id]

        if self.pieceInHand(piece.rLoc):

            print('Pick the piece.')

            # Align the rLoc
            piece.rLoc = self.app.rLoc
            self.cache_piece = piece

            puzzle.rmPiece(piece.id)

            # The operation will be going on the simulator board,
            # so we have to record the index change if needed.

            return True

        else:
            print('No piece is nearby.')

            return False

    def place(self, puzzle):
        """
        @brief Place a puzzle piece to where the hand is.

        Args:
            puzzle: A puzzle board.

        Returns:
            Whether have successfully performed the operation.
        """
        if self.cache_piece is not None:

            print('Place the piece.')

            # Todo: Maybe with the original id?
            puzzle.addPiece(self.cache_piece)
            self.cache_piece = None

            return True
        else:
            print('No piece is hand.')

            return False

    # Todo: To be implemented
    def pause(self):
        return True

    def rotate(self, action_param):

        if self.cache_piece is None:
            raise RuntimeError('There is no piece in hand')

        self.cache_piece = self.cache_piece.rotatePiece(
            action_param)

        return True

    def execute(self, puzzle, action_type, action_param=None):
        """
        Execute an action given the action label and parameter

        Overwrite the execute function since we need to keep the self.app.rLoc updated
        NOTE:This is necessary only when we are using the puzzle.template as the appearance model
        """

        # if it is pick action, then get the puzzle piece as the real parameter
        if action_type == "pick":
            return self.pick(puzzle, action_param)
        elif action_type == "rotate":
            return self.rotate(action_param)
        elif action_type == "move":
            return self.move(action_param)
        elif action_type == "place":
            return self.place(puzzle)
        elif action_type == "pause":
            return self.pause()

    def placeInImage(self, img, offset=[0, 0], CONTOUR_DISPLAY=True):
        self.app.placeInImage(img, offset, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

    @staticmethod
    def buildSphereAgent(radius, color, rLoc=None):
        app_sphere = Template.buildSphere(radius, color, rLoc)
        return Hand(app_sphere)

    @staticmethod
    def buildSquareAgent(size, color, rLoc=None):
        app_Square = Template.buildSquare(size, color, rLoc)
        return Hand(app_Square)

#
# ========================= puzzle.simulator.hand ========================
