#======================== puzzle.builder.fromMask ========================
#
# @brief    Create digital puzzles from a puzzle partition mask and a
#           source image with a similar aspect ratio.
#
# The mask is white or "true" where the puzzle piece regions are and is
# black or "false" where the boundaries are. For an image and mask pair
# that are not the same aspect ratio, the image or the mask, or both can
# be warped to fit. If the image is bigger, then it can be cropped to
# fit. 
#
# In addition, the puzzle pieces are automatically extracted and stored
# into a puzzle piece template class instance.
#
#======================== puzzle.builder.fromMask ========================

#
# @file     fromMask.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/07/25  [started]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#======================== puzzle.builder.fromMask ========================

# Imports go here. Aim for the bare minimum. 

# Make sure to include in dependencies for this package.
# Delete this comment when done.


#
#======================== puzzle.builder.fromMask ========================
#

class fromMask:


  #============================== fromMask =============================
  #
  # @brief  Constructor for mask-based puzzle builder. Can pass contents
  #         at instantiation time or delay until later.
  #
  # @param[in]  theMask     The puzzle template mask. (optional)
  # @param[in]  theImage    The puzzle image source. (optional)
  #
  def __init__(self, theMask = [], theImage = []):

    self.pieces = []        # @< The puzzle pieces.
    pass

    # Remainder of this constructor needs to be coded up.
    # Is processing automatic or triggered by calling scope?
    # If automatic, then need proper logic in member functions.

  #============================== setMask ==============================
  #
  # @brief  Provide the mask to use.
  #
  # @param[in]  theMask     The puzzle template mask. (optional)
  #
  def setMask(self, theMask):

    self.mask = theMask
    # Should more be done?
    # Is processing automatic or triggered by calling scope?

  #============================== setImage =============================
  #
  # @param[in]  theImage    The puzzle image source. (optional)
  #
  def setImage(self, theImage):

    self.image = theImage
    # Should more be done?
    # Is processing automatic or triggered by calling scope?

  #========================== setMaskAndImage ==========================
  #
  # @brief  Specify the mask and the image to use.
  #
  # @param[in]  theMask     The puzzle template mask.
  # @param[in]  theImage    The puzzle image source. 
  # @param[in]  doParse     perform follow-up parsing? (optional boolean)
  #
  def setMaskAndImage(self, theMask, theImage, doParse = False):

    self.mask = theMask
    self.image = theImage

    if doParse:
      self.process()
      # Should more be done?
      # Is processing automatic or triggered by calling scope?
      # If automatic, then not need for flag. Remove it.

  #============================== process ==============================
  #
  # @brief  Parse the mask and apply to source image.
  #
  # When parsing is done, the pieces member variable is populated with
  # the puzzle piece information.
  #
  def process(self):
    pass
  #=========================== explodedPuzzle ==========================
  #
  # @brief  Create an exploded version of the puzzle. It is an image
  #         with no touching pieces.
  #
  # The value for an exploded puzzle image is that it can be used to
  # generate a simulated puzzle scenario that can be passed to a puzzle
  # solver. It can also be used to define a quasi-puzzle problem, where
  # the objective is to place the pieces in grid ordering like the
  # exploded view (without needing to interlock). Doing see keeps puzzle
  # piece well separated for simple puzzle interpretation algorithms to
  # rapidly parse.
  #
  # @param[in]  bgColor     The background color to use.
  # @param[in]  dx          The horizontal offset when exploding.
  # @param[in]  dy          The vertical offset when exploding.
  #
  # @param[out] epImage     Exploded puzzle image.
  #
  def explodedPuzzle(self, bgColor):

    # @todo
    # Will implement it later
    pass

    # #--[1] First figure out how big the exploded image should be based
    # #      on the puzzle image dimensions, the number of puzzle pieces
    # #      across rows and columns, and the chosen spacing.
    # [nr, nc] = image size.
    #
    # dr = 0 # ADDITIONAL ROWS TO ADD. ACCUMULATE.
    # dc = 0 # ADDITIONAL COLUMNS TO ADD. ACCUMULATE.
    #
    # nr = nr + dr
    # nc = nc + dc
    #
    # epImage = image of size nr x nc with bgColor.
    #
    # #--[2] Place image data into the exploded puzzle image.
    # #
    # for loop over pieces
    #   x = self.piece[ii].r
    #   p = self.piece[i]].p
    #
    #   dr = x + [dx, dy] .* p
    #
    #   self.piece[ii].placeInImage(epImage, x)
    #
    #   # ABOVE IS JUST PSEUDOCODE. NEEDS CORRECTION.

#
#======================== puzzle.builder.fromMask ========================
