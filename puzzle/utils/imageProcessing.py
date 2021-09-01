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
#====================== puzzle.utils.imageProcessing ======================


# ================================ bb_intersection_over_union ==============================
#
# @brief  Crop and resize a cover image, which has the same shape with the mask.
#
# @param[in]  image   The source image.
# @param[in]  template   The mask image.
#
# @param[out] dst    The resized image.
#
def cropImage(image, template):

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


#
#====================== puzzle.utils.imageProcessing ======================