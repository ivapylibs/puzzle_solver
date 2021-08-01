#======================= puzzle.builder.arrangement ======================
#
# @class    arrangement
#
# @brief    This type of puzzle is simply a set of shapes arranged at
#           specific locations in the image with no occlusion or
#           overlap. Touching is not necessary (typically not the case)
#
#======================= puzzle.builder.arrangement ======================

#
# @file     arrangement.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   WHO ELSE?
# @date     2021/07/30  [started]
#
#======================= puzzle.builder.arrangement ======================

#===== Environment / Dependencies
#

#===== Helper Elements
#

#
#======================= puzzle.builder.arrangement ======================
#

class arrangement (puzzle.board):


  #============================ arrangement ============================
  #
  # @brief  Constructor for the puzzle.builder.arrangement class.
  #
  #
  def __init__(self_):

    WHAT DO WE NEED?
    I WOULD SAY THAT AT MINIMUM, WE NEED A SOLUTION TO THE PUZZLE.

    HOW IS THIS DIFFERENT FROM A BOARD?

    I SUPPOSE IT COULD HAVE SCORING FUNCTIONS IF GIVEN A BOARD LAYOUT
    WHOSE PIECE SORT ORDERING IS 1-1 WITH THE SOLUTION.

  #=============================== score ===============================
  #
  def score(self, theBoard):
    pass

  #============================== progress =============================
  #
  def progress(self, theBoard)
    pass

  #=========================== buildFrom_File ==========================
  #
  # @brief      Load a previously saved arrangement calibration/solution.
  #
  # The python file contains XXXXX WHAT DOES IT CONTAIN???? XXXXX
  #
  #
  # @param[in]  fileName    The python file to load.
  #
  # @param[out] thePuzzle   The arrangement puzzle board instance.
  #
  @staticmethod
  def buildFrom_File(self, fileName)

    OPEN FILE / LOAD DATA
    SHOULD BE A BOARD.

    thePuzzle = arrangement(theBoard)
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

    pParser = BUILD FROMLAYER PUZZLE PARSER.  

    pParser.process(theImage, theMask)

    thePuzzle = arrangement(pParser.getMeasurement())
    return thePuzzle

  #===================== buildFrom_ImageProcessing =====================
  #
  # @brief      Given an image with regions clearly separated by some
  #             color or threshold, parse it to recover the puzzle
  #             calibration/solution.
  #
  # Instantiates a REPLACE WITH CORRECT TEXT: puzzle parsing operator, then applies it to the
  # submitted data to create a puzzle board instance. That instance is
  # the calibration/solution.
  #
  # @param[in]  theImage        The puzzle image data.
  # @param[in]  theProcessor    The processing scheme.
  #
  # @param[out] thePuzzle   The arrangement puzzle board instance.
  #
  @staticmethod
  def buildFrom_ImageAndMask(self, theImage, theMask)

    pParser = BUILD SIMPLE PERCEIVER PUZZLE PARSER.  

    pParser.process(theImage)

    thePuzzle = arrangement(pParser.getMeasurement())
    return thePuzzle

#
#======================= puzzle.builder.arrangement ======================
