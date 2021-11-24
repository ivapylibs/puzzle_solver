# ========================= puzzle.simulator.action ========================
#
# @class    puzzle.simulator.agent
#
# @brief    The atomic action class
#
# ========================= puzzle.simulator.action ========================
#
# @file     action.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/02
#
#
# ========================= puzzle.simulator.action ========================

import numpy as np

from puzzle.piece.template import Template


class Actions():
    """
    The base action class defines all the atomic actions that an agent can execute.
    """

    def __init__(self, loc):
        self.loc = loc
        self.cache_piece = None  # piece in hand
        self.ACTION_LABELS = {
            "move": self.move,
            "pick": self.pick,
            "place": self.place,
            "pause": self.pause
        }

    def move(self, targetLoc):
        self.loc = np.array(targetLoc)
        if self.cache_piece is not None:
            self.cache_piece.setPlacement(targetLoc)

    def pick(self, piece: Template):
        # TODO:verify the piece is close

        # pick
        self.cache_piece = piece

    def place(self):
        self.cache_piece = None

    def pause(self):
        return

    def execute(self, action_label, action_param=None):
        """
        Execute an action given the action label and parameter

        TODO: currently assume all actions only take one parameter. What if some action in the future requires more? How to update the API?
        """
        if action_param is None:
            self.ACTION_LABELS[action_label]()
        else:
            self.ACTION_LABELS[action_label](action_param)
