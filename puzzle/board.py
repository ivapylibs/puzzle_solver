#=============================== puzzle.board ==============================
#
# @class    puzzle.board
#
# @brief    A base representation for a puzzle board, which is basically
#           a collection of pieces.  Gets used in many different ways.
#
# A puzzle board consists of a collection of puzzle pieces and their
# locations. There is no assumption on where the pieces are located. 
# A board just keeps track of a candidate jigsaw puzzle state, or
# possibly the state of a subset of a given jigsaw puzzle.  Think of it
# as a bag class for puzzle pieces, just that they also have locality.
#
# ============================== puzzle.board =============================
#
# @file     board.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
#           Yiye Chen,              yychen2019@gatech.edu
# @date     2021/07/28 [created]
#           2021/08/01 [modified]
#           2022/07/03 [modified]
#
#
# NOTES:
#   4 space indent.
#   100 columns.
#============================== puzzle.board =============================


#============================== Dependencies =============================

#===== Environment / Dependencies
#
import cv2
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist

from puzzle.piece import Template


#
#---------------------------------------------------------------------------
#================================== Board ==================================
#---------------------------------------------------------------------------
#

class Board:
    """!
    @brief  Class description for a board, which is a locality sensitive bag.
    """

    def __init__(self, *argv):
        """
        @brief  Constructor for puzzle board. Can pass contents at
                instantiation time or delay until later.

        Args:
            *argv: The input params.
        """

        # Note that Python 3.7+ has preserved the order of the element in the dict
        # No need to use OrderedDict
        # https://stackoverflow.com/a/40007169
        self.pieces = {}  # @< The puzzle pieces.

        self.id_count = 0

        if len(argv) == 1:
            if issubclass(type(argv[0]), Board):
                self.pieces = argv[0].pieces
                self.id_count = argv[0].id_count
            elif isinstance(argv[0], np.ndarray):
                self.pieces = argv[0]
                self.id_count = len(self.pieces)
            else:
                raise TypeError('Unknown input.')
        elif len(argv) == 2:
            if isinstance(argv[0], np.ndarray) and isinstance(argv[1], int):
                self.pieces = argv[0]
                self.id_count = argv[1]
            else:
                raise TypeError('Unknown input.')
        elif len(argv) > 2:
            raise TypeError('Too many inputs.')

    #============================= addPiece ============================
    #
    def addPiece(self, piece, ORIGINAL_ID=False):
        """
        @brief  Add puzzle piece instance to the board.

        Args:
            piece: A puzzle piece instance.
        """
        # Do not directly modify piece
        piece_copy = deepcopy(piece)

        if ORIGINAL_ID:
            self.pieces[piece_copy.id] = piece_copy
        else:
            piece_copy.id = self.id_count
            self.pieces[self.id_count] = piece_copy
            self.id_count += 1

    #============================ addPieces ============================
    #
    def addPieces(self, pieces):
      for piece in pieces:
        self.addPiece(piece)


    #============================= rmPiece =============================
    #
    def rmPiece(self, id):
        """
        @brief Remove puzzle piece instance from the board

        Args:
            id: The puzzle piece id (for display)
        """

        rm_id = None
        for key in self.pieces.keys():
            if key == id:
                rm_id = id
                break

        if rm_id is not None:
            del self.pieces[rm_id]
        else:
            raise RuntimeError('Cannot find the target')
    
    #============================= getPiece ============================
    #
    def getPiece(self, id)->Template:
        """Get a puzzle piece instance given the id

        Args:
            id (int): The puzzle piece id
        """
        assert id in self.pieces.keys(), "The required piece is not in the board."
        return self.pieces[id]

    #============================== clear ==============================
    #
    def clear(self):
        """
        @brief Clear all the puzzle pieces from the board.
        """

        self.pieces = {}
        self.id_count = 0

    # def getSubset(self, subset):
    #     """
    #     @brief  Return a new board consisting of a subset of pieces.
    #
    #     Args:
    #         subset: A list of indexes for the subset of puzzle pieces.
    #
    #     Returns:
    #         A new board following the input subset.
    #     """
    #
    #     theBoard = board(np.array(self.pieces)[subset], len(subset))
    #
    #     return theBoard

    # def getAssigned(self, pAssignments):
    #     """
    #     @brief  Return a new board consisting of a subset of pieces.
    #
    #     Args:
    #         pAssignments: A list of assignments for the subset.
    #
    #     Returns:
    #         A new board following assignment.
    #     """
    #
    #     if len(pAssignments) > 0:
    #         theBoard = board(np.array(self.pieces)[np.array(pAssignments)[:, 0]], self.id_count)
    #     else:
    #         print('No assignments is found. Return an empty board.')
    #         theBoard = board()
    #
    #     return theBoard

    #=========================== testAdjacent ==========================
    #
    def testAdjacent(self, id_A, id_B, tauAdj):
        """!
        @brief  Check if two puzzle pieces are adjacent or not

        @param[in]  id_A    Id of puzzle piece A.
        @param[in]  id_B    Id of puzzle piece B.
        @param[in]  tauAdj  Distance threshold for concluding adjacency.

        @param[out] adjFlag Flag indicating adjacency of the two pieces. 
        """

        # Based on the nearest points on the contours

        # # Obtain the pts locations after subsampling
        # def obtain_sub_pts(piece, num_samples=500):
        #     pts = np.array(np.flip(np.where(piece.y.contour), axis=0)) + piece.rLoc.reshape(
        #         -1, 1)
        #     pts = pts.T
        #     idx = np.random.choice(np.arange(len(pts)), num_samples)
        #     pts = pts[idx]
        #     return pts

        # Obtain the pts locations after subsampling
        def obtain_sub_pts(piece):
            pts = []
            cnt = piece.y.contour_pts
            hull = cv2.convexHull(cnt, returnPoints=False)
            defects = cv2.convexityDefects(cnt, hull)

            if defects is not None:
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]

                    start = cnt[s][0]
                    end = cnt[e][0]
                    far = cnt[f][0]

                    # Debug only
                    # start = tuple(cnt[s][0])
                    # end = tuple(cnt[e][0])
                    # far = tuple(cnt[f][0])
                    # cv2.line(img, start, far, [0, 255, 0], 2)
                    # cv2.line(img, far, end, [0, 255, 0], 2)
                    # cv2.circle(img, far, 5, [0, 0, 255], -1)

                    pts.append(start)
                    pts.append(far)
                    pts.append(end)
                    if i > 0:
                        pts.append(((start + far) / 2).astype('int'))
                        pts.append(((far + end) / 2).astype('int'))

                # Debug only
                # cv2.imshow('demo',img)
                # cv2.waitKey()
            else:
                for i in range(hull.shape[0]):
                    pts.append(cnt[hull[i][0]][0])
                    if i > 0:
                        pts.append(((cnt[hull[i][0]][0] + cnt[hull[i - 1][0]][0]) / 2).astype('int'))

            # Remove duplicates
            pts = np.unique(pts, axis=0)

            return pts

        pts_A = self.pieces[id_A].rLoc + obtain_sub_pts(self.pieces[id_A])
        pts_B = self.pieces[id_B].rLoc + obtain_sub_pts(self.pieces[id_B])

        dists = cdist(pts_A, pts_B, 'euclidean')

        theFlag = dists.min() < tauAdj

        return theFlag

    #=============================== size ==============================
    #
    def size(self):
        """!
        @brief  Number of pieces on the board.

        @param[out] nPieces Number of pieces on the board.
        """
        return len(self.pieces)

    #============================= extents =============================
    def extents(self):
        """!
        @brief  Iterate through puzzle pieces to get tight bounding box 
                extents of the board.

        @param[out] lengths Bounding box side lengths. [x,y]
        """

        # [[min x, min y], [max x, max y]]
        bbox = self.boundingBox()

        if bbox is not None:
            lengths = bbox[1] - bbox[0]
            return lengths
        else:
            return None

    #=========================== boundingBox ===========================
    #
    def boundingBox(self):
        """!
        @brief  Iterate through pieces to get tight bounding box.

        @param[out] bbox    Bounding box coordinates: [[min x, min y], [max x, max y]]
        """

        if self.size() == 0:
            return None
            # raise RuntimeError('No pieces exist')
        else:
            # process to get min x, min y, max x, and max y
            bbox = np.array([[float('inf'), float('inf')], [0, 0]])

            # piece is a puzzleTemplate instance, see template.py for details.
            for key in self.pieces:
                piece = self.pieces[key]

                # top left coordinate
                tl = piece.rLoc

                # bottom right coordinate
                br = piece.rLoc + piece.size()

                bbox[0] = np.min([bbox[0], tl], axis=0)
                bbox[1] = np.max([bbox[1], br], axis=0)

            return bbox

    #=============================== pieceLocations ==============================
    #
    def pieceLocations(self, isCenter=False):
        """!
        @brief      Returns list/array of puzzle piece locations.

        @param[in]  isCenter    Flag indicating whether the given location is for center.
                                Otherwise, location returned is the upper left corner.

        @param[out] pLocs       A dict of puzzle piece id & location.
        """
        pLocs = {}
        for key in self.pieces:
            piece = self.pieces[key]

            if isCenter:
                pLocs[piece.id] = piece.rLoc + np.ceil(piece.y.size / 2)
            else:
                pLocs[piece.id] = piece.rLoc

        return pLocs

    #============================= toImage =============================
    #
    def toImage(self, theImage=None, ID_DISPLAY=False, COLOR=(0, 0, 0),
                ID_COLOR=(255, 255, 255), CONTOUR_DISPLAY=True, BOUNDING_BOX=True):
        """!
        @brief  Uses puzzle piece locations to create an image for visualizing them.  If given
                an image, then will place in it.
                Recommended to provide theImage & BOUNDING_BOX option off.
                Currently, we have four cases:
                - Image provided & BOUNDING_BOX off -> An exact region is visible
                - Image provided & BOUNDING_BOX on -> The visible region will be adjusted. Should have the same size image output.
                - Image not provided & BOUNDING_BOX off -> May have some trouble if some region is out of the bounds (e.g., -2) then they will be shown on the other boundary.
                - Image not provided & BOUNDING_BOX on -> A bounding box region is visible.

        @param[in]  theImage            Image to insert pieces into.
        @param[in]  ID_DISPLAY          Flag indicating displaying ID or not.
        @param[in]  COLOR               Background color.
        @param[in]  ID_COLOR            ID color.
        @param[in]  CONTOUR_DISPLAY     Flag indicating drawing contour or not.
        @param[in]  BOUNDING_BOX        Flag indicating outputting a bounding box area 
                                        (with updated (0,0)) or not (with original (0,0)).

        @param[out] theImage            Rendered image.
        """

        if theImage is not None:
            # Check dimensions ok and act accordingly, should be equal or bigger, not less.

            lengths = self.extents()

            if lengths is None:
                # No piece found
                return theImage

            lengths = lengths.astype('int')
            bbox = self.boundingBox().astype('int')

            enlarge = [0, 0]
            if bbox[0][0] < 0:
                enlarge[0] = bbox[0][0]
            if bbox[0][1] < 0:
                enlarge[1] = bbox[0][1]

            theImage_enlarged = np.zeros((theImage.shape[0] + abs(enlarge[0]), theImage.shape[1] + abs(enlarge[1]), 3),
                                         dtype='uint8')

            # Have to deal with cases where pieces are out of bounds
            if theImage.shape[1] - lengths[0] >= 0 and theImage.shape[0] - lengths[1] >= 0:
                for key in self.pieces:

                    piece = self.pieces[key]

                    piece.placeInImage(theImage_enlarged, offset=(abs(enlarge[0]), abs(enlarge[1])),
                                       CONTOUR_DISPLAY=CONTOUR_DISPLAY)

                    if ID_DISPLAY == True:
                        txt = str(piece.id)
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        char_size = cv2.getTextSize(txt, font, 0.5, 2)[0]

                        y, x = np.nonzero(piece.y.mask)

                        pos = (int(piece.rLoc[0] + np.mean(x)) - char_size[0] + abs(enlarge[0]),
                               int(piece.rLoc[1] + np.mean(y)) + char_size[1] + abs(enlarge[1]))

                        font_scale = min((max(x) - min(x)), (max(y) - min(y))) / 30
                        cv2.putText(theImage_enlarged, str(piece.id), pos, font,
                                    font_scale, ID_COLOR, 1, cv2.LINE_AA)
                        #
                        # @todo Text display should be a configuration setting.
                        #
                        #DEBUG
                        #print(font_scale)

                theImage = theImage_enlarged[abs(enlarge[0]):abs(enlarge[0]) + theImage.shape[0],
                           abs(enlarge[1]):abs(enlarge[1]) + theImage.shape[1], :]

            else:
                raise RuntimeError('The image is too small. Please try again.')
        else:

            lengths = self.extents()

            if lengths is None:
                # No piece found
                raise RuntimeError('No piece found')

            lengths = lengths.astype('int')
            bbox = self.boundingBox().astype('int')

            if BOUNDING_BOX:
                # Just the exact bounding box size
                theImage = np.full((lengths[1], lengths[0], 3), COLOR, dtype='uint8')
            else:
                # The original (0,0) and outermost point size
                theImage = np.full((bbox[1, 1], bbox[1, 0], 3), COLOR, dtype='uint8')

            for key in self.pieces:

                piece = self.pieces[key]

                if BOUNDING_BOX:
                    piece.placeInImage(theImage, offset=-bbox[0], CONTOUR_DISPLAY=CONTOUR_DISPLAY)
                else:
                    piece.placeInImage(theImage, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

                if ID_DISPLAY == True:
                    txt = str(piece.id)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    char_size = cv2.getTextSize(txt, font, 0.5, 2)[0]

                    y, x = np.nonzero(piece.y.mask)

                    if BOUNDING_BOX:
                        pos = (int(piece.rLoc[0] - bbox[0][0] + np.mean(x)) - char_size[0],
                               int(piece.rLoc[1] - bbox[0][1] + np.mean(y)) + char_size[1])
                    else:
                        pos = (int(piece.rLoc[0] + np.mean(x)) - char_size[0],
                               int(piece.rLoc[1] + np.mean(y)) + char_size[1])

                    font_scale = min((max(x) - min(x)), (max(y) - min(y))) / 100
                    cv2.putText(theImage, str(piece.id), pos, font,
                                font_scale, ID_COLOR, 2, cv2.LINE_AA)

            # # For better segmentation result, we need some black paddings
            # # However, it may cause some problems
            # theImage_enlarged = np.zeros((lengths[1] + 4, lengths[0] + 4, 3), dtype='uint8')
            # theImage_enlarged[2:-2, 2:-2, :] = theImage
            # theImage = theImage_enlarged
        return theImage

    #============================= display =============================
    #
    def display_mp(self, theImage=None, fh=None, ID_DISPLAY=False, CONTOUR_DISPLAY=False, 
                                                                   BOUNDING_BOX=False):
        """!
        @brief  Display the puzzle board as an image using matplot library.

        @param[in]  theImage
        @param[in]  fh                  Figure handle if available.
        @param[in]  ID_DISPLAY          Flag indicating displaying ID or not.
        @param[in]  CONTOUR_DISPLAY     Flag indicating drawing contour or not.

        @param[out] fh                  Figure handle.
        """

        if fh:
            # See https://stackoverflow.com/a/7987462/5269146
            fh = plt.figure(fh.number)
        else:
            fh = plt.figure()

        theImage = self.toImage(theImage=theImage, ID_DISPLAY=ID_DISPLAY, 
                                CONTOUR_DISPLAY=CONTOUR_DISPLAY,
                                BOUNDING_BOX=BOUNDING_BOX)

        plt.imshow(theImage)

        return fh


#
#---------------------------------------------------------------------------
#============================= Correspondences =============================
#---------------------------------------------------------------------------
#

#===== Environment / Dependencies
#
from dataclasses import dataclass

from scipy.optimize import linear_sum_assignment

from puzzle.pieces.matcher import MatchDifferent
from puzzle.pieces.matcher import MatchSimilar
from puzzle.pieces.matchDifferent import Moments

# ===== Helper Elements
#
# DEFINE ENUMERATED TYPE HERE FOR scoreType.
SCORE_DIFFERENCE = 0
SCORE_SIMILAR = 1


@dataclass
class CorrespondenceParms:
    matcher: any = Moments(20)

class Correspondences:

    def __init__(self, theParams=CorrespondenceParms, initBoard = None):
        """!
        @brief  Constructor for the board matcher class.

        @param[in]
            solution: A solution/calibrated board instance.
            theParams: Any additional parameters in a structure.
        """

        self.bPrior = initBoard             # @< The previous/prior board measurement.

        self.pAssignments = {}              # @< Assignments: meas to last.
        self.pAssignments_rotation = {}     # @< Assignments: meas to last rotation angles (degree).

        self.matcher = theParams.matcher    # @< Puzzle piece matcher instance.

        self.skipList = []                  # @< Set up by simulator. Skip some pieces in clutter.

        self.scoreType = None               # @< Puzzle piece comparator type.
        if isinstance(self.matcher, MatchDifferent):
            self.scoreType = SCORE_DIFFERENCE  
        elif isinstance(self.matcher, MatchSimilar):
            self.scoreType = SCORE_SIMILAR
        else:
            raise TypeError('The matcher is of wrong input.')

        # Save for debug
        self.scoreTable_shape = None

    #============================= correspond ============================
    #
    #
    def correspond(self, measBoard):
        """!
        @brief Get correspondences based on the input.

        @param[in] measBoard    Measured board.
        """

        self.bMeas = measBoard

        # Compare with previous board and generate associations
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

            #DEBUG 
            #print(ret)

        # pAssignments refers to the id of the puzzle piece
        # print(pFilteredAssignments)
        self.pAssignments = pFilteredAssignments

    #=========================== matchPieces ===========================
    #
    def matchPieces(self):
        """!
        @brief  Match all the measured puzzle pieces with previous board in a pairwise manner
                to get meas to sol.
        """

        scoreTable_shape = np.zeros((self.bMeas.size(), self.solution.size()))
        scoreTable_color = np.zeros((self.bMeas.size(), self.solution.size()))
        scoreTable_edge_color = np.zeros((self.bMeas.size(), self.solution.size(), 4))

        for idx_x, MeaPiece in enumerate(self.bMeas.pieces):
            for idx_y, SolPiece in enumerate(self.solution.pieces):

                # @todo Does not support two scoreTables. Currently using sift features (one table).
                if idx_y in self.skipList:
                    if self.scoreType == SCORE_DIFFERENCE:
                        scoreTable_shape[idx_x][idx_y] = 1e18
                    else:
                        scoreTable_shape[idx_x][idx_y] = -100
                    continue

                ret = self.matcher.score(self.bMeas.pieces[MeaPiece], self.solution.pieces[SolPiece])
                #DEBUG 
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

        # The measured piece will be assigned a solution piece
        # Some measured piece may not have a match according to the threshold.
        # self.pAssignments = self.greedyAssignment(scoreTable_shape, scoreTable_color, scoreTable_edge_color)

        self.pAssignments = self.hungarianAssignment(scoreTable_shape, scoreTable_color, scoreTable_edge_color)


    #======================= hungarianAssignment =======================
    #
    def hungarianAssignment(self, scoreTable_shape, scoreTable_color, scoreTable_edge_color):
        """!
        @brief  Run Hungarian Assignment for the score table.

        Args:
            scoreTable_shape:  The score table for the pairwise comparison (shape).
            scoreTable_color:  The score table for the pairwise comparison (color).
            scoreTable_edge_color: The score table for the pairwise comparison (edge_color).

        Returns:
            matched_id: The matched pair dict.
        """

        # Todo: Currently we only use scoreTable_shape
        pieceKeysList_bMeas    = list(self.bMeas.pieces.keys())
        pieceKeysList_solution = list(self.bPrior.pieces.keys())

        matched_id = {}

        if self.scoreType == SCORE_DIFFERENCE:
            row_ind, col_ind = linear_sum_assignment(scoreTable_shape)
        else:
            row_ind, col_ind = linear_sum_assignment(scoreTable_shape, maximize=True)

        for i, idx in enumerate(col_ind):
            matched_id[pieceKeysList_bMeas[i]] = pieceKeysList_solution[idx]

        return matched_id

    #========================= greedyAssignment ========================
    #
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

    #============================= process =============================
    #
    def process(self, bMeas):
        """
        @brief  Run correspondence pipeline to preserve identity of puzzle pieces.

        @param[in]  bMeas   Measured board.
        """

        # Reset
        self.pAssignments = {}
        self.pAssignments_rotation = {}

        self.correspond(bMeas)




#
#============================== puzzle.board ==============================
