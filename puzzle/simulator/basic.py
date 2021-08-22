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


  #============================ setPositions ===========================
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
  def setPositions(self, pLocs):

    for ii in range(self.puzzle.size()):
      if self.puzzle.piece[ii].id in pLocs.keys():
        self.puzzle.piece[ii].setPlacement(pLocs[self.puzzle.piece[ii].id])

  #============================= dragPiece =============================
  #
  # @brief  Moves pieces incrementally from where it is.
  #
  # @param[in]  pVecs    A dict of puzzle pieces ids and movement vector.
  # 
  def dragPiece(self, pVecs):

    for ii in range(self.puzzle.size()):
      if self.puzzle.piece[ii].id in pVecs.keys():

        self.puzzle.piece[ii].offset(pVecs[self.puzzle.piece[ii].id])

  #============================== display ============================== 
  #
  # @brief  Displays the current puzzle board.
  #
  def display(self):

    if not self.fig:
      self.fig = plt.figure()

    self.puzzle.display(fh=self.fig)

#
#========================= puzzle.simulator.basic ========================
