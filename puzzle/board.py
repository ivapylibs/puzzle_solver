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

    # BASICALLY, CALL boundingBox, GET THE BBOX
    # COMPUTE DIFFERENCES TO CONVERT INTO SIDE LENGTHS.
    # RETURN LENGTHS
    pass 


  #============================ boundingBox ============================
  #
  # @brief  Iterate through the puzzle pieces to figure out the tight
  #         bounding box of the board.
  #
  # @param[out] bbox        The bounding box coordinates.
  #
  def boundingBox(self):

    # @todo
    # bbox = np.full((2,2), (0, 0))
    #
    # for piece in self.pieces:
    #   piece
    #   # PROCESS TO GET MIN X, MIN Y, MAX X, and MAX X
    #
    # return bbox

    pass

  #=========================== pieceLocations ==========================
  #
  # @brief      Returns list/array of puzzle piece locations.
  #
  # @param[out] pLocs
  def pieceLocations(self):

    # @ todo
    # pLocs = numpy array of size 2 x #pieces (rows x cols)
    #
    # for ii = 1 : length(self.pieces)
    #   pLocs(:, piece_num) = self.pieces(ii).getLocation()
    #
    pass
  #============================== toImage ==============================
  #
  # @brief  Uses puzzle piece locations to create an image for
  #         visualizing them.  If given an image, then will place in it.
  #
  # @todo   Figure out what to do if image too small. Expand it or abort?
  #
  # @param[in]  theImage    The image to insert pieces into.
  #
  def toImage(self, theImage):

    # @todo
    # COMPUTE EXTENTS OF BOARD OR USE BOUNDING BOX.
    # MIGHT ALSO NEED OFFSET SO THAT TOP-LEFT EXTENT STARTS AT (0,0).

    # if not theImage:
    #   CREATE IMAGE WITH PROPER DIMENSIONS.
    # else:
    #   CHECK DIMENSIONS OK AND ACT ACCORDINGLY.
    #   SHOULD BE EQUAL OR BIGGER, NOT LESS.

    pass

  #============================== display ==============================
  #
  # @brief  Display the puzzle board as an image.
  #
  # Display in an image the puzzle board.  
  #
  def display(self, fh = []):

    theImage = self.toImage()

    plt.figure(fh)
    plt.imshow(theImage, extent=[0,1,0,1])

    # @todo     Generating new image each time is time inefficient.
    #       
    # MOST LIKELY WANT TO STORE FIGURE AND IMAGE IF GENERATED, THEN TEST
    # IF AVAILABLE. THIS INTRODUCTES PROBLEMS THOUGH SINCE KEEP TRACK OF
    # DIRTY STATUS REQUIRES KNOWLEDGE ABOUT PUZZLE PIECES AND SOME FORM
    # OF COMMUNICATION OR COORDINATION. NOT WORTH THE EFFORT RIGHT NOW.
    #

#
#============================== puzzle.board =============================
