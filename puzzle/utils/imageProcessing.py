# ====================== puzzle.utils.imageProcessing ======================
#
# @brief    Some image processing functions.
#
# ====================== puzzle.utils.imageProcessing ======================
#
# @file     imageProcessing.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/01 [created]
#
#
# ====================== puzzle.utils.shapeProcessing ======================


# ============================== Dependencies =============================

import math
import numpy as np

import cv2

import improcessor.basic as improcessor
from puzzle.utils.shapeProcessing import bb_intersection_over_union
# ====================== puzzle.utils.imageProcessing ======================

def cropImage(image, template):
    """
    @brief  Crop and resize a cover image, which has the same shape with the mask.

    Args:
        image: The source image.
        template: The mask image.

    Returns:
        The resized image.
    """

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


def rotate_im(image, angle, mask=None):
    """
    @brief Compute the rotated image. See https://stackoverflow.com/a/47290920/5269146.

    Args:
        image: The input image.
        angle: The rotated angle.

    Returns:
        The rotated image (cropped) & The rotated image (not cropped) & the rotation matrix & padding_left & padding_top.
    """

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

    # boundingRect is meant to work on a black and white image
    if mask is not None:
        x, y, w, h = cv2.boundingRect(mask)
    else:
        x, y, w, h = cv2.boundingRect(rotated_image)

    # print(x, y, w, h)
    # cv2.imshow('rotate', rotated_image)
    # cv2.imshow('src', image)

    final_image = rotated_image[y:y + h, x:x + w]

    # Maybe this step is redundant
    final_image = cv2.copyMakeBorder(final_image,
                                     top=2,
                                     bottom=2,
                                     left=2,
                                     right=2,
                                     borderType=cv2.BORDER_CONSTANT,
                                     value=0
                                     )
    # cv2.imshow('dst', final_image)
    # cv2.waitKey()
    return final_image, rotated_image, transform_matrix, (padding_left, - x, 2), (padding_top, -y, 2)


def preprocess_real_puzzle(img, areaThresh = 1000):
    """
    @brief Preprocess the RGB image of a segmented puzzle piece in a circle area to obtain a mask.

    Args:
        img: RGB image input.
        areaThresh: The lower threshold of the area.

    Returns:
        The mask.
    """

    improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                               cv2.medianBlur, (5,),
                               cv2.Canny, (30, 200,),
                               improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

    imout = improc.apply(img)

    # cv2.imshow('debug',imout)
    # cv2.waitKey()

    cnts, hierarchy = cv2.findContours(imout, cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)

    # hierarchy = hierarchy[0]

    regions = []

    # Filter out some contours according to area threshold & circle area
    for c in cnts:

        area = cv2.contourArea(c)

        # Filtered by the area threshold
        if area > areaThresh:

            seg_img = np.zeros(imout.shape[:2], dtype="uint8")  # reset a blank image every time
            cv2.drawContours(seg_img, [c], -1, (255, 255, 255), thickness=-1)

            circles = cv2.HoughCircles(seg_img, cv2.HOUGH_GRADIENT, 1.2, 100)

            if circles is None:
                regions.append([seg_img, area])

    regions.sort(key=lambda x: x[1])

    return regions[0][0]

#
# ====================== puzzle.utils.imageProcessing ======================
