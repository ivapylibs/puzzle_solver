# ======================= puzzle.builder.arrangement ======================
#
# @class    arrangement
#
# @brief    This type of puzzle is simply a set of shapes arranged at
#           specific locations in the image with no occlusion or
#           overlap. Touching is not necessary (typically not the case)
#
#
# This class is the most basic type of puzzle specification.  It
# provide a tempalte puzzle board consisting of puzzle pieces that
# should be placed at specific locations.  It also includes a scoring
# mechanism to indicate how "close" a current solution would be to the
# calibrated solution.
#
# ======================= puzzle.builder.arrangement ======================
#
# @file     arrangement.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/30 [created]
#           2021/08/05 [modified]
#
# ======================= puzzle.builder.arrangement ======================

import pickle
from dataclasses import dataclass

# ===== Environment / Dependencies
#
import cv2
import detector.inImage as detector
import improcessor.basic as improcessor
import numpy as np

import puzzle.parser.simple as perceiver
from puzzle.builder.board import Board
from puzzle.parser.fromLayer import FromLayer, ParamPuzzle


# ===== Helper Elements
#

@dataclass
class ParamArrange(ParamPuzzle):
    tauDist: int = 20  # @< The threshold of whether two puzzle pieces are correctly matched.


#
# ======================= puzzle.builder.arrangement ======================
#

class Arrangement(Board):

    def __init__(self, theBoard=[], theParams=ParamArrange):
        """
        @brief  Constructor for the puzzle.builder.arrangement class.

        Args:
            theBoard: A board instance.
            theParams: The parameters.
        """

        super(Arrangement, self).__init__(theBoard)

        self.params = theParams  # @<A distance threshold for considering a piece
        # to be correctly placed.

    def corrections(self, pLoc):
        """
        @brief  Given an array of locations that correspond to the puzzle
                board (e.g., in the same order as puzzle board list), provide
                the correction vector that would move them to the calibrated
                locations.

        Args:
            pLoc: A dict of puzzle piece id & location.

        Returns:
            theVects(A dict of puzzle piece id & vectors)
        """
        # @note
        # pLocTrue = GET ARRAY OF SOLUTION LOCATIONS.
        # theVects = pLocTrue - pLoc
        #
        # RETURN theVects
        # SIMPLIFY PYTHON AS DESIRED.

        theVects = {}
        pLocTrue = self.pieceLocations()

        for id in pLoc:
            theVects[id] = np.array(pLocTrue[id]) - np.array(pLoc[id])

        # @todo Yunzhi: We may not need this check?
        # if len(pLocTrue) == len(pLoc):
        #   for id in pLoc:
        #     theVects[id] = np.array(pLocTrue[id]) - np.array(pLoc[id])
        # else:
        #   raise RuntimeError('Error of unmatched puzzle piece number!')

        return theVects

    def distances(self, pLoc):
        """
        @brief  Given an array of locations that correspond to the puzzle
                board (e.g., in same order as puzzle board list), provide
                the distances between the locations and the calibrated
                locations.

        Args:
            pLoc: A dict of puzzle piece id & location.

        Returns:
            theDists(A dict of puzzle piece id & distance to the solution)
        """

        theDists = {}
        pLocTrue = self.pieceLocations()

        for id in pLoc:
            theDists[id] = np.linalg.norm(np.array(pLocTrue[id]) - np.array(pLoc[id]))

        # @todo Yunzhi: We may not need this check?
        # if len(pLocTrue) == len(pLoc):
        #   for id in pLoc:
        #     theDists[id] = np.linalg.norm(np.array(pLocTrue[id]) - np.array(pLoc[id]))
        # else:
        #   raise RuntimeError('Error of unmatched puzzle piece number!')

        return theDists

    def scoreByLocation(self, pLoc):
        """
        @brief  Given an array of locations that correspond to the puzzle
                board (e.g., in same order as puzzle board list), provide a
                score for the distance between the locations and the
                calibrated locations.

        The score here is just the sum of the error norms (or the incorrect
        distance of the placed part to the true placement). The locations
        are assumed to be ordered according to puzzle piece ordering in the
        calibrated puzzle board.

        Args:
            pLoc: A dict of puzzle piece id & location.

        Returns:
            theScore(The score for the current board)
        """

        errDists = self.distances(pLoc)

        theScore = []
        for _, errDist in errDists.items():
            theScore.append(errDist)
        theScore = np.sum(theScore)

        return theScore

    def scoreBoard(self, theBoard):
        """
        @brief  Given a puzzle board with in ordered correspondence with the
                calibrated puzzle board, in the same order as puzzle board
                list), provide a score for the distance between the puzzle
                piece locations and the calibrated locations.

        The score here is just the sum of the error norms (or the incorrect
        distance of the placed part to the true placement).

        Args:
            theBoard: A puzzle board in 1-1 ordered correspondence with solution.

        Returns:
            theScore(The score compared with the given board)
        """

        if theBoard.size() == self.size():
            pLocs = theBoard.pieceLocations()
            theScore = self.scoreByLocation(pLocs)
        else:
            theScore = float('inf')

        return theScore

    def piecesInPlace(self, pLoc):
        """
        @brief  Return boolean array indicating whether the piece is
                correctly in place or not.

        Args:
            pLoc: A dict of puzzle piece id & location.

        Returns:
            theScores(A dict of id & bool variable indicating whether the piece is correctly in place or not.)
        """

        errDists = self.distances(pLoc)

        theScores = {}
        for id, errDist in errDists.items():
            theScores[id] = errDist < self.params.tauDist

        return theScores

    # ============================== progress =============================
    #
    # @brief Check the status of the progress.
    #        (Return the ratio of the completed puzzle pieces)
    #
    # @param[in]  theBoard    A puzzle board in 1-1 ordered correspondence
    #                         with solution.
    #
    # @param[out] thePercentage The progress.
    #
    def progress(self, theBoard):
        pLocs = theBoard.pieceLocations()
        inPlace = self.piecesInPlace(pLocs)

        val_list = [val for _, val in inPlace.items()]

        thePercentage = '{:.1%}'.format(np.count_nonzero(val_list) / len(inPlace))

        return thePercentage

    # ======================== buildFromFile_Puzzle =======================
    #
    # @brief      Load a saved arrangement calibration/solution puzzle board.
    #
    # The python file contains the puzzle board information. It gets
    # dumped into an arrangement instance. If a threshold variable
    # ``tauDist`` is found, then it is applied to the # arrangement
    # instance.
    #
    # @param[in]  fileName    The python file (.obj) to load
    #
    # @param[out] thePuzzle   The arrangement puzzle board instance.
    #
    @staticmethod
    def buildFromFile_Puzzle(fileName, theParams=None):

        theBoard = None
        with open(fileName, 'rb') as fp:
            data = pickle.load(fp)

            if hasattr(data, 'board'):
                theBoard = data.board
            if hasattr(data, 'tauDist'):
                theParams = ParamArrange(tauDist=data.tauDist)

        if isinstance(theBoard, Board):
            if hasattr(theParams, 'tauDist'):
                thePuzzle = Arrangement(theBoard, theParams)
            else:
                thePuzzle = Arrangement(theBoard)
        else:
            raise TypeError('There is no board instance saved in the file!')

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
    # @param[in]  fileName    The python file (.obj) to load.
    #
    # @param[out] thePuzzle   The arrangement puzzle board instance.
    #
    @staticmethod
    def buildFromFile_ImageAndMask(fileName, theParams=None):

        I = None
        M = None

        with open(fileName, 'rb') as fp:
            data = pickle.load(fp)

            if hasattr(data, 'I'):
                I = data.I
            if hasattr(data, 'M'):
                M = data.M

        if isinstance(I, np.ndarray) and isinstance(M, np.ndarray):
            thePuzzle = Arrangement.buildFrom_ImageAndMask(I, M, theParams)
        else:
            raise TypeError('There is no Image or Mask saved in the file!')

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
    # @param[in]  imFile      The image file (.png) to load.
    # @param[in]  maskFile    The mask file (.png) to load.
    #
    # @param[out] thePuzzle   The arrangement puzzle board instance.
    #
    @staticmethod
    def buildFromFiles_ImageAndMask(imFile, maskFile, theParams=None):

        I = cv2.imread(imFile)
        M = cv2.imread(maskFile, cv2.IMREAD_GRAYSCALE)

        # Sometimes the value in M may not be strictly 0 or 255
        if np.bitwise_and(M > 0, M < 255).any():
            _, M = cv2.threshold(M, 10, 255, cv2.THRESH_BINARY)

        if isinstance(I, np.ndarray) and isinstance(M, np.ndarray):
            thePuzzle = Arrangement.buildFrom_ImageAndMask(I, M, theParams)
        else:
            raise TypeError('There is no Image or Mask saved in the file!')

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

        if hasattr(theParams, 'areaThresholdLower'):
            pParser = FromLayer(theParams)
        else:
            pParser = FromLayer()

        pParser.process(theImage, theMask)
        if hasattr(theParams, 'tauDist'):
            thePuzzle = Arrangement(pParser.getState(), theParams)
        else:
            thePuzzle = Arrangement(pParser.getState())

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

        if theDetector is None and theProcessor is None:
            if theImage.ndim == 3:
                # May not be enough
                theProcessor = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,), \
                                                 improcessor.basic.thresh,
                                                 ((0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU),))
                theDetector = detector.inImage(theProcessor)
            elif theImage.ndim == 2:
                theProcessor = improcessor.basic(improcessor.basic.thresh,
                                                 ((0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU),))
                theDetector = detector.inImage(theProcessor)
        elif theDetector is None and theProcessor is not None:
            theDetector = detector.inImage(theProcessor)

        if hasattr(theParams, 'areaThresholdLower'):
            theLayer = FromLayer(theParams)
        else:
            theLayer = FromLayer()

        pParser = perceiver.Simple(theDetector=theDetector, theTracker=theLayer, theParams=None)

        pParser.process(theImage)

        if hasattr(theParams, 'tauDist'):
            thePuzzle = Arrangement(pParser.board, theParams)
        else:
            thePuzzle = Arrangement(pParser.board)

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

        if theDetector is None and theProcessor is None:
            if theImage.ndim == 3:
                # May not be enough
                theProcessor = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,), \
                                                 improcessor.basic.thresh,
                                                 ((0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU),))
                theDetector = detector.inImage(theProcessor)
            elif theImage.ndim == 2:
                theProcessor = improcessor.basic(improcessor.basic.thresh,
                                                 ((0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU),))
                theDetector = detector.inImage(theProcessor)
        elif theDetector is None and theProcessor is not None:
            theDetector = detector.inImage(theProcessor)

        if hasattr(theParams, 'areaThresholdLower'):
            theLayer = FromLayer(theParams)
        else:
            theLayer = FromLayer()

        pParser = perceiver.Simple(theDetector=theDetector, theTracker=theLayer, theParams=None)

        pParser.process(theImage, theMask)

        if hasattr(theParams, 'tauDist'):
            thePuzzle = Arrangement(pParser.board, theParams)
        else:
            thePuzzle = Arrangement(pParser.board)

        return thePuzzle

#
# ======================= puzzle.builder.arrangement ======================
