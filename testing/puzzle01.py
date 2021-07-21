#=============================== puzzle01 ==============================
#
# @brief    Code to create
#
#
#=============================== puzzle01 ==============================

#
# @file     puzzle01.py
#
# @author   Yunzhi Lin,         yunzhi.lin@gatech.edu
# @date     2021/07/20 [created]

#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
# @quit
#=============================== trackTri01 ==============================


#==[0] Prep environment.
#
import operator
import numpy as np

import Lie.group.SE2.Homog
import improcessor.basic as improcessor
import detector.inImage as detector

import cv2
import os

import itertools
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist


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
    'x':x,
    'y':y,
    'v1': v1,
    'v2': v2,
  }

  return dict

#==[1] Build up a puzzle solver

#--[1.1] Create the detector instance.

#--[1.2] Package up into a perceiver.


#==[2] Apply puzzle solver to simple image.

#--[2.1] Read a binary image

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# White represents the template and puzzle piece masks
# src_img = cv2.imread(cpath + '/data/image_1.jpg',0)
src_img = cv2.imread(cpath + '/data/image_2.png',0)
_, mask = cv2.threshold(src_img,127,255,cv2.THRESH_BINARY_INV)





# src_img = np.zeros((100,100),dtype='uint8')
# # Create two boxes, 20*10
# src_img[5:25, 5:15] = 255
# src_img[70:80, 60:80] = 255
# mask = src_img

plt.imshow(mask)
plt.show()

#--[2.2] Apply to simple image


# For details of options, see https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga819779b9857cc2f8601e6526a3a5bc71
# and https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga4303f45752694956374734a03c54d5ff
cnts =  cv2.findContours(mask.copy(), cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)
# For OpenCV 4+
cnts = cnts[0]

# areaThreshold for contours
areaThreshold = 100

desired_cnts = []

# Filter out some contours according to length threshold
for c in cnts:
  # Draw the contour and show it
  cv2.drawContours(mask, [c], -1, (0, 255, 0), 2)
  area = cv2.contourArea(c)
  if area > areaThreshold:
    # c is N x 1 x 2
    x, y = np.sum(np.array(c).reshape(-1,2),axis=0)
    mean_x = int(x/c.shape[0])
    mean_y = int(y/c.shape[0])

    desired_cnts.append(c)

    print(f'center: {mean_x},{mean_y}')
print('size of desired_cnts is', len(desired_cnts))

seg_img_list = []
# Get the individual part
for c in desired_cnts:
  seg_img = np.zeros(mask.shape[:2], dtype="uint8") # reset a blank image every time
  cv2.polylines(seg_img, [c], True, (255,255,255), thickness = 3)
  seg_img_list.append(seg_img)

  cv2.imshow("Image_Redrawn", seg_img)
  cv2.waitKey(0)

# Get the matched pairs
seg_img_pair_list = []
for pair in itertools.combinations(seg_img_list,2):
  d2 = cv2.matchShapes(pair[0],pair[1],cv2.CONTOURS_MATCH_I2,0)
  if d2 < 0.05:
    seg_img_pair_list.append([pair[0],pair[1],d2])
    print(f'Shape distance: {d2}')

# threshold variable
threshold = 0.5

for pair in seg_img_pair_list:
  # We assume that the template is on the right while the puzzle piece is on the left
  dict_template = eig_getter(pair[1])
  dict_puzzle = eig_getter(pair[0])

  scale = 10
  # Plot the Main axis of the puzzle piece
  plt.plot(dict_puzzle['v1'][0]*np.array([-scale,scale]*4),
           dict_puzzle['v1'][1]*np.array([-scale,scale]*4), color='red')
  # Minor axis
  plt.plot(dict_puzzle['v2'][0] * np.array([-scale,scale]),
           dict_puzzle['v2'][1] * np.array([-scale,scale]), color='blue')

  plt.plot(dict_puzzle['x'], dict_puzzle['y'], 'r.')
  plt.plot(dict_template['x'], dict_template['y'], 'g.')

  plt.axis('equal')
  plt.gca().invert_yaxis()  # Match the image system with origin at top left

  theta_puzzle = np.arctan2(dict_puzzle['v1'][1], dict_puzzle['v1'][0])
  theta_template = np.arctan2(dict_template['v1'][1], dict_template['v1'][0])
  print('Puzzle', theta_puzzle)
  print('Template', theta_template)
  theta = theta_template - theta_puzzle
  print('Theta diff', theta)

  # Case 1:
  rotation_mat = np.matrix([[np.cos(theta), -np.sin(theta)],
                            [np.sin(theta), np.cos(theta)]])
  coords = np.vstack([dict_puzzle['x'], dict_puzzle['y']])
  transformed_mat = rotation_mat * coords
  # plot the transformed blob
  x_transformed, y_transformed = transformed_mat.A
  # make the two lists
  template_coords = np.hstack((np.array(dict_template['x']).reshape(-1, 1), np.array(dict_template['y']).reshape(-1, 1)))
  transform_coords = np.hstack((np.array(x_transformed).reshape(-1, 1), np.array(y_transformed).reshape(-1, 1)))
  # compare the two lists pairwise
  dists = cdist(template_coords, transform_coords, 'euclidean')
  idx1 = np.count_nonzero(dists < threshold)
  print('Found number of matching points', idx1)

  # Case 2:
  rotation_mat_new = np.matrix([[np.cos(np.pi), -np.sin(np.pi)],
                                [np.sin(np.pi), np.cos(np.pi)]])
  transformed_mat_new = rotation_mat_new * transformed_mat
  x_transformed_new, y_transformed_new = transformed_mat_new.A
  # number of matching points for inverted (180 degrees) case
  transformed_coords = np.hstack(
    (np.array(x_transformed_new).reshape(-1, 1), np.array(y_transformed_new).reshape(-1, 1)))
  # compare the two lists pairwise
  dists = cdist(template_coords, transformed_coords, 'euclidean')
  idx2 = np.count_nonzero(dists < threshold)
  print('Found number of matching points in 180 case', idx2)

  # if idx2> idx1, the inverted case is correct
  if idx2 > idx1:
    plt.plot(x_transformed_new, y_transformed_new, 'b.')
    angle = (np.pi - theta) % np.pi
  # else stick with the normal case.
  else:
    plt.plot(x_transformed, y_transformed, 'b.')
    angle = -theta

  print(f'Angle to be rotated counter-clockwise by motor 5 is {angle} rad')


  center_puzzle = np.mean(np.nonzero(pair[0]),axis=1)[::-1]
  center_template = np.mean(np.nonzero(pair[1]), axis=1)[::-1]
  movement = center_template - center_puzzle
  print(f'Center to be moved by {movement}')
  plt.show()

#--[2.3] Visualize the output.




#
#=============================== puzzle01 ==============================