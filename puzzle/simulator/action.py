#========================= puzzle.simulator.action ========================
#
# @class    puzzle.simulator.agent
#
# @brief    The atomic action class
#
#========================= puzzle.simulator.action ========================

#
# @file     action.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/02
#
#
#========================= puzzle.simulator.action ========================

from puzzle.piece.template import template

class Actions():
    """
    The base action classses defines all the atomic actions that an agent can execute.
    """
    def __init__(self, loc):
        self.loc = loc
        self.cache_piece = None

    def move(self, targetLoc):
        self.loc = targetLoc
        if self.cache_piece is None:
            self.cache_piece.setPlacement(targetLoc)

    def pick(self, piece:template):
        # TODO:verify the piece is close

        # pick
        self.cache_piece = piece
    
    def place(self):
        self.cache_piece = None

    def pause(self):
        return
