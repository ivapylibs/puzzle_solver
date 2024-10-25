#======================== puzzle.builder.adjacent ========================
##
# @package  puzzle.builder.adjacent
# @brief    This type of puzzle is simply a set of shapes arranged at
#           specific locations with adjacency permitted.  Touching or
#           very close proximity should hold for most or all pieces.
#
# @ingroup  Puzzle_Types
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#
# @date     2021/08/05 [modified]
# @date     2021/08/04 [created]
#

#======================== puzzle.builder.adjacent ========================
#
# NOTE
#   90 columns, 4 space indent.
#
#======================== puzzle.builder.adjacent ========================

import pickle
from dataclasses import dataclass

# ===== Environment / Dependencies
#
import numpy as np

from puzzle.builder.arrangement import Arrangement, CfgArrangement
from puzzle.board import Board


# ===== Helper Elements
#

#@dataclass
#class ParamAdj(ParamArrange):
#    tauAdj: float = 35
# DELETE WHEN NEW CODE WORKS. BROKEN MANY PLACES.

#---------------------------------------------------------------------------
#====================== Configuration Node : Adjacent ======================
#---------------------------------------------------------------------------
#

class CfgAdjacent(CfgArrangement):
    '''!
    @ingroup  Puzzle_Types
    @brief  Configuration setting specifier for Arrangement.
    '''
  
    #============================= __init__ ============================
    #
    def __init__(self, init_dict=None, key_list=None, new_allowed=True):
        '''!
        @brief        Constructor of configuration instance.
      
        @param[in]    cfg_files   List of config files to load to merge settings.
        '''
        if (init_dict == None):
          init_dict = CfgAdjacent.get_default_settings()
    
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
        default_dict = super(CfgAdjacent,CfgAdjacent).get_default_settings()
        default_dict.update(dict(tauAdj = 35))
    
        return default_dict
  


#
# ======================== puzzle.builder.adjacent ========================
#

class Adjacent(Arrangement):
    """!
    @ingroup    Puzzle_Types
    @brief      Puzzle whose pieces will be touching as part of the solution.

    This class is a step up from the arrangement class. It provide a
    template puzzle board consisting of puzzle pieces that should be
    placed at specific locations, along with adjacency information.  
    Adjacency tests can either use a provided threshold argument or 

    It also includes a scoring mechanism to indicate how "close" a current
    solution would be to the calibrated solution.
    """

    def __init__(self, theBoard=[], theParams=CfgAdjacent):
        """!
        @brief Constructor for the puzzle.builder.adjacent class.

        Args:
            theBoard: The input board instance.
            theParams: The params.
        """

        super(Adjacent, self).__init__(theBoard, theParams)

        if isinstance(theBoard, Board):
            # Note that the Mat's index may not be the same as id in the piece dict.
            # Have to be translated for further use.
            self.adjMat = np.eye(theBoard.size()).astype('bool')
        else:
            raise TypeError('Not initialized properly')

        # Todo: May have problems if the pieces are not good
        self.processAdjacency()

    def processAdjacency(self):
        """!
        @brief  Process the solution board and determine what pieces are
                adjacent or "close enough." It will determine the adjacency
                matrix.

        Assume that adjacent matrix has been instantiated and what is
        needed is to populate its values with the correct ones.
        """

        # Reset
        self.adjMat[:,:] = np.eye(self.size()).astype('bool')


        pieceKeysList = list(self.pieces.keys())

        for ii in range(self.size()):
            for jj in range(ii + 1, self.size()):
                if self.testAdjacent(pieceKeysList[ii], pieceKeysList[jj], self.params.tauAdj):
                    self.adjMat[ii, jj] = True
                    self.adjMat[jj, ii] = True

    # OTHER CODE / MEMBER FUNCTIONS
    @staticmethod
    def buildFromFile_Puzzle(fileName, theParams=None):
        """!
        @brief Load a saved arrangement calibration/solution puzzle board.

        Args:
            fileName: The python file to load.
            theParams: The params.

        Returns:
            thePuzzle: The adjacent puzzle board instance.
        """

        aPuzzle = Arrangement.buildFromFile_Puzzle(fileName, theParams)

        with open(fileName, 'rb') as fp:
            data = pickle.load(fp)

        if hasattr(data, 'tauAdj'):     # ARGH!! DELETE LIKE OTHERS WHEN WORKING,.
            theParams = CfgAdjacent()   # HAS TO DO WITH BAD SAVE/LOAD. MOVE TO HDF5
            theParams.tauAdj = data.tauAdj

        thePuzzle = Adjacent(aPuzzle, theParams)
        #if hasattr(theParams, 'tauAdj'):
        #    thePuzzle = Adjacent(aPuzzle, theParams)
        #else:
        #    thePuzzle = Adjacent(aPuzzle)

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
            thePuzzle: The adjacent puzzle board instance.
        """

        aPuzzle = Arrangement.buildFromFile_ImageAndMask(fileName, theParams)

        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

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
            thePuzzle: The adjacent puzzle board instance.
        """

        aPuzzle = Arrangement.buildFromFiles_ImageAndMask(imFile, maskFile, theParams)

        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

        return thePuzzle

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
            thePuzzle: The adjacent puzzle board instance.
        """

        aPuzzle = Arrangement.buildFrom_ImageAndMask(theImage, theMask, theParams)

        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

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
            thePuzzle: The adjacent puzzle board instance.
        """

        aPuzzle = Arrangement.buildFrom_ImageProcessing(theImage, theProcessor, theDetector, theParams)
        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

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
            thePuzzle: The adjacent puzzle board instance.
        """

        aPuzzle = Arrangement.buildFrom_Sketch(theImage, theMask, theProcessor, theDetector, theParams)
        if hasattr(theParams, 'tauAdj'):
            thePuzzle = Adjacent(aPuzzle, theParams)
        else:
            thePuzzle = Adjacent(aPuzzle)

        return thePuzzle

#
# ======================== puzzle.builder.adjacent ========================
