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

import cv2
import improcessor.basic as improcessor
import numpy as np

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
    (clockwise)

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

    transform_matrix_full = np.eye(3)
    transform_matrix_full[:2, :] = transform_matrix
    rLoc_relative = transform_matrix_full @ np.array([padding_left, padding_top, 1]).reshape(-1, 1)
    rLoc_relative = rLoc_relative.flatten()[:2]

    # boundingRect is meant to work on a black and white image
    if mask is not None:
        x, y, w, h = cv2.boundingRect(mask)
    else:
        x, y, w, h = cv2.boundingRect(rotated_image)

    rLoc_relative = rLoc_relative - np.array([x, y])

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

    rLoc_relative = rLoc_relative + np.array([2, 2])

    # cv2.imshow('dst', final_image)
    # cv2.waitKey()

    # return final_image, rotated_image, transform_matrix, (padding_left, - x, 2), (padding_top, -y, 2)

    return final_image, rotated_image, transform_matrix, (padding_left, - x, 2), (padding_top, -y, 2), rLoc_relative


def white_balance(img):
    """

    Args:
        img: Input image.

    Returns:
        Processed image with white balance.
    """
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result


def preprocess_real_puzzle(img, mask=None, areaThresh=1000, verbose=False):
    """
    @brief Preprocess the RGB image of a segmented puzzle piece in a circle area to obtain a mask.

    Args:
        img: RGB image input.
        mask: Mask image input.
        areaThresh: The lower threshold of the area.

    Returns:
        The mask region list.
    """

    # Manually add a bounding box on the edges,
    # otherwise, the region connected to the border will be removed
    img_black_border = np.zeros_like(img, 'uint8')
    img_black_border[2:-2,2:-2,:] = img[2:-2,2:-2,:]

    if verbose:
        cv2.imshow('img_black_border', img_black_border)
        cv2.waitKey()

    if mask is None:

        # Manually threshold the img if mask is not given. It should not be better than the one
        # obtained by the surveillance system.
        improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                                   cv2.medianBlur, (5,),
                                   improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),),
                                   cv2.dilate, (np.ones((5, 5), np.uint8),)
                                   )
        mask = improc.apply(img_black_border)

        if verbose:
            cv2.imshow('mask', mask)
            cv2.waitKey()

    improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                               # cv2.medianBlur, (5,),
                               cv2.Canny, (30, 50, None, 3, True,),
                               # cv2.Canny, (30, 200,),
                               improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

    # Step 1: with threshold
    im_pre_canny = improc.apply(img_black_border)

    if verbose:
        cv2.imshow('im_pre_canny+thresh', im_pre_canny)
        cv2.waitKey()

    # # Cannot use connectedComponents assumption
    num_labels, labels = cv2.connectedComponents(mask)

    # desired_cnts = findCorrectedContours(mask)

    regions = []  # The mask region list.
    for i in range(1, num_labels):

        # if i == 1:
        #     verbose = True
        # else:
        #     verbose = False

        im_pre_connected = cv2.bitwise_and(im_pre_canny, im_pre_canny,
                                           mask=np.where(labels == i, 1, 0).astype('uint8'))

        if verbose:
            cv2.imshow('im_pre_connected', im_pre_connected)
            cv2.waitKey()

        # 3 will lead to better split while 5 is with fewer holes
        kernel = np.ones((3, 3), np.uint8)
        im_pre_dilate = cv2.dilate(im_pre_connected, kernel)

        if verbose:
            cv2.imshow('im_pre_dilate', im_pre_dilate)
            cv2.waitKey()

        cnts, hierarchy = cv2.findContours(im_pre_dilate, cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

        # Filter out the outermost contours
        regions_single = []
        for c in cnts:

            area = cv2.contourArea(c)

            seg_img = np.zeros(img.shape[:2], dtype="uint8")  # reset a blank image every time
            cv2.drawContours(seg_img, [c], -1, (255, 255, 255), thickness=-1)

            # Get ROI, OpenCV style
            x, y, w, h = cv2.boundingRect(c)

            # Double check if ROI has a large IoU with the previous ones
            skipflag = False
            for region in regions_single:
                if bb_intersection_over_union(region[2], [x, y, x + w, y + h]) > 0.85:
                    skipflag = True
                    break
            if not skipflag:
                regions_single.append((seg_img, area, [x, y, x + w, y + h]))

        regions_single.sort(key=lambda x: x[1])

        # if verbose:
        #     for i in range(len(regions_single)):
        #         cv2.imshow('regions_single',regions_single[i][0])
        #         cv2.waitKey()

        # Step 2: Remove the outermost contour
        seg_img_combined = np.zeros(img.shape[:2], dtype="uint8")  # reset a blank image every time
        for i in range(len(regions_single) - 1):
            seg_img_combined = seg_img_combined | regions_single[i][0]

        if verbose:
            cv2.imshow('seg_img_combined', seg_img_combined)
            cv2.waitKey()

        # Step 3: Dilation
        kernel = np.ones((3, 3), np.uint8)
        im_processed = cv2.dilate(seg_img_combined, kernel)

        # Alternative, not to use dilation
        # im_processed = seg_img_combined

        if verbose:
            cv2.imshow('im_processed_dilation', im_processed)
            cv2.waitKey()

        # Step 4: Floodfill

        # Copy the thresholded image.
        im_floodfill = im_processed.copy()

        # Mask used to flood filling.
        # Notice the size needs to be 2 pixels than the image.
        h, w = im_processed.shape[:2]
        mask = np.zeros((h + 2, w + 2), np.uint8)

        # Floodfill from point (0, 0)
        cv2.floodFill(im_floodfill, mask, (0, 0), 255)

        # Invert floodfilled image
        im_floodfill_inv = cv2.bitwise_not(im_floodfill)

        # Step3: Combine the two images to get the foreground.
        im_floodfill = im_processed | im_floodfill_inv

        if verbose:
            cv2.imshow('im_floodfill', im_floodfill)
            cv2.waitKey()

        regions.append(im_floodfill)

    seg_img_combined = np.zeros(img.shape[:2], dtype="uint8")  # reset a blank image every time
    for i in range(len(regions)):
        seg_img_combined = seg_img_combined | regions[i]

    return seg_img_combined


def find_nonzero_mask(mask):
    """
    @brief Extract the coordinates of the non-zero elements (x,y style) from a mask image

    Args:
        mask: The input mask image with 0 or 1

    Returns:
        The coordinates of the non-zero elements (x,y style)
    """

    rcoords = list(np.nonzero(mask))  # 2 (row,col) x N
    # Updated to OpenCV style -> (x,y)
    rcoords[0], rcoords[1] = rcoords[1], rcoords[0]
    rcoords = np.array(rcoords)

    return rcoords

#
# ====================== puzzle.utils.imageProcessing ======================
