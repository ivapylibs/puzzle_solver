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

#==== Imports
#
from dataclasses import dataclass
import itertools

from puzzle.parser.fromLayer import fromLayer

#==== Helper 
#

# DEFINE ENUMERATED TYPE HERE FOR scoreType.
SCORE_DIFFERENCE = 0
SCORE_SIMILAR = 1

@dataclass
class managerParms:
  scoreType: int = SCORE_SIMILAR

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
  def __init__(self, solution, theParms = []):
    super(manager, self).__init__()

    if not theParms:
      theParms = managerParms

    # @todo
    # Yunzhi: we have to simulate a gt here. It is designed to be done in builder?

    self.solution = solution              # @< The solution puzzle board.
    self.scoreType = theParms.scoreType   # @< The type of comparator.
    self.pAssignments = []                # @< Assignments: measurement of all the pairwise comparisons.
    self.bAssigned = []                   # @< Puzzle board of assigned pieces.

  #============================== predict ==============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #============================== measure ==============================
  #
  # @brief  Process the passed imagery to recover puzzle pieces and
  #         manage their track states.
  #
  def measure(self, I, M):

    # @todo
    # WRITE THIS FUNCTION.
    # DIFFERENTIATE BETWEEN SIMILARITY VERSUS DIFFERENCES AND HAVE
    # BOOLEAN CHECK FOR THAT FLAG HERE TO HAVE ASSIGNMENT CONDITIONED ON
    # SIMILARITY VS DIFFERENCE (ONE MINIMIZES SCORE, ONE MAXIMIZES
    # SCORE), SO DIFFERENCE SHOULD BE IN DIRECTION OF SCORE COMPARISONS.

    # PUT CODE HERE FOR PUZZLE PIECE MANAGEMENT AND TRACKING.
    # WHATEVER WORKS FOR OPENCV.
    #
    # THIS PROCESSING IS USUALLY BROKEN INTO PHASES. THEY SHOULD HAVE
    # THEIR OWN MEMBER FUNCTIONS FOR OVERLOADING AS NEEDED.

    # Call measure function from fromLayer to generate a measured board
    # self.bMeas
    super().measure(I,  M)

    # Compare with ground truth/generate associates
    self.matchPieces()

    # STORE AND CLOSE OUT -> SHOULD GENERATE A PUZZLE.BOARD AS FINAL ANSWER.
    iPieces = []
    for idx, assignment in enumerate(self.pAssignments):
      # @todo
      # criteria is related to similarity or difference
      if assignment >0:
        iPieces.append(idx)

    # @todo
    # getSubset has not implemented yet in the board class
    self.bAssigned = self.bMeas.getSubset(iPieces)

    pass

  #=========================== matchPieces ==========================
  #
  # @brief  Match all the puzzle pieces with the ground truth in a pairwise manner.
  #
  def matchPieces(self):
    # @todo

    pair_list = [[x,y] for x in self.bMeas.pieces for y in self.solution.pieces]
    for pair in pair_list:
      pass


  #============================== correct ==============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #=============================== adapt ===============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #=========================== process ==========================
  #
  # @brief  Run the tracking pipeline for image measurement.
  #
  # @param[in]  I   Source image.
  # @param[in]  M   Layer mask (binary)
  #
  def process(self, I, M):

    self.measure(I, M)

    pass
#
#================================ manager ================================
