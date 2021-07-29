#========================= puzzle.piece.template =========================
#
# @brief    The base class for puzzle piece specification or description
#           encapsulation. This simply stores the template image and
#           related data for a puzzle piece in its canonical
#           orientation.
#
#========================= puzzle.piece.template =========================

#
# @file     template.m
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/07/24
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================= puzzle.piece.template =========================

#============================= Dependencies ==============================

import numpy as np
from dataclasses import dataclass

import matplotlib.pyplot as mplot

#=========================== Helper Components ===========================

@dataclass
class puzzleTemplate:
  size:    np.ndarray   # @< tight bbox size of puzzle piece image.
  icoords: list[int]    # @< Linear index coordinates.
  rcoords: np.ndarray   # @< Puzzle piece linear image coordinates.
  appear:  np.ndarray   # @< Puzzle piece linear color/appearance. 
  image:   np.ndarray   # @< Template image with BG default fill.

#
#========================= puzzle.piece.template =========================
#

class template:

  #================================ base ===============================
  #
  # @brief  Constructor for the puzzle.piece.base class.
  #
  def __init__(self, y = None, r = (0, 0)):
    self.y = y          # @< The puzzle piece template source data, if given.
    self.rLoc = np.array(r)       # @< The puzzle piece location in pixels.

    # self.pLoc = p       # @< The puzzle piece discrete grid piece coordinates.
    # @note     Opting not to use discrete grid puzzle piece description.
    # @note     Excluding orientation for now. Can add later. Or sub-class it.

  #================================ size ===============================
  #
  # @brief  Returns the dimensionds of the puzzle piece.
  #
  def size(self):
    return self.y.size

  #============================== setSource ============================
  #
  # @brief  Pass along the source data describing the puzzle piece.
  #
  def setSource(self, y, r = []):
    self.y = y

    if r:
      self.r = r

  #============================ setPlacement ===========================
  #
  # @brief  Provide pixel placement location information.
  #
  # @param[in]  r           Location of its frame origin. 
  # @param[in]  isCenter    Boolean indicating r is center instead.
  #
  def setPlacement(self, r, isCenter = False):
    if isCenter:
      self.r = r - np.ceil(self.y.size/2)
    else:
      self.r = r

  #============================ placeInImage ===========================
  #
  # @brief  Insert the puzzle piece into the image at the given location.
  #         
  # @param[in]  theImage    The source image to put puzzle piece into.
  # @param[in]  rc          The coordinate location
  # @param[in]  theta       The orientation of the puzzle piece (default = 0)
  #
  def placeInImageAt(self, theImage):

    # Remap coordinates from own image sprite coordinates to bigger
    # image coordinates.
    rcoords = self.y.rLoc + self.y.rcoords
      
    # Dump color/appearance information into the image.
    theImage[rcoords[1,:], rcoords[2,:], :] = self.y.appear

    # FOR NOW JUST PROGRAM WITHOUT ORIENTATION CHANGE. LATER, INCLUDE THAT
    # OPTION.  IT WILL BE A LITTLE MORE INVOLVED. WOULD REQUIRE HAVING A
    # ROTATED IMAGE TEMPLATE AS A MEMBER VARIABLE.

    pass    # REPLACE WITH ACTUAL CODE.

  #============================ placeInImageAt ===========================
  #
  # @brief  Insert the puzzle piece into the image at the given location.
  #         
  # @param[in]  theImage    The source image to put puzzle piece into.
  # @param[in]  rc          The coordinate location
  # @param[in]  theta       The orientation of the puzzle piece (default = 0)
  #
  def placeInImageAt(self, theImage, rc, theta = 0, isCenter = False):

    if not theta:
      theta = 0

    # @ todo
    # need check
    # # If specification is at center, then compute offset to top-left corner.
    # if isCenter:
    #   rc = rc - half dimensions of puzzle piece

    # Remap coordinates from own image sprite coordinates to bigger
    # image coordinates.
    rcoords = rc + self.y.rcoords
      
    # Dump color/appearance information into the image.
    theImage[rcoords[1,:], rcoords[2,:], :] = self.y.appear

    # FOR NOW JUST PROGRAM WITHOUT ORIENTATION CHANGE. LATER, INCLUDE THAT
    # OPTION.  IT WILL BE A LITTLE MORE INVOLVED.

    pass    # REPLACE WITH ACTUAL CODE.

  #============================== display ==============================
  #
  # @brief  Display the puzzle piece contents in an image window.
  #
  # @param[in]  fh  The figure label/handle if available (optional).
  #
  def display(self, fh = []):

    fh = mplot.figure(fh)
    mplot.imshow(self.y.image, extent = [0, 1, 0, 1])

    # figure acts like Matlab's figure.
    # imshow with extents acts like imagesc, so image will scale with
    # window size. Correct code if wrong interpretation.

    # From googling, the above code seems to do what is described.
    # If works, delete the notes and this comment. If not, correct based
    # on notes below.

    # Need to figure this out.  Should a figure label/handler be given?
    # If not given, then create a new handle, display data and
    # return the handle?
    # Sounds reasonable.
    # What about some kind of display plot scaling parameter?
    
    # Should the template class have an optional parms structure that
    # indicates how much to scale, with default value of 2 or 3x
    # upscaling?  How does matplotlibs plot things? Can the plot be
    # opened in such a way that it is not native resolution?
    # I think so. We want outcome like in Matlab where small things are
    # still plotted reasonably large for easy visualization.



  #======================= buildFromMaskAndImage =======================
  #
  # @brief  Given a mask and an image of same base dimensions, use to
  #         instantiate a puzzle piece template.
  #
  @staticmethod
  def buildFromMaskAndImage(theMask, theImage, rLoc = []):

    # @ todo
    # need check
    # y = puzzleTemplate()
    #
    # # Populate dimensions.
    # y.size  = np.size(theMask)
    #
    # # Populate coordinate/indexing information.
    # y.icoords = find(theMasK)
    # y.rcoords = ind2sub(y.icoords, y.size)
    #
    # # Populate appearance
    # linImage = reshape(theImage, [prod(imsize), np.size(theImage,2)])
    # y.appear   = linImage[y.icoords,:]
    #
    # # Store template image.
    # # @note     For now, not concerned about bad image data outside of mask.
    # y.image = theImage
    #
    # if not rLoc:
    #   thePiece = template(y)
    # else:
    #   thePiece = template(y, rLoc)

    pass

#
#========================= puzzle.piece.template =========================
