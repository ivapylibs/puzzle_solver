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
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/25 [created]
#           2021/08/01 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#======================== puzzle.builder.fromMask ========================

# Imports go here. Aim for the bare minimum. 

# Make sure to include in dependencies for this package.
# Delete this comment when done.

from puzzle.board import board

#
#======================== puzzle.builder.fromMask ========================
#

class fromMask(board):

  #============================== fromMask =============================
  #
  # @brief  Constructor for mask-based puzzle builder. Can pass contents
  #         at instantiation time or delay until later.
  #
  # @param[in]  theMask     The puzzle template mask. (optional)
  # @param[in]  theImage    The puzzle image source. (optional)
  #
  def __init__(self, theMask = [], theImage = []):

    super(fromMask, self).__init__()

    if theMask and theImage:
      self.setMaskAndImage(theMask, theImage)
    elif theImage:
      self.setMask(theMask)
    elif theMask:
      self.setImage(theImage)

      # @note
      # HAVE PROCESS CALLED HERE EXPLICITLY, OR EXPECT TO BE
      # AUTOMATICALLY DONE IN setMaskAndImage FUNCTION?
      # Is processing automatic or triggered by calling scope?
      # If triggered externally, this would be the calling scope, so add.
      #   Or use third binary argument indicating a process call.
      # If automatic, then need proper logic in member functions.

  #============================== setMask ==============================
  #
  # @brief  Provide the mask to use.
  #
  # @param[in]  theMask     The puzzle template mask. (optional)
  #
  def setMask(self, theMask):

    self.mask = theMask

    # @note
    # Should more be done?
    # Is processing automatic or triggered by calling scope?

  #============================== setImage =============================
  #
  # @param[in]  theImage    The puzzle image source. (optional)
  #
  def setImage(self, theImage):

    self.image = theImage
    # @note
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

      # @note
      # Should more be done?
      # Is processing automatic or triggered by calling scope?
      # If automatic, then no need for flag. Remove it.

  #============================== process ==============================
  #
  # @brief  Parse the mask and apply to source image.
  #
  # When parsing is done, the pieces member variable is populated with
  # the puzzle piece information.
  #
  def process(self):

    # @todo
    # Parse the mask to get the connection components. Hopefully they are
    # returned in some sensible ordering that can be discerned.

    # Best is to make a new class called puzzle.parser since it can
    # probably be recycled here and elsewhere. It should be a perceiver
    # instance. Figure out best way to handle it.

    # Once the mask has been parsed, extract information from the color
    # image to instantiate the puzzle piece template elements the define
    # the entire puzzle.

    # @todo
    # Yunzhi: call puzzle.parser.fromLayer to instantiate the puzzle piece template

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
    # Yunzhi: Will implement it later

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

    pass
#
#======================== puzzle.builder.fromMask ========================
