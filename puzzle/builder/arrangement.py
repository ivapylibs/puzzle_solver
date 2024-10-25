#======================= puzzle.builder.arrangement ======================
##
# @package  PuzzleArrangement 
# @brief    This type of puzzle is simply a set of shapes arranged at
#           specific locations in the image with no occlusion or
#           overlap. Touching is not necessary (typically not the case)
# @ingroup  Puzzle_Types
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#
# @date     2021/08/05 [modified]
# @date     2021/07/30 [created]
#
# @todo     May need more work to align with current revisions.
# @todo     Some of the test scripts may have bad Cfg parameter names.
#

#======================= puzzle.builder.arrangement ======================
#
# NOTES:
#   90 columns.
#   indent is 4 spaces.
#
#======================= puzzle.builder.arrangement ======================


import pickle
from dataclasses import dataclass

# ===== Environment / Dependencies
#
import cv2
import detector.inImage as detector
import improcessor.basic as improcessor
import numpy as np

import puzzle.parse.simple as perceiver
from puzzle.board import Board
from puzzle.parser import boardMeasure, CfgBoardMeasure


# ===== Helper Elements
#

#---------------------------------------------------------------------------
#===================== Configuration Node : Arrangement ====================
#---------------------------------------------------------------------------
#

class CfgArrangement(CfgBoardMeasure):
  '''!
  @ingroup  Puzzle_Types
  @brief  Configuration setting specifier for centroidMulti.
  '''

  #============================= __init__ ============================
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief        Constructor of configuration instance.
  
    @param[in]    cfg_files   List of config files to load to merge settings.
    '''
    if (init_dict == None):
      init_dict = CfgArrangement.get_default_settings()

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
    default_dict = super(CfgArrangement,CfgArrangement).get_default_settings()
    default_dict.update(dict(tauDist = 20))

    return default_dict


#
# ======================= puzzle.builder.arrangement ======================
#

class Arrangement(Board):
    """!
    @ingroup    Puzzle_Types
    @brief  A puzzle that simply needs to arrange pieces on a workspace.

    This class is the most basic type of puzzle specification.  It provide a
    template puzzle board consisting of puzzle pieces that should be placed
    at specific locations.  It also includes a scoring mechanism to indicate
    how 'close' a current solution would be to the calibrated solution.
    """

    def __init__(self, theBoard=[], theParams=CfgArrangement):
        """!
        @brief  Constructor for the puzzle.builder.arrangement class.

        Args:
            theBoard: A board instance.
            theParams: The parameters.
        """

        super(Arrangement, self).__init__(theBoard)

        self.params = theParams  # @<A distance threshold for considering a piece
        # to be correctly placed.

    def corrections(self, pLoc):
        """!
        @brief  Given an array of locations that correspond to the puzzle
                board (e.g., in the same order as puzzle board list), provide
                the correction vector that would move them to the calibrated
                locations.

        @param[in]  pLoc        A dict of puzzle piece id & location.

        @return     theVects    A dict of puzzle piece id & vectors.
        """

        theVects = {}
        pLocTrue = self.pieceLocations()

        for id in pLoc:
            theVects[id] = np.array(pLocTrue[id]) - np.array(pLoc[id])

        # Todo: We may not need this check?
        # if len(pLocTrue) == len(pLoc):
        #   for id in pLoc:
        #     theVects[id] = np.array(pLocTrue[id]) - np.array(pLoc[id])
        # else:
        #   raise RuntimeError('Error of unmatched puzzle piece number!')

        return theVects

    def distances(self, pLoc):
        """!
        @brief  Given an array of locations that correspond to the puzzle
                board (e.g., in same order as puzzle board list), provide
                the distances between the locations and the calibrated
                locations.

        @param[in]  pLoc        Dict of puzzle piece id & location.

        @return     theDists    Dict of puzzle piece id & distance to solution
        """

        theDists = {}
        pLocTrue = self.pieceLocations()

        for id in pLoc:
            theDists[id] = np.linalg.norm(np.array(pLocTrue[id]) - np.array(pLoc[id]))

        # Todo: We may not need this check?
        # if len(pLocTrue) == len(pLoc):
        #   for id in pLoc:
        #     theDists[id] = np.linalg.norm(np.array(pLocTrue[id]) - np.array(pLoc[id]))
        # else:
        #   raise RuntimeError('Error of unmatched puzzle piece number!')

        return theDists

    def scoreByLocation(self, pLoc):
        """!
        @brief  Given an array of locations that correspond to the puzzle
                board (e.g., in same order as puzzle board list), provide a
                score for the distance between the locations and the
                calibrated locations.

        The score here is just the sum of the error norms (or the incorrect
        distance of the placed part to the true placement). The locations
        are assumed to be ordered according to puzzle piece ordering in the
        calibrated puzzle board.

        @param[in]  pLoc        Dict of puzzle piece id & location.

        @return     theScore    Completion score for the current board.
        """

        errDists = self.distances(pLoc)

        theScore = []
        for _, errDist in errDists.items():
            theScore.append(errDist)
        theScore = np.sum(theScore)

        return theScore

    def scoreBoard(self, theBoard):
        """!
        @brief  Given a puzzle board with in ordered correspondence with the
                calibrated puzzle board, in the same order as puzzle board
                list), provide a score for the distance between the puzzle
                piece locations and the calibrated locations.

        The score here is just the sum of the error norms (or the incorrect
        distance of the placed part to the true placement).

        @param[in] theBoard     Puzzle board in 1-1 ordered correspondence with solution.

        @return     theScore    The score compared with the given board.
        """

        if theBoard.size() == self.size():
            pLocs = theBoard.pieceLocations()
            theScore = self.scoreByLocation(pLocs)
        else:
            theScore = float('inf')

        return theScore

    def piecesInPlace(self, pLoc, tauDist=None):
        """!
        @brief  Return boolean array indicating whether the piece is
                correctly in place or not.

        Args:
            pLoc: A dict of puzzle piece id & location.

        Returns:
            theScores: A dict of id & bool variable indicating whether the piece is correctly in place or not.
        """

        errDists = self.distances(pLoc)

        if tauDist is None:
            tauDist = self.params.tauDist

        theScores = {}
        for id, errDist in errDists.items():
            theScores[id] = errDist < tauDist

        return theScores

    @staticmethod
    def buildFromFile_Puzzle(fileName, theParams=None):
        """!
        @brief Load a saved arrangement calibration/solution puzzle board.

        Args:
            fileName: The python file to load.
            theParams: The params.

        Returns:
            thePuzzle: The arrangement puzzle board instance.
        """

        theBoard = None
        with open(fileName, 'rb') as fp:
            data = pickle.load(fp)

            if hasattr(data, 'board'):
                theBoard = data.board
            elif issubclass(type(data), Board):
                theBoard = data

            if hasattr(data, 'tauDist'):            # NOT GOOD PRACTICE!!!
                theParams = CfgArrangement()        # DELETE ONCE FIGURE PROCESS.
                theParams.tauDist = data.tauDist    # LOOKS TO BE CRAPPY SAVE/LOAD APPROACH.

        if isinstance(theBoard, Board):
            thePuzzle.Arrangement(theBoard, theParams)
            # DELETE WHEN ABOVE WORKS.
            #if hasattr(theParams, 'tauDist'):
            #    thePuzzle = Arrangement(theBoard, theParams)
            #else:
            #    thePuzzle = Arrangement(theBoard)
        else:
            raise TypeError('There is no board instance saved in the file!')

        return thePuzzle

    @staticmethod
    def buildFromFile_ImageAndMask(fileName, theParams=None):
        """!
        @brief Load a saved arrangement calibration/solution stored as an image and a mask.

        The python file contains the puzzle board mask and image source
        data. It gets processed into an arrangement instance. If a threshold
        variable ``tauDist`` is found, then it is applied to the arrangement
        instance.

        Args:
            fileName: The python file to load.
            theParams: The params.

        Returns:
            thePuzzle: The arrangement puzzle board instance.
        """

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

    @staticmethod
    def buildFromFiles_ImageAndMask(imFile, maskFile, theParams=None):
        """!
        @brief Load a saved arrangement calibration/solution stored as
               separate image and mask files.

        The source file contain the puzzle board image and mask data. It
        gets processed into an arrangement instance. If a threshold variable
        ``tauDist`` is found, then it is applied to the arrangement instance.

        Args:
            imFile: The image file to load.
            maskFile: The mask file to load.
            theParams: The params.

        Returns:
            thePuzzle: The arrangement puzzle board instance.
        """

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

    #====================== buildFrom_ImageAndMask =====================
    #
    @staticmethod
    def buildFrom_ImageAndMask(theImage, theMask, theParams=None):
        """!
        @brief Given an image and an image mask, parse both to recover
               the puzzle calibration/solution.

        Instantiates a puzzle parser that gets applied to the submitted data
        to create a puzzle board instance. That instance is the calibration/solution.

        Args:
            theImage: The puzzle image data.
            theMask: The puzzle mask data.
            theParams: The params.

        Returns:
            thePuzzle: The arrangement puzzle board instance.
        """

        if theParams is None:
            pParser = boardMeasure()
        else:
            pParser = boardMeasure(theParams)

        # DEBUGGING: BREAKS HERE.
        pParser.process(theImage, theMask)
        if hasattr(theParams, 'tauDist'):
            thePuzzle = Arrangement(pParser.getState(), theParams)
        else:
            thePuzzle = Arrangement(pParser.getState())

        return thePuzzle

    @staticmethod
    def buildFrom_ImageProcessing(theImage, theProcessor=None, theDetector=None, theParams=None):
        """!
        @brief Given an image with regions clearly separated by some
               color or threshold, parse it to recover the puzzle
               calibration/solution. Can source alternative detector.

        Instantiates a puzzle parser that gets applied to the submitted data
        to create a puzzle board instance. That instance is the calibration/solution.

        Args:
            theImage: The puzzle image data.
            theProcessor: The processing scheme.
            theDetector: The detector scheme.
            theParams: The params.

        Returns:
            thePuzzle: The arrangement puzzle board instance.
        """

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

        if theParams is None:
            pParser = boardMeasure()
        else:
            pParser = boardMeasure(theParams)

        #DELETE WHEN ABOVE RUNS.
        #if hasattr(theParams, 'areaThresholdLower'):
        #    theLayer = FromLayer(theParams)
        #else:
        #    theLayer = FromLayer()

        pParser = perceiver.Simple(theDetector=theDetector, theTracker=theLayer, theParams=None)

        pParser.process(theImage)

        if hasattr(theParams, 'tauDist'):
            thePuzzle = Arrangement(pParser.board, theParams)
        else:
            thePuzzle = Arrangement(pParser.board)

        return thePuzzle

    @staticmethod
    def buildFrom_Sketch(theImage, theMask, theProcessor=None, theDetector=None, theParams=None):
        """!
        @brief Given an image with regions clearly separated by some
               color or threshold, parse it to recover the puzzle
               calibration/solution. Can source alternative detector.

        Instantiates a puzzle parser that gets applied to the submitted data
        to create a puzzle board instance. That instance is the calibration/solution.

        Args:
            theImage: The puzzle image data.
            theMask: The puzzle mask data.
            theProcessor: The processing scheme.
            theDetector: The detector scheme.
            theParams: The params.

        Returns:
            thePuzzle: The arrangement puzzle board instance.
        """

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

        if theParams is None:
            pParser = boardMeasure()
        else:
            pParser = boardMeasure(theParams)

        #DELETE WHEN ABOVE RUNS.
        #if hasattr(theParams, 'areaThresholdLower'):
        #    theLayer = FromLayer(theParams)
        #else:
        #    theLayer = FromLayer()

        pParser = perceiver.Simple(theDetector=theDetector, theTracker=theLayer, theParams=None)

        pParser.process(theImage, theMask)

        if hasattr(theParams, 'tauDist'):
            thePuzzle = Arrangement(pParser.board, theParams)
        else:
            thePuzzle = Arrangement(pParser.board)

        return thePuzzle

#
#======================= puzzle.builder.arrangement ======================
