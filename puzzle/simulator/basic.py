# ========================= puzzle.simulator.basic ========================
#
# @class    puzzle.simulator.basic
#
# @brief    This is the simplest puzzle simulator, which keeps track of a
#           puzzle board and applies atomic moves to it when requested.
#
# ========================= puzzle.simulator.basic ========================
#
# @file     basic.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/06 [created]
#           2021/08/22 [modified]
#
#
# ========================= puzzle.simulator.basic ========================

# ===== Dependencies / Packages
#
import matplotlib.pyplot as plt


# ===== Class Helper Elements
#

#
# ========================= puzzle.simulator.basic ========================
#

class basic:

    def __init__(self, thePuzzle, theFig=None):
        """
        @brief  Constructor for the class. Requires a puzzle board.

        Args:
            thePuzzle: The puzzle board info for simulation.
            theFig: The figure handle to use (optional).
        """

        self.puzzle = thePuzzle
        self.layers = list(range(self.puzzle.size()))

        self.fig = theFig

        #
        # @todo Should it also have the calibrated solution to know when the
        #       puzzle has been solved? Or should it simply not care about this
        #       part and it should be for another class instance. Leaning
        #       towards not caring since it is not part of the simulation but
        #       rather part of the interpretation of the puzzle board.
        #

    def addPiece(self, piece):
        """
        @brief  Add puzzle piece instance to the board.

        Args:
            piece:  A puzzle piece instance.
        """

        self.puzzle.addPiece(piece)

    def rmPiece(self, id):
        """
        @brief  Remove puzzle piece instance from the board.

        Args:
            id: The puzzle piece id.
        """

        self.puzzle.rmPiece(id)

    def setPieces(self, pLocs):
        """
        @brief  Sets the positions of pieces.
        @note
        Yunzhi: Since we use a dict to manage the pLocs input, it does not matter
        if pLocs have less pieces or not. So we can combine several functions together.

        Args:
            pLocs: A dict of puzzle pieces ids and their locations.

        Returns:

        """
        for ii in range(self.puzzle.size()):
            if self.puzzle.pieces[ii].id in pLocs.keys():
                self.puzzle.pieces[ii].setPlacement(pLocs[self.puzzle.pieces[ii].id])

    def takeAction(self, plan):
        """
        @brief  Perform the plan.

        Args:
            plan: A tuple (piece_id, piece_index, action_type, action)

        Returns:
            FINISHED(Signal indicating the end of plan)
        """

        FINISHED = False

        for i in plan:
            if i is None:
                print('All the matched puzzle pieces have been in position. No move.')
                FINISHED = True
            else:

                piece_id = i[0]
                piece_index = i[1]
                action_type = i[2]
                action = i[3]

                if action_type == 'rotate':
                    print(f'Rotate piece {piece_id} by {int(action)} degree')
                    self.puzzle.pieces[piece_index] = self.puzzle.pieces[piece_index].rotatePiece(
                        action)
                elif action_type == 'move':
                    print(f'Move piece {piece_id} by {action}')
                    self.puzzle.pieces[piece_index].setPlacement(action, offset=True)

        return FINISHED

    def dragPieces(self, pVecs):
        """
        @brief  Moves pieces incrementally from where it is.

        Args:
            pVecs: A dict of puzzle pieces ids and movement vector.
        """

        for ii in range(self.puzzle.size()):
            if self.puzzle.pieces[ii].id in pVecs.keys():
                self.puzzle.pieces[ii].setPlacement(pVecs[self.puzzle.pieces[ii].id], offset=True)

    def toImage(self, theImage=None, ID_DISPLAY=False, COLOR=(255, 255, 255), CONTOUR_DISPLAY=True, BOUNDING_BOX=True):
        """
        @brief  Uses puzzle piece locations to create an image for
                visualizing them.  If given an image, then will place in it.
        Args:
            theImage: The image to insert pieces into. (optional)
            ID_DISPLAY:  Flag indicating ID_DISPLAY or not.
            COLOR: The color of the background.
            CONTOUR_DISPLAY:  Flag indicating CONTOUR_DISPLAY or not.
            BOUNDING_BOX: Flag indicating display with a limited bouding box region or not.

        Returns:
            theImage(the output image)
        """

        theImage = self.puzzle.toImage(theImage=theImage, ID_DISPLAY=ID_DISPLAY, COLOR=COLOR,
                                       CONTOUR_DISPLAY=CONTOUR_DISPLAY, BOUNDING_BOX=BOUNDING_BOX)

        return theImage

    def display(self, ID_DISPLAY=True, CONTOUR_DISPLAY=True):
        """
        @brief  Displays the current puzzle board.

        Args:
            ID_DISPLAY: Flag indicating ID_DISPLAY or not.
        """

        if not self.fig:
            self.fig = plt.figure()

        self.puzzle.display(fh=self.fig, ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

#
# ========================= puzzle.simulator.basic ========================
