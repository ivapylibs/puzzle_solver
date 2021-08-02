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
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/28 [created]
#           2021/08/01 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#============================== puzzle.board =============================


#============================== Dependencies =============================

# Imports go here. Aim for the bare minimum. 

# Make sure to include in dependencies for this package.
# Delete this comment when done.

import numpy as np
import matplotlib.pyplot as plt
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
  def __init__(self, thePieces = []):

    self.pieces = thePieces     # @< The puzzle pieces.

  #=========================== addPiece ==========================
  #
  # @brief      Add puzzle piece instance to the board
  #
  # @param[in]  piece a puzzle piece instance
  #
  def addPiece(self, piece):

    self.pieces.append(piece)

  #=============================== clear ===============================
  #
  # @brief  Clear the puzzle pieces from the board.
  #
  def clear(self):

    self.pieces = []

  #================================ size ===============================
  #
  # @brief  Return the number of pieces on the board.
  #
  # @param[out] nPieces     The number of pieces on the board.
  #
  def size(self):

    nPieces = len(self.pieces)

    return nPieces

  #============================== extents ==============================
  #
  # @brief  Iterate through the puzzle pieces to figure out the tight
  #         bounding box extents of the board.
  #
  # @param[out] lengths     The bounding box side lengths.
  #
  def extents(self):

    # [[min x, min y], [max x, max y]]
    bbox = self.boundingBox()
    lengths = bbox[1]-bbox[0]

    return lengths

  #============================ boundingBox ============================
  #
  # @brief  Iterate through the puzzle pieces to figure out the tight
  #         bounding box of the board.
  #
  # @param[out] bbox        The bounding box coordinates.
  #
  def boundingBox(self):

    if self.size() == 0:
      # @todo
      # Yunzhi: Not sure what to do here
      print('No pieces exist')
      exit()
    else:
      # process to get min x, min y, max x, and max y
      bbox = np.array([[float('inf'), float('inf')], [0, 0]])

      # piece is a puzzleTemplate instance, see template.py for details.
      for piece in self.pieces:
        # top left coordinate
        tl = piece.rLoc
        # bottom right coordinate
        br = piece.rLoc + piece.size()

        bbox[0] = np.min([bbox[0], tl], axis=0)
        bbox[1] = np.max([bbox[1], br], axis=0)

      return bbox


  #=========================== pieceLocations ==========================
  #
  # @brief      Returns list/array of puzzle piece locations.
  #
  # @param[out] pLocs list/array of puzzle piece locations.
  #
  def pieceLocations(self):

    pLocs = []
    for piece in self.pieces:
      pLocs.append(piece.rLoc)

    # from N x 2 to 2 x N
    pLocs = np.array(pLocs).reshape(2,-1)

    return pLocs

  #============================== toImage ==============================
  #
  # @brief  Uses puzzle piece locations to create an image for
  #         visualizing them.  If given an image, then will place in it.
  #
  # @param[in]  theImage    The image to insert pieces into. (optional)
  #
  # @param[out] theImage    The image to insert pieces into.
  #
  def toImage(self, theImage = None):

    if theImage is not None:
      # Check dimensions ok and act accordingly, should be equal or bigger, not less.
      lengths = self.extents().astype('int')
      bbox = self.boundingBox().astype('int')
      if (theImage.shape[:2]-lengths>0).all():
        for piece in self.pieces:
          piece.placeInImage(theImage, offset=-bbox[0])
      else:
        # @todo
        #  Figure out what to do if image too small. Expand it or abort?
        #  Yunzhi: Currently abort.
        print('The image is too small. Please try again.')
        exit()
    else:
      # Create image with proper dimensions.
      lengths = self.extents().astype('int')
      bbox = self.boundingBox().astype('int')
      theImage = np.zeros((lengths[0],lengths[1],3),dtype='uint8')
      for piece in self.pieces:

        piece.placeInImage(theImage, offset=-bbox[0])

    return theImage

  #============================== display ==============================
  #
  # @brief  Display the puzzle board as an image.
  #
  # @param[in]  fh  The figure label/handle if available (optional).
  #
  # @param[out] fh  The handle of the image.
  #
  def display(self, fh = None):

    # @note
    #
    # Generating new image each time is time inefficient.
    #
    # MOST LIKELY WANT TO STORE FIGURE AND IMAGE IF GENERATED, THEN TEST
    # IF AVAILABLE. THIS INTRODUCTES PROBLEMS THOUGH SINCE KEEP TRACK OF
    # DIRTY STATUS REQUIRES KNOWLEDGE ABOUT PUZZLE PIECES AND SOME FORM
    # OF COMMUNICATION OR COORDINATION. NOT WORTH THE EFFORT RIGHT NOW.
    #

    theImage = self.toImage()

    if fh:
      # See https://stackoverflow.com/a/7987462/5269146
      fh = plt.figure(fh.number)
      # See https://stackoverflow.com/questions/13384653/imshow-extent-and-aspect
    else:
      fh = plt.figure()
    # @note
    # Yunzhi: extent is used to change the axis tick, we should use figsize
    # See https://stackoverflow.com/a/66315574/5269146
    # plt.imshow(theImage, extent=[0, 1, 0, 1])
    plt.imshow(theImage)
    # plt.show()

    return fh


#
#============================== puzzle.board =============================
