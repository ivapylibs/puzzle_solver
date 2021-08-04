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
  def __init__(self_, solBoard = [], tauDist = 3):

    SHOULD tauDist BE REPLACED WITH A PARAMETER STRUCTURE?
    I THINK SO SINCE SUB-CLASSES MAY HAVE THEIR OWN PARAMETERS.
    FOR SURE ADJACENCY DOES.

    self.solution = solBoard
    self.tauDist = tauDist

    WHAT DO WE NEED? ADDING TWO ARGUMENTS FOR NOW.
    AT MINIMUM, WE NEED A SOLUTION TO THE PUZZLE.
    WE PROBABLY ALSO NEED A DISTANCE THRESHOLD FOR CONSIDERING A PIECE
    TO BE CORRECTLY PLACED.

    WHAT MAKES THIS DIFFERENCE FROM A BOARD?
    IT SHOULD HAVE SCORING FUNCTIONS FOR A NEW BOARD LAYOUT
    WHOSE PIECE SORT ORDERING DIRECTLY MATCHES THE SOLUTION.

    IT SHOULD HAVE AN INPLACE DETECTION ROUTINE THAT GETS USED TO
    ESTIMATE PROGRESS (OR WHAT FRACTION OF PIECE ARE CORRECTLY IN
    PLACE).

    CHECK THAT DOCUMENTATION IS CONSISTENT WITH ABOVE.  ADD CODE AND
    UPDATE DOCUMENTATION.

  #============================ corrections ============================
  #
  # @brief  Given an array of locations that correspond to the puzzle
  #         board (e.g., in same order as puzzle board list), provide
  #         the correction vector that would move them to the calibrated
  #         locations.
  #
  # The locations are assumed to be ordered according to puzzle piece
  # ordering in the calibrated puzzle board.
  #
  # @param[in]  pLoc        Ordered (by association) puzzle piece locations.
  #
  # @param[out] theVects   The puzzle piece to solution vectors.
  #
  def corrections(self, pLoc):

    CHECK THAT pLoc HAS SAME CARDINALITY AS puzzle board.
    DOES length(self.solution) or is it size(self.solution) == size(pLoc,2)
    WHAT SHOULD RETURN IN CASE OF FAILURE? A NONE. CALLING SCOPE SHOULD
    CHECK FOR A NONE RETURN VALUE.

    pLocTrue = GET ARRAY OF SOLUTION LOCATIONS.
    theVects = pLocTrue - pLoc 

    RETURN theVects
    SIMPLIFY PYTHON AS DESIRED.

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
  # @param[in]  pLoc        Ordered (by association) puzzle piece locations.
  #
  # @param[out] theDists    The puzzle piece distance to solution.
  #
  def distances(self, pLoc):

    CHECK THAT pLoc HAS SAME CARDINALITY AS puzzle board.
    DOES length(self.solution) or is it size(self.solution) == size(pLoc,2)
    WHAT SHOULD RETURN IN CASE OF FAILURE? INF FOR ALL DISTANCES TO
    CALIBRATED PUZZLE? ONLY PARTIAL CHECK + INF FOR REMAINING?

    pLocTrue = GET ARRAY OF SOLUTION LOCATIONS.
    COMPARE TO pLoc ARRAY to plocTrue, GET DISTANCE.

    RETURN the distances.

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
  # @param[in]  pLoc        Ordered (by association) puzzle piece locations.
  #
  # @param[out] theScore    The score for the given board.
  #
  def scoreByLocation(self, pLoc):
    pass

    errDists = self.distances(pLoc)
    score = sum(errDists)
    RETURN SUM.

  #============================= scoreBoard ============================
  #
  # @brief  Given a puzzle board with in ordered correspondence with the
  #         calibrated puzzle board, in same order as puzzle board
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

    if size(theBoard) == size(self.solution):
      pLocs = theBoard.locations()    MAY NEED TO WRITE. RETURNS ARRAY.
      return self.scoreByLocation(pLocs)
    else:
      return INFINITY
      IF NOT INFINITY, THEN WHAT?

  #=========================== piecesInPlace ===========================
  #
  # @brief  Return boolean array indicating whether the piece is
  #         correctly in place or not.
  #
  # @param[in]  pLoc        Ordered (by association) puzzle piece locations.
  #
  def piecesInPlace(self, pLoc):
    pass

    Threshold on the scoreByLocation.
    return boolean array

  #============================== progress =============================
  #
  def progress(self, theBoard)
    pLocs   = theBoard.locations()
    inPlace = self.piecesInPlace(pLocs)

    return nnz(inPlace) / numel(inPlace)

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
  def buildFromFile_Puzzle(self, fileName, tauDist = None)

    OPEN FILE / LOAD DATA
    SHOULD BE A BOARD.
    MATLAB ALLOWS OPENING FILE INTO A STRUCTURE. LIKE:
    data = load(file)
    data.puzzle will exist if puzzle variable saved.
    data.tauDist will exist if tauDist variable saved.
    in matlab would check with isfield(data, 'NAME')
    FIGURE OUT EQUIVALENT IMPLEMENTATION

    if not tauDist:
      CHECK IF FILE CONTAINS tauDist. OVERWRITE ARGUMENT IF SO.
      LEAVE ALONG OTHERWISE

    if tauDist:
      thePuzzle = arrangement(theBoard, tauDist)
    else
      thePuzzle = arrangement(theBoard)

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
  def buildFromFile_ImageAndMask(self, fileName, tauDist = None)

    OPEN FILE / LOAD DATA
    SHOULD BE A IMAGE, MASK, AND tauDist (OPTIONAL).

    if not tauDist:
      CHECK IF FILE CONTAINS tauDist. OVERWRITE ARGUMENT IF SO.
      LEAVE ALONG OTHERWISE

    thePuzzle = arrangement.buildFrom_ImageAndMask(I, M)

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
  def buildFromFiles_ImageAndMask(self, fileName, tauDist = None)

    I = LOAD IMAGE 
    M = LOAD MASK
    POSSIBLE DO CONVERSION ON MASK TO BOOLEAN.

    if not tauDist:
      CHECK IF FILE CONTAINS tauDist. OVERWRITE ARGUMENT IF SO.
      LEAVE ALONG OTHERWISE

    thePuzzle = arrangement.buildFrom_ImageAndMask(I, M)

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

    if not theDetector:
      CHECK IF COLOR IMAGE:
        theDetector = IMPROCESSOR THAT CONVERTS TO GRAYSCALE, APPLY OTSU
          THRESHOLD OR OTHER ADAPTIVE THRESHOLD METHOD.
      else GRAYSCALE:
        theDetector = IMPROCESSOR THAT APPLIES OTSU THRESHOLD OR OTHER ADAPTIVE THRESHOLD METHOD.

    pParser = BUILD SIMPLE PERCEIVER PUZZLE PARSER with theDetector and fromLayers.

    pParser.process(theImage)
    thePuzzle = arrangement(pParser.getMeasurement())
    return thePuzzle

#
#======================= puzzle.builder.arrangement ======================
