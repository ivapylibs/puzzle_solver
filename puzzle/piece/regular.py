#================================ puzzle.piece.regular ================================
#
# @brief    Establish a regular puzzle piece (4 sides with locks)
#
#================================ puzzle.piece.regular ================================

#
# @file     regular.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/17 [created]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#================================ puzzle.piece.regular ================================

#===== Environment / Dependencies
#
import cv2
import math
import numpy as np

from enum import Enum

from puzzle.piece.template import template

from puzzle.utils.sideExtractor import sideExtractor

#===== Helper Elements
#
class EdgeType(Enum):
  """ EdgeType used to keep track of the type of edges """

  UNDEFINED = 0
  IN = 1
  OUT = 2
  FLAT = 3

# @todo Yunzhi: May need to upgrade to other forms when we have rotations
class EdgeDirection(Enum):
  """ EdgeDirection used to keep track of the direction of edges """

  LEFT = 0
  RIGHT = 1
  TOP = 2
  BOTTOM = 3

class EdgeDes:
  type: int= EdgeType.UNDEFINED       # To save the type: in/out/flat.
  image: np.ndarray =np.array([])  # To save the image of the edge.
  mask: np.ndarray = np.array([])  # To save the mask of the edge.



#
#================================ puzzle.piece.regular ================================
#
class regular(template):

  #=============================== regular ==============================
  #
  # @brief  Constructor for the regular puzzle piece.
  #
  def __init__(self, *argv):

    y = None
    r = (0,0)
    id = None

    if len(argv)==1:
      if isinstance(argv[0], template):
        y = argv[0].y
        r = argv[0].rLoc
        id = argv[0].id
      else:
        y = argv[0]
    elif len(argv)==2:
      y = argv[0]
      r = argv[1]
      super(regular, self).__init__(y, r)
    elif len(argv) == 3:
      y = argv[0]
      r = argv[1]
      id = argv[2]
      super(regular, self).__init__(y, r, id)
    elif len(argv) == 4:
      raise TypeError('Too many parameters!')

    super(regular, self).__init__(y, r, id)

    # Assume the order 0, 1, 2, 3 correspond to left, right, top, bottom
    self.edge = [EdgeDes() for i in range(4)]

    self.class_image = None

    self._process()

  # ============================== setEdgeImg ==============================
  #
  # @brief  Set up the img of the chosen edge.
  #
  # @param[in]   direction      The edge to be set up.
  # @param[in]   type           The type.
  #
  def setEdgeImg(self, direction, mask):

    image_masked = cv2.bitwise_and(self.y.image, self.y.image, mask=mask)
    self.edge[direction].image = image_masked
    self.edge[direction].mask = mask

  # ============================== setEdgeType ==============================
  #
  # @brief  Set up the type of the chosen edge
  #
  # @param[in]   direction      The edge to be set up.
  # @param[in]   type           The type.
  #
  def setEdgeType(self, direction, type):
    self.edge[direction].type = type

  # ============================== displayEdgeType ==============================
  #
  # @brief  Display the edge type of the piece
  #
  def displayEdgeType(self):

    for direction in EdgeDirection:
      print(f'{direction.name}:',self.edge[direction.value].type)

  # ============================== process ==============================
  #
  # @brief  Run the sideExtractor
  #
  #
  def _process(self):

    out_dict = sideExtractor(self.y, scale_factor=1,
                             harris_block_size=5, harris_ksize=5,
                             corner_score_threshold=0.2, corner_minmax_threshold=100)

    # Set up the type/img of the chosen edge
    for direction in EdgeDirection:
      self.setEdgeType(direction.value, out_dict['inout'][direction.value])
      self.setEdgeImg(direction.value, out_dict['side_images'][direction.value])

    # @note Just for display for now
    self.class_image = out_dict['class_image']

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
  def buildFromMaskAndImage(theMask, theImage, rLoc=None):

    thePiece = template.buildFromMaskAndImage(theMask, theImage, rLoc=rLoc)
    theRegular = regular(thePiece)

    return theRegular
#
#================================ puzzle.piece.regular ================================
