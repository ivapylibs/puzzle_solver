# ====================== puzzle.builder.interlocking ======================
#
# @class    interlocking
#
# @brief    This type of puzzle is simply a set of shapes arranged at
#           specific locations that should actually interlock. Placement
#           for them is less forgiving. In principle, they need to fit
#           together.
#
# This class is a step up from the adjacency class. The adjacent puzzle
# pieces actually interlock.
#
# It also includes a scoring mechanism to indicate how "close" a current
# solution would be to the calibrated solution.
#
# ====================== puzzle.builder.interlocking ======================
#
# @file     interlocking.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/04 [created]
#           2021/08/05 [modified]
#
# ====================== puzzle.builder.interlocking ======================

# ===== Environment / Dependencies
#

import pickle
from dataclasses import dataclass

import numpy as np

from puzzle.builder.adjacent import Adjacent, ParamAdj
from puzzle.builder.arrangement import Arrangement
from puzzle.builder.board import Board


# ===== Helper Elements
#

@dataclass
class ParamInter(ParamAdj):
    tauInter: float = 35


#
# ====================== puzzle.builder.interlocking ======================
#

class Interlocking(Adjacent):

    # ============================== adjacent =============================
    #
    # @brief  Constructor for the puzzle.builder.adjacent class.
    #
    #
    def __init__(self, theBoard=[], theParams=ParamInter):
        """
        @brief  Constructor for the puzzle.builder.adjacent class.

        Args:
            theBoard: The input board instance.
            theParams: The params.
        """

        super(Interlocking, self).__init__(theBoard, theParams)

        if isinstance(theBoard, Board):
            self.ilMat = np.eye(theBoard.size()).astype('bool')
        else:
            raise TypeError('Not initialized properly')

        self.processInterlocking()

    def processInterlocking(self):
        """
        @brief Process the solution board and determine what pieces are
               interlocking or adjacent.

               Some pieces might be close to each other but not really
               interlocking.  Mostly this happens at the corners, but maybe there
               are weird puzzles that can be thought of with a mix of adjacent and
               interlocking.
        """

        # Todo: Wait for further development
        self.ilMat = self.adjMat

        # @note
        # For now interlocking and adjacency will be the same.
        # Eventually need to figure out how to differentiate.
        # This may just make things a bit stricter than they should
        # be.  That's OK.
        #

        # @note One way to cheaply differentiate interlocking from adjacent
        # is based on the number of neighboring points. Interlocking have
        # many (on the cardinality of the corresponding side length for the
        # bounding box. Corner touching or simply adjacent will have much
        # less, say less than half the smallest side length or even less.
        # Maybe on the order of 3*tauAdj boundary neighbors.
        # OR DEFINE A NEW PARAMETER TO SPECIFY THE THRESHOLD. WHATEVER IS
        # EASIEST. REQUIRES NEW PARAMETER CLASS MOST LIKELY.
        #

    @staticmethod
    def buildFromFile_Puzzle(fileName, theParams=None):
        """
        @brief Load a saved arrangement calibration/solution puzzle board.

        Args:
            fileName: The python file to load.
            theParams: The params.

        Returns:
            thePuzzle: The interlocking puzzle board instance.
        """

        aPuzzle = Arrangement.buildFromFile_Puzzle(fileName,theParams)

        with open(fileName, 'rb') as fp:
            data = pickle.load(fp)

        if hasattr(data, 'tauInter'):
            theParams = ParamInter(tauAdj=data.tauInter)

        if hasattr(theParams, 'tauInter'):
            thePuzzle = Interlocking(aPuzzle, theParams)
        else:
            thePuzzle = Interlocking(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFromFile_ImageAndMask(fileName, theParams=None):
        """
        @brief Load a saved arrangement calibration/solution stored as an image and a mask.

        The python file contains the puzzle board mask and image source
        data. It gets processed into an arrangement instance. If a threshold
        variable ``tauDist`` is found, then it is applied to the arrangement
        instance.

        Args:
            fileName: The python file to load.
            theParams: The params.

        Returns:
            thePuzzle: The interlocking puzzle board instance.
        """

        aPuzzle = Arrangement.buildFromFile_ImageAndMask(fileName, theParams)

        if hasattr(theParams, 'tauInter'):
            thePuzzle = Interlocking(aPuzzle, theParams)
        else:
            thePuzzle = Interlocking(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFromFiles_ImageAndMask(imFile, maskFile, theParams=None):
        """
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
            thePuzzle: The interlocking puzzle board instance.
        """

        aPuzzle = Arrangement.buildFromFiles_ImageAndMask(imFile, maskFile, theParams)

        if hasattr(theParams, 'tauInter'):
            thePuzzle = Interlocking(aPuzzle, theParams)
        else:
            thePuzzle = Interlocking(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFrom_ImageAndMask(theImage, theMask, theParams=None):
        """
        @brief Given an image and an image mask, parse both to recover
               the puzzle calibration/solution.

        Instantiates a puzzle parser that gets applied to the submitted data
        to create a puzzle board instance. That instance is the calibration/solution.

        Args:
            theImage: The puzzle image data.
            theMask: The puzzle mask data.
            theParams: The params.

        Returns:
            thePuzzle: The interlocking puzzle board instance.
        """

        aPuzzle = Arrangement.buildFrom_ImageAndMask(theImage, theMask, theParams)

        if hasattr(theParams, 'tauInter'):
            thePuzzle = Interlocking(aPuzzle, theParams)
        else:
            thePuzzle = Interlocking(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFrom_ImageProcessing(theImage, theProcessor=None, theDetector=None, theParams=None):
        """
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
            thePuzzle: The interlocking puzzle board instance.
        """

        aPuzzle = Arrangement.buildFrom_ImageProcessing(theImage, theProcessor, theDetector, theParams)

        if hasattr(theParams, 'tauInter'):
            thePuzzle = Interlocking(aPuzzle, theParams)
        else:
            thePuzzle = Interlocking(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFrom_Sketch(theImage, theMask, theProcessor=None, theDetector=None, theParams=None):
        """
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
            thePuzzle: The interlocking puzzle board instance.
        """

        aPuzzle = Arrangement.buildFrom_Sketch(theImage, theMask, theProcessor, theDetector, theParams)
        if hasattr(theParams, 'tauInter'):
            thePuzzle = Interlocking(aPuzzle, theParams)
        else:
            thePuzzle = Interlocking(aPuzzle)

        return thePuzzle

#
# ====================== puzzle.builder.interlocking ======================
