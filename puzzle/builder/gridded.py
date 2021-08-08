#========================= puzzle.builder.gridded ========================
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
#========================= puzzle.builder.gridded ========================

#
# @file     gridded.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/04 [created]
#           2021/08/05 [modified]
#
#========================= puzzle.builder.gridded ========================

#===== Environment / Dependencies
#

import numpy as np
from dataclasses import dataclass

from puzzle.board import board
from puzzle.builder.arrangement import arrangement
from puzzle.builder.interlocking import interlocking, paramInter
#===== Helper Elements
#

@dataclass
class paramGrid(paramInter):
  tauInter: float = 20

#
#====================== puzzle.builder.interlocking ======================
#

class gridded(interlocking):

  #============================== adjacent =============================
  #
  # @brief  Constructor for the puzzle.builder.adjacent class.
  #
  #
  def __init__(self, solBoard = [], theParams = paramGrid):

    super(gridded, self).__init__(solBoard, theParams)

    if isinstance(solBoard, board):
      self.gc = np.zero(2, solBoard.size())
    else:
      print('Not initialized properly')
      exit()

    # @< Will store the calibrated grid location of the puzzle piece.

    self.__processGrid()

  #============================ processGrid ============================
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
  def __processGrid(self):

    # @todo
    # THIS ONE SHOULD BE COMPLETELY OVERLOADED.
    # TEST TO INTERLOCKING
    # TEST COORDINATES TO DETERMINE GRIDDING.
    # ORDERED FROM TOP LEFT OR FROM BOTTOM LEFT? YOU PICK AND BE CONSISTENT.
    #
    # NEED TO SET
    # self.adjMat
    # self.ilMat
    # self.gc the grid coordinates. I THINK MY NOTES HAD A DIFFERENT
    # VARIABLE NAME. WILL POST TO ISSUE IF I HAVE A STRONG OPINION.

    pass

  # OTHER CODE / MEMBER FUNCTIONS
  #
  # @todo Definitely need to overload the scoring and distance function
  #         to consider adjacency. Not clear how to do so now, so
  #         ignoring and pushing down the road.
  #
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
  def buildFromFile_Puzzle(fileName, theParams=paramGrid):

    aPuzzle = arrangement.buildFromFile_Puzzle(fileName)
    thePuzzle = gridded(aPuzzle.solution, theParams)

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
  def buildFromFile_ImageAndMask(fileName, theParams=paramGrid):

    aPuzzle = arrangement.buildFromFile_ImageAndMask(fileName)
    thePuzzle = gridded(aPuzzle.solution, theParams)

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
  def buildFromFiles_ImageAndMask(imFile, maskFile, theParams=paramGrid):

    aPuzzle = arrangement.buildFromFiles_ImageAndMask(imFile, maskFile)
    thePuzzle = gridded(aPuzzle.solution, theParams)

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
  def buildFrom_ImageAndMask(theImage, theMask, theParams=paramGrid):

    aPuzzle = arrangement.buildFrom_ImageAndMask(theImage, theMask)
    thePuzzle = gridded(aPuzzle.solution, theParams)

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
  def buildFrom_ImageProcessing(theImage, theProcessor=None, theDetector=None, theParams=paramGrid):

    aPuzzle = arrangement.buildFrom_ImageProcessing(theImage, theProcessor, theDetector)
    thePuzzle = gridded(aPuzzle.solution, theParams)

    return thePuzzle

#
#========================= puzzle.builder.gridded ========================
