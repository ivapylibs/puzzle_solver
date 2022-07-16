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
import numpy as np
import matplotlib.pyplot as plt
import cv2
from dataclasses import dataclass

from puzzle.utils.dataProcessing import checkKey
# ===== Class Helper Elements
#

@dataclass
class ParamBasic:

    canvas_H: int = 2500  # @< The height of the scene.
    canvas_W: int = 3500  # @< The width of the scene.

    fig_H: int = 15
    fig_W: int = 20

#
# ========================= puzzle.simulator.basic ========================
#

class Basic:

    def __init__(self, thePuzzle, theSolution=None, thePlanner=None, theFig=None, shareFlag=True, theParams=ParamBasic):
        """
        @brief  Constructor for the class. Requires a puzzle board.

        Args:
            thePuzzle: The puzzle board.
            theSolution: The solution board.
            thePlanner: The planner instance.
            theFig: The figure handle to use.
            shareFlag: Whether to share the board with the display.
            theParams: The params.
        """


        self.puzzle = thePuzzle  # @< The display board.
        self.solution = theSolution # @< The solution board.

        self.planner = thePlanner # @< The planner for the robot (without hand).

        self.params = theParams

        # Save background info
        self.canvas = np.zeros(
            (self.params.canvas_H, self.params.canvas_W, 3),
            dtype=np.uint8
        )

        self.fig = theFig

        # The setting for the displayed board. If True, we assume the planner will share
        # the same board instance with the simulator. Otherwise, they will be different.
        # Accordingly, the takeAction operation has to be translated first.
        # shareFlag is more realistic
        self.shareFlag = shareFlag

        # We only need the matched index.
        # It is only used for simulation cases and we assume that this matching result should always be perfect.
        if shareFlag == False:
            self.planner.manager.process(self.puzzle)
            self.matchSimulator = self.planner.manager.pAssignments

    def progress(self, gt_pAssignments):
        """
        @brief Check the status of the progress. (Return the ratio of the completed puzzle pieces)

        @note
        It is still a simplified function which assumes if a puzzle piece shares the
        same id occupies the same place, then it is completed.

        It is not always true when the rotation is not correct.

        Args:
            gt_pAssignments: The ground truth assignment.

        Returns:
            thePercentage: The progress.
        """

        # We should check the current display board to get all the pieces location
        pLocs = self.puzzle.pieceLocations()
        print(pLocs)

        # Get match between measured board and the solution board, it may be incomplete
        # Then we have some matched pieces id: location
        pLocs_sol = {}
        for match in self.planner.manager.pAssignments.items():
            pLocs_sol[match[1]] = pLocs[match[0]]

        print(pLocs_sol)

        # Check all the matched pieces
        # inPlace is just checking the top left corner for now. It is not 100% accurate.
        # Todo: We may add a solution board to the simulator to make it easier
        inPlace = self.planner.manager.solution.piecesInPlace(pLocs_sol, tauDist=3)

        # Another check if match is correct.
        # It only makes sense when all the pieces have been successfully extracted in the solution board.
        val_list = []
        for key in inPlace:
            if checkKey(self.planner.manager.pAssignments, gt_pAssignments, key):
                val_list.append(key)

        print(val_list)
        # # Debug only
        # print(val_list)

        thePercentage = '{:.1%}'.format(len(val_list) / len(self.planner.manager.solution.pieces))

        return thePercentage

    def addPiece(self, piece):
        """
        @brief  Add puzzle piece instance to the board.

        Args:
            piece: A puzzle piece instance.
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
        @brief Sets the positions of pieces.

        Args:
            pLocs: A dict of puzzle pieces ids and their locations.
        """
        for ii in range(self.puzzle.size()):
            if self.puzzle.pieces[ii].id in pLocs.keys():
                self.puzzle.pieces[ii].setPlacement(pLocs[self.puzzle.pieces[ii].id])

    def translateAction(self, pAssignments, piece_id):
        """
        @brief Translation based on the current match and self.matchSimulator

        Args:
            pAssignments: The planner's match.
            piece_id: Index of the piece in the planner's board.

        Returns:
            piece_id: Updated ID of the piece.
        """

        if piece_id is not None:
            # Todo: Need double check if we can always find a match here
            for match in pAssignments.items():
                if match[0] == piece_id:
                    piece_index_sol = match[1]
                    for match2 in self.matchSimulator.items():
                        if match2[1] == piece_index_sol:
                            # Get the result in the simulator's board
                            # piece_id = self.puzzle.pieces[match2[0]].id
                            piece_id = match2[0]
                            break
                    break

            return piece_id
        else:
            return None


    def takeAction(self, plan, verbose=False):
        """
        @brief Perform the plan.

        Args:
            plan: A tuple (piece_id, piece_index, action_type, action_param)

        Returns:
            finishFlag: Signal indicating the end of plan.
        """

        finishFlag = False

        for action in plan:
            if action is None:
                print('All the matched puzzle pieces have been in position. No move.')
                finishFlag = True
            else:

                piece_id = action[0]

                # Translation based on the current match and self.matchSimulator
                if self.shareFlag == False:

                    piece_id = self.translateAction(self.planner.manager.pAssignments, piece_id)

                action_type = action[2]
                action_param = action[3]

                if action_type == 'rotate':
                    if verbose:
                        print(f'Rotate piece {piece_id} by {int(action_param)} degree')
                    self.puzzle.pieces[piece_id] = self.puzzle.pieces[piece_id].rotatePiece(
                        action_param)
                elif action_type == 'move':
                    if verbose:
                        print(f'Move piece {piece_id} by {action_param}')
                    self.puzzle.pieces[piece_id].setPlacement(action_param, offset=True)


        return finishFlag

    def dragPieces(self, pVecs):
        """
        @brief  Moves pieces incrementally from where it is.

        Args:
            pVecs: A dict of puzzle pieces ids and movement vector.
        """

        for ii in range(self.puzzle.size()):
            if self.puzzle.pieces[ii].id in pVecs.keys():
                self.puzzle.pieces[ii].setPlacement(pVecs[self.puzzle.pieces[ii].id], offset=True)

    def toImage(self, theImage=None, theMask=None, ID_DISPLAY=False, COLOR=(0, 0, 0), CONTOUR_DISPLAY=True, BOUNDING_BOX=True):
        """
        @brief  Uses puzzle piece locations to create an image for
                visualizing them.  If given an image, then will place in it.
        Args:
            theImage: The image to insert pieces into. (optional)
            theMask: The binary mask to remove hand/or other instances. (optional)
            ID_DISPLAY: The flag indicating ID_DISPLAY or not.
            COLOR: The color of the background.
            CONTOUR_DISPLAY: The flag indicating CONTOUR_DISPLAY or not.
            BOUNDING_BOX: The flag indicating display with a limited bounding box region or not.

        Returns:
            theImage: The output image.
        """

        theImage = self.puzzle.toImage(theImage=theImage, ID_DISPLAY=ID_DISPLAY, COLOR=COLOR,
                                       CONTOUR_DISPLAY=CONTOUR_DISPLAY, BOUNDING_BOX=BOUNDING_BOX)

        if theMask is not None:
            theImage = cv2.bitwise_and(theImage, theImage, mask=theMask.astype('uint8'))

        # cv2.imshow('debug',cv2.resize(theImage,(0,0),fx=0.3,fy=0.3))
        # cv2.waitKey()

        return theImage

    def display(self, theImage=None, ID_DISPLAY=True, CONTOUR_DISPLAY=True, BOUNDING_BOX=True):
        """
        @brief  Displays the current puzzle board.

        Args:
            theImage: The image to insert pieces into. (optional)
            ID_DISPLAY: The flag indicating ID_DISPLAY or not.
            CONTOUR_DISPLAY: The flag indicating CONTOUR_DISPLAY or not.
            BOUNDING_BOX: The flag indicating display with a limited bounding box region or not.
        """

        if not self.fig:
            self.fig = plt.figure(figsize=(self.params.fig_W, self.params.fig_H), dpi=80)

        if theImage is None:
            self.puzzle.display(theImage=np.zeros_like(self.canvas), fh=self.fig, ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY, BOUNDING_BOX=BOUNDING_BOX)
        else:
            self.puzzle.display(theImage=theImage, fh=self.fig, ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY, BOUNDING_BOX=BOUNDING_BOX)

#
# ========================= puzzle.simulator.basic ========================
