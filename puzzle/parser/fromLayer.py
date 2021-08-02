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
# @file     fromLayer.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/29 [created]
#           2021/08/01 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#======================== puzzle.parser.fromLayer ========================

#==== Imports
#

import cv2
import numpy as np

from trackpointer.centroidMulti import centroidMulti
from puzzle.piece.template import template
from puzzle.board import board
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

    self.bMeas = board()             # @< The measured board.

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
  #             Mainly based on findContours function.
  #
  # @param[in]  I   Source image.
  # @param[in]  M   Layer mask (binary).
  #
  # @param[out] regions   A list of regions (mask, segmented image, location in the source image).
  #
  def mask2regions(self, I, M):

    # Convert mask to an image
    mask = M.astype('uint8')

    # For details of options, see https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga819779b9857cc2f8601e6526a3a5bc71
    # and https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga4303f45752694956374734a03c54d5ff
    cnts = cv2.findContours(mask, cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)
    # For OpenCV 4+
    cnts = cnts[0]

    # @todo
    # Yunzhi: create a param class for it
    # areaThreshold for contours
    areaThreshold = 20

    desired_cnts = []

    # Filter out some contours according to length threshold
    for c in cnts:
      # Draw the contours
      # cv2.drawContours(mask, [c], -1, (0, 255, 0), 2)
      area = cv2.contourArea(c)

      # @todo
      # Yunzhi: this basic processing may be put somewhere else
      # Filtered by the area threshold
      if area > areaThreshold:
        desired_cnts.append(c)

    # print('size of desired_cnts is', len(desired_cnts))

    regions = []
    # Get the individual part
    for c in desired_cnts:
      seg_img = np.zeros(mask.shape[:2], dtype="uint8")  # reset a blank image every time
      # cv2.polylines(seg_img, [c], True, (255, 255, 255), thickness=3)
      cv2.drawContours(seg_img, [c], -1, (255, 255, 255), thickness=-1)

      # # Convert to boolen image
      # _, seg_img = cv2.threshold(seg_img, 127, 255, cv2.THRESH_BINARY)
      # seg_img = seg_img>0

      # Get ROI
      x, y, w, h = cv2.boundingRect(c)

      regions.append((seg_img[y:y+h, x:x+w],I[y:y+h, x:x+w,:],[x,y]))

      # cv2.imshow("Segments", seg_img)
      # cv2.waitKey(0)

    return regions


  #========================== regions2pieces ===========================
  #
  # @brief  Convert the region information into puzzle pieces.
  #
  # @param[in]  regions   a list of region pairs (mask, segmented image, location in the source image).
  #
  # @param[out]  pieces   a list of puzzle pieces instances.
  #
  def regions2pieces(self, regions):

    pieces = []
    for region in regions:
      theMask = region[0]
      theImage = region[1]
      rLoc = region[2]
      thePiece = template.buildFromMaskAndImage(theMask, theImage, rLoc = [rLoc[0],rLoc[1]])

      # @todo
      # Have to update from MatLab coordinate system to OpenCV one later
      pieces.append(thePiece)

    return pieces

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


#
#======================== puzzle.parser.fromLayer ========================
