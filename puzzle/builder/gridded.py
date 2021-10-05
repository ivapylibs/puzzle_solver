# ========================= puzzle.builder.gridded ========================
#
# @class    gridded
#
# @brief    This type of puzzle is simply a set of interlocking puzzle
#           pieces that get put together in a grid structure.
#
# This class is an organized version of the interlocking class. Since
# the interlocking pieces lie on a regular grid, we can establish a
# relative ordering. If needed, it can be used for evaluating or
# interpreting a puzzle board and its correctness. 
#
# It also includes a scoring mechanism to indicate how "close" a current
# solution would be to the calibrated solution.
#
# ========================= puzzle.builder.gridded ========================
#
# @file     gridded.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/04 [created]
#           2021/08/05 [modified]
#
# ========================= puzzle.builder.gridded ========================

# ===== Environment / Dependencies
#

import pickle
from copy import deepcopy
from dataclasses import dataclass

import numpy as np
import scipy.cluster.hierarchy as hcluster

from puzzle.builder.arrangement import arrangement
from puzzle.builder.board import board
from puzzle.builder.interlocking import interlocking, paramInter
from puzzle.utils.dataProcessing import updateLabel


# ===== Helper Elements
#

@dataclass
class paramGrid(paramInter):
    tauGrid: float = 35  # Not used yet
    reorder: bool = False


#
# ====================== puzzle.builder.interlocking ======================
#

class gridded(interlocking):

    # ============================== adjacent =============================
    #
    # @brief  Constructor for the puzzle.builder.adjacent class.
    #
    #
    def __init__(self, solBoard=[], theParams=paramGrid):

        super(gridded, self).__init__(solBoard, theParams)

        if isinstance(solBoard, board):
            # Store the calibrated grid location of the puzzle piece.
            self.gc = np.zeros((2, solBoard.size()))
        else:
            raise TypeError('Not initialized properly')

        self.__processGrid(theParams.reorder)

    # ============================ processGrid ============================
    #
    # @brief  Process the solution board and determine what pieces are
    #         interlocking and the grid ordering. Grid ordering helps to
    #         determine adjacency.
    #
    # Some pieces might be close to each other but not really
    # interlocking.  Mostly this happens at the corners, but maybe there
    # are weird puzzles that can be thought of with a mix of adjacent and
    # interlocking.
    #
    def __processGrid(self, reorder=False):

        pLoc = self.pieceLocations()

        x_list = np.array([rLoc[0] for _, rLoc in pLoc.items()]).reshape(-1, 1)
        y_list = np.array([rLoc[1] for _, rLoc in pLoc.items()]).reshape(-1, 1)

        # @note
        # Check the puzzle shape size to determine the thresh here.
        # It is based on the assumption that all the puzzle pieces are of similar sizes.

        x_thresh = np.mean([piece.y.size[0] for piece in self.pieces]) / 2
        x_label = hcluster.fclusterdata(x_list, x_thresh, criterion="distance")  # from 1
        x_label = updateLabel(x_list, x_label) # from 0

        y_thresh = np.mean([piece.y.size[1] for piece in self.pieces]) / 2
        y_label = hcluster.fclusterdata(y_list, y_thresh, criterion="distance")
        y_label = updateLabel(y_list, y_label) # from 0

        # Reorder the pieces, so the id will correspond to the grid location
        if reorder:
            pieces_src = deepcopy(self.pieces)
            num = 0

            # Save the changes, {new:old}
            dict_conversion = {}

            for jj in range(max(y_label) + 1):
                for ii in range(max(x_label) + 1):
                    for idx, pts in enumerate(zip(x_label, y_label)):
                        if pts[0] == ii and pts[1] == jj:
                            self.pieces[num] = pieces_src[idx]
                            dict_conversion[num] = idx
                            self.pieces[num].id = num
                            self.gc[:, num] = ii, jj
                            num = num + 1
                            break

            # Have to re-compute adjMat/ilMat
            adjMat_src = deepcopy(self.adjMat)
            for ii in range(self.size()):
                for jj in range(ii + 1, self.size()):
                    self.adjMat[ii, jj] = adjMat_src[dict_conversion[ii], dict_conversion[jj]]
                    self.adjMat[jj, ii] = self.adjMat[ii, jj]

            self.ilMat = self.adjMat

        else:
            for ii in range(self.size()):
                # The order is in line with the one saving in self.pieces

                # @todo Yunzhi: Eventually, this has to be upgraded to a dict?
                self.gc[:, ii] = x_label[ii], y_label[ii]

    # OTHER CODE / MEMBER FUNCTIONS

    def swapPuzzle(self, num=100):
        """
        @brief  Randomly swap rLoc of two puzzle pieces for num times.

        Returns:
          Generated puzzle image & Generated puzzle board.
        """

        # @note We do not care about id in this function.
        epBoard = deepcopy(self)
        for i in range(num):
            target_list = np.random.randint(0, epBoard.size(), 2)

            temp = epBoard.pieces[target_list[0]].rLoc
            epBoard.pieces[target_list[0]].rLoc = epBoard.pieces[target_list[1]].rLoc
            epBoard.pieces[target_list[1]].rLoc = temp

        epImage = epBoard.toImage(CONTOUR_DISPLAY=False)

        return epImage, epBoard

    def explodedPuzzle(self, dx=100, dy=50, bgColor=(0, 0, 0)):
        """
        @brief  Create an exploded version of the puzzle. It is an image
        with no touching pieces.

        The value for an exploded puzzle image is that it can be used to
        generate a simulated puzzle scenario that can be passed to a puzzle
        solver. It can also be used to define a quasi-puzzle problem, where
        the objective is to place the pieces in grid ordering like the
        exploded view (without needing to interlock). Doing see keeps puzzle
        piece well separated for simple puzzle interpretation algorithms to
        rapidly parse.

        Args:
          dx: The horizontal offset when exploding.
          dy: The vertical offset when exploding.
          bgColor: The background color to use.
          Exploded puzzle image & Exploded puzzle board.
        """

        # --[1] First figure out how big the exploded image should be based
        #      on the puzzle image dimensions, the number of puzzle pieces
        #      across rows and columns, and the chosen spacing.
        [nc, nr] = self.extents()
        bbox = self.boundingBox()
        r_origin = bbox[0]

        # The max index of pieces for x,y
        x_max = np.max(self.gc[0, :])
        y_max = np.max(self.gc[1, :])

        nr = int(nr + y_max * dy)
        nc = int(nc + x_max * dx)

        epImage = np.zeros((nr, nc, 3), dtype='uint8')
        epImage[:, :, :] = bgColor

        # --[2] Place image data into the exploded puzzle image.
        #

        # Work on the epBoard
        epBoard = deepcopy(self)
        for idx, piece in enumerate(epBoard.pieces):
            r_new = -r_origin + piece.rLoc + np.array([dx, dy]) * self.gc[:, idx].flatten()
            r_new = r_new.astype('int')
            piece.placeInImageAt(epImage, rc=r_new)
            # epBoard.pieces[idx].setPlacement(r_new)
            piece.setPlacement(r_new)
        # epImage = epBoard.toImage(CONTOUR_DISPLAY=False)

        """
        @todo Yunzhi: Currently, it is just explode but without changing the order.
        Otherwise, gc has to be updated too.
        """

        return epImage, epBoard

    # ======================== buildFromFile_Puzzle =======================
    #
    # @brief      Load a saved arrangement calibration/solution puzzle board.
    #
    # The python file contains the puzzle board information. It gets
    # dumped into an arrangement instance. If a threshold variable
    # ``tauDist`` is found, then it is applied to the # arrangement
    # instance.
    #
    # @param[in]  fileName    The python file to load.
    #
    # @param[out] thePuzzle   The arrangement puzzle board instance.
    #
    @staticmethod
    def buildFromFile_Puzzle(fileName, theParams=None):

        aPuzzle = arrangement.buildFromFile_Puzzle(fileName)

        with open(fileName, 'rb') as fp:
            data = pickle.load(fp)

        if theParams is None and hasattr(data, 'tauGrid'):
            theParams = paramGrid(data.tauGrid)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = gridded(aPuzzle, theParams)
        else:
            thePuzzle = gridded(aPuzzle)

        return thePuzzle

    # ===================== buildFromFile_ImageAndMask ====================
    #
    # @brief      Load a saved arrangement calibration/solution stored as
    #             an image and a mask.
    #
    # The python file contains the puzzle board mask and image source
    # data. It gets processed into an arrangement instance. If a threshold
    # variable ``tauDist`` is found, then it is applied to the arrangement
    # instance.
    #
    # @param[in]  fileName    The python file to load.
    #
    # @param[out] thePuzzle   The arrangement puzzle board instance.
    #
    @staticmethod
    def buildFromFile_ImageAndMask(fileName, theParams=None):

        aPuzzle = arrangement.buildFromFile_ImageAndMask(fileName, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = gridded(aPuzzle, theParams)
        else:
            thePuzzle = gridded(aPuzzle)

        return thePuzzle

    # ==================== buildFromFiles_ImageAndMask ====================
    #
    # @brief      Load a saved arrangement calibration/solution stored as
    #             separate image and mask files.
    #
    # The source file contain the puzzle board image and mask data. It
    # gets processed into an arrangement instance. If a threshold variable
    # ``tauDist`` is found, then it is applied to the arrangement
    # instance.
    #
    # @param[in]  imFile      The image file to load.
    # @param[in]  maskFile    The maske file to load.
    #
    # @param[out] thePuzzle   The arrangement puzzle board instance.
    #
    @staticmethod
    def buildFromFiles_ImageAndMask(imFile, maskFile, theParams=None):

        aPuzzle = arrangement.buildFromFiles_ImageAndMask(imFile, maskFile, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = gridded(aPuzzle, theParams)
        else:
            thePuzzle = gridded(aPuzzle)

        return thePuzzle

    # ======================= buildFrom_ImageAndMask ======================
    #
    # @brief      Given an image and an image mask, parse both to recover
    #             the puzzle calibration/solution.
    #
    # Instantiates a puzzle parsing operator, then applies it to the
    # submitted data to create a puzzle board instance. That instance is
    # the calibration/solution.
    #
    # @param[in]  theImage    The puzzle image data.
    # @param[in]  theMask     The puzzle piece mask information.
    #
    # @param[out] thePuzzle   The arrangement puzzle board instance.
    #
    @staticmethod
    def buildFrom_ImageAndMask(theImage, theMask, theParams=None):

        aPuzzle = arrangement.buildFrom_ImageAndMask(theImage, theMask, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = gridded(aPuzzle, theParams)
        else:
            thePuzzle = gridded(aPuzzle)

        return thePuzzle

    # ===================== buildFrom_ImageProcessing =====================
    #
    # @brief      Given an image with regions clearly separated by some
    #             color or threshold, parse it to recover the puzzle
    #             calibration/solution. Can source alternative detector.
    #
    # Instantiates a puzzle parser that gets applied to the submitted data
    # to create a puzzle board instance. That instance is the
    # calibration/solution.
    #
    # @param[in]  theImage        The puzzle image data.
    # @param[in]  theProcessor    The processing scheme.
    # @param[in]  theDetector     The detector scheme.
    #
    # @param[out] thePuzzle   The arrangement puzzle board instance.
    #
    @staticmethod
    def buildFrom_ImageProcessing(theImage, theProcessor=None, theDetector=None, theParams=None):

        aPuzzle = arrangement.buildFrom_ImageProcessing(theImage, theProcessor, theDetector, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = gridded(aPuzzle, theParams)
        else:
            thePuzzle = gridded(aPuzzle)

        return thePuzzle

    # ===================== buildFrom_Sketch =====================
    #
    # @brief      Given an image with regions clearly separated by some
    #             color or threshold, parse it to recover the puzzle
    #             calibration/solution. Can source alternative detector.
    #
    # Instantiates a puzzle parser that gets applied to the submitted data
    # to create a puzzle board instance. That instance is the
    # calibration/solution.
    #
    # @param[in]  theImage        The puzzle image data.
    # @param[in]  theMask         The puzzle mask data.
    # @param[in]  theProcessor    The processing scheme.
    # @param[in]  theDetector     The detector scheme.
    #
    # @param[out] thePuzzle   The arrangement puzzle board instance.
    #
    @staticmethod
    def buildFrom_Sketch(theImage, theMask, theProcessor=None, theDetector=None, theParams=None):

        aPuzzle = arrangement.buildFrom_Sketch(theImage, theMask, theProcessor, theDetector, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = gridded(aPuzzle, theParams)
        else:
            thePuzzle = gridded(aPuzzle)

        return thePuzzle

#
# ========================= puzzle.builder.gridded ========================
