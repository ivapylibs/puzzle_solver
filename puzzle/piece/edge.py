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
  # @brief  Constructor for the puzzle piece edge class.
  #
  #
  def __init__(self, tau_shape=100, tau_color=150):
    super(edge, self).__init__()

    self.tau_shape = tau_shape
    self.tau_color = tau_color

  # ============================== shapeFeaExtrct ==============================
  #
  # @brief  Extract the edge shape feature from an input image of the edge.
  #
  # @param[in]   edge            An EdgeDes instance.
  #
  @staticmethod
  def shapeFeaExtract(edge, method = None):

    if method == 'type':
      shapeFea = edge.type
    else:
      y, x = np.nonzero(edge.mask)
      shapeFea = np.hstack((x.reshape(-1, 1), y.reshape(-1, 1)))

    return shapeFea
  # ============================== colorFeaExtrct ==============================
  #
  # @brief  Extract the edge color feature from an input image of the edge.
  #
  # @param[in]   edge           An EdgeDes instance.
  #
  @staticmethod
  def colorFeaExtract(edge, feaLength=200):
    y, x = np.nonzero(edge.mask)

    # Extract the valid pts
    pts = edge.image[y, x]
    # pts = dst[y, x]

    # import matplotlib.pyplot as plt
    # plt.imshow(edge.mask)
    # plt.show()

    # Expand dim for further processing
    feaOri = np.expand_dims(pts, axis=0)

    # Resize to a unit length
    feaResize = cv2.resize(feaOri, (feaLength, 1))

    # self.edge[direction].feature_color = feaResize

    # # @todo Yunzhi: May need to double check the color space
    feaResize = cv2.cvtColor(feaResize, cv2.COLOR_RGB2Lab)

    return feaResize.astype('float32')

  #=========================== process ==========================
  #
  # @brief  Compute features from the data.
  #
  # @param[in]  y    An EdgeDes instance.
  #
  #
  def process(self, y, method=None):

    feature_shape = edge.shapeFeaExtract(y, method=method)
    feature_color = edge.colorFeaExtract(y)

    return [feature_shape, feature_color]

  #=============================== score ===============================
  #
  # @brief  Compute the score between two passed puzzle piece data.
  #
  # @param[in]  yA    A regular instance or an EdgeDes instance.
  # @param[in]  yB    A regular instance or an EdgeDes instance.
  #
  # @param[out]  distance_shape    The shape distance between the two passed data.
  # @param[out]  distance_color    The color distance between the two passed data.
  #
  def score(self, yA, yB, method = 'type'):

    def dis_shape(feature_shape_A, feature_shape_B, method=method):

      # similaritymeasures.pcm
      # similaritymeasures.frechet_dist
      # similaritymeasures.area_between_two_curves
      # similaritymeasures.curve_length_measure
      # similaritymeasures.dtw

      if method=='type':
        if feature_shape_A==feature_shape_B:
          distance = 0
        else:
          distance = float('inf')
      else:
        distance = method(feature_shape_A, feature_shape_B)
      # For dtw
      if isinstance(distance,tuple):
        distance = distance[0]
      return distance

    def dis_color(feature_color_A, feature_color_B):

      distance = np.mean(np.sum((feature_color_A[0]-feature_color_B[0]) ** 2, axis=1) ** (1. / 2))

      return distance

    distance_shape = []
    distance_color = []

    if type(yA) != type(yB):
      raise TypeError('Input should be of the same type.')
    else:
      if isinstance(yA, regular):

        for i in range(4):
          feature_shape_A, feature_color_A = self.process(yA.edge[i],method=method)
          feature_shape_B, feature_color_B = self.process(yB.edge[i],method=method)

          distance_shape.append(dis_shape(feature_shape_A, feature_shape_B, method=method))
          distance_color.append(dis_color(feature_color_A, feature_color_B))

      elif isinstance(yA, EdgeDes):
        feature_shape_A, feature_color_A = self.process(yA,method=method)
        feature_shape_B, feature_color_B = self.process(yB,method=method)
        distance_shape.append(dis_shape(feature_shape_A, feature_shape_B, method=method))
        distance_color.append(dis_color(feature_color_A, feature_color_B))

      else:
        raise TypeError('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

    return distance_shape, distance_color

  #============================== compare ==============================
  #
  # @brief  Compare between two passed puzzle piece data.
  #
  # @param[in]  yA    A template instance or puzzleTemplate instance saving a piece's info.
  # @param[in]  yB    A template instance or puzzleTemplate instance saving a piece's info.
  #
  # @param[out]       Return comparison result
  #
  def compare(self, yA, yB, method= 'type'):

    # score is to calculate the similarity while it will call the feature extraction process inside

    distance_shape, distance_color = self.score(yA, yB, method = method)

    if (np.array(distance_shape) < self.tau_shape).all() and (np.array(distance_color) < self.tau_color).all():
      return True
    else:
      return False



#
#================================ puzzle.piece.edge ================================
