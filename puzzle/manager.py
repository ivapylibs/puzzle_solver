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
# @file     manager.m
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/07/26
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#================================ manager ================================

#==== Imports
#
from trackpointer.centroidMulti import centroidMulti

#==== Helper 
#

# DEFINE ENUMERATED TYPE HERE FOR scoreType.
# SCORE_DIFFERENCE, SCORE_SIMILAR for SURE.
#
SCORE_DIFFERENCE = 0
SCORE_SIMILAR = 1
#
#================================ manager ================================
#
from dataclasses import dataclass

@dataclass
class managerParms:
  scoreType:int = SCORE_DIFFERENCE


class manager (centroidMulti):
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

  #=============================== manager ==============================
  #
  # @brief  Constructor for the puzzle piece manager class.
  #
  # @param[in]  solution    A solution/calibrated board instance.
  # @param[in]  theParms    Any additional parameters in a structure.
  #
  def __init__(self, solution, theParms = []):
    super(manager, self).__init__(WHAT)

    if not theParms:
      theParms = managerParms;

    self.solution = solution                # @< The solution puzzle board.
    self.scoreType = theParms.scoreType     # @< The type of comparator.
    self.bMeas   = puzzle.board             # @< The measured board.
    self.bAssign = []                       # @< Assignments: meas to sol.

  #============================== predict ==============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #============================== measure ==============================
  #
  # @brief  Process the passed imagery to recover puzzle pieces and
  #         manage their track states.
  #
  def measure(self, I):
    pass
    # WRITE THIS FUNCTION.
    # DIFFERENTIATE BETWEEN SIMILARITY VERSUS DIFFERENCES AND HAVE
    # BOOLEAN CHECK FOR THAT FLAG HERE TO HAVE ASSIGNMENT CONDITIONED ON
    # SIMILARITY VS DIFFERENCE (ONE MINIMIZES SCORE, ONE MAXIMIZES
    # SCORE), SO DIFFERENCE SHOULD BE IN DIRECTION OF SCORE COMPARISONS.
    #
    # PUT CODE HERE FOR PUZZLE PIECE MANAGEMENT AND TRACKING.
    # WHATEVER WORKS FOR OPENCV.

    # THIS PROCESSING IS USUALLY BROKEN INTO PHASES. THEY SHOULD HAVE
    # THEIR OWN MEMBER FUNCTIONS FOR OVERLOADING AS NEEDED.

    # 1] EXTRACT PIECES BASED ON DISCONNECTED COMPONENT REGIONS
    #
    #       BEST IF DONE AS A MEMBER FUNCTION. MIGHT BE OVERLOADED.
    #       OR IGNORE HIERARCHY FOR NOW. FIX LATER.
    #
    # 2] INSTANTIATE PUZZLE PIECE ELEMENTS FROM EXTRACTED DATA
    #
    #       OPTIONAL: TO DO AS MEMBER FUNCTION. I'D PROBABLY DO IT THAT
    #       WAY FOR RE-USABILITY PURPOSES.
    #
    # 3] COMPARE TO GROUND TRUTH (PAIRWISE TESTS)
    # 4] GENERATE ASSOCIATIONS
    #
    #       BOTH COMBINED AS PART OF A MEMBER FUNCTION
    #
    # 5] STORE AND CLOSE OUT (MAYBE NOT USED, OR JUST UNIQUE CODE IN
    #       EACH MEASURE MEMBER FUNCTION)
    #
    #       SHOULD GENERATE A PUZZLE.BOARD AS FINAL ANSWER.
    #
    # IF DONE RIGHT, THE SUPER CLASS CAN DO ABOUT 50% OF THE ABOVE AND
    # THIS CLASS HAS SOME SPECIALIZED PROCESSING FOR THE PUZZLE PIECES
    # FOR THE OTHER 50% (NOTE: THE PERCENT SPLIT COULD BE DIFFERENT).
    #
    # 2021/07/29: LOOKS LIKE THE SUPER CLASS SHOULD ONLY BE HELPING WITH
    # STEP 1. IT IS OK TO JUST CODE AS MEMBER FUNCTION HERE AND WORRY
    # ABOUT ALTERNATIVES LATER.
    #

  #============================== correct ==============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #=============================== adapt ===============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #=========================== process ==========================
  #
  # @brief  TO FILL OUT.
  #
  def process(self, y):
    pass
    # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  # WHAT ELSE SHOULD BE HERE IN THE INTERFACE?
  # BUILD OUT AS NEEDED FROM THE REMOVAL OF CODE FROM THE
  # DETECTOR_PUZZLE CLASS TO HERE.
  # MAKE SURE TO THINK ABOUT WHAT MIGHT BE GENERAL AND FIT IN THE SUPERCLASS.
  # ANYTHING SPECIALIZED IS BEST FOR THIS CLASS.

#
#================================ manager ================================
