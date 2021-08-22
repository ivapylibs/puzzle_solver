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
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/06 [created]
#           2021/08/22 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================= puzzle.simulator.basic ========================

#===== Dependencies / Packages 
#
import matplotlib.pyplot as plt

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
  def __init__(self, thePuzzle, theFig = None):

    self.puzzle = thePuzzle
    self.layers = list(range(self.puzzle.size()))  # change to python

    self.fig = theFig

    #
    # @todo Should it also have the calibrated solution to know when the
    #       puzzle has been solved? Or should it simply not care about this
    #       part and it should be for another class instance. Leaning
    #       towards not caring since it is not part of the simulation but
    #       rather part of the interpretation of the puzzle board.
    #


  #============================ setPieces ===========================
  #
  # @brief  Sets the positions of pieces.
  #
  # @param[in]  pLocs   A dict of puzzle pieces ids and their locations.
  #
  # If the array of locations is correct, then the puzzle board is updated
  # according to the specified locations.
  #
  # @note
  # Yunzhi: Since we use a dict to manage the pLocs input, it does not matter
  # if pLocs have less pieces or not. So we can combine several functions together.
  #
  def setPieces(self, pLocs):

    for ii in range(self.puzzle.size()):
      if self.puzzle.pieces[ii].id in pLocs.keys():
        self.puzzle.pieces[ii].setPlacement(pLocs[self.puzzle.pieces[ii].id])

  #============================= dragPieces =============================
  #
  # @brief  Moves pieces incrementally from where it is.
  #
  # @param[in]  pVecs    A dict of puzzle pieces ids and movement vector.
  # 
  def dragPieces(self, pVecs):

    for ii in range(self.puzzle.size()):
      if self.puzzle.pieces[ii].id in pVecs.keys():
        self.puzzle.pieces[ii].setPlacement(pVecs[self.puzzle.pieces[ii].id], offset=True)


  #============================== toImage ==============================
  #
  # @brief  Uses puzzle piece locations to create an image for
  #         visualizing them.  If given an image, then will place in it.
  #
  # @param[in]  theImage    The image to insert pieces into. (optional)
  #
  # @param[out] theImage    The image to insert pieces into.
  #
  def toImage(self, theImage=None, ID_DISPLAY=False, COLOR=(255, 255, 255), CONTOUR_DISPLAY=True):

    theImage = self.puzzle.toImage(theImage=theImage, ID_DISPLAY=ID_DISPLAY, COLOR=COLOR, CONTOUR_DISPLAY=CONTOUR_DISPLAY )

    return theImage

  #============================== display ============================== 
  #
  # @brief  Displays the current puzzle board.
  #
  def display(self, ID_DISPLAY = True):

    if not self.fig:
      self.fig = plt.figure()

    self.puzzle.display(fh=self.fig, ID_DISPLAY= ID_DISPLAY)

#
#========================= puzzle.simulator.basic ========================
