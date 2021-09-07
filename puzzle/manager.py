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

from puzzle.piece.matchDifferent import matchDifferent
from puzzle.piece.matchSimilar import matchSimilar

#===== Helper Elements
#
# DEFINE ENUMERATED TYPE HERE FOR scoreType.
SCORE_DIFFERENCE = 0
SCORE_SIMILAR = 1

@dataclass
class managerParms:
  # scoreType: int = SCORE_DIFFERENCE
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
    self.pAssignments = []                # @< Assignments: meas to sol.
    self.bAssigned = []                   # @< Puzzle board of assigned pieces.

    self.matcher = theParms.matcher       # @< Matcher instance

    if isinstance(self.matcher,matchDifferent):
      self.scoreType = SCORE_DIFFERENCE   # @< The type of comparator.
    elif isinstance(self.matcher,matchSimilar):
      self.scoreType = SCORE_SIMILAR   # @< The type of comparator.
    else:
      raise TypeError('The matcher is of wrong input.')

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

    scoreTable_shape = np.zeros((self.bMeas.size(),self.solution.size()))
    scoreTable_color = np.zeros((self.bMeas.size(), self.solution.size()))
    scoreTable_edge_color = np.zeros((self.bMeas.size(), self.solution.size(),4))
    for idx_x, bMea in enumerate(self.bMeas.pieces):
      for idx_y, bSol in enumerate(self.solution.pieces):
        ret = self.matcher.score(bMea, bSol)
        '''
        @todo Yunzhi: Will update this part. We may need two scoreTables. 
        Currently, only use the shape feature and add up the distances.
        '''
        # if idx_x==56 and (idx_y==58 or idx_y==56):
        #   print('s')
        if type(ret) is tuple and len(ret)>0:
          scoreTable_shape[idx_x][idx_y] = np.sum(ret[0])
          scoreTable_color[idx_x][idx_y] = np.sum(ret[1])
          scoreTable_edge_color[idx_x][idx_y] = ret[1]
        else:
          scoreTable_shape[idx_x][idx_y] = ret

    # The measured piece will be assigned a solution piece
    # However, for some measured piece, they may not have a match according to the threshold.
    self.pAssignments = self.greedyAssignment(scoreTable_shape, scoreTable_color, scoreTable_edge_color)


  #=========================== greedyAssignment ==========================
  #
  # @brief  Run the greedyAssignment for the score table.
  #
  # @param[in]  scoreTable   The score table for the pairwise comparison.
  #
  # @param[out]  matched_indices   The matched pairs. N x 2
  #
  def greedyAssignment(self, scoreTable_shape, scoreTable_color, scoreTable_edge_color):

    # Single feature
    if np.count_nonzero(scoreTable_color)==0:
      # @note Yunzhi: Only focus on the difference in the scoreTable_shape
      matched_indices = []
      if scoreTable_shape.shape[1] == 0:
        return np.array(matched_indices).reshape(-1, 2)
      for i in range(scoreTable_shape.shape[0]):
        if self.scoreType == SCORE_DIFFERENCE:
          j = scoreTable_shape[i].argmin()
          # @todo Yunzhi: The threshold needs to be decided by the feature method
          if scoreTable_shape[i][j] < 1e16:
            scoreTable_shape[:, j] = 1e18
            matched_indices.append([i, j])
        else:
          j = scoreTable_shape[i].argmax()
          # @todo Yunzhi: The threshold needs to be decided by the feature method
          if scoreTable_shape[i][j] > 2:
            scoreTable_shape[:, j] = -100
            matched_indices.append([i, j])

      # matched_indices refers to the index but not the id of the puzzle piece
      matched_indices = np.array(matched_indices).reshape(-1, 2)

    else:
      # @todo Yunzhi: Currently, it is hard-coded for edge feature
      # Shape + Color feature

      def getKeepList(score_list, diff_thresh=150):

        # Create new lists by removing the first element or the last element
        # score_list_cmp_1 = np.delete(score_list, -1) # incremental change

        score_list_cmp_1 = np.ones_like(score_list) *score_list[0] # absolute change with the first element
        score_list_cmp_1 = np.delete(score_list_cmp_1, -1)

        score_list_cmp_2 = np.delete(score_list, 0)

        score_diff_list = score_list_cmp_2-score_list_cmp_1

        keep = [0]
        for idx, score_diff in enumerate(score_diff_list):
          if not np.isnan(score_diff) and score_diff< diff_thresh :
            keep.append(idx+1)
          else:
            break

        return keep


      matched_indices = []
      if scoreTable_shape.shape[1] == 0:
        return np.array(matched_indices).reshape(-1, 2)
      for i in range(scoreTable_shape.shape[0]):
        # j = scoreTable_shape[i].argmin()

        shape_list = scoreTable_shape[i]
        ind_shape_sort = np.argsort(shape_list, axis=0)
        shape_sort_list = np.sort(shape_list, axis=0)

        # Update ind_shape_sort and shape_sort_list in a small range since
        # distance between shape features may be similar, we want to keep all of them
        keep_list = getKeepList(shape_sort_list)
        ind_shape_sort = ind_shape_sort[keep_list] # ind in shape_list (complete)

        # Not used for now
        shape_sort_list = shape_sort_list[keep_list]

        if ind_shape_sort.size==1:
          # @todo Yunzhi: The threshold needs to be decided by the feature method
          j = ind_shape_sort[0]
        else:

          color_list = scoreTable_color[i][ind_shape_sort]
          ind_color_sort = np.argsort(color_list, axis=0) # ind in color_list (not complete)
          color_sort_list = np.sort(color_list, axis=0)

          # Update ind_shape_sort and shape_sort_list in a small range since
          # distance between shape features may be similar, we want to keep all of them

          keep_list = getKeepList(color_sort_list,10)
          ind_color_sort = ind_color_sort[keep_list]  # ind in color_list (not complete)

          color_sort_list = color_sort_list[keep_list]

          if ind_color_sort.size == 1:
            # @todo Yunzhi: The threshold needs to be decided by the feature method
            j = ind_shape_sort[ind_color_sort[0]]
          else:
            # Check color_sort_list, find the one with lowest edge score for now
            edge_color_list = scoreTable_edge_color[i][ind_shape_sort[ind_color_sort]]
            ind_edge_color = np.where(edge_color_list == np.amin(edge_color_list))

            j = ind_shape_sort[ind_color_sort[ind_edge_color[0]]][0]

          # # Check scoreTable_color, find the lowest for now
          # # The index of the lowest score in the scoreTable_color[i][ind_shape_sort]
          # j = scoreTable_color[i][ind_shape_sort].argmin()
          # # The final index based on scoreTable_shape and scoreTable_color
          # j = ind_shape_sort[j]

        if scoreTable_shape[i][j] < 1e16:
          scoreTable_shape[:, j] = 1e18
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
