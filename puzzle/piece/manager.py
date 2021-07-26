#================================ manager ================================
#
# @brief    Manage the tracking of puzzle pieces. 
#
#
# This puzzle piece manager keeps track of the puzzle pieces and their
# association over time as new imagery of the scene is captured. This
# manager stores the puzzle piece instances and organizes the code for
# data association. Even though the individual puzzle piece instances
# has some form of recognition, this one can override that using other
# considerations such as multi-piece competition or changes in the image
# and what regions are tagged to those changes.
#
# As an example, this manager can get all similarity (or difference)
# scores are use them for generating assignments instead of greedily
# creating assignments for each puzzle piece independently of the other
# pieces.
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
from BASE.CLASS.PACKAGE import OPTIONAL.PROBABLY.DONT.DO

#==== Helper 
#

# DEFINE ENUMERATED TYPE HERE FOR scoreType.
# SCORE_DIFFERENCE, SCORE_SIMILAR for SURE.
#

#
#================================ manager ================================
#


class manager (SUPERCLASS???):
# SHOULD MOST LIKELY BE SOME FORM OF TRACKPOINTER. INTERFACE SHOULD
# MATCH. WHAT SHOULD THE SUPERCLASS BE? IT MIGHT BE THAT CREATING A NEW
# TRACKPOINTER CLASS WITH SOME LIMITED FUNCTIONALITY IS IN ORDER.
# LIKE ONE CALLED multiRegions or regionsMulti or something like that.
# IT TAKES IN AN IMAGE (POSSIBLY ALREADY BINARIZED) AND RECOVERS THE
# DISTINCT REGIONS ASSOCIATED TO IT.

  #=============================== manager ==============================
  #
  # @brief  Constructor for the puzzle piece matchSimilar class.
  #
  # @todo Decide later if initialization/calibration data can be passed
  # at instantiation.
  #
  def __init__(self, WHAT):
    super(SUPERCLASS, self).__init__(WHAT)

    self.scoreType = SCORE_DIFFERENCE

  #============================== predict ==============================
  #
  # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

  #============================== measure ==============================
  #
  # @brief  Process the passed imagery to recover puzzle pieces and
  #         manage their track states.
  #
  def measure(self, I)
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
    # 2] INSTANTIATE PUZZLE PIECE ELEMENTS FROM EXTRACTED DATA
    # 3] COMPARE TO GROUND TRUTH (PAIRWISE TESTS)
    # 4] GENERATE ASSOCIATIONS
    # 5] STORE AND CLOSE OUT (MAYBE NOT USED, OR JUST UNIQUE CODE IN
    #       EACH MEASURE MEMBER FUNCTION)
    #
    # IF DONE RIGHT, THE SUPER CLASS CAN DO ABOUT 50% OF THE ABOVE AND
    # THIS CLASS HAS SOME SPECIALIZED PROCESSING FOR THE PUZZLE PIECES
    # FOR THE OTHER 50% (NOTE: THE PERCENT SPLIT COULD BE DIFFERENT).
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
