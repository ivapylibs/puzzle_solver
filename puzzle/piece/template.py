#========================= puzzle.piece.template =========================
#
# @brief    The base class for puzzle piece specification or description
#           encapsulation. This simply stores the template image and
#           related data for a puzzle piece in its canonical
#           orientation.
#
#========================= puzzle.piece.template =========================

#
# @file     template.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/24 [created]
#           2021/07/28 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================= puzzle.piece.template =========================

#============================= Dependencies ==============================

import numpy as np
from dataclasses import dataclass
import cv2

import matplotlib.pyplot as plt

#=========================== Helper Components ===========================

@dataclass
class puzzleTemplate:
  size:    np.ndarray = np.array([])   # @< tight bbox size of puzzle piece image.
  rcoords: np.ndarray = np.array([])  # @< Puzzle piece linear image coordinates.
  appear:  np.ndarray = np.array([])  # @< Puzzle piece linear color/appearance.
  image:   np.ndarray = np.array([],dtype='uint8')  # @< Template image with BG default fill.
  mask:     np.ndarray = np.array([],dtype='uint8') # @< Template mask.
  contour:  np.ndarray = np.array([],dtype='uint8') # @< Template contour.
#
#========================= puzzle.piece.template =========================
#

class template:

  #================================ base ===============================
  #
  # @brief  Constructor for the puzzle.piece.base class.
  #
  def __init__(self, y = None, r = (0, 0)):
    self.y = y          # @< The puzzle piece template source data, if given. It is a class instance, see puzzleTemplate
    self.rLoc = np.array(r)       # @< The puzzle piece location in the whole image.

    self.id = None  # @< The puzzle piece id in the measured board. Be set up by the board.

    # self.pLoc = p       # @< The puzzle piece discrete grid piece coordinates.
    # @note     Opting not to use discrete grid puzzle piece description.
    # @note     Excluding orientation for now. Can add later. Or sub-class it.

  #================================ size ===============================
  #
  # @brief  Returns the dimensions of the puzzle piece image.
  #
  def size(self):
    return self.y.size

  #================================ setMeasurement ===============================
  #
  # @brief  Pass along to the instance a measurement of the puzzle
  #         piece.
  #
  # @param[in]  thePiece    A measurement of the puzzle piece.
  #
  def setMeasurement(self, thePiece):

    self.y = thePiece.y
    self.rLoc = thePiece.rLoc


  #============================== setSource ============================
  #
  # @brief  Pass along the source data describing the puzzle piece.
  #
  def setSource(self, y, r = None):
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
  def setPlacement(self, r, offset = False, isCenter = False):
    if isCenter:
      if offset:
        self.rLoc = self.rLoc + r - np.ceil(self.y.size/2)
      else:
        self.rLoc = r - np.ceil(self.y.size/2)
    else:
      if offset:
        self.rLoc = self.rLoc + r
      else:
        self.rLoc = r

  #============================ placeInImage ===========================
  #
  # @brief  Insert the puzzle piece into the image at the given location.
  #
  # @param[in]  theImage    The source image to put puzzle piece into.
  #
  def placeInImage(self, theImage, offset=[0,0], CONTOUR_DISPLAY = True):

    # Remap coordinates from own image sprite coordinates to bigger
    # image coordinates.
    rcoords = np.array(offset).reshape(-1,1) +  self.rLoc.reshape(-1,1) + self.y.rcoords

    # Dump color/appearance information into the image (It will override the original image).
    theImage[rcoords[1], rcoords[0], :] = self.y.appear

    # May have to re-draw the contour for better visualization
    if CONTOUR_DISPLAY:
      rcoords = list(np.where(self.y.contour))
      rcoords[0], rcoords[1] = rcoords[1], rcoords[0]
      rcoords = np.array(offset).reshape(-1,1) +  self.rLoc.reshape(-1,1) + rcoords
      theImage[rcoords[1], rcoords[0], :] = [0,0,0]

    # @todo
    # FOR NOW JUST PROGRAM WITHOUT ORIENTATION CHANGE. LATER, INCLUDE THAT
    # OPTION.  IT WILL BE A LITTLE MORE INVOLVED. WOULD REQUIRE HAVING A
    # ROTATED IMAGE TEMPLATE AS A MEMBER VARIABLE.

  #============================ placeInImageAt ===========================
  #
  # @brief  Insert the puzzle piece into the image at the given location.
  #         
  # @param[in]  theImage    The source image to put puzzle piece into.
  # @param[in]  rc          The coordinate location.
  # @param[in]  theta       The orientation of the puzzle piece (default = 0).
  #
  def placeInImageAt(self, theImage, rc, theta = 0, isCenter = False, CONTOUR_DISPLAY = True):

    if not theta:
      theta = 0

    # If specification is at center, then compute offset to top-left corner.
    if isCenter:
      rc = rc - np.ceil(self.y.size / 2)

    # Remap coordinates from own image sprite coordinates to bigger image coordinates.
    rcoords = rc.reshape(-1,1) + self.y.rcoords

    # Dump color/appearance information into the image.
    theImage[rcoords[1], rcoords[0], :] = self.y.appear

    # May have to re-draw the contour for better visualization
    if CONTOUR_DISPLAY:
      rcoords = list(np.where(self.y.contour))
      rcoords[0], rcoords[1] = rcoords[1], rcoords[0]
      rcoords =  rc.reshape(-1,1) + rcoords
      theImage[rcoords[1], rcoords[0], :] = [0,0,0]

    # @todo
    # FOR NOW JUST PROGRAM WITHOUT ORIENTATION CHANGE. LATER, INCLUDE THAT
    # OPTION.  IT WILL BE A LITTLE MORE INVOLVED.

  #============================== display ==============================
  #
  # @brief  Display the puzzle piece contents in an image window.
  #
  # @param[in]  fh  The figure label/handle if available. (optional)
  #
  # @param[out] fh  The handle of the image.
  #
  def display(self, fh = None):
    if fh:
      # See https://stackoverflow.com/a/7987462/5269146
      fh = plt.figure(fh.number)
    else:
      fh = plt.figure()

    # See https://stackoverflow.com/questions/13384653/imshow-extent-and-aspect
    # plt.imshow(self.y.image, extent = [0, 1, 0, 1])
    theImage = np.zeros_like(self.y.image)
    theImage[self.y.rcoords[1], self.y.rcoords[0], :] = self.y.appear
    plt.imshow(theImage)
    plt.show()

    return fh

  #======================= buildFromMaskAndImage =======================
  #
  # @brief  Given a mask (individual) and an image of same base dimensions, use to
  #         instantiate a puzzle piece template.
  #
  # @param[in]  theMask    The individual mask.
  # @param[in]  theImage   The source image.
  # @param[in]  rLoc       The puzzle piece location in the whole image.
  #
  # @param[out] thePiece   The puzzle piece instance.
  #
  @staticmethod
  def buildFromMaskAndImage(theMask, theImage, rLoc = None):

    y = puzzleTemplate()

    # Populate dimensions.
    # Updated to OpenCV style
    y.size = [theMask.shape[1], theMask.shape[0]]

    y.mask = theMask.astype('uint8')

    # Create a contour of the mask
    cnts = cv2.findContours(y.mask, cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)
    y.contour = np.zeros_like(y.mask).astype('uint8')
    cv2.drawContours(y.contour, cnts[0], -1, (255, 255, 255), thickness=2)

    y.rcoords = list(np.nonzero(theMask)) # 2 (row,col) x N
    # Updated to OpenCV style -> (x,y)
    y.rcoords[0], y.rcoords[1] = y.rcoords[1], y.rcoords[0]
    y.appear = theImage[y.rcoords[1],y.rcoords[0], :]
    # Store template image.
    # @note
    # For now, not concerned about bad image data outside of mask.
    y.image = theImage

    if not rLoc:
      thePiece = template(y)
    else:
      thePiece = template(y, rLoc)

    return thePiece

#
#========================= puzzle.piece.template =========================
