#================================ puzzle.piece.edge ================================
#
# @brief    Uses edge features to establish similarity.
#
#================================ puzzle.piece.edge ================================

#
# @file     edge.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/26 [created]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#================================ puzzle.piece.edge ================================

#===== Environment / Dependencies
#
import cv2
import math
import numpy as np

import similaritymeasures

from puzzle.piece.matchDifferent import matchDifferent

from puzzle.piece.regular import regular, EdgeDes
#
#================================ puzzle.piece.edge ================================
#
class edge(matchDifferent):

  #=============================== puzzle.piece.edge ==============================
  #
  # @brief  Constructor for the puzzle piece matchDifferent class.
  #
  #
  def __init__(self, tau=-float('inf')):
    super(edge, self).__init__(tau)

  #=========================== process ==========================
  #
  # @brief  Compute features from the data.
  #
  # @param[in]  y    An EdgeDes instance.
  #
  #
  def process(self, y):

    # @todo Yunzhi: No additional processing for now

    feature_color = cv2.cvtColor(y.feature_color,cv2.COLOR_RGB2Lab)

    return [y.feature_shape, feature_color]

  #=============================== score ===============================
  #
  # @brief  Compute the score between passed puzzle piece data and
  #         stored puzzle piece.
  #
  # @param[in]  yA    A regular instance or an EdgeDes instance.
  # @param[in]  yB    A regular instance or an EdgeDes instance.
  #
  # @param[out]  distance_shape    The shape distance between the two passed data.
  # @param[out]  distance_color    The color distance between the two passed data.
  #
  def score(self, yA, yB, method = 'pcm'):

    def dis_shape(feature_shape_A, feature_shape_B, method=method):
      if method == 'pcm':
        distance = similaritymeasures.pcm(feature_shape_A, feature_shape_B)
      elif method == 'frechet':
        distance = similaritymeasures.frechet_dist(feature_shape_A, feature_shape_B)
      elif method == 'area':
        distance = similaritymeasures.area_between_two_curves(feature_shape_A, feature_shape_B)
      elif method == 'length':
        distance = similaritymeasures.curve_length_measure(feature_shape_A, feature_shape_B)
      elif method == 'dtw':
        distance, _ = similaritymeasures.dtw(feature_shape_A, feature_shape_B)

      return distance

    def dis_color(feature_color_A, feature_color_B):

      distance = np.linalg.norm(feature_color_A-feature_color_B)

      return distance

    distance_shape = []
    distance_color = []

    if type(yA) != type(yB):
      raise TypeError('Input should be of the same type.')
    else:
      if isinstance(yA, regular):

        for i in range(4):
          feature_shape_A, feature_color_A = self.process(yA.edge[i])
          feature_shape_B, feature_color_B = self.process(yB.edge[i])

          distance_shape.append(dis_shape(feature_shape_A, feature_shape_B, method))
          distance_color.append(dis_color(feature_color_A, feature_color_B))

      elif isinstance(yA, EdgeDes):
        feature_shape_A, feature_color_A = self.process(yA)
        feature_shape_B, feature_color_B = self.process(yB)
        distance_shape.append(dis_shape(feature_shape_A, feature_shape_B, method))
        distance_color.append(dis_color(feature_color_A, feature_color_B))

      else:
        raise TypeError('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

    return distance_shape, distance_color

  #============================== compare ==============================
  #
  # @brief  Compare a measured puzzle piece to this particular one.
  #
  # @param[in]  yA    A template instance or puzzleTemplate instance saving a piece's info.
  # @param[in]  yB    A template instance or puzzleTemplate instance saving a piece's info.
  #
  # @param[out]       Return comparison result
  #
  def compare(self, yA, yB):

    # score is to calculate the similarity while it will call the feature extraction process inside
    distance_shape, distance_color = self.score(yA, yB)

    if (np.array(distance_shape) < self.tau).all() and (np.array(distance_color) < self.tau).all():
      return True
    else:
      return False



#
#================================ puzzle.piece.edge ================================
