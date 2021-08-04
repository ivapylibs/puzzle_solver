#====================== puzzle.builder.interlocking ======================
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
#====================== puzzle.builder.interlocking ======================

#
# @file     interlocking.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   WHO ELSE?
# @date     2021/08/04  [started]
#
#====================== puzzle.builder.interlocking ======================

#===== Environment / Dependencies
#

#===== Helper Elements
#

paramSpec class definition with inheritance

#
#====================== puzzle.builder.interlocking ======================
#

class interlocking (puzzle.builder.adjacent):

  #============================== adjacent =============================
  #
  # @brief  Constructor for the puzzle.builder.adjacent class.
  #
  #
  def __init__(self_, solBoard = [], theParms = []):

    CODING THIS ONE AS THOUGH THERE IS A PARMS STRUCT
    if not theParms:
      theParms = paramSpec()

    __init_super__(self_, solBoard, theParms)

    self.adjMat = identity matrix of trues. num pieces x num pieces.
      YES IT IS MEMORY WASTEFUL, BUT WE CAN FIX LATER.
      MATRIX SHOULD BE SYMMETRIC.
    self.ilMat = identity matrix of trues. num pieces x num pieces.

    self.__processInterlocking()

  #======================== processInterlocking ========================
  #
  # @brief  Process the calibration board and determine what pieces are
  #         interlocking or adjacent. 
  #
  # Some pieces might be close to each other but not really
  # interlocking.  Mostly this happens at the corners, but maybe there
  # are weird puzzles that can be thought of with a mix of adjacent and
  # interlocking.
  #
  def __processInterlocking(self):

    self.__processAdjacency()  HOW TO CALL FOR SUPER CLASS?

    self.ilMat = self.adjMat    
    # @note For now interlocking and adjacency will be the same.
    #       Eventually need to figure out how to differentiate.
    #       This may just make things a bit stricter than they should
    #       be.  That's OK.
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


  # OTHER CODE / MEMBER FUNCTIONS
  #
  # @todo Definitely need to overload the scoring and distance function
  #         to consider adjacency. Not clear how to do so now, so
  #         ignoring and pushing down the road.
  #
  # OTHER CODE / MEMBER FUNCTIONS

  #======================== buildFromFile_Puzzle =======================
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
  def buildFromFile_Puzzle(fileName, theParms = paramSpec())

    SEE ADJACENCY FOR HOW TO HANDLE. BE CAREFUL TO AVOID DUPLICATE PROCESSING.
    thePuzzle = interlocking(aPuzzle.solution, theParms)
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
  # @param[in]  fileName    The python file to load.
  #
  # @param[out] thePuzzle   The arrangement puzzle board instance.
  #
  @staticmethod
  def buildFromFile_ImageAndMask(self, fileName, theParms = paramSpec())

    SEE ADJACENCY FOR HOW TO HANDLE. BE CAREFUL TO AVOID DUPLICATE PROCESSING.
    thePuzzle = interlocking(aPuzzle.solution, theParms)
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
  # @param[in]  imFile      The image file to load.
  # @param[in]  maskFile    The maske file to load.
  #
  # @param[out] thePuzzle   The arrangement puzzle board instance.
  #
  @staticmethod
  def buildFromFile_Puzzle(self, fileName, tauDist = None)

    SEE ADJACENCY FOR HOW TO HANDLE. BE CAREFUL TO AVOID DUPLICATE PROCESSING.
    thePuzzle = interlocking(aPuzzle.solution, theParms)
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
  # @param[in]  theMask     The puzzle piece mask information.
  # @param[in]  theImage    The puzzle image data.
  #
  # @param[out] thePuzzle   The arrangement puzzle board instance.
  #
  @staticmethod
  def buildFrom_ImageAndMask(self, theImage, theMask)

    SEE ADJACENCY FOR HOW TO HANDLE. BE CAREFUL TO AVOID DUPLICATE PROCESSING.
    thePuzzle = interlocking(aPuzzle.solution, theParms)
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
  #
  # @param[out] thePuzzle   The arrangement puzzle board instance.
  #
  @staticmethod
  def buildFrom_ImageAndMask(self, theImage, theMask, theDetector = None)

    SEE ADJACENCY FOR HOW TO HANDLE. BE CAREFUL TO AVOID DUPLICATE PROCESSING.
    thePuzzle = interlocking(aPuzzle.solution, theParms)
    return thePuzzle

#
#====================== puzzle.builder.interlocking ======================
