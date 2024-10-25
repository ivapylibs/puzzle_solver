#================================== manager ==================================
##
# @package  puzzle.manager
# @brief    Manage the tracking of puzzle pieces. 
#
# This puzzle piece manager keeps track of the puzzle pieces and their
# association over time as new imagery of the scene is captured. This
# manager stores the puzzle piece instances and organizes the code for
# data association. Even though the individual puzzle piece instances
# has some mechanism to recognize matches in their class API, the
# implementation in the manager can override those matching mechanisms
# using other considerations such as multi-piece competition or changes
# in the image and what regions are linked to those changes.
#
# As an example, this manager can get all similarity (or difference)
# scores and use them for generating assignments instead of greedily
# creating assignments for each puzzle piece independently of the other
# pieces.
#
# To be able to generate the associations, the puzzle manager should
# have a template or calibration puzzle board.
#
# @ingroup  Puzzle_Tracking
#
# @note     This code may be outdated.  A review on 2024/10/25 led to the
# understanding that the manager is quite similar to board correspondences.
# The newer code seems to use board correspondences over board.manager.
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#
# @date     2021/07/26 [created]
# @date     2021/08/01 [modified]
# @date     2024/10/20 [refactored & merged]
#

#================================== manager ==================================

#===== Environment / Dependencies
#
from dataclasses import dataclass

import numpy as np

from scipy.optimize import linear_sum_assignment

from puzzle.parser.fromLayer import FromLayer
from puzzle.piece.matchDifferent import MatchDifferent
from puzzle.piece.matchSimilar import MatchSimilar
from puzzle.piece.moments import Moments

# ===== Helper Elements
#
# DEFINE ENUMERATED TYPE HERE FOR scoreType.
SCORE_DIFFERENCE = 0
SCORE_SIMILAR = 1


@dataclass
class ManagerParms:
    matcher: any = Moments(20)
    assignmentMethod: any = 'hungarian'

#
# ================================ manager ================================
#

class Manager(FromLayer):
    """!
    @ingroup    Puzzle_Tracking
    @brief  A class for associating puzzle pieces across boards.  It "manages"
            the puzzle interpretation process over time, where each sensing
            cycle generates a new board instance.

    A puzzle manager is a base class for recovering and identifying or
    associating puzzle pieces across different board measurements, usually
    reflecting measurements at different times.  A calibrated solution board
    can also be associated to a given measured board, which then provides
    information about how to solve the board.

    There are different scoring systems for matching puzzle pieces.  This
    class manages that matching process based on a given puzzle piece Matcher
    instance and compatible feature generator from puzzle piece image patches.
    """

    # Note: trackpointer.centroidMulti -> PUZZLE.PARSER.FROMLAYER -> puzzle.manager

    def __init__(self, solution, theParams=ManagerParms):
        """
        @brief  Constructor for the puzzle piece manager class.

        Args:
            solution: A solution/calibrated board instance.
            theParams: Any additional parameters in a structure.
        """

        super(Manager, self).__init__()

        self.solution = solution  # @< The solution puzzle board.

        self.pAssignments = {}  # @< Assignments: meas to sol.
        self.pAssignments_rotation = {}  # @< Assignments: meas to sol. The rotation angles (degree).

        self.matcher = theParams.matcher  # @< Matcher instance.
        self.assignmentMethod = theParams.assignmentMethod  # @< Assignment method.

        self.skipList = [] # @< Be set up by the simulator. We want to skip some pieces that are in a clutter.

        if isinstance(self.matcher, MatchDifferent):
            self.scoreType = SCORE_DIFFERENCE  # @< The type of comparator.
        elif isinstance(self.matcher, MatchSimilar):
            self.scoreType = SCORE_SIMILAR  # @< The type of comparator.
        else:
            raise TypeError('The matcher is of wrong input.')

        # Save for debug
        self.scoreTable_shape = None

    #============================== measure ==============================
    #
    def measure(self, *argv):
        """!
        @brief Get the match based on the input.

        Args:
            I: RGB image.
            M: Mask image.
            board: The measured board.
        """

        if len(argv) == 1:
            self.bMeas = argv[0]
        else:
            I = argv[0]
            M = argv[1]
            # Call measure function from fromLayer to generate a measured board
            # self.bMeas
            super().measure(I, M)

        # Compare with ground truth/generate associates
        self.matchPieces()

        # Generate a new board for association, filtered by the matcher threshold
        pFilteredAssignments = {}
        for assignment in self.pAssignments.items():
            ret = self.matcher.compare(self.bMeas.pieces[assignment[0]], self.solution.pieces[assignment[1]])


            # Some matchers calculate the rotation as well
            # from mea to sol (counter-clockwise)
            if isinstance(ret, tuple):
                if ret[0]:
                    self.pAssignments_rotation[assignment[0]]=ret[1]

                    pFilteredAssignments[assignment[0]] = assignment[1]
            else:
                if ret:
                    self.pAssignments_rotation[assignment[0]] = \
                        self.bMeas.pieces[assignment[0]].theta-self.solution.pieces[assignment[1]].theta

                    pFilteredAssignments[assignment[0]] = assignment[1]

            # # Debug only
            # print(ret)

        # pAssignments refers to the id of the puzzle piece
        # print(pFilteredAssignments)
        self.pAssignments = pFilteredAssignments

    def matchPieces(self):
        """!
        @brief  Match all the measured puzzle pieces with the ground truth in a pairwise manner
                to get meas to sol.
        """

        scoreTable_shape = np.zeros((self.bMeas.size(), self.solution.size()))
        scoreTable_color = np.zeros((self.bMeas.size(), self.solution.size()))
        scoreTable_edge_color = np.zeros((self.bMeas.size(), self.solution.size(), 4))
        for idx_x, MeaPiece in enumerate(self.bMeas.pieces):
            for idx_y, SolPiece in enumerate(self.solution.pieces):

                # Todo: Currently, it does not support two scoreTables. We currently use the sift features, only one table.
                if idx_y in self.skipList:
                    if self.scoreType == SCORE_DIFFERENCE:
                        scoreTable_shape[idx_x][idx_y] = 1e18
                    else:
                        scoreTable_shape[idx_x][idx_y] = -100
                    continue

                ret = self.matcher.score(self.bMeas.pieces[MeaPiece], self.solution.pieces[SolPiece])

                # Debug only
                # if idx_x==11 and (idx_y==2):
                #     ret = self.matcher.score(self.bMeas.pieces[MeaPiece], self.solution.pieces[SolPiece])
                #     print('s')
                if type(ret) is tuple and len(ret) > 0:
                    scoreTable_shape[idx_x][idx_y] = np.sum(ret[0])
                    scoreTable_color[idx_x][idx_y] = np.sum(ret[1])
                    scoreTable_edge_color[idx_x][idx_y] = ret[1]
                else:
                    scoreTable_shape[idx_x][idx_y] = ret

        # Save for debug
        self.scoreTable_shape = scoreTable_shape.copy()

        if self.assignmentMethod == 'greedy':
            # The measured piece will be assigned a solution piece
            # However, for some measured piece, they may not have a match according to the threshold.
            self.pAssignments = self.greedyAssignment(scoreTable_shape, scoreTable_color, scoreTable_edge_color)
        elif self.assignmentMethod == 'hungarian':
            # Todo: Currently, it does not support scoreTable_edge_color. (We do not use edge color feature now)
            self.pAssignments = self.hungarianAssignment(scoreTable_shape, scoreTable_color, scoreTable_edge_color)
        else:
            raise TypeError('The assignment method is of wrong input.')


    def hungarianAssignment(self, scoreTable_shape, scoreTable_color, scoreTable_edge_color):
        """!
        @brief  Run the hungarianAssignment for the score table.

        Args:
            scoreTable_shape:  The score table for the pairwise comparison (shape).
            scoreTable_color:  The score table for the pairwise comparison (color).
            scoreTable_edge_color: The score table for the pairwise comparison (edge_color).

        Returns:
            matched_id: The matched pair dict.
        """

        # Todo: Currently we only use scoreTable_shape

        pieceKeysList_bMeas = list(self.bMeas.pieces.keys())
        pieceKeysList_solution = list(self.solution.pieces.keys())

        matched_id = {}

        if self.scoreType == SCORE_DIFFERENCE:
            row_ind, col_ind = linear_sum_assignment(scoreTable_shape)
        else:
            row_ind, col_ind = linear_sum_assignment(scoreTable_shape, maximize=True)


        for i, idx in enumerate(col_ind):
            matched_id[pieceKeysList_bMeas[i]] = pieceKeysList_solution[idx]

        return matched_id

    def greedyAssignment(self, scoreTable_shape, scoreTable_color, scoreTable_edge_color):
        """!
        @brief  Run the greedyAssignment for the score table.

        Args:
            scoreTable_shape:  The score table for the pairwise comparison (shape).
            scoreTable_color:  The score table for the pairwise comparison (color).
            scoreTable_edge_color: The score table for the pairwise comparison (edge_color).

        Returns:
            matched_id: The matched pair dict.
        """

        pieceKeysList_bMeas = list(self.bMeas.pieces.keys())
        pieceKeysList_solution = list(self.solution.pieces.keys())

        # Single feature
        if np.count_nonzero(scoreTable_color) == 0:
            # @note Yunzhi: Only focus on the difference in the scoreTable_shape
            matched_id = {}

            if scoreTable_shape.shape[1] == 0:
                return matched_id
            for i in range(scoreTable_shape.shape[0]):
                if self.scoreType == SCORE_DIFFERENCE:
                    j = scoreTable_shape[i].argmin()
                    # Todo: The threshold needs to be decided by the feature method
                    if scoreTable_shape[i][j] < 1e16:
                        scoreTable_shape[:, j] = 1e18
                        matched_id[pieceKeysList_bMeas[i]] = pieceKeysList_solution[j]
                else:
                    j = scoreTable_shape[i].argmax()
                    # Todo: The threshold needs to be decided by the feature method
                    if scoreTable_shape[i][j] > 2:
                        scoreTable_shape[:, j] = -100

                        matched_id[pieceKeysList_bMeas[i]] = pieceKeysList_solution[j]
        else:
            # @note Yunzhi: Currently, it is hard-coded for edge feature
            # It cannot work very well especially in real scenario.

            # Shape + Color feature

            def getKeepList(score_list, diff_thresh=150):

                # Create new lists by removing the first element or the last element
                # score_list_cmp_1 = np.delete(score_list, -1) # incremental change

                score_list_cmp_1 = np.ones_like(score_list) * score_list[0]  # absolute change with the first element
                score_list_cmp_1 = np.delete(score_list_cmp_1, -1)

                score_list_cmp_2 = np.delete(score_list, 0)

                score_diff_list = score_list_cmp_2 - score_list_cmp_1

                keep = [0]
                for idx, score_diff in enumerate(score_diff_list):
                    if not np.isnan(score_diff) and score_diff < diff_thresh:
                        keep.append(idx + 1)
                    else:
                        break

                return keep

            matched_id = {}
            if scoreTable_shape.shape[1] == 0:
                return matched_id
            for i in range(scoreTable_shape.shape[0]):
                # j = scoreTable_shape[i].argmin()

                shape_list = scoreTable_shape[i]
                ind_shape_sort = np.argsort(shape_list, axis=0)
                shape_sort_list = np.sort(shape_list, axis=0)

                # Update ind_shape_sort and shape_sort_list in a small range since
                # distance between shape features may be similar, we want to keep all of them
                keep_list = getKeepList(shape_sort_list)
                ind_shape_sort = ind_shape_sort[keep_list]  # ind in shape_list (complete)

                # Not used for now
                shape_sort_list = shape_sort_list[keep_list]

                if ind_shape_sort.size == 1:
                    # Todo: The threshold needs to be decided by the feature method
                    j = ind_shape_sort[0]
                else:

                    color_list = scoreTable_color[i][ind_shape_sort]
                    ind_color_sort = np.argsort(color_list, axis=0)  # ind in color_list (not complete)
                    color_sort_list = np.sort(color_list, axis=0)

                    # Update ind_shape_sort and shape_sort_list in a small range since
                    # distance between shape features may be similar, we want to keep all of them

                    keep_list = getKeepList(color_sort_list, 10)
                    ind_color_sort = ind_color_sort[keep_list]  # ind in color_list (not complete)

                    color_sort_list = color_sort_list[keep_list]

                    if ind_color_sort.size == 1:
                        # Todo: The threshold needs to be decided by the feature method
                        j = ind_shape_sort[ind_color_sort[0]]
                    else:
                        # Check color_sort_list, find the one with lowest edge score for now
                        edge_color_list = scoreTable_edge_color[i][ind_shape_sort[ind_color_sort]]
                        ind_edge_color = np.where(edge_color_list == np.amin(edge_color_list))

                        j = ind_shape_sort[ind_color_sort[ind_edge_color[0]]][0]

                    # # Check scoreTable_color, find the lowest for now
                    # # The index of the lowest score in the scoreTable_color[i][ind_shape_sort]
                    # j = scoreTable_color[i][ind_shape_sort].argmin()
                    # # The final index based on scoreTable_shape and scoreTable_color
                    # j = ind_shape_sort[j]

                if scoreTable_shape[i][j] < 1e16:
                    scoreTable_shape[:, j] = 1e18
                    matched_id[pieceKeysList_bMeas[i]] = pieceKeysList_solution[j]

        return matched_id

    def process(self, *argv):
        """!
        @brief  Run the tracking pipeline for image measurement or directly work
                on a measured board. Assume two modes: 1. I & M or 2. A measured board.
        Args:
            I: RGB image.
            M: Mask image.
            board: The measured board.
        """

        # Reset
        self.pAssignments = {}
        self.pAssignments_rotation = {}

        self.measure(*argv)

#
#================================== manager ==================================
