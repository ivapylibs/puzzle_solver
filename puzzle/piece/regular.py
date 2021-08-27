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

# @todo
# Yunzhi: May need to upgrade to other forms when we have rotations
class EdgeDirection(Enum):
  """ EdgeDirection used to keep track of the direction of edges """

  LEFT = 0
  RIGHT = 1
  TOP = 2
  BOTTOM = 3

class EdgeDes:
  type: int= EdgeType.UNDEFINED
  feature_shape: np.ndarray =np.array([])  # To save the shape feature
  feature_color: np.ndarray =np.array([])  # To save the color feature

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
      print('Too many parameters!')
      exit()

    super(regular, self).__init__(y, r, id)

    # Assume the order 0, 1, 2, 3 correspond to left, right, top, bottom
    self.edge = [EdgeDes() for i in range(4)]


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

  # ============================== shapeFeaExtrct ==============================
  #
  # @brief  Extract the edge shape feature from an input image
  #
  # @param[in]   direction      The edge to be set up.
  # @param[in]   img            The input image.
  #
  def shapeFeaExtract(self, direction, img):

    y, x = np.nonzero(img)
    shapeFea = np.hstack((x.reshape(-1,1), y.reshape(-1,1)))
    self.edge[direction].feature_shape = shapeFea

  # ============================== colorFeaExtrct ==============================
  #
  # @brief  Extract the edge color feature from an input image
  #
  # @param[in]   direction      The edge to be set up.
  # @param[in]   img            The input image.
  #
  def colorFeaExtract(self, direction, img, feaLength=50):

    y, x = np.nonzero(img)

    # Extract the valid pts
    pts = self.y.image[y,x]

    # Expand dim for further processing
    feaOri = np.expand_dims(pts, axis=0)

    # Resize to a unit length
    feaResize = cv2.resize(feaOri,(1,feaLength))

    self.edge[direction].feature_color = feaResize


  # ============================== process ==============================
  #
  # @brief  Run the sideExtractor
  #
  #
  def process(self):

    out_dict = sideExtractor(self.y, scale_factor=1,
                             harris_block_size=5, harris_ksize=5,
                             corner_score_threshold=0.2, corner_minmax_threshold=100)

    # Set up the type of the chosen edge
    for direction in EdgeDirection:
      self.setEdgeType(direction.value, out_dict['inout'][direction.value])
      self.shapeFeaExtract(direction.value, out_dict['side_images'][direction.value])
      self.colorFeaExtract(direction.value, out_dict['side_images'][direction.value])

    # @todo
    # Yunzhi: will remove afterwards
    return out_dict
#
#================================ puzzle.piece.regular ================================
