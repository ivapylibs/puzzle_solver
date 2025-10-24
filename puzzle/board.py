#=============================== puzzle.board ==============================
##
# @package  puzzle.board
# @brief    A base representation for a puzzle board, which is basically
#           a collection of pieces.  Gets used in many different ways.
#
# A puzzle board consists of a collection of puzzle pieces and their
# locations. There is no assumption on where the pieces are located. 
# A board just keeps track of a candidate jigsaw puzzle state, or
# possibly the state of a subset of a given jigsaw puzzle.  Think of it
# as a bag class for puzzle pieces, just that they also have locality.
#
# @ingroup  PuzzleSolver
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2024/10/20 [refactored and merged]
# @date     2022/07/03 [modified]
# @date     2021/08/01 [modified]
# @date     2021/07/28 [created]
#
#! NOTES: 4 space indent. 100 columns.
#
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
from puzzle.piece import PieceStatus
from scipy.signal import convolve2d

#===== Environment / Dependencies [Correspondences]
#
from dataclasses import dataclass

from scipy.optimize import linear_sum_assignment

from detector.Configuration import AlgConfig
from puzzle.pieces.matcher import MatchDifferent
from puzzle.pieces.matcher import MatchSimilar
import puzzle.pieces.matchDifferent as diffScore
import puzzle.pieces.matchSimilar as simScore


#
#---------------------------------------------------------------------------
#================================== Board ==================================
#---------------------------------------------------------------------------
#

class Board:
    """!
    @ingroup  PuzzleSolver
    @brief  Class description for a board, which is a locality sensitive bag.
    """

    def __init__(self, *argv):
        """!
        @brief  Constructor for puzzle board. Can pass contents at
                instantiation time or delay until later.

        Args:
            *argv: The input params.
        """

        # Note that Python 3.7+ has preserved the order of the element in the dict
        # No need to use OrderedDict
        # https://stackoverflow.com/a/40007169
        self.pieces = {}                # @< The puzzle pieces.
        self.id_count = 0               # @< Internal ID count for pieces (affects new ID assignments)

        if len(argv) == 1:
            if issubclass(type(argv[0]), Board):
                self.pieces   = argv[0].pieces
                self.id_count = argv[0].id_count
            elif isinstance(argv[0], np.ndarray):
                self.pieces   = argv[0]
                self.id_count = len(self.pieces)
            else:
                raise TypeError('Unknown input.')

        elif len(argv) == 2:
            if isinstance(argv[0], np.ndarray) and isinstance(argv[1], int):
                self.pieces   = argv[0]
                self.id_count = argv[1]
            else:
                raise TypeError('Unknown input.')

        elif len(argv) > 2:
            raise TypeError('Too many inputs.')

    #============================= addPiece ============================
    #
    def addPiece(self, piece, ORIGINAL_ID=False):
        """!
        @brief  Add puzzle piece instance to the board.

        @param[in]  piece           Puzzle piece instance.
        @param[in]  ORIGINAL_ID     Flag indicating where to keep piece ID or re-assign.
        """
        # Do not directly modify piece
        piece_copy = deepcopy(piece)

        if ORIGINAL_ID:
            self.pieces[piece_copy.id] = piece_copy
        else:
            piece_copy.id = self.id_count+1
            self.pieces[self.id_count] = piece_copy
            self.id_count += 1

    #============================ addPieces ============================
    #
    def addPieces(self, pieces):
      """!
      @brief    Add puzzle piece to board.
      """

      for piece in pieces:
        self.addPiece(piece)


    #===================== addPieceFromMaskAndImage ====================
    #
    def addPieceFromMaskAndImage(self, theImage, theMask, \
                                 centroidLoc=None, cLoc=None):
        """!
        @brief  Given a mask and an image of same base dimensions, use to
                instantiate a puzzle piece template.  

        This implementation assumes that a whole image and an image-wide mask 
        are provided for recovering a single piece.  Then cLoc is not needed. 
        rLoc can still be used.

        @param[in]  theMask     Mask of individual piece.
        @param[in]  theImage    Source image with puzzle piece.
        @param[in]  cLoc        Corner location of puzzle piece [optional: None].
        """

        mi, mj = np.nonzero(theMask)
        bbTL = np.array([np.min(mi), np.min(mj)])
        bbBR = np.array([np.max(mi), np.max(mj)])+1

        pcMask  = theMask[bbTL[0]:bbBR[0], bbTL[1]:bbBR[1]]
        pcImage = theImage[bbTL[0]:bbBR[0], bbTL[1]:bbBR[1], :]

        if (cLoc is None):
          pcLoc = np.array([bbTL[1],bbTL[0]])
        else:
          pcLoc = cLoc

        self.addPiece(Template.buildFromMaskAndImage(pcMask, pcImage, pcLoc, \
                                                     centroidLoc=centroidLoc))

    #============================= rmPiece =============================
    #
    def rmPiece(self, id):
        """
        @brief Remove puzzle piece instance from board

        @param[in]  id  ID label of piece to remove.

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
        """!
        @brief  Get puzzle piece instance based on id

        @param[out] thePiece    Returns the puzzle piece matcing the ID (if exists)
        """
        assert id in self.pieces.keys(), "The required piece is not in the board."
        return self.pieces[id]

    #============================== offset =============================
    #
    def offset(self, dr):
        """!
        @brief  Offset the location of the entire puzzle in the board.

        @param[in]  dr  Offset in pixel units (dx, dy).
        """

        for pk in self.pieces:
          self.pieces[pk].setPlacement(dr, isOffset = True)


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

    #============================= relabel =============================
    #
    def relabel(self, newLabels, idContinue):
        """!
        @brief  Relabel the puzzle piece IDs in the board using new label reassignments
                and adjust IDs for those without reassignment.

        The relabel operation is to preserve label consistency over time for a board.  
        That way, when plotting or displaying the board, the display is sensible amongst other
        reasons.  The use of iContinue is to prevent an unassigned piece from displaying
        its original label that might duplicate a label reassignment or even be associated
        to a previously seen, but currently not seen, piece.  Over the long term, we want
        the IDs to be unique, at least for the known pieces.  

        The current approach does not care to handle birth/death outcomes that result in
        a new piece being assigned an ID matching that of a previously new/birthed piece that
        then disappeared/died.

        It is up to the calling context to ensure that the new ID labels are correct, and that
        the pieces missing labels should be given new IDs starting from idContinue.

        @param[in]  newLabels   Should be board index to new ID tuple list.
        @param[in]  idContinue  Index to continue from for unmatched pieces.

        """

        # [1] Relabel the known pieces.
        #
        iLabeled = set()
        for pair in newLabels:
            #DEBUG
            #print("Assign piece number" + str(pair[0]) + "of " + str(self.size()) + " to ID" + str(pair[1]))
            self.pieces[pair[0]].id = pair[1]
            iLabeled.add(pair[0])

            # @note For now doing naive assignment.  Not sure if good idea to assume that
            #       assignment id is same as association numbers due to potential for
            #       birth/death in other instances.  
            #       Does that concept apply to puzzle pieces placed in solution area?
            #
            #       10/26: Above might be corrected.  Need further testing to confirm.
            #               Added note that outer context needs to provide proper ID.
            #               No checking for correctness: not possible given what is known
            #               in this context.

        iUnlabeled = set(range(self.size())).difference( iLabeled )

        # [2] Get un-matched pieces and assign new IDs
        #
        # @todo This part is untested as of 10/26 but should work. No detected births in current test suite.
        #
        # @todo 2024/12/07 Did get some errors here.  Not sure why though.  They don't happen
        #       anymore, so the problem may be from elsewhere.  Nevertheless, this routine should
        #        not be crashing!  Somehow there is an unlabeled piece (whose index might be too
        #        big/invalid) and then it bonks out because pieces[i] can't be indexed.  Why?

        # DEBUG - Trying to figure out problem from 2024/12/07 above.
        #print(type(self))
        #print(self.size())
        #print(self.pshape)
        #print(newLabels)
        #print(idContinue)
        #print(iLabeled)
        #DEBUG
        #print(iUnlabeled)
        idSet = idContinue
        for i in iUnlabeled:
          self.pieces[i].id = idSet
          idSet = idSet + 1
          #DEBUG
          print("New piece. New ID. Displaying to confirm functionality. Delete once confirmed.")

      
    #=========================== markMissing ===========================
    #
    def markMissing(self, indSetMeasured):
        """!
        @brief  Given set of indices to measured pieces, mark remaining as unmeasured.

        @param[in] indSetMeasured   Index set indicating measured pieces.
        """

        indUnlabeled = set(range(self.size())).difference(indSetMeasured) 
        for i in indUnlabeled:
          #DEBUG
          #print("Missing: " + str(i) + " == " + str(self.pieces[i].id))
          if i in self.pieces:
            self.pieces[i].status = PieceStatus.GONE

        # @todo What is proper status for these pieces?  Shouldn't it agree with
        #       the puzzle piece status enumerations?? Need to resolve.
        #
        # TODO: Resolve status assignment here.  Maybe send as argument?
        #

    #=============================== size ==============================
    #
    def size(self):
        """!
        @brief  Number of pieces on the board.

        @param[out] nPieces     Number of pieces on the board.
        """
        return len(self.pieces)

    #============================= extents =============================
    #
    def extents(self):
        """!
        @brief  Iterate through puzzle pieces to get tight bounding box 
                extents of the board.

        @param[out] lengths Bounding box side lengths. [x,y]
        """

        # [[min x, min y], [max x, max y]]
        bbox = self.boundingBox()
        #DEBUG
        #print(f'bbox =  {bbox}')

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

                #print((piece.y.pcorner, piece.rLoc, piece.size(), tl, br))
                #DEBUG VISUAL
                #import ivapy.display_cv as display
                #display.rgb(piece.y.image)
                #display.wait()

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

    #======================== fromImageAndLabels =======================
    #
    def fromImageAndLabels(self, theImage, theLabels):

      lMax = np.amax(theLabels)

      for ii in range(1,1+lMax.astype(int)):
        self.addPiece(Template.buildFromFullMaskAndImage(theLabels == ii, theImage))

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
            #print(theImage.shape)
            #print(theImage_enlarged.shape)
            #print(lengths)
            #if theImage.shape[1] - lengths[0] < 0 or theImage.shape[0] - lengths[1] < 0:
            #  theImage_enlarged = np.zeros((lengths[1]+1,lengths[0]+1,3))

            if True or theImage.shape[1] - lengths[0] >= 0 and theImage.shape[0] - lengths[1] >= 0:
                for key in self.pieces:

                    piece = self.pieces[key]

                    piece.placeInImage(theImage_enlarged, offset=(abs(enlarge[0]), abs(enlarge[1])),
                                       CONTOUR_DISPLAY=CONTOUR_DISPLAY)

                    if ID_DISPLAY == True:
                        txt = str(piece.id)
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        char_size = cv2.getTextSize(txt, font, 1, 1)[0]

                        y, x = np.nonzero(piece.y.mask)

                        # @todo  This should be rLoc or y.pcorner?
                        pos = (int(piece.rLoc[0] + np.mean(x)) - char_size[0] + abs(enlarge[0]),
                               int(piece.rLoc[1] + np.mean(y)) + char_size[1] + abs(enlarge[1]))

                        font_scale = 1 #min((max(x) - min(x)), (max(y) - min(y))) / 30
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
            bbox    = self.boundingBox().astype('int')

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
                    char_size = cv2.getTextSize(txt, font, 0.15, 2)[0]

                    y, x = np.nonzero(piece.y.mask)

                    if BOUNDING_BOX:
                        print("bbox")
                        pos = (int(piece.rLoc[0] - bbox[0][0] + np.mean(x)) - char_size[0],
                               int(piece.rLoc[1] - bbox[0][1] + np.mean(y)) + char_size[1])
                    else:
                        pos = (int(piece.y.pcorner[0] + np.mean(x)) - 3*char_size[0],
                               int(piece.y.pcorner[1] + np.mean(y)) + char_size[1])

                    font_scale = 1 #np.floor(min((max(x) - min(x)), (max(y) - min(y))) / 100)
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
    def display_mp(self, theImage=None, ax=None, fh=None, ID_DISPLAY=False, CONTOUR_DISPLAY=False, 
                                                                   BOUNDING_BOX=False):
        """!
        @brief  Display the puzzle board as an image using matplot library.

        @param[in]  theImage
        @param[in]  fh                  Figure handle if available.
        @param[in]  ID_DISPLAY          Flag indicating displaying ID or not.
        @param[in]  CONTOUR_DISPLAY     Flag indicating drawing contour or not.
        @param[in]  ax                  Subplot Axes if available

        @param[out] fh                  Figure handle.
        """
        
        theImage = self.toImage(theImage=theImage, ID_DISPLAY=ID_DISPLAY, 
                                CONTOUR_DISPLAY=CONTOUR_DISPLAY,
                                BOUNDING_BOX=BOUNDING_BOX)
        
        if ax is not None:  # Plot in a subplot
            ax.clear()  
            plt.imshow(theImage) 

        else:  # Create or update a full figure
            if fh:  
                fh = plt.figure(fh.number)  
            else:  
                fh = plt.figure()
            plt.imshow(theImage)

            return fh

    #============================= display_cv ============================
    #
    def display_cv(self, theImage=None, fh=None, ID_DISPLAY=False, CONTOUR_DISPLAY=False, 
                                                 BOUNDING_BOX=False, window_name='Puzzle'):
        """!
        @brief  Display the puzzle board as an image using matplot library.

        @param[in]  theImage
        @param[in]  fh                  Figure handle if available.
        @param[in]  ID_DISPLAY          Flag indicating displaying ID or not.
        @param[in]  CONTOUR_DISPLAY     Flag indicating drawing contour or not.

        @param[out] fh                  Figure handle.
        """
        import ivapy.display_cv as display

        #DEBUG
        #print(f'display shape: {np.shape(theImage)}.')
        theImage = self.toImage(theImage=theImage, ID_DISPLAY=ID_DISPLAY, 
                                CONTOUR_DISPLAY=CONTOUR_DISPLAY,
                                BOUNDING_BOX=BOUNDING_BOX)

        #DEBUG
        #print("display now")
        display.rgb(theImage, window_name = window_name)
        #print("display done")

#
#---------------------------------------------------------------------------
#================================== SolutionBoard ==========================
#---------------------------------------------------------------------------
#

class SolutionBoard(Board):
    """!
    @ingroup  PuzzleSolver
    @brief  Solution board stores information about the solution board.
    """
    def __init__(self, *argv):
        """!
        @brief  Constructor for puzzle solution board. Can pass contents at
                instantiation time or delay until later.

        Args:
            *argv: The input params.
        """

        super().__init__(*argv)
        # Dict containing id to zone mapping
        self.zones = {}
 
    #===================== addPieceFromMaskAndImage ====================
    #
    def addPieceFromMaskAndImage(self, theImage, theMask, centroidLoc=None, cLoc=None, zone=0):
        """!
        @brief: Overrides parent method with zone value
        """
        super().addPieceFromMaskAndImage(theImage, theMask, centroidLoc, cLoc)
        self.zones[self.id_count-1] = zone

    #======================== createPartialBoard =======================
    def createPartialBoard(self, recordedBoard, solutionStateMask: np.ndarray, threshold=0.1):
        """!
        @brief  Create a partial board from the recorded board and solution state mask.

        @param[in]  recordedBoard      The recorded board to create the partial board from.
        @param[in]  solutionStateMask  The mask indicating the solution state.
        """
        # Implementation goes here

        # Apply a convolution operation on solutionStateMask to get scores at
        # each potential piece location.
        kernel = np.ones((5, 5), dtype=np.float32) / 25.0
        convolved = convolve2d(solutionStateMask, kernel, mode='same')


        # For each piece in recordedBoard, check if its location
        # corresponds to a low score in the convolved mask.
        # If so, add it to the partial board.

        for key in recordedBoard.pieces:
            piece = recordedBoard.pieces[key]

            # Check the score at centroid location
            centroid = piece.centroidLoc.astype(int)
            score = convolved[centroid[1], centroid[0]]

            if score < threshold:
                self.addPiece(piece, ORIGINAL_ID=False)
                self.zones[self.id_count-1] = recordedBoard.zones.get(key, 0)

#---------------------------------------------------------------------------
#=================== Configuration Node : Correspondences ==================
#---------------------------------------------------------------------------
#

@dataclass
class CorrespondenceParms:
    matcher: any = diffScore.Moments(20)

# ===== Helper Elements
#
# DEFINE ENUMERATED TYPE HERE FOR scoreType.
SCORE_DIFFERENCE = 0
SCORE_SIMILAR = 1

class CfgCorrespondences(AlgConfig):
  '''!
  @ingroup  PuzzleSolver
  @brief  Configuration setting specifier for Correspondences class.
  

  The different configuration settings are:
  | field        | influences or controls |
  | ------------ | ---------------------- | 
  | doUpdate     | Boolean indicating whether to update IDs with assigned piece IDs or not. |
  | haveGarbage  | Include garbage classes for pieces? Pemits non-assignment if too off. |
  | tauGarbage   | Value to apply to garbage classes. How threshold applies is based on matcher type |
  | forceMatches | Boolean indicating whether matches should be forced or post-filtered and removed. |
  | matcher      | String indicating what Matcher to use. |
  | matchParams  | Matcher parameter settings as a dictionary. |

  @note Added but not yet implemented: haveGarbage, tauGarbage, forceMatches.
        They have no influence on processing.  This is being worked on.
  '''

  #============================= __init__ ============================
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief        Constructor of configuration instance.
  
    @param[in]    cfg_files   List of config files to load to merge settings.
    '''
    if (init_dict == None):
      init_dict = CfgCorrespondences.get_default_settings()

    super().__init__(init_dict, key_list, new_allowed)


  #========================= get_default_settings ========================
  #
  # @brief    Recover the default settings in a dictionary.
  #
  @staticmethod
  def get_default_settings():
    '''!
    @brief  Defines most basic, default settings for RealSense D435.

    @param[out] default_dict  Dictionary populated with minimal set of
                              default settings.
    '''
    default_dict = dict(doUpdate = True, haveGarbage = False, tauGarbage = float('inf'),
                   forceMatches = True,
                   matcher = 'Moments',  
                   matchParams = diffScore.CfgMoments.get_default_settings())

    return default_dict

  #============================= buildNearest ============================
  #
  #
  @staticmethod
  def buildNearest():
    matchCfg = CfgCorrespondences();
    matchCfg.matcher = 'Distance'
    matchCfg.matchParams = None      # None means to use default settings.
    return matchCfg

  #=========================== buildColorMatchCV===========================
  #
  #
  @staticmethod
  def buildColorMatchCV():
    matchCfg = CfgCorrespondences();
    matchCfg.matcher = 'ColorHistCV'
    matchCfg.matchParams = None      # None means to use default settings.
    return matchCfg

#
#---------------------------------------------------------------------------
#============================= Correspondences =============================
#---------------------------------------------------------------------------
#


class Correspondences:
    """!
    @ingroup  PuzzleSolver
    @brief    Class that compares two boards and generates correspondences across them.
   
    The comparison technique and properties are completely up to the programmer/engineer
    to establish.  This class simply structures and faclitates the implementation.  There
    is an implicit static assumption underlying the elements temporal evolution.
    """

    def __init__(self, theParams=CfgCorrespondences(), initBoard = None):
        """!
        @brief  Constructor for the board matcher class.

        @param[in]
            solution: A solution/calibrated board instance.
            theParams: Any additional parameters in a structure.
        """

        self.params = theParams             # @< Runtime parameters.
        self.boardEstimate  = initBoard     # @< The board estimate (prior & posterior).
        self.boardMeasurement = None        # @< The most recently measured board.
        self.pAssignments = {}              # @< Assignments: meas to last.
        self.pAssignments_rotation = {}     # @< Assignments: meas to last rotation angles (degree).

        self.matcher = Correspondences.buildMatcher(theParams.matcher, theParams.matchParams)

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
    def correspond(self):
        """!
        @brief Get correspondences based on the most recent measurement (contained).

        """

        if (self.boardEstimate is None):
          #DEBUG
          #print('Setting to measured board since there is no prior. Trivial correspondence.')

          self.boardEstimate = self.boardMeasurement

          keyList = self.boardMeasurement.pieces.keys()
          matched_id = {}

          for i in keyList:
            matched_id[i] = i

          self.pAssignments = matched_id

        else:
          #DEBUG
          #print('C-process | Generating correspondences.')

          # Compare with previous board and generate associations
          # Associations are stored in member variable (pAssignments).
          self.matchPieces()

          # Generate a new board for association, filtered by the matcher threshold. At this point,
          # the associations are candidate associations.  They are not locked in.  If the matcher
          # comparator indicates that the two associated elements are the same, then the
          # assignment is preserved.  Otherwise, it is effectively tossed out.
          #
          # @todo This seems weird, since a variant of the Hungarian should permit the same
          #       outcome more natively.  The variant should have some sort of threshold
          #       for association.  Thus, not only does it seek the best match but it seeks the
          #       best passing match, where there is usually a garbage match score that must
          #       be beat for the association to occur.  Need more in depth review to see if
          #       this is the case.
          #
          pFilteredAssignments = {}
          for assignment in self.pAssignments.items():
              # @todo   If adding option to have no match, taht means a match to a garbage class
              #         whose index will be greater than the number of pieces in the compared board.
              #         When that happens, the comparison should be rejected. ret = False.
              #         Need to add this when haveGarbage option is coded up.

              ret = self.matcher.compare(self.boardMeasurement.pieces[assignment[0]], self.boardEstimate.pieces[assignment[1]])
  
              # @todo PAV[10/16] Need to remove this part.  A different process should try to 
              #       decode or act on the rigid body displacement information.  Maybe even the
              #       update function.  This is part of the tracker to work out, not part of the
              #       assignment system though it might need or benefit from the displacement
              #       information.
              # @todo PAV[11/14] Changing would break to much code.  Need to first do a review or
              #       where needed and used, what impacts on code there would be, and what all needs
              #       to happen at once to resolve.  Will require a branch to resolve.
              #       Looks like uses internally derived orientation to
              #       establish rotation alignment if the SIFT approach is not
              #       used.
              #
              # Some matchers calculate the rotation as well from mea to sol (counter-clockwise)
              if isinstance(ret, tuple):
                  if (self.params.forceMatches):
                      self.pAssignments_rotation[assignment[0]]=ret[1]
                      pFilteredAssignments[assignment[0]] = assignment[1]
                  elif ret[0]:
                      self.pAssignments_rotation[assignment[0]]=ret[1]
                      pFilteredAssignments[assignment[0]] = assignment[1]
              else:
                  if (self.params.forceMatches):
                      self.pAssignments_rotation[assignment[0]] = \
                                          self.boardMeasurement.pieces[assignment[0]].theta \
                                          - self.boardEstimate.pieces[assignment[1]].theta
                      pFilteredAssignments[assignment[0]] = assignment[1]
                  elif ret:
                      self.pAssignments_rotation[assignment[0]] = \
                                          self.boardMeasurement.pieces[assignment[0]].theta \
                                          - self.boardEstimate.pieces[assignment[1]].theta
                      pFilteredAssignments[assignment[0]] = assignment[1]
  
  
          # pAssignments refers to the id of the puzzle piece
          #
          self.pAssignments = pFilteredAssignments

          #DEBUG
          #print(self.pAssignments)

    #=========================== matchPieces ===========================
    #
    def matchPieces(self):
        """!
        @brief  Match all the measured puzzle pieces with board prior in a pairwise manner
                to get meas to prior. Only gets matches, does not act on them.


        The matching outcome is internally stored in member variable (pAssignments).
        
        """

        # @todo Removed the multiple score tables (via commenting).  Best for there to be
        #       a multi-objective Matching class that takes care of everything properly.
        #       Don't have the Correspondences class assume this responsibility because
        #       it negatively impacts abstraction capabilities. Delete code when revisions
        #       confirmed to work.
        # @note Moving to a single score table.
        #
        #scoreTable_shape = np.zeros((self.boardMeasurement.size(), self.boardEstimate.size()))
        #scoreTable_color = np.zeros((self.boardMeasurement.size(), self.boardEstimate.size()))
        #scoreTable_edge_color = np.zeros((self.boardMeasurement.size(), self.boardEstimate.size(), 4))

        # @todo What about having a garbage collecting match? with score?
        #
        scoreTable = np.zeros((self.boardMeasurement.size(), self.boardEstimate.size()))

        for idx_x, MeaPiece in enumerate(self.boardMeasurement.pieces):
            if self.boardMeasurement.pieces[MeaPiece].featVec is None: # @todo Is this proper?
                self.boardMeasurement.pieces[MeaPiece].genFeature(self.matcher)

            for idx_y, SolPiece in enumerate(self.boardEstimate.pieces):
            
                ret = self.matcher.score(self.boardMeasurement.pieces[MeaPiece], self.boardEstimate.pieces[SolPiece])
                scoreTable[idx_x][idx_y] = ret

                # If above craps out during operation due to multiple return
                # values, it is because the scoring method is improper.

                #DEBUG 
                #print( (self.boardMeasurement.pieces[MeaPiece].rLoc, self.boardEstimate.pieces[SolPiece].rLoc) )
                #if type(ret) is tuple and len(ret) > 0:
                #    scoreTable_shape[idx_x][idx_y] = np.sum(ret[0])
                #    scoreTable_color[idx_x][idx_y] = np.sum(ret[1])
                #    scoreTable_edge_color[idx_x][idx_y] = ret[1]
                #else:
                #    scoreTable_shape[idx_x][idx_y] = ret

        # Save for debug or post-matching processing if needed.
        self.scoreTable = scoreTable.copy()
        #DEBUG
        #print(self.scoreTable)

        # The measured piece will be assigned a solution piece.
        # Some measured piece may not have a match according to the threshold.
        # self.pAssignments = self.greedyAssignment(scoreTable_shape, scoreTable_color, scoreTable_edge_color)
        self.pAssignments = self.HungarianAssignment(scoreTable)


    #======================= HungarianAssignment =======================
    #
    def HungarianAssignment(self, scoreTable, getInverse = False):
        """!
        @brief  Run Hungarian Assignment for the score table.

        Atempts to associate row elements with column elements to define an assignment
        mapping that gives column elements (ideally) the same ID as the row elements.
        Per [scipy documentation for linear_sum_assignment]
        (https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html):
        > Can also solve a generalization of the classic assignment problem
        > where the cost matrix is rectangular. If it has more rows than
        > columns, then not every row needs to be assigned to a column, and
        > vice versa.

        The score table shape will influence the operation of the Hungarian Assignment implementation.
        If the matrix is:
        - square, then association will be a 1-1 assignment;
        - wide, then the associated will be a 1-1 assignment with unassigned columns;
        - tall, then the association is permissive of unassigned row elements, not 1-1.

        It is up to the outer scope to establish what is the best way to pass
        in the scoreTable and then to interpret the results.  If the 1-1 association
        should operate in the opposite direction, then set getInverse to True.

        Returning assignments as a dictionary to permit non-assignment. 

        @param[in]  scoreTAble  Score table for the pairwise comparison.
        @param[out] matched_id  Matched pair dict.
        """

        # Todo: Currently we only use scoreTable_shape
        pieceKeysList_bMeas    = list(self.boardMeasurement.pieces.keys())
        pieceKeysList_solution = list(self.boardEstimate.pieces.keys())

        matched_id = {}

        #
        if self.scoreType == SCORE_DIFFERENCE:
            row_ind, col_ind = linear_sum_assignment(scoreTable)
        else:
            row_ind, col_ind = linear_sum_assignment(scoreTable, maximize=True)

        if getInverse:
          for i, idx in enumerate(col_ind):
              matched_id[pieceKeysList_solution[i]] = pieceKeysList_bMeas[idx]
        else:
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

        pieceKeysList_bMeas = list(self.boardMeasurement.pieces.keys())
        pieceKeysList_solution = list(self.boardEstimate.pieces.keys())

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

    #============================= correct =============================
    #
    def correct(self):
        """!
        @brief    Perform correspondence correction if sensible.
  
        If the correspondences rely on information that evolves in time 
        and should be filtered or updated, this is where that gets 
        implemented.  Actions to occur here:

        1. Update puzzle piece information (raw and feature).
        2. Relabel the measured board to reflect association with known pieces.
        3. Relabel status of estimated board to reflect status of (not) measured pieces.
        """
  
        # @todo   Perform feature correction here.  Make sense for position
        #         type updates to go here. Not in adaptation.
  
        # @todo   Where it is unclear to place is appearance based updating.
        #         Is that a correction or an adaptation?  Is the appearance
        #         fundamentally a state property or some other property?
        #         Not resolving now, but leaving for later.

        # @todo   To what degree should some of these changes be in the measure routine?
        #         Actually, the correspondence doesn't have that.  A filter generally has
        #         predict, correct, adapt, and that's it.  Thus the process routine
        #         would implement the predict, trigger a correspondence action, then correct
        #         and adapt.  Putting in correct seems reasonable since it performs corrections
        #         once the associations are known (predictions already made).  
        #         Here it is not possible to run each routing individually since process also
        #         includes association.
        #
  
        matchedLabels = {}
        matchedIndices = set()
        if self.params.doUpdate:
            for assignment in self.pAssignments.items():
                self.boardEstimate.pieces[assignment[1]].update(self.boardMeasurement.pieces[assignment[0]])
                matchedLabels[assignment[0]] = self.boardEstimate.pieces[assignment[1]].id
                matchedIndices.add(assignment[1])
            
        # @todo Need to work out labeling of visible/not visible, which for correspondences
        #       really means associated or not associated, so that track misses can be
        #       established.  That has more to do with the boardEstimate.
        #       10/25: Assigning missing pieces the label "GONE"  Need to work out proper labels.
        #
        #print('CCCCCCCCCCCCCCCCC')
        #print(self.pAssignments)
        #print(matchedLabels)
        self.boardMeasurement.relabel(matchedLabels.items(), self.boardEstimate.size()+1)
        self.boardEstimate.markMissing(matchedIndices)
        # @todo Seems like this should be more like markStatus for the piece so that
        #       those with and w/out assignments get proper status label.
        #       How does it get more complex as we go though?

    #============================== adapt ==============================
    #
    def adapt(self):
      """!
      @brief    Perform adaptation based on correspondence as applicable.

      If something special in the matching model depends on an underlying 
      representation that is evolving over time and needs adaptation, then 
      this is the place to implement.  Adaptation differs from correction
      in that it may represent meta-parameters that support correspondence.
      These meta-parameters may need adjustment also.
      """

      pass

    #============================= process =============================
    #
    def process(self, bMeas):
        """!
        @brief  Run correspondence pipeline to preserve identity of puzzle pieces.

        @param[in]  bMeas   Measured board.
        """

        # Reset
        self.pAssignments = {}
        self.pAssignments_rotation = {}

        self.boardMeasurement = bMeas
        self.correspond()

        self.correct()
        self.adapt()

    #============================ buildMatcher ===========================
    #
    @staticmethod
    def buildMatcher(typeStr, matchConfig = None):
      """!
      @brief    Build out a Matcher instance for data association / puzzle
                correspondences.

      @param[in]    typeStr     Matching approach as string specification.
      @param[in]    matchConfig Matching configuration (optional: uses default)
      """

      if (typeStr == 'Moments'):
        theConfig = diffScore.CfgMoments()
        matchType = diffScore.Moments
      elif (typeStr == 'Distance'):
        theConfig = diffScore.CfgDistance()
        matchType = diffScore.Distance
      elif (typeStr == 'ColorHistCV'):
        theConfig = diffScore.CfgHistogramCV()
        matchType = diffScore.HistogramCV
      elif (typeStr == 'SIFTCV'):
        theConfig = simScore.CfgSIFTCV()
        matchType = simScore.SIFTCV

      if (matchConfig is not None):
        theConfig.merge_from_other_cfg(matchConfig)

      theMatcher = matchType(theConfig)

      return theMatcher


#
#============================== puzzle.board ==============================
