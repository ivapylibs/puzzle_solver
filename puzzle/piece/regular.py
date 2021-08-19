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
class TypeEdge(Enum):
  """ TypeEdge used to keep track of the type of edges """

  UNDEFINED = 0
  IN = 1
  OUT = 2
  FLAT = 3

# @todo
# Yunzhi: May need to upgrade to other forms when we have rotations
class DirectionEdge(Enum):
  """ DirectionEdge used to keep track of the direction of edges """

  LEFT = 0
  RIGHT = 1
  TOP = 2
  BOTTOM = 3

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
    self.edge = [TypeEdge.UNDEFINED] * 4

  # ============================== setTypeEdge ==============================
  #
  # @brief  Set up the type of the chosen edge
  #
  # @param[in]   direction      The edge to be set up.
  # @param[in]   type           The type.
  #
  def setTypeEdge(self, direction, type):

    self.edge[direction] = type

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
    for direction, type in enumerate(out_dict['inout']):
      self.setTypeEdge(direction, type)

    return out_dict
#
#================================ puzzle.piece.regular ================================
