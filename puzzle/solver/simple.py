#========================== puzzle.solver.simple =========================
#
# @class    puzzle.solver.simple
#
# @brief    A basic puzzle solver that just puts puzzle pieces where they
#           belong based on sequential ordering.
#
# @file     simple.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/06 [created]
#           2021/08/12 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================== puzzle.solver.simple =========================

#===== Environment / Dependencies
#
import numpy as np
import itertools

from puzzle.solver.base import base
from puzzle.builder.arrangement import arrangement
from puzzle.builder.gridded import gridded

#===== Helper Elements
#


#
#========================== puzzle.solver.simple =========================
#

class simple(base):

  #=============================== simple ==============================
  #
  # @brief  Constructor for the simple puzzle solver.  Assumes existence
  #         of solution state and current puzzle state, the match is built up by
  #         the manager.
  #
  def __init__(self, theSol, thePuzzle):

    super(simple, self).__init__(theSol, thePuzzle)

    self.match = None    # @< Mapping from current to desired.

    self.plan = None

  #============================== setMatch =============================
  #
  # @brief  Set up the match
  #
  # @param[in]  match   The match between the id in the measured board
  #                     and the solution board.
  #
  def setMatch(self, match):
    self.match = np.array(match)

  #============================== takeTurn =============================
  #
  # @brief  Perform a single puzzle solving action, which move a piece
  #         to its correct location.
  #
  def takeTurn(self, thePlan = None, defaultPlan='score'):

    if self.plan is None:
      if thePlan is None:
        if defaultPlan=='score':
          self.planByScore()
        elif defaultPlan=='order':
          self.planOrdered()
        else:
          print('No default plan has been correctly initlized.')

      else:
        '''
        @todo Get and apply move from thePlan
        Plans not figured out yet, so ignore for now.
        '''
        pass
    else:
      '''
      @todo Get and apply move from self.plan
      Plans not figured out yet, so ignore for now.
      '''
      pass



  #============================ planByScore ============================
  #
  # @brief      Plan is to solve in the order of lowest score.
  #             Will display the plan and update the puzzle piece.
  #
  def planByScore(self):

    # @note
    # Check current puzzle against desired for correct placement boolean
    # Find lowest false instance
    # Establish were it must be placed to be correct.
    # Move to that location.

    # Upgrade to a builder instance to have more functions
    theArrange = arrangement(self.desired)

    # the pLoc of current ones
    pLoc_cur = self.current.pieceLocations()

    # Obtain the id in the solution board according to match
    pLoc_sol = {}
    for i in self.match:
      pLoc_sol[i[1]] = pLoc_cur[i[0]]

    theScores = theArrange.piecesInPlace(pLoc_sol)
    theDists = theArrange.distances(pLoc_sol)

    # Filter the result by piecesInPlace, only take the False into consideration
    theDists_filtered = {}
    for key in theScores:
      if theScores[key] == False:
        theDists_filtered[key] = theDists[key]

    if len(theDists_filtered) > 0:
      # Note that the key refers to the index in the solution board.
      best_index_sol = min(theDists_filtered, key=theDists_filtered.get)

      # Obtain the correction plan for all the matched pieces
      theCorrect = theArrange.corrections(pLoc_sol)

      index = np.where(self.match[:, 1] == best_index_sol)[0]

      if index.size>0:
        # Obtain the corresponding index in the measured board
        best_index_mea = self.match[:, 0][index][0]

        # Display the plan
        print(f'Move piece {best_index_mea} by', theCorrect[best_index_sol])

        # Execute the plan and update the current board
        self.current.pieces[best_index_mea].setPlacement(theCorrect[best_index_sol], offset=True)
      else:
        print('No assignment found')
    else:
      print('All the puzzle pices have been in position. No move.')

  #============================ planOrdered ============================
  #
  # @brief      Plan is to just solve in order (col-wise).
  #
  def planOrdered(self):

    # Upgrade to a builder instance to have more functions
    theGrid = gridded(self.desired)

    # the pLoc of current ones
    pLoc_cur = self.current.pieceLocations()

    # Obtain the id in the solution board according to match
    pLoc_sol = {}
    for i in self.match:
      pLoc_sol[i[1]] = pLoc_cur[i[0]]

    # Obtain the correction plan for all the matched pieces
    theCorrect = theGrid.corrections(pLoc_sol)

    theScores = theGrid.piecesInPlace(pLoc_sol)

    if all(value == True for value in theScores.values()):
      print('All the puzzle pices have been in position. No move.')

    x_max, y_max = np.max(theGrid.gc, axis=1)

    for i,j in itertools.product(range(int(x_max+1)), range(int(y_max+1))):

      # best_index_sol is just the next target, no matter if the assignment is ready or not
      best_index_sol = np.argwhere((theGrid.gc.T == [i,j]).all(axis=1)).flatten()[0]

      # Check if can find the match for best_index_sol and if theScore is False
      if best_index_sol not in theScores:
        print(f'No assignment found')
        continue
      elif theScores[best_index_sol] == True:
        continue
      else:
        index = np.where(self.match[:, 1] == best_index_sol)[0]

        # Obtain the corresponding index in the measured board
        best_index_mea = self.match[:, 0][index][0]

        # Display the plan
        print(f'Move piece {best_index_mea} by', theCorrect[best_index_sol])

        # Execute the plan and update the current board
        self.current.pieces[best_index_mea].setPlacement(theCorrect[best_index_sol], offset=True)
        break



  #=========================== planGreedyTSP ===========================
  #
  # @brief      Generate a greedy plan based on TS-like problem.
  #
  # The travelling salesman problem is to visit a set of cities in a
  # path optimal manner.  This version applies the same idea in a greed
  # manner. That involves finding the piece closest to the true
  # solution, then placing it.  After that it seearches for a piece that
  # minimizes to distance to pick and to place (e.g., distance to the
  # next piece + distance to its true location).  That piece is added to
  # the plan, and the process repeats until all pieces are planned.
  #
  def planGreedyTSP(self):

    self.plan = None    # EVENTUALLY NEED TO CODE. IGNORE FOR NOW.


#
#========================== puzzle.solver.simple =========================
