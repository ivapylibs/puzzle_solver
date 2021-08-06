#========================= puzzle.simulator.basic ========================
#
# @class    puzzle.simulator.basic
#
# @brief    This is the simplest puzzle simulator, which keeps track of a
#           puzzle board and applies atomic moves to it when requested.
#
#========================= puzzle.simulator.basic ========================

#
# @file     basic.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   WHO WHO
# @date     2021/08/06  [started]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================= puzzle.simulator.basic ========================

#===== Dependencies / Packages 
#
WHAT

#===== Class Helper Elements
#

#
#========================= puzzle.simulator.basic ========================
#

class basic:

  #=============================== basic ===============================
  #
  # @brief  Constructor for the class. Requires a puzzle board.
  #
  # @param[in]  thePuzzle   The puzzle board info for simulation.
  # @param[in]  theFig      The figure handle to use (optional).
  #
  def __init__(self, thePuzzle, theFig = None)

    self.puzzle = thePuzzle
    self.layers = 1:self.puzzle.length  # change to python

    self.fig = theFig

    #
    # @todo Should it also have the calibrated solution to know when the
    #       puzzle has been solved? Or should it simply not care about this
    #       part and it should be for another class instance. Leaning
    #       towards not caring since it is not part of the simulation but
    #       rather part of the interpretation of the puzzle board.
    #


  #============================ setPositions ===========================
  #
  # @brief  Sets the positions of all of the pieces.
  #
  # @param[in]  pLocs   Ordered array of puzzle pieces. 
  #
  # If the array of locations is correct, then the puzzle board is updated
  # according to the specified locations.
  #
  def setPositions(self, pLocs):

    pass # REMOVE WHEN WRITTEN
    for ii = 1:self.puzzle.length
      self.puzzle.piece(ii).setPlacement(pLocs(:, ii))

  #============================= movePiece =============================
  #
  # @brief  Moves a single piece to the given location.
  #
  # @param[in]  pInd    The puzzle piece index.
  # @param[in]  pLoc    The puzzle piece location.
  # 
  def setPositions(self, pInd, pLoc):

    pass # REMOVE WHEN WRITTEN
    if pInd is valid
      self.puzzle.piece(pInd).setPlacement(pLoc)
      

  #============================= movePieces ============================
  #
  # @brief  Moves specified pieces to given locations.
  #
  # @param[in]  pInds   The puzzle pieces indices.
  # @param[in]  pLocs   The puzzle pieces locations.
  # 
  def setPositions(self, pInds, pLocs):

    pass # REMOVE WHEN WRITTEN
    pInds = only valid indices.

    for pInd in pInds
      self.puzzle.piece(pInd).setPlacement(pLoc(:,pInd))
      

  #============================= dragPiece =============================
  #
  # @brief  Moves a piece incrementally from where it is.
  #
  # @param[in]  pInd    The puzzle piece index.
  # @param[in]  pVec    The puzzle piece movement vector.
  # 
  def dragPiece(self, pInd, pVec):

    pass # REMOVE WHEN WRITTEN
    if pInd is valid:
      self.puzzle.piece(pInd).offset(pVec)
      NEED TO WRITE offset MEMBER FUNCTION
      IN FUTURE WILL NOT COMMENT ON NEW MEMBER FUNCTIONS.
      SHOULD BE INFERRED FROM ITS BEING MISSING

  #============================= dragPiece =============================
  #
  # @brief  Moves a piece incrementally from where it is.
  #
  # @param[in]  pInds   The puzzle pieces indices.
  # @param[in]  pVecs   The puzzle pieces movement vectors.
  # 
  def setPositions(self, pInds, pLocs):

    pass # REMOVE WHEN WRITTEN. NOT GONNA WRITE ANYMORE.
    pInds = only valid indices.

    for pInd in pInds
      self.puzzle.piece(pInd).offset(pVecs(:,pInd))
  
  #============================== display ============================== 
  #
  # @brief  Displays the current puzzle board.
  #
  def display(self):

    if not self.fig:
      self.fig = create new figure.

    self.puzzle.display(self.fig)

#
#========================= puzzle.simulator.basic ========================
