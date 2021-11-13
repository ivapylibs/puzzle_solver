# ====================== puzzle.utils.puzzleProcessing ======================
#
# @brief    Some processing functions for the puzzle.
#
# ====================== puzzle.utils.puzzleProcessing ======================
#
# @file     imageProcessing.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/11/13 [created]
#
#
# ====================== puzzle.utils.puzzleProcessing ======================


# ============================== Dependencies =============================
import glob
import os

import cv2
import improcessor.basic as improcessor
import numpy as np

from puzzle.builder.arrangement import arrangement, paramPuzzle
from puzzle.builder.board import board
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]


# ====================== puzzle.utils.puzzleProcessing ======================


def calibrate_real_puzzle(img_folder, option, verbose=False):
    """
    @brief  To obtain the solution board from an image sequence for calibration.

    Args:
        img_folder: The path to the image folder. We assume the image name like XX_0.png
        option: The option 0 is to assemble the puzzle while option 1 is to disassemble the puzzle
        verbose: Whether to debug

    Returns:
        theCalibrated(A board of calibrated pieces)
    """

    img_path_list = glob.glob(os.path.join(cpath + '/../testing/' + img_folder, '*.png'))
    img_path_list.sort()

    theCalibrated = board()

    improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_RGB2GRAY,),
                               improcessor.basic.thresh, ((50, 255, cv2.THRESH_BINARY),),
                               )

    for i in range(1, len(img_path_list)):
        if i == 1:
            thePrevImage = cv2.imread(img_path_list[i - 1])
            thePrevImage = cv2.cvtColor(thePrevImage, cv2.COLOR_BGR2RGB)

            thePrevMask = preprocess_real_puzzle(thePrevImage, verbose=False)
            thePrevImage = cv2.bitwise_and(thePrevImage, thePrevImage, mask=thePrevMask)
        else:
            thePrevImage = theCurImage

        # Step 1: preprocess real imgs
        theCurImage = cv2.imread(img_path_list[i])
        theCurImage = cv2.cvtColor(theCurImage, cv2.COLOR_BGR2RGB)

        theCurMask = preprocess_real_puzzle(theCurImage, verbose=False)
        theCurImage = cv2.bitwise_and(theCurImage, theCurImage, mask=theCurMask)

        if verbose:
            cv2.imshow('theCurMask', theCurMask)
            cv2.waitKey()

        # Step 2: frame difference
        diff = cv2.absdiff(theCurImage, thePrevImage)
        mask = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

        th = 30
        imask = mask > th

        canvas = np.ones_like(theCurImage, np.uint8)

        if option == 0:
            canvas[imask] = theCurImage[imask]
        else:
            canvas[imask] = thePrevImage[imask]

        # Step 3: threshold
        theMaskMea = improc.apply(canvas)
        if verbose:
            cv2.imshow('theMaskMea', theMaskMea)
            cv2.waitKey()
        theBoard_single = arrangement.buildFrom_ImageAndMask(canvas, theMaskMea,
                                                             theParams=paramPuzzle(areaThresholdLower=1000))

        theCalibrated.addPiece(theBoard_single.pieces[0])

    return theCalibrated

#
# ====================== puzzle.utils.puzzleProcessing ======================
