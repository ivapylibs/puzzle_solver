# ============================== puzzle.board =============================
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
# @date     2021/07/28 [created]
#           2021/08/01 [modified]
#
#
# ============================== puzzle.board =============================


# ============================== Dependencies =============================

# ===== Environment / Dependencies
#

import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist


#
# ============================== puzzle.board =============================
#

class board:

    def __init__(self, *argv):
        """
        @brief  Constructor for puzzle board. Can pass contents at
                instantiation time or delay until later.

        Args:
            *argv: The input params

        """
        self.pieces = []  # @< The puzzle pieces.
        self.id_count = 0

        if len(argv) == 1:
            if issubclass(type(argv[0]), board):
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

    def addPiece(self, piece):
        """
        @brief      Add puzzle piece instance to the board.

        Args:
          piece: A puzzle piece instance.

        """

        piece.id = self.id_count
        self.id_count += 1
        self.pieces.append(piece)

    def rmPiece(self, id):
        """
        @brief      Remove puzzle piece instance from the board

        Args:
            id: The puzzle piece id

        """
        rm_index = None
        for idx, piece in enumerate(self.pieces):
            if piece.id == id:
                rm_index = idx
                break

        if rm_index:
            del self.pieces[rm_index]

    def clear(self):
        """
        @brief  Clear all the puzzle pieces from the board.

        """
        self.pieces = []
        self.id_count = 0

    def getSubset(self, subset):
        """
        @brief  Return a new board consisting of a subset of pieces.

        Args:
            subset: A list of indexes for the subset of puzzle pieces.

        Returns:
            A new board following the input subset.
        """

        theBoard = board(np.array(self.pieces)[subset], len(subset))

        return theBoard

    def getAssigned(self, pAssignments):
        """
        @brief  Return a new board consisting of a subset of pieces.

        Args:
            pAssignments: A list of assignments for the subset.

        Returns:
            A new board following assignment.
        """

        if len(pAssignments) > 0:
            theBoard = board(np.array(self.pieces)[np.array(pAssignments)[:, 0]], self.id_count)
        else:
            print('No assignments is found. Return an empty board.')
            theBoard = board()

        return theBoard

    def testAdjacent(self, index_A, index_B, tauAdj):
        """
        @brief  Check if two puzzle pieces are adjacent or not

        Args:
            index_A: The index of the puzzle piece A.
            index_B: The index of the puzzle piece B.
            tauAdj: The threshold of the distance.

        Returns:
            The flag indicating whether two puzzle pieces are adjacent or not.
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
                    if i>0:
                        pts.append(((cnt[hull[i][0]][0]+cnt[hull[i-1][0]][0])/2).astype('int'))


            # Remove duplicates
            pts = np.unique(pts, axis=0)

            return pts


        pts_A = self.pieces[index_A].rLoc + obtain_sub_pts(self.pieces[index_A])
        pts_B = self.pieces[index_B].rLoc + obtain_sub_pts(self.pieces[index_B])

        dists = cdist(pts_A, pts_B, 'euclidean')

        theFlag = dists.min() < tauAdj

        return theFlag

    def size(self):
        """
        @brief  Return the number of pieces on the board.

        Returns:
            The number of pieces on the board.
        """

        nPieces = len(self.pieces)

        return nPieces

    def extents(self):
        """
        @brief  Iterate through the puzzle pieces to figure out the tight
                bounding box extents of the board.

        Returns:
            The bounding box side lengths. [x,y]
        """

        # [[min x, min y], [max x, max y]]
        bbox = self.boundingBox()

        lengths = bbox[1] - bbox[0]

        return lengths

    def boundingBox(self):
        """
        @brief  Iterate through the puzzle pieces to figure out the tight
                bounding box of the board.

        Returns:
            The bounding box coordinates. [[min x, min y], [max x, max y]]
        """

        if self.size() == 0:
            raise RuntimeError('No pieces exist')
        else:
            # process to get min x, min y, max x, and max y
            bbox = np.array([[float('inf'), float('inf')], [0, 0]])

            # piece is a puzzleTemplate instance, see template.py for details.
            for piece in self.pieces:
                # top left coordinate
                tl = piece.rLoc
                # bottom right coordinate
                br = piece.rLoc + piece.size()

                bbox[0] = np.min([bbox[0], tl], axis=0)
                bbox[1] = np.max([bbox[1], br], axis=0)

            return bbox

    def pieceLocations(self):
        """
        @brief      Returns list/array of puzzle piece locations.

        Returns:
            A dict of puzzle piece id & location.
        """

        # @note
        # Previously, return a list/array of puzzle piece locations.
        # pLocs = []
        # for piece in self.pieces:
        #   pLocs.append(piece.rLoc)
        #
        # # from N x 2 to 2 x N
        # pLocs = np.array(pLocs).reshape(-1,2).T

        pLocs = {}
        for piece in self.pieces:
            pLocs[piece.id] = piece.rLoc

        return pLocs

    def toImage(self, theImage=None, ID_DISPLAY=False, COLOR=(0, 0, 0), ID_COLOR=(255, 255, 255), CONTOUR_DISPLAY=True,
                BOUNDING_BOX=True):
        """
        @brief  Uses puzzle piece locations to create an image for
                visualizing them.  If given an image, then will place in it.

        Args:
            theImage: The image to insert pieces into.
            ID_DISPLAY: The flag indicating displaying ID or not.
            COLOR: The background color.
            ID_COLOR: The ID color.
            CONTOUR_DISPLAY: The flag indicating drawing contour or not.
            BOUNDING_BOX: The flag indicating outputting a bounding box area or not.

        Returns:
            The rendered image.
        """

        if theImage is not None:
            # Check dimensions ok and act accordingly, should be equal or bigger, not less.
            lengths = self.extents().astype('int')
            bbox = self.boundingBox().astype('int')
            if theImage.shape[1] - lengths[0] >= 0 and theImage.shape[0] - lengths[1] >= 0:
                for piece in self.pieces:

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
            else:
                raise RuntimeError('The image is too small. Please try again.')
        else:
            # Create image with proper dimensions.
            lengths = self.extents().astype('int')
            bbox = self.boundingBox().astype('int')

            if BOUNDING_BOX:
                theImage = np.full((lengths[1], lengths[0], 3), COLOR, dtype='uint8')
            else:
                theImage = np.full((bbox[1, 1], bbox[1, 0], 3), COLOR, dtype='uint8')

            for piece in self.pieces:
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

    def display(self, fh=None, ID_DISPLAY=False, CONTOUR_DISPLAY=True):
        """
        @brief  Display the puzzle board as an image.

        Args:
            fh: The figure handle if available.
            ID_DISPLAY:  The flag indicating displaying ID or not.
            CONTOUR_DISPLAY: The flag indicating drawing contour or not.

        Returns:
            The figure handle.
        """

        if fh:
            # See https://stackoverflow.com/a/7987462/5269146
            fh = plt.figure(fh.number)
        else:
            fh = plt.figure()

        theImage = self.toImage(ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

        plt.imshow(theImage)

        return fh

#
# ============================== puzzle.board =============================
