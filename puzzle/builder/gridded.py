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
import pickle

import scipy.cluster.hierarchy as hcluster

from puzzle.utils.dataProcessing import updateLabel

from puzzle.board import board
from puzzle.builder.arrangement import arrangement
from puzzle.builder.interlocking import interlocking, paramInter
#===== Helper Elements
#

@dataclass
class paramGrid(paramInter):
  tauGrid: float = 30

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
      # @< Will store the calibrated grid location of the puzzle piece.
      self.gc = np.zeros((2, solBoard.size()))
    else:
      print('Not initialized properly')
      exit()

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

    pLoc = self.solution.pieceLocations()

    x_list = np.array([rLoc[0] for _, rLoc  in pLoc.items()]).reshape(-1,1)
    y_list = np.array([rLoc[1] for _, rLoc  in pLoc.items()]).reshape(-1,1)

    # Check the puzzle shape size to determine the thresh here
    x_thresh = np.mean([piece.y.size[0] for piece in self.solution.pieces])
    x_label = hcluster.fclusterdata(x_list, x_thresh, criterion="distance")
    x_label = updateLabel(x_list, x_label)

    y_thresh = np.mean([piece.y.size[1] for piece in self.solution.pieces])
    y_label = hcluster.fclusterdata(y_list, y_thresh, criterion="distance")
    y_label = updateLabel(y_list, y_label)

    for ii in range(self.solution.size()):
      # The order is in line with the one saving in self.solution.pieces
      self.gc[:,ii]= x_label[ii], y_label[ii]

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
  def buildFromFile_Puzzle(fileName, tauGrid= None):

    aPuzzle = arrangement.buildFromFile_Puzzle(fileName)

    with open(fileName, 'rb') as fp:
      data = pickle.load(fp)

    if tauGrid is None and hasattr(data, 'tauGrid'):
      tauGrid = data.tauGrid

    if tauGrid is not None:
      thePuzzle = gridded(aPuzzle.solution, paramGrid(tauGrid))
    else:
      thePuzzle = gridded(aPuzzle.solution, paramGrid())


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
