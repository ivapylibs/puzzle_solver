#======================== puzzle.parser.fromLayer ========================
#
# @class    puzzle.parser.fromLayer
#
# @brief    A basic detector class that processes a layered image
#           (or mask and image) detection output. Converts all isolated
#           regions into their own puzzle piece instances.
#
#======================== puzzle.parser.fromLayer ========================

#
# @file     fromLayer.m
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/07/29
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#======================== puzzle.parser.fromLayer ========================

#==== Imports
#
from trackpointer.centroidMulti import centroidMulti

#==== Helper 
#

#
#======================== puzzle.parser.fromLayer ========================
#

class fromLayer(centroidMulti):

  #============================= fromLayer =============================
  #
  # @brief  Constructor for the puzzle piece layer parsing class.
  #
  def __init__(self):
    super(fromLayer, self).__init__()

    # @ todo
    # Need double check
    # self.bMeas   = puzzle.board             # @< The measured board.

  #============================== measure ==============================
  #
  # @brief  Process the passed imagery to recover puzzle pieces and
  #         manage their track states.
  #
  # @param[in]  I   Source image.
  # @param[in]  M   Layer mask (binary)
  #
  def measure(self, I, M):

    # 1] Extract pieces based on disconnected component regions
    #
    regions = self.mask2regions(I, M)
    
    # 2] Instantiate puzzle piece elements from extracted data
    #
    pieces = self.regions2pieces(regions)

    # 3] Package into a board.
    #
    self.bMeas.clear()
    self.bMeas.pieces = pieces


  #=========================== mask2regions ============================
  #
  # @brief      Convert the selection mask into a bunch of regions.
  #
  # @param[in]  I   Source image.
  # @param[in]  M   Layer mask (binary).
  #
  def mask2regions(self, I, M):

    # Find all connected components.
    # Get image coordinates, centroid, bounding box, top left corner,
    # etc. as needed.

    # Using region data to extract the image color information.
    # return regions
    pass

  #========================== regions2pieces ===========================
  #
  # @brief  Convert the region information into puzzle pieces.
  #
  def regions2pieces(self, regions):

    # # Use all of these elements to instantiate a puzzle piece.
    # for loop over found items (is it by index or as list?)
    #   repackage found region data into puzzle piece.
    #
    # return pieces

    pass

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
#======================== puzzle.parser.fromLayer ========================
