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

#===== Environment / Dependencies
#
import numpy as np
from dataclasses import dataclass
import cv2

import matplotlib.pyplot as plt

from puzzle.utils.imageProcessing import rotate_im

from copy import deepcopy
#===== Helper Elements
#
@dataclass
class puzzleTemplate:
  size:    np.ndarray = np.array([])   # @< Tight bbox size of puzzle piece image.
  rcoords: np.ndarray = np.array([])  # @< Puzzle piece linear image coordinates.
  appear:  np.ndarray = np.array([])  # @< Puzzle piece linear color/appearance.
  image:   np.ndarray = np.array([],dtype='uint8')  # @< Template RGB image with BG default fill.
  mask:     np.ndarray = np.array([],dtype='uint8') # @< Template binary mask image.
  contour:  np.ndarray = np.array([],dtype='uint8') # @< Template binary contour image.
  contour_pts: np.ndarray = np.array([]) # @< Template contour points.
#
#========================= puzzle.piece.template =========================
#

class template:

  def __init__(self, y = None, r = (0, 0), theta=0, id = None):
    '''
    @brief  Constructor for the puzzle.piece.base class.

    :param y: The puzzle piece template source data, if given. It is a class instance, see puzzleTemplate.
    :param r: The puzzle piece location in the whole image.
    :param theta: The puzzle piece aligned angle.
    :param id: The puzzle piece id in the measured board. Be set up by the board.
    '''

    self.y = y          # @< The puzzle piece template source data, if given. It is a class instance, see puzzleTemplate

    # The default location is the top left corner
    self.rLoc = np.array(r)       # @< The puzzle piece location in the whole image.

    self.id = id  # @< The puzzle piece id in the measured board. Be set up by the board.

    # self.pLoc = p       # @< The puzzle piece discrete grid piece coordinates.
    # @note     Opting not to use discrete grid puzzle piece description.
    # @note     Excluding orientation for now. Can add later. Or sub-class it.

    # Should be set up later by the align function
    self.theta = theta  # @< The puzzle piece aligned angle

  def size(self):
    '''
    @brief  Return the dimensions of the puzzle piece image.

    :return: Dimensions of the puzzle piece image
    '''

    return self.y.size

  def setMeasurement(self, thePiece):
    '''
    @brief  Pass along to the instance a measurement of the puzzle piece.

    :param thePiece: A measurement of the puzzle piece.
    '''

    self.y = thePiece.y
    self.rLoc = thePiece.rLoc

  def setSource(self, y, r = None):
    '''
    @brief  Pass along the source data describing the puzzle piece.

    :param y: Puzzle piece template.
    :param r: The puzzle piece location in the whole image.
    '''

    self.y = y

    if r:
      self.r = r

  @staticmethod
  def getEig(img):
    '''
    @brief  To find the major and minor axes of a blob and then return the aligned rotation.
    See https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/ for details.

    :param  img:           A contour image.
    :return: The aligned angle (rad).
    '''

    # @note
    # Currently, we use the image center

    y, x = np.nonzero(img)
    # x = x - np.mean(x)
    # y = y - np.mean(y)
    #
    x = x - np.mean(img.shape[1]/2)
    y = y - np.mean(img.shape[0]/2)

    coords = np.vstack([x, y])
    cov = np.cov(coords)
    evals, evecs = np.linalg.eig(cov)
    sort_indices = np.argsort(evals)[::-1]
    v1 = evecs[:, sort_indices[0]]  # Eigenvector with largest eigenvalue
    v2 = evecs[:, sort_indices[1]]

    dict = {
      'x': x,
      'y': y,
      'v1': v1,
      'v2': v2,
    }

    theta = np.arctan2(dict['v1'][1], dict['v1'][0])

    # # Debug only
    #
    # scale = 20
    # plt.plot([dict['v1'][0] * -scale * 2, dict['v1'][0] * scale * 2],
    #          [dict['v1'][1] * -scale * 2, dict['v1'][1] * scale * 2], color='red')
    # plt.plot([dict['v2'][0] * -scale, dict['v2'][0] * scale],
    #          [dict['v2'][1] * -scale, dict['v2'][1] * scale], color='blue')
    # plt.plot(x, y, 'k.')
    # plt.axis('equal')
    # plt.gca().invert_yaxis()  # Match the image system with origin at top left
    # plt.show()

    return theta

  def setPlacement(self, r, offset = False, isCenter = False):
    '''
    @brief  Provide pixel placement location information.

    :param  r:           Location of its frame origin.
    :param  isCenter:    Boolean indicating r is center instead.
    '''

    if isCenter:
      if offset:
        self.rLoc = np.array(self.rLoc + r - np.ceil(self.y.size/2))
      else:
        self.rLoc = np.array(r - np.ceil(self.y.size/2))
    else:
      if offset:
        self.rLoc = np.array(self.rLoc + r)
      else:
        self.rLoc = np.array(r)

  def placeInImage(self, theImage, offset=[0,0], CONTOUR_DISPLAY = True):
    '''
    @brief  Insert the puzzle piece into the image at the given location.

    :param theImage: The source image to put puzzle piece into.
    :param offset: The offset list.
    :param CONTOUR_DISPLAY: The flag indicating whether to display the contours.
    '''

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

  def placeInImageAt(self, theImage, rc, theta = None, isCenter = False, CONTOUR_DISPLAY = True):
    '''
    @brief  Insert the puzzle piece into the image at the given location.

    :param theImage: The source image to put puzzle piece into.
    :param rc: The coordinate location.
    :param theta: The orientation of the puzzle piece (default = 0).
    :param isCenter: The flag indicating whether the given location is for the center.
    :param CONTOUR_DISPLAY: The flag indicating whether to display the contours.
    '''

    if theta is not None:
      thePiece= self.rotatePiece(theta)
    else:
      thePiece = self

    # If specification is at center, then compute offset to top-left corner.
    if isCenter:
      rc = rc - np.ceil(thePiece.y.size / 2)

    # Remap coordinates from own image sprite coordinates to bigger image coordinates.
    rcoords = rc.reshape(-1,1) + thePiece.y.rcoords

    # Dump color/appearance information into the image.
    theImage[rcoords[1], rcoords[0], :] = thePiece.y.appear

    # May have to re-draw the contour for better visualization
    if CONTOUR_DISPLAY:
      rcoords = list(np.where(thePiece.y.contour))
      rcoords[0], rcoords[1] = rcoords[1], rcoords[0]
      rcoords =  rc.reshape(-1,1) + rcoords
      theImage[rcoords[1], rcoords[0], :] = [0,0,0]


  def toImage(self):
    '''
    @brief  Return the puzzle piece image (cropped).

    :return: The puzzle piece image (cropped).
    '''

    theImage = np.zeros_like(self.y.image)
    theImage[self.y.rcoords[1], self.y.rcoords[0], :] = self.y.appear

    return theImage

  def display(self, fh = None):
    '''
    @brief  Display the puzzle piece contents in an image window.

    :param fh: The figure label/handle if available. (optional)
    :return: The handle of the image.
    '''

    if fh:
      # See https://stackoverflow.com/a/7987462/5269146
      fh = plt.figure(fh.number)
    else:
      fh = plt.figure()

    # See https://stackoverflow.com/questions/13384653/imshow-extent-and-aspect
    # plt.imshow(self.y.image, extent = [0, 1, 0, 1])

    theImage = self.toImage()
    plt.imshow(theImage)

    # plt.show()

    return fh

  @staticmethod
  def buildFromMaskAndImage(theMask, theImage, rLoc = None):
    '''
    @brief  Given a mask (individual) and an image of same base dimensions, use to
    instantiate a puzzle piece template.

    :param theMask: The individual mask.
    :param theImage: The source image.
    :param rLoc: The puzzle piece location in the whole image.
    :return: The puzzle piece instance.
    '''

    y = puzzleTemplate()

    # Populate dimensions.
    # Updated to OpenCV style
    y.size = [theMask.shape[1], theMask.shape[0]]

    y.mask = theMask.astype('uint8')

    # Create a contour of the mask
    cnts = cv2.findContours(y.mask, cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)

    y.contour_pts = cnts[0][0]
    y.contour = np.zeros_like(y.mask).astype('uint8')
    cv2.drawContours(y.contour, cnts[0], -1, (255, 255, 255), thickness=2)

    # @note
    # Yunzhi: For debug
    # hull = cv2.convexHull(cnts[0][0])
    # aa = np.zeros_like(y.mask).astype('uint8')
    # cv2.drawContours(aa, hull, -1, (255, 255, 255), thickness=10)
    # cv2.imshow('Test', aa)
    # cv2.waitKey()

    y.rcoords = list(np.nonzero(theMask)) # 2 (row,col) x N
    # Updated to OpenCV style -> (x,y)
    y.rcoords[0], y.rcoords[1] = y.rcoords[1], y.rcoords[0] # 2 (x;y) x N
    y.rcoords = np.array(y.rcoords)

    y.appear = theImage[y.rcoords[1],y.rcoords[0], :]
    # Store template image.
    # @note
    # For now, not concerned about bad image data outside of mask.
    y.image = theImage

    if not rLoc:
      thePiece = template(y)
    else:
      thePiece = template(y, rLoc)

    # Set up the rotation
    thePiece.theta = template.getEig(thePiece.y.contour)

    return thePiece

  def rotatePiece(self, theta):
    '''
    @brief Rotate the puzzle template instance by the given angle.

    :param theta: The rotated angle.
    :return: A new puzzle template instance.
    '''

    # Create a new instance. Without rLoc.
    thePiece = template(y=deepcopy(self.y),id=deepcopy(self.id))

    # By default the rotation is around its center (img center)
    thePiece.y.mask,M,x_pad,y_pad = rotate_im(thePiece.y.mask, theta)

    # Have to apply a thresh to deal with holes caused by interpolation
    _, thePiece.y.mask = cv2.threshold(thePiece.y.mask, 10, 255, cv2.THRESH_BINARY)

    thePiece.y.image,_,_,_ = rotate_im(thePiece.y.image, theta)

    thePiece.y.size = [thePiece.y.mask.shape[1], thePiece.y.mask.shape[0]]

    thePiece.y.rcoords = list(np.nonzero(thePiece.y.mask))  # 2 (row;col) x N

    # Updated to OpenCV style -> (x,y)
    thePiece.y.rcoords[0], thePiece.y.rcoords[1] = thePiece.y.rcoords[1], thePiece.y.rcoords[0]  # 2 (x;y) x N
    thePiece.y.rcoords = np.array(thePiece.y.rcoords)

    thePiece.y.appear = thePiece.y.image[thePiece.y.rcoords[1], thePiece.y.rcoords[0], :]

    # @note If we simply transform the original info, the result may be inaccurate?

    # Create a contour of the mask
    cnts = cv2.findContours(thePiece.y.mask, cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)

    thePiece.y.contour_pts = cnts[0][0]
    thePiece.y.contour = np.zeros_like(thePiece.y.mask).astype('uint8')
    cv2.drawContours(thePiece.y.contour, cnts[0], -1, (255, 255, 255), thickness=2)

    # Might be negative
    thePiece.rLoc = self.rLoc-np.array([x_pad,y_pad])

    return thePiece

  @staticmethod
  def buildSquare(size, color, rLoc = None):
    '''
    @brief  Build a square piece.

    :param size: The side length of the square
    :param color: (3,). The RGB color.
    :param rLoc: (x, y). The puzzle piece location in the whole image. x: left-to-right. y:top-to-down
    :return: The puzzle piece instance.
    '''
    
    y = puzzleTemplate()

    # the tight bbox is just the square itself, so size is just size 
    y.size = np.array([size, size])
    y.mask = np.ones((size, size), dtype=np.uint8)*255

    # Create a contour of the mask
    cnts = cv2.findContours(y.mask, cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)

    y.contour_pts = cnts[0][0]
    y.contour = np.zeros_like(y.mask).astype('uint8')
    cv2.drawContours(y.contour, cnts[0], -1, (255, 255, 255), thickness=2)

    y.rcoords = list(np.nonzero(y.mask)) # 2 (row,col) x N
    # Updated to OpenCV style -> (x,y)
    y.rcoords[0], y.rcoords[1] = y.rcoords[1], y.rcoords[0]
    y.rcoords = np.array(y.rcoords)

    y.image = np.zeros((size, size, 3), dtype=np.uint8)
    y.image = cv2.rectangle(y.image, (0,0), (size-1, size-1), color=color, thickness=-1)
    y.appear = y.image[y.rcoords[1],y.rcoords[0], :]

    if not rLoc:
      thePiece = template(y)
    else:
      thePiece = template(y, rLoc)

    return thePiece

  @staticmethod
  def buildSphere(radius, color, rLoc = None):
    '''
    @brief  Build a sphere piece

    :param radius: The radius of the sphere.
    :param color: (3,). The RGB color.
    :param rLoc: (x, y). The puzzle piece location in the whole image. x: left-to-right. y:top-to-down
    :return: The puzzle piece instance.
    '''

    y = puzzleTemplate()

    # the tight bbox is just the square itself, so size is just size 
    y.size = np.array([radius, radius]) * 2
    y.mask = np.zeros((2*radius, 2*radius), dtype=np.uint8)
    y.mask = cv2.circle(y.mask, center=(radius-1, radius-1), radius=radius, color=(255,255,255), thickness=-1)

    # Create a contour of the mask
    cnts = cv2.findContours(y.mask, cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)

    y.contour_pts = cnts[0][0]
    y.contour = np.zeros_like(y.mask).astype('uint8')
    cv2.drawContours(y.contour, cnts[0], -1, (255, 255, 255), thickness=2)

    y.rcoords = list(np.nonzero(y.mask)) # 2 (row,col) x N
    # Updated to OpenCV style -> (x,y)
    y.rcoords[0], y.rcoords[1] = y.rcoords[1], y.rcoords[0]
    y.rcoords = np.array(y.rcoords)

    y.image = np.ones((2*radius, 2*radius, 3), dtype=np.uint8)
    y.image = cv2.circle(y.image, radius=radius, center=(radius-1, radius-1), color=color, thickness=-1)
    y.appear = y.image[y.rcoords[1],y.rcoords[0], :]

    if not rLoc:
      thePiece = template(y)
    else:
      thePiece = template(y, rLoc)

    return thePiece

#
#========================= puzzle.piece.template =========================
