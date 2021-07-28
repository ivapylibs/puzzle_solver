#============================== puzzle.board =============================
#
# @brief    A base representation for a puzzle board, which is basically
#           a collection of pieces.  Gets used in many different ways.
#
# A puzzle board consists of a collection of puzzle pieces and their
# locations. There is no assumption on where the pieces are located. 
# A board just keeps track of a candidate jigsaw puzzle state, or
# possibly the state of a subset of a given jigsaw puzzle.  Think of it
# as a bag class for puzzle pieces, just that they also have locality.
#
#============================== puzzle.board =============================

#
# @file     board.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/07/28  [started]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#============================== puzzle.board =============================


#============================== Dependencies =============================
%
# Imports go here. Aim for the bare minimum. 

# Make sure to include in dependencies for this package.
# Delete this comment when done.


#
#============================== puzzle.board =============================
#

class board:


  #================================ board ==============================
  #
  # @brief  Constructor for puzzle board. Can pass contents at
  #         instantiation time or delay until later.
  #
  # @param[in]  thePieces   The puzzle pieces. (optional)
  #
  def __init__(self, thePieces = []) 

    self.pieces = thePieces     # @< The puzzle pieces.

  #============================== extents ==============================
  #
  # @brief  Iterate through the puzzle pieces to figure out the tight
  #         bounding box extents of the board.
  #
  # @param[out] lengths     The bounding box side lengths.
  #
  def lengths = extents(self)
    lengths = np.array([0,0])

    return lengths

  #============================ boundingBox ============================
  #
  # @brief  Iterate through the puzzle pieces to figure out the tight
  #         bounding box of the board.
  #
  # @param[out] bbox        The bounding box coordinates.
  #
  def boundingBox(self)
    bbox = np.full((2,2), (0, 0));
    return bbox

  #============================== toImage ==============================
  #
  # @brief  Uses puzzle piece locations to create an image for
  #         visualizing them.  If given an image, then will place in it.
  #
  # @todo   Figure out what to do if image too small. Expand it or abort?
  #
  # @param[in]  theImage    The image to insert pieces into.
  #
  def toImage(self, theImage)

    COMPUTE EXTENTS OF BOARD OR USE BOUNDING BOX.
    MIGHT ALSO NEED OFFSET.

    if not theImage:
      CREATE IMAGE WITH PROPER DIMENSIONS.
    else:
      CHECK DIMENSIONS OK AND ACT ACCORDINGLY.

    for piece in self.pieces
      POPULATE IMAGE WITH PUZZLE PIECE VISUAL.


  #============================== display ==============================
  #
  # @brief  Display the puzzle board as an image.
  #
  # Display in an image the puzzle board.  
  #
  def display(self, fh = []):

    theImage = self.toImage()

    mplot.figure(fh)
    mplot.imshow(theImage, extent=[0,1,0,1])

#
#============================== puzzle.board =============================
