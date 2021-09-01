#================================ manager ================================
#
# @brief    Manage the tracking of puzzle pieces. 
#
#
# This puzzle piece manager keeps track of the puzzle pieces and their
# association over time as new imagery of the scene is captured. This
# manager stores the puzzle piece instances and organizes the code for
# data association. Even though the individual puzzle piece instances
# has some mechanism to recognize matches in their class API, the
# implementation in the manager can override those matching mechanisms
# using other considerations such as multi-piece competition or changes
# in the image and what regions are linked to those changes.
#
# As an example, this manager can get all similarity (or difference)
# scores and use them for generating assignments instead of greedily
# creating assignments for each puzzle piece independently of the other
# pieces.
#
# To be able to generate the associations, the puzzle manager should
# have a template or calibration puzzle board.
#
#================================ manager ================================

#
# @file     manager.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/26 [created]
#           2021/08/01 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#================================ manager ================================

#===== Environment / Dependencies
#
from dataclasses import dataclass
import itertools

import numpy as np

from puzzle.parser.fromLayer import fromLayer

from puzzle.piece.moments import moments
from puzzle.piece.edge import edge

#===== Helper Elements
#
# DEFINE ENUMERATED TYPE HERE FOR scoreType.
SCORE_DIFFERENCE = 0
SCORE_SIMILAR = 1

@dataclass
class managerParms:
  scoreType: int = SCORE_DIFFERENCE
  matcher: any = moments(20)
#
#================================ manager ================================
#

class manager(fromLayer):

  # @note
  # SHOULD MOST LIKELY BE SOME FORM OF TRACKPOINTER. INTERFACE SHOULD
  # MATCH. WHAT SHOULD THE SUPERCLASS BE? IT MIGHT BE THAT CREATING A NEW
  # TRACKPOINTER CLASS WITH SOME LIMITED FUNCTIONALITY IS IN ORDER.
  # LIKE ONE CALLED multiRegions or regionsMulti or something like that.
  # IT TAKES IN AN IMAGE (POSSIBLY ALREADY BINARIZED) AND RECOVERS THE
  # DISTINCT REGIONS ASSOCIATED TO IT.

  # 2021/07/28
  #
  # ELSEWHERE I HAD NOTED IT SHOULD BE A PERCEIVER AND POSSIBLE EVEN A
  # SUB-CLASS OF PUZZLE.PARSER.SIMPLE.  I TAKE THAT BACK. IT SHOULD BE A
  # TRACKPOINTER FOR NOW. WHETHER IT IS DERIVED FROM CENTROIDMULTI IS
  # ANOTHER STORY. DOESN'T HURT RIGHT NOW. LATER ON MIGHT REQUIRE A
  # CHANGE.
  #

  # 2021/07/29
  # WILL END UP A SUB-CLASS OF PUZZLE.PARSER.FROMLAYER DOING REPLACEMENT
  # NOW.

  # @note
  # Yunzhi: trackpointer.centroidMulti -> PUZZLE.PARSER.FROMLAYER -> puzzle.manager

  #=============================== manager ==============================
  #
  # @brief  Constructor for the puzzle piece manager class.
  #
  # @param[in]  solution    A solution/calibrated board instance.
  # @param[in]  theParms    Any additional parameters in a structure.
  #
  def __init__(self, solution, theParms = managerParms):
    super(manager, self).__init__()

    self.solution = solution              # @< The solution puzzle board.
    self.scoreType = theParms.scoreType   # @< The type of comparator.
    self.pAssignments = []                # @< Assignments: meas to sol.
    self.bAssigned = []                   # @< Puzzle board of assigned pieces.

    self.matcher = theParms.matcher

  #============================== predict ==============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #============================== measure ==============================
  #
  # @brief  Process the passed imagery to recover puzzle pieces and
  #         manage their track states.
  #
  # @param[in]  I   Source image.
  # @param[in]  M   Layer mask (binary)
  # OR
  # @param[in]  board The measured board.
  #
  def measure(self, *argv):

    if len(argv)==1:
      self.bMeas = argv[0]
    else:
      I = argv[0]
      M = argv[1]
      # Call measure function from fromLayer to generate a measured board
      # self.bMeas
      super().measure(I,  M)


    # Compare with ground truth/generate associates
    self.matchPieces()

    # Generate a new board for association, filtered by the matcher threshold
    pFilteredAssignments = []
    for assignment in self.pAssignments:
      ret = self.matcher.compare(self.bMeas.pieces[assignment[0]], self.solution.pieces[assignment[1]])
      if ret:
        pFilteredAssignments.append(assignment)

    # pAssignments refers to the index but not the id of the puzzle piece
    self.pAssignments = pFilteredAssignments
    self.bAssigned = self.bMeas.getAssigned(self.pAssignments)

  #=========================== matchPieces ==========================
  #
  # @brief  Match all the measured puzzle pieces with the ground truth in a pairwise manner
  #         to get meas to sol.
  #
  def matchPieces(self):

    scoreTable = np.zeros((self.bMeas.size(),self.solution.size()))
    for idx_x, bMea in enumerate(self.bMeas.pieces):
      for idx_y, bSol in enumerate(self.solution.pieces):
        ret = self.matcher.score(bMea, bSol)
        '''
        @todo Yunzhi: Will update this part. We may need two scoreTables. 
        Currently, only use the shape feature and add up the distances.
        '''
        if type(ret) is tuple and len(ret)>0:
          scoreTable[idx_x][idx_y] = np.sum(ret[0])
        else:
          scoreTable[idx_x][idx_y] = ret

    # The measured piece will be assigned a solution piece
    # However, for some measured piece, they may not have a match according to the threshold.
    self.pAssignments = self.greedyAssignment(scoreTable)


  #=========================== greedyAssignment ==========================
  #
  # @brief  Run the greedyAssignment for the score table.
  #
  # @param[in]  scoreTable   The score table for the pairwise comparison.
  #
  # @param[out]  matched_indices   The matched pairs. N x 2
  #
  def greedyAssignment(self, scoreTable):
    matched_indices = []
    if scoreTable.shape[1] == 0:
      return np.array(matched_indices).reshape(-1, 2)
    for i in range(scoreTable.shape[0]):
      if self.scoreType == SCORE_DIFFERENCE:
        j = scoreTable[i].argmin()
        # @todo Yunzhi: The threshold needs to be decided by the feature method
        if scoreTable[i][j] < 1e16:
          scoreTable[:, j] = 1e18
          matched_indices.append([i, j])
      else:
        j = scoreTable[i].argmax()
        # @todo Yunzhi: The threshold needs to be decided by the feature method
        if scoreTable[i][j] > 10:
          scoreTable[:, j] = 100
          matched_indices.append([i, j])

    # matched_indices refers to the index but not the id of the puzzle piece
    matched_indices = np.array(matched_indices).reshape(-1, 2)

    return matched_indices

  #============================== correct ==============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #=============================== adapt ===============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #=========================== process ==========================
  #
  # @brief  Run the tracking pipeline for image measurement or directly work
  #         on a measured board. Assume two modes: 1. I & M 2. the measured board.
  #
  # @param[in]  I   Source image.
  # @param[in]  M   Layer mask (binary)
  # @param[in]  board The measured board.
  #
  def process(self, *argv):

    self.measure(*argv)

#
#================================ manager ================================
