#====================== puzzle.utils.imageProcessing ======================
#
# @brief    Some image processing functions.
#
#====================== puzzle.utils.imageProcessing ======================

#
# @file     imageProcessing.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/01 [created]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#====================== puzzle.utils.shapeProcessing ======================


#============================== Dependencies =============================

import cv2
import math
#====================== puzzle.utils.imageProcessing ======================

def cropImage(image, template):
  '''
  @brief  Crop and resize a cover image, which has the same shape with the mask.

  :param image: The source image.
  :param template: The mask image.
  :return: The resized image.
  '''

  template_x, template_y = template.shape[1], template.shape[0]
  image_x, image_y = image.shape[1], image.shape[0]

  ratio = template_x / template_y

  if ratio * image_y > image_x:
    # same x
    new_image_y = int(image_x / ratio)
    new_image_x = image_x
    dst = image[int((image_y - new_image_y) / 2):int((image_y - new_image_y) / 2) + new_image_y, :]

  else:
    # same y
    new_image_y = image_y
    new_image_x = int(ratio * image_y)
    dst = image[:, int((image_x - new_image_x) / 2):int((image_x - new_image_x) / 2) + new_image_x]

  dst = cv2.resize(dst, (template_x, template_y))

  return dst

def rotate_im(image, angle):
  '''
  @brief Compute the rotated image. See https://stackoverflow.com/a/47290920/5269146.

  :param image: The input image.
  :param angle: The rotated angle.
  :return: The rotated image & the rotation matrix & padding_left & padding_top.
  '''

  image_height = image.shape[0]
  image_width = image.shape[1]
  diagonal_square = (image_width * image_width) + (
          image_height * image_height
  )
  #
  diagonal = round(math.sqrt(diagonal_square))
  padding_top = round((diagonal - image_height) / 2)
  padding_bottom = round((diagonal - image_height) / 2)
  padding_right = round((diagonal - image_width) / 2)
  padding_left = round((diagonal - image_width) / 2)


  padded_image = cv2.copyMakeBorder(image,
                                    top=padding_top,
                                    bottom=padding_bottom,
                                    left=padding_left,
                                    right=padding_right,
                                    borderType=cv2.BORDER_CONSTANT,
                                    value=0
                                    )
  padded_height = padded_image.shape[0]
  padded_width = padded_image.shape[1]
  transform_matrix = cv2.getRotationMatrix2D(
    (padded_height / 2,
     padded_width / 2),  # center
    angle,  # angle
    1.0)  # scale
  rotated_image = cv2.warpAffine(padded_image,
                                 transform_matrix,
                                 (diagonal, diagonal),
                                 flags=cv2.INTER_NEAREST)

  return rotated_image, transform_matrix, padding_left, padding_top

#
#====================== puzzle.utils.imageProcessing ======================