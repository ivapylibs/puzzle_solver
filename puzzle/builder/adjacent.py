# ======================== puzzle.builder.adjacent ========================
#
# @class    adjacent
#
# @brief    This type of puzzle is simply a set of shapes arranged at
#           specific locations with adjacency permitted.  Touching or
#           very close proximity should hold for most or all pieces.
#
#
# This class is a step up from the arrangement class. It provide a
# template puzzle board consisting of puzzle pieces that should be
# placed at specific locations, along with adjacency information.  
# Adjacency tests can either use a provided threshold argument or 
#
# It also includes a scoring mechanism to indicate how "close" a current
# solution would be to the calibrated solution.
#
# ======================== puzzle.builder.adjacent ========================
#
# @file     adjacent.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/04 [created]
#           2021/08/05 [modified]
#
# ======================== puzzle.builder.adjacent ========================

import pickle
from dataclasses import dataclass

# ===== Environment / Dependencies
#
import numpy as np

from puzzle.builder.arrangement import Arrangement, ParamArrange
from puzzle.builder.board import Board


# ===== Helper Elements
#

@dataclass
class ParamAdj(ParamArrange):
    tauAdj: float = 35


#
# ======================== puzzle.builder.adjacent ========================
#

class Adjacent(Arrangement):

    # ============================== adjacent =============================
    #
    # @brief  Constructor for the puzzle.builder.adjacent class.
    #
    #
    def __init__(self, theBoard=[], theParams=ParamAdj):

        super(Adjacent, self).__init__(theBoard, theParams)

        if isinstance(theBoard, Board):
            self.adjMat = np.eye(theBoard.size()).astype('bool')
        else:
            raise TypeError('Not initialized properly')

        # Todo: May have problems if the pieces are not good
        self.processAdjacency()

    def processAdjacency(self):
        """
        @brief  Process the solution board and determine what pieces are
                adjacent or "close enough." It will determine the adjacency
                matrix.

        Assumes that adjacent matrix has been instantiated and what is
        needed is to populate its values with the correct ones.
        """

        # Reset
        self.adjMat[:,:] = False

        for ii in range(self.size()):
            for jj in range(ii + 1, self.size()):
                if self.testAdjacent(ii, jj, self.params.tauAdj):
                    self.adjMat[ii, jj] = True
                    self.adjMat[jj, ii] = True

    # OTHER CODE / MEMBER FUNCTIONS

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

        aPuzzle = Arrangement.buildFromFile_Puzzle(fileName)

        with open(fileName, 'rb') as fp:
            data = pickle.load(fp)

        if hasattr(data, 'tauAdj'):
            theParams = ParamAdj(tauAdj=data.tauAdj)

        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

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

        aPuzzle = Arrangement.buildFromFile_ImageAndMask(fileName, theParams)

        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

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

        aPuzzle = Arrangement.buildFromFiles_ImageAndMask(imFile, maskFile, theParams)

        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

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

        aPuzzle = Arrangement.buildFrom_ImageAndMask(theImage, theMask, theParams)

        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

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

        aPuzzle = Arrangement.buildFrom_ImageProcessing(theImage, theProcessor, theDetector, theParams)
        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

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

        aPuzzle = Arrangement.buildFrom_Sketch(theImage, theMask, theProcessor, theDetector, theParams)
        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

        return thePuzzle

#
# ======================== puzzle.builder.adjacent ========================
