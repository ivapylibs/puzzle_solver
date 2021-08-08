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
import cv2
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
  def __init__(self, thePieces = [], id_count = 0):

    self.pieces = thePieces     # @< The puzzle pieces.
    self.id_count = id_count
  #=========================== addPiece ==========================
  #
  # @brief      Add puzzle piece instance to the board
  #
  # @param[in]  piece   A puzzle piece instance
  #
  def addPiece(self, piece):

    piece.id = self.id_count
    self.id_count +=1
    self.pieces.append(piece)

  #=============================== clear ===============================
  #
  # @brief  Clear the puzzle pieces from the board.
  #
  def clear(self):

    self.pieces = []
    self.id_count = 0

  #=============================== getSubset ===============================
  #
  # @brief  Return a new board consisting of a subset of pieces.
  #
  # @param[in]  subset   A list of indexes for the subset.
  #
  def getSubset(self, subset):

    bSubset = board(np.array(self.pieces)[subset], len(subset))

    return bSubset

  # =============================== getAssigned ===============================
  #
  # @brief  Return a new board consisting of a subset of pieces.
  #
  # @param[in]  pAssignments   A list of assignments for the subset.
  #
  # @param[out] theBoard   A new board with assignment.
  #
  def getAssigned(self, pAssignments):

    for assignment in pAssignments:
      # assignment[1] is for the solution board, where the instance shares the same id as the index
      self.pieces[assignment[0]].id_sol = assignment[1]
    theBoard = board(np.array(self.pieces)[np.array(pAssignments)[:, 0]], self.id_count)

    return theBoard

  # =============================== testAdjacent ===============================
  #
  # @brief  Check if two puzzle pieces are adjacent or not
  #
  # @param[in]  index_A   The index of the puzzle piece A.
  # @param[in]  index_B   The index of the puzzle piece B.
  # @param[in]  tauAdj    The threshold of the distance.
  #
  # @param[out] theFlag   The flag signalling whether two puzzle pieces are adjacent or not.
  #
  def testAdjacent(self, index_A, index_B, tauAdj):

    # @todo
    # Need a better check based on shape instead of simple distance
    theFlag = np.linalg.norm(np.array(self.pieces[index_A].rLoc)-np.array(self.pieces[index_B].rLoc))<tauAdj

    return theFlag

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
  # @param[out] pLocs   A dict of puzzle piece id & location.
  #
  def pieceLocations(self):

    # @note
    # Previously, return a list/array of puzzle piece locations.
    # pLocs = []
    # for piece in self.pieces:
    #   pLocs.append(piece.rLoc)
    #
    # # from N x 2 to 2 x N
    # pLocs = np.array(pLocs).reshape(-1,2).T

    pLocs = {}
    for piece in self.pieces:
      pLocs[piece.id] = piece.rLoc


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
  def toImage(self, theImage = None, ID_DISPLAY = False, ID_SOLUTION = False):

    if theImage is not None:
      # Check dimensions ok and act accordingly, should be equal or bigger, not less.
      lengths = self.extents().astype('int')
      bbox = self.boundingBox().astype('int')
      if (theImage.shape[:2]-lengths>0).all():
        for piece in self.pieces:
          if ID_DISPLAY == True:
            piece.placeInImage(theImage, offset=-bbox[0])
            pos = (int(piece.rLoc[0] - bbox[0][0] + piece.size()[0] / 2),
                   int(piece.rLoc[1] - bbox[0][1] + piece.size()[1] / 2))
            if ID_SOLUTION == True:
              cv2.putText(theImage, str(piece.id_sol), pos, cv2.FONT_HERSHEY_SIMPLEX,
                          1, (255, 255, 255), 2, cv2.LINE_AA)
            else:
              cv2.putText(theImage, str(piece.id), pos, cv2.FONT_HERSHEY_SIMPLEX,
                          1, (255, 255, 255), 2, cv2.LINE_AA)
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
      theImage = np.zeros((lengths[1],lengths[0],3),dtype='uint8')
      for piece in self.pieces:
        piece.placeInImage(theImage, offset=-bbox[0])
        if ID_DISPLAY == True:
          pos = (int(piece.rLoc[0] - bbox[0][0] + piece.size()[0]/2),
                 int(piece.rLoc[1] - bbox[0][1] + piece.size()[1]/2))
          if ID_SOLUTION == True:
            cv2.putText(theImage, str(piece.id_sol), pos, cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 255), 2, cv2.LINE_AA)
          else:
            cv2.putText(theImage, str(piece.id), pos, cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 255), 2, cv2.LINE_AA)

    return theImage

  #============================== display ==============================
  #
  # @brief  Display the puzzle board as an image.
  #
  # @param[in]  fh  The figure label/handle if available (optional).
  #
  # @param[out] fh  The handle of the image.
  #
  def display(self, fh = None, ID_DISPLAY = False):

    # @note
    #
    # Generating new image each time is time inefficient.
    #
    # MOST LIKELY WANT TO STORE FIGURE AND IMAGE IF GENERATED, THEN TEST
    # IF AVAILABLE. THIS INTRODUCTES PROBLEMS THOUGH SINCE KEEP TRACK OF
    # DIRTY STATUS REQUIRES KNOWLEDGE ABOUT PUZZLE PIECES AND SOME FORM
    # OF COMMUNICATION OR COORDINATION. NOT WORTH THE EFFORT RIGHT NOW.
    #


    if fh:
      # See https://stackoverflow.com/a/7987462/5269146
      fh = plt.figure(fh.number)
    else:
      fh = plt.figure()

    theImage = self.toImage(ID_DISPLAY=ID_DISPLAY )

    # @note
    # Yunzhi: extent is used to change the axis tick, we should use figsize
    # See https://stackoverflow.com/a/66315574/5269146
    # plt.imshow(theImage, extent=[0, 1, 0, 1])
    plt.imshow(theImage)
    # plt.show()

    return fh


#
#============================== puzzle.board =============================
