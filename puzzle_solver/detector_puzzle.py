# =========================== detector_puzzle ============================
#
# @brief    A derived class from detector/inImage, mainly for puzzle solver
#
# =========================== detector_puzzle ============================

#
# @file     detector_puzzle.py
#
# @author   Yunzhi Lin,   yunzhi.lin@gatech.edu
# @date     2021/07/20 [created]
#
# !NOTE:
# !  Indent is set to 2 spaces.
# !  Tab is set to 4 spaces with conversion to spaces.
#
# =========================== detector_puzzle ============================

import numpy as np
import cv2
import itertools
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

from detector.inImage import inImage


class detector_puzzle(inImage):

  def __init__(self, processor=None):

    super(detector_puzzle, self).__init__(processor)

    # For debug purpose, enable debug flag
    self.debug = False

    # For saving movement (x,y,rotation)
    self.movement_list = []


  # ============================== measure ==============================
  #
  # @brief  Override the measure function for puzzle solver
  #
  def measure(self, I):
    if self.processor:
      mask = self.processor.apply(I)
    else:
      raise Exception('Processor has not been initialized yet')

    seg_img_list = self.get_segmented_mask(mask)
    seg_img_pair_list = self.get_matched_pairs(seg_img_list)
    self.movement_list = self.get_movement(seg_img_pair_list)

  # ============================== get_segmented_mask ==============================
  #
  # @brief  To get the segmented masks from a source mask image
  #
  # @param[in]   mask          The mask for the whole view
  # @param[out]  seg_img_list  A list of segmented masks
  #
  def get_segmented_mask(self, mask):

    # For details of options, see https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga819779b9857cc2f8601e6526a3a5bc71
    # and https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga4303f45752694956374734a03c54d5ff
    cnts = cv2.findContours(mask.copy(), cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)
    # For OpenCV 4+
    cnts = cnts[0]

    # @todo
    # areaThreshold for contours
    areaThreshold = 100

    desired_cnts = []

    # Filter out some contours according to length threshold
    for c in cnts:
      # Draw the contours
      cv2.drawContours(mask, [c], -1, (0, 255, 0), 2)
      area = cv2.contourArea(c)

      # Filtered by the area threshold
      if area > areaThreshold:

        desired_cnts.append(c)

        if self.debug:
          # For debug only
          # c is N x 1 x 2
          x, y = np.sum(np.array(c).reshape(-1, 2), axis=0)
          mean_x = int(x / c.shape[0])
          mean_y = int(y / c.shape[0])
          print(f'center: {mean_x},{mean_y}')

    if self.debug:
      print('size of desired_cnts is', len(desired_cnts))

    seg_img_list = []
    # Get the individual part
    for c in desired_cnts:
      seg_img = np.zeros(mask.shape[:2], dtype="uint8")  # reset a blank image every time
      cv2.polylines(seg_img, [c], True, (255, 255, 255), thickness=3)
      seg_img_list.append(seg_img)


      cv2.imshow("Segments", seg_img)
      cv2.waitKey(0)

    return seg_img_list

  # ============================== get_matched_pairs ==============================
  #
  # @brief  To get the matched puzzle-template pairs
  #
  # @param[in]   seg_img_list       A list of segmented masks
  # @param[out]  seg_img_pair_list  A list of matched puzzle-template pairs and its corresponding distance
  #                                 It is based on the Hu moments alforithm
  #
  def get_matched_pairs(self, seg_img_list):

    # Get the matched pairs
    seg_img_pair_list = []
    for pair in itertools.combinations(seg_img_list, 2):
      d2 = cv2.matchShapes(pair[0], pair[1], cv2.CONTOURS_MATCH_I2, 0)
      # @todo
      if d2 < 0.05:
        seg_img_pair_list.append([pair[0], pair[1], d2])

        if self.debug:
          print(f'Shape distance: {d2}')

    return seg_img_pair_list

  # ============================== get_movement ==============================
  #
  # @brief  For each pair, get the movement (x,y,rotation)
  #
  # @param[in]   seg_img_pair_list  A list of matched puzzle-template pairs and its corresponding distance.
  #                                 It is based on the Hu moments alforithm.
  # @param[out]  movement_list      A list of movements (x,y,rotation)
  #
  #
  def get_movement(self, seg_img_pair_list):

    movement_list = []

    for pair in seg_img_pair_list:
      # Currently, we randomly pick up one as the template and the other one as the puzzle piece
      dict_template = detector_puzzle.eig_getter(pair[0])
      dict_puzzle = detector_puzzle.eig_getter(pair[1])


      # @todo
      scale = 10
      # Plot the Main axis of the puzzle piece
      plt.plot(dict_puzzle['v1'][0] * np.array([-scale, scale] * 4),
               dict_puzzle['v1'][1] * np.array([-scale, scale] * 4), color='red')
      # Minor axis
      plt.plot(dict_puzzle['v2'][0] * np.array([-scale, scale]),
               dict_puzzle['v2'][1] * np.array([-scale, scale]), color='blue')

      plt.plot(dict_puzzle['x'], dict_puzzle['y'], 'r.')
      plt.plot(dict_template['x'], dict_template['y'], 'g.')


      # The obtained rotation angle
      theta_puzzle = np.arctan2(dict_puzzle['v1'][1], dict_puzzle['v1'][0])
      theta_template = np.arctan2(dict_template['v1'][1], dict_template['v1'][0])
      theta = theta_template - theta_puzzle

      if self.debug:
        print('Puzzle', theta_puzzle)
        print('Template', theta_template)
        print('Theta diff', theta)

      # Case 1:
      coords = np.vstack([dict_puzzle['x'], dict_puzzle['y']])
      # transform_coords 2 * N
      transform_coords = np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]]) @ coords
      # make the two lists
      template_coords = np.hstack(
        (np.array(dict_template['x']).reshape(-1, 1), np.array(dict_template['y']).reshape(-1, 1)))
      dists = cdist(transform_coords.reshape(-1, 2),template_coords, 'euclidean')
      adds_1 = np.sum(np.min(dists,axis=1))/transform_coords.shape[1]
      if self.debug:
        print('ADDS:', adds_1)

      # Case 2:
      rotation_mat_new = np.array([[np.cos(np.pi), -np.sin(np.pi)],
                                   [np.sin(np.pi), np.cos(np.pi)]])
      transformed_coords_new = rotation_mat_new @ transform_coords
      dists = cdist(transformed_coords_new.reshape(-1, 2), template_coords, 'euclidean')
      adds_2 = np.sum(np.min(dists,axis=1))/transformed_coords_new.shape[1]
      if self.debug:
        print('ADDS with another half circle', adds_2)

      if adds_2 < adds_1:

        plt.plot(transformed_coords_new[0, :], transformed_coords_new[1, :], 'b.')
        angle = (np.pi - theta) % (2*np.pi)
      else:
        plt.plot(transform_coords[0, :], transform_coords[1, :], 'b.')
        angle = -theta

      print(f'Angle to be rotated counter-clockwise by {angle} rad')

      center_puzzle = np.mean(np.nonzero(pair[0]), axis=1)[::-1]
      center_template = np.mean(np.nonzero(pair[1]), axis=1)[::-1]
      movement = center_template - center_puzzle
      print(f'Center to be moved by {movement}')

      movement_list.append([movement,angle])


      plt.axis('equal')
      plt.gca().invert_yaxis()  # Match the image system with origin at top left
      plt.show()

    return movement_list

  # ============================== eig_getter ==============================
  #
  # @brief  To find the major and minor axes of a blob.
  #         See https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/ for details.
  #
  # @param[in]   img       A mask image
  # @param[out]  dict      A dict saving centerized points, main vectors
  #
  @staticmethod
  def eig_getter(img):
    y, x = np.nonzero(img)
    x = x - np.mean(x)
    y = y - np.mean(y)
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

    return dict

#
# =========================== detector_puzzle ============================
