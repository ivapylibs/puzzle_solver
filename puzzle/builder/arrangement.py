#======================= puzzle.builder.arrangement ======================
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
#======================= puzzle.builder.arrangement ======================

#
# @file     arrangement.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/30 [created]
#           2021/08/05 [modified]
#
#======================= puzzle.builder.arrangement ======================

#===== Environment / Dependencies
#
import cv2
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
import pickle

from puzzle.board import board
from puzzle.parser.fromLayer import fromLayer
import puzzle.parser.simple as perceiver

import improcessor.basic as improcessor
import detector.inImage as detector

#===== Helper Elements
#

@dataclass
class paramSpec:
  tauDist: int = 50

#
#======================= puzzle.builder.arrangement ======================
#

class arrangement(board):

  #============================ arrangement ============================
  #
  # @brief  Constructor for the puzzle.builder.arrangement class.
  #
  #
  def __init__(self, solBoard = [], theParams = paramSpec()):
    super(arrangement,self).__init__()

    self.solution = solBoard
    self.tauDist = theParams.tauDist # @<A distance threshold for considering a piece
    # to be correctly placed.

    # @note
    # WHAT DO WE NEED? ADDING TWO ARGUMENTS FOR NOW.
    # AT MINIMUM, WE NEED A SOLUTION TO THE PUZZLE.
    # WE PROBABLY ALSO NEED A DISTANCE THRESHOLD FOR CONSIDERING A PIECE
    # TO BE CORRECTLY PLACED.
    #
    # WHAT MAKES THIS DIFFERENCE FROM A BOARD?
    # IT SHOULD HAVE SCORING FUNCTIONS FOR A NEW BOARD LAYOUT
    # WHOSE PIECE SORT ORDERING DIRECTLY MATCHES THE SOLUTION.
    #
    # IT SHOULD HAVE AN INPLACE DETECTION ROUTINE THAT GETS USED TO
    # ESTIMATE PROGRESS (OR WHAT FRACTION OF PIECE ARE CORRECTLY IN
    # PLACE).
    #
    # CHECK THAT DOCUMENTATION IS CONSISTENT WITH ABOVE.  ADD CODE AND
    # UPDATE DOCUMENTATION.

  #============================ corrections ============================
  #
  # @brief  Given an array of locations that correspond to the puzzle
  #         board (e.g., in the same order as puzzle board list), provide
  #         the correction vector that would move them to the calibrated
  #         locations.
  #
  # The locations are assumed to be ordered according to puzzle piece
  # ordering in the calibrated puzzle board.
  #
  # @param[in]  pLoc       A dict of puzzle piece id & location.
  #
  # @param[out] theVects   A dict of puzzle piece id & solution vectors.
  #
  def corrections(self, pLoc):
    # @note
    # CHECK THAT pLoc HAS SAME CARDINALITY AS puzzle board.
    # DOES length(self.solution) or is it size(self.solution) == size(pLoc,2)
    # WHAT SHOULD RETURN IN CASE OF FAILURE? A NONE. CALLING SCOPE SHOULD
    # CHECK FOR A NONE RETURN VALUE.

    # @note
    # pLocTrue = GET ARRAY OF SOLUTION LOCATIONS.
    # theVects = pLocTrue - pLoc
    #
    # RETURN theVects
    # SIMPLIFY PYTHON AS DESIRED.

    theVects = {}
    pLocTrue = self.solution.pieceLocations()
    if len(pLocTrue) == len(pLoc):
      for id in pLoc:
        # @todo
        # Need double check if the id or id_sol will always be marched with the solution ?
        # I prefer id as build has access to the solution from the very beginning
        theVects[id] = np.array(pLocTrue[id]) - np.array(pLoc[id])
    else:
      # @todo
      # Not decided what to do else if the size does not match yet
      print('Error of unmatched puzzle piece number!')

    return theVects

  #============================= distances =============================
  #
  # @brief  Given an array of locations that correspond to the puzzle
  #         board (e.g., in same order as puzzle board list), provide
  #         the distances between the locations and the calibrated
  #         locations.
  #
  # The locations are assumed to be ordered according to puzzle piece
  # ordering in the calibrated puzzle board.
  #
  # @param[in]  pLoc        A dict of puzzle piece id & location.
  #
  # @param[out] theDists    A dict of puzzle piece id & distance to the solution.
  #
  def distances(self, pLoc):

    # @todo
    # pLocTrue = GET ARRAY OF SOLUTION LOCATIONS.
    # COMPARE TO pLoc ARRAY to plocTrue, GET DISTANCE.
    #
    # RETURN the distances.

    theDists = {}
    pLocTrue = self.solution.pieceLocations()
    if len(pLocTrue) == len(pLoc):
      for id in pLoc:
        # @todo
        # Need double check if the id or id_sol will always be marched with the solution ?
        # I prefer id as build has access to the solution from the very beginning
        theDists[id] = np.linalg.norm(np.array(pLocTrue[id]) - np.array(pLoc[id]))
    else:
      # @todo
      # Not decided what to do else if the size does not match yet
      print('Error of unmatched puzzle piece number!')

    return theDists

  #========================== scoreByLocation ==========================
  #
  # @brief  Given an array of locations that correspond to the puzzle
  #         board (e.g., in same order as puzzle board list), provide a
  #         score for the distance between the locations and the
  #         calibrated locations.
  #
  # The score here is just the sum of the error norms (or the incorrect
  # distance of the placed part to the true placement). The locations
  # are assumed to be ordered according to puzzle piece ordering in the
  # calibrated puzzle board.
  #
  # @param[in]  pLoc        A dict of puzzle piece id & location.
  #
  # @param[out] theScore    The score for the given board.
  #
  def scoreByLocation(self, pLoc):

    errDists = self.distances(pLoc)

    theScore = []
    for _, errDist in errDists.items():
      theScore.append(errDist)
    theScore = np.sum(theScore)

    return theScore

  #============================= scoreBoard ============================
  #
  # @brief  Given a puzzle board with in ordered correspondence with the
  #         calibrated puzzle board, in the same order as puzzle board
  #         list), provide a score for the distance between the puzzle
  #         piece locations and the calibrated locations.
  #
  # The score here is just the sum of the error norms (or the incorrect
  # distance of the placed part to the true placement). 
  #
  # @param[in]  theBoard    A puzzle board in 1-1 ordered correspondence
  #                         with solution.
  #
  # @param[out] theScore    The score for the given board.
  #
  def scoreBoard(self, theBoard):

    if theBoard.size() == self.solution.size():
      pLocs = theBoard.pieceLocations()
      theScore = self.scoreByLocation(pLocs)
    else:
      theScore = float('inf')

    return theScore

  #=========================== piecesInPlace ===========================
  #
  # @brief  Return boolean array indicating whether the piece is
  #         correctly in place or not.
  #
  # @param[in]  pLoc        A dict of puzzle piece id & location.
  #
  # @param[out] theScores    A dict of id & bool variable indicating
  #                         whether the piece is correctly in place or not.
  #
  def piecesInPlace(self, pLoc):

    # @todo
    # Threshold on the scoreByLocation.
    # return boolean array

    errDists = self.distances(pLoc)

    theScores = {}
    for id, errDist in errDists.items():
      theScores[id] = errDist < self.tauDist

    return theScores

  #============================== progress =============================
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
    pLocs   = theBoard.pieceLocations()
    inPlace = self.piecesInPlace(pLocs)

    val_list = [val for _, val in inPlace.items()]

    thePercentage = '{:.1%}'.format(np.count_nonzero(val_list) / len(inPlace))

    return thePercentage

  #======================== buildFromFile_Puzzle =======================
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
  def buildFromFile_Puzzle(fileName, tauDist = None):

    theBoard = None
    with open(fileName,'rb') as fp:
      data = pickle.load(fp)

      if hasattr(data, 'board'):
        theBoard = data.board
      if tauDist is None and hasattr(data, 'tauDist'):
        tauDist = data.tauDist

    if isinstance(theBoard, board):
      if tauDist is not None:
        thePuzzle = arrangement(theBoard, paramSpec(tauDist))
      else:
        thePuzzle = arrangement(theBoard)
    else:
      print('There is no board instance saved in the file!')
      exit()

    return thePuzzle

  #===================== buildFromFile_ImageAndMask ====================
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
  def buildFromFile_ImageAndMask(fileName, tauDist = None):

    I = None
    M = None

    with open(fileName,'rb') as fp:
      data = pickle.load(fp)

      if hasattr(data, 'I'):
        I = data.I
      if hasattr(data, 'M'):
        M = data.M
      if tauDist is None and hasattr(data, 'tauDist'):
        tauDist = data.tauDist

    if isinstance(I, np.ndarray) and isinstance(M, np.ndarray):
      if tauDist is not None:
        thePuzzle = arrangement.buildFrom_ImageAndMask(I, M, paramSpec(tauDist))
      else:
        thePuzzle = arrangement.buildFrom_ImageAndMask(I, M)
    else:
      print('There is no Image or Mask saved in the file!')
      exit()

    return thePuzzle

  #==================== buildFromFiles_ImageAndMask ====================
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
  def buildFromFiles_ImageAndMask(imFile, maskFile, tauDist = None):

    I = cv2.imread(imFile)
    M = cv2.imread(maskFile, cv2.IMREAD_GRAYSCALE)

    # Sometimes the value in M may not be strictly 0 or 255
    if np.bitwise_and(M > 0, M < 255).any():
      _, M = cv2.threshold(M, 10, 255, cv2.THRESH_BINARY)


    if isinstance(I, np.ndarray) and isinstance(M, np.ndarray):
      if tauDist is not None:
        thePuzzle = arrangement.buildFrom_ImageAndMask(I, M, paramSpec(tauDist))
      else:
        thePuzzle = arrangement.buildFrom_ImageAndMask(I, M)
    else:
      print('There is no Image or Mask saved in the file!')
      exit()

    return thePuzzle

  #======================= buildFrom_ImageAndMask ======================
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
  def buildFrom_ImageAndMask(theImage, theMask, tauDist = None):

    pParser = fromLayer()
    pParser.process(theImage, theMask)
    if tauDist is not None:
      thePuzzle = arrangement(pParser.getState(), paramSpec(tauDist))
    else:
      thePuzzle = arrangement(pParser.getState())

    return thePuzzle

  #===================== buildFrom_ImageProcessing =====================
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
  def buildFrom_ImageProcessing(theImage, theProcessor = None, theDetector = None):

    if theDetector is None and theProcessor is None:
      if theImage.ndim == 3:
        theProcessor = improcessor.basic(cv2.cvtColor,(cv2.COLOR_BGR2GRAY,),\
                           improcessor.basic.thresh,((0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU),))
        theDetector = detector.inImage(theProcessor)
      elif theImage.ndim == 2:
        theProcessor = improcessor.basic(improcessor.basic.thresh, ((0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU),))
        theDetector = detector.inImage(theProcessor)
    elif theDetector is None and theProcessor is not None:
      theDetector = detector.inImage(theProcessor)

    theLayer = fromLayer()
    pParser = perceiver.simple(theDetector=theDetector , theTracker=theLayer, theParams=None)

    pParser.process(theImage)
    thePuzzle = arrangement(pParser.board)

    return thePuzzle

#
#======================= puzzle.builder.arrangement ======================
