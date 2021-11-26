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

        self.cache_piece = None  # piece in hand

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

    def pieceInHand(self, rLoc):

        theDist = np.linalg.norm(np.array(rLoc) - np.array(self.app.rLoc))

        return theDist < 80

    def pick(self, puzzle, piece: Template = None):
        if piece is None:

            theDists = {}
            pLocTrue = puzzle.pieceLocations()

            for id in pLocTrue.keys():
                theDists[id] = np.linalg.norm(np.array(pLocTrue[id]) - np.array(self.app.rLoc))

            piece_id = min(theDists, key=theDists.get)

            for i, piece in enumerate(puzzle.pieces):
                if piece_id == piece.id:
                    piece_index = i
                    break

            piece = puzzle.pieces[piece_index]

        if self.pieceInHand(piece.rLoc):

            print('Pick the piece.')

            # Align the rLoc
            piece.rLoc = self.app.rLoc
            self.cache_piece = piece

            puzzle.rmPiece(piece.id)
        else:
            print('No piece is nearby.')

    def place(self, puzzle):

        if self.cache_piece is not None:

            print('Place the piece.')

            # Todo: Maybe with the original id?
            puzzle.addPiece(self.cache_piece)
            self.cache_piece = None
        else:
            print('No piece is hand.')

    # Todo: To be implemented
    def pause(self):
        return

    def rotate(self, action_param):

        if self.cache_piece is None:
            raise RuntimeError('There is no piece in hand')

        self.cache_piece = self.cache_piece.rotatePiece(
            action_param)

    def execute(self, puzzle, action_type, action_param=None):
        """
        Execute an action given the action label and parameter

        Overwrite the execute function since we need to keep the self.app.rLoc updated
        NOTE:This is necessary only when we are using the puzzle.template as the appearance model
        """

        # if it is pick action, then get the puzzle piece as the real parameter
        if action_type == "pick":
            if isinstance(action_param, int):
                action_param = puzzle.pieces[action_param]
                self.pick(puzzle, action_param)
            else:
                self.pick(puzzle)
        elif action_type == "rotate":
            self.rotate(action_param)
        elif action_type == "move":
            self.move(action_param)
        elif action_type == "place":
            self.place(puzzle)
        elif action_type == "pause":
            self.pause()

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
