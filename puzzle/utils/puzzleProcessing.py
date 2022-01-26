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

from puzzle.builder.arrangement import Arrangement, ParamPuzzle
from puzzle.builder.board import Board
from puzzle.utils.imageProcessing import preprocess_real_puzzle
from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.parser.fromSketch import FromSketch
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]


# ====================== puzzle.utils.puzzleProcessing ======================


def calibrate_real_puzzle(img_folder, option, fsize=1, verbose=False):
    """
    @brief  To obtain the solution board from an image sequence for calibration.

    Args:
        img_folder: The path to the image folder. We assume the image name like XX_0.png
        option: The option 0 is to assemble the puzzle while option 1 is to disassemble the puzzle
        fsize: The scale to resize the input image.
        verbose: Whether to debug

    Returns:
        theCalibrated(A board of calibrated pieces)
    """

    img_path_list = glob.glob(os.path.join(cpath + '/../testing/' + img_folder, '*.png'))
    img_path_list.sort()

    theCalibrated = Board()

    improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_RGB2GRAY,),
                               improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),),
                               cv2.erode, (np.ones((3, 3), np.uint8),),
                               cv2.dilate, (np.ones((3, 3), np.uint8),)
                               )

    for i in range(1, len(img_path_list)):

        # if i==6:
        #     verbose=True

        if i == 1:
            thePrevImage = cv2.imread(img_path_list[i - 1])

            if fsize != 1:
                thePrevImage = cv2.resize(thePrevImage, (0, 0), fx=fsize, fy=fsize)

            thePrevImage = cv2.cvtColor(thePrevImage, cv2.COLOR_BGR2RGB)
            thePrevMask = preprocess_real_puzzle(thePrevImage, verbose=False)
            thePrevImage = cv2.bitwise_and(thePrevImage, thePrevImage, mask=thePrevMask)
        else:
            thePrevImage = theCurImage

        # Step 1: preprocess real imgs
        theCurImage = cv2.imread(img_path_list[i])

        if fsize !=1:
            theCurImage = cv2.resize(theCurImage, (0,0), fx=fsize, fy=fsize)

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
        theBoard_single = Arrangement.buildFrom_ImageAndMask(canvas, theMaskMea,
                                                             theParams=ParamPuzzle(areaThresholdLower=1000))

        theCalibrated.addPiece(theBoard_single.pieces[0])

    return theCalibrated

def create_synthetic_puzzle(theImageSol, theMaskSol_src, explodeDis=(200,200), moveDis=(2000,100), rotateRange=70, ROTATION_ENABLED=True,verbose=False):
    """
    @brief create a synthetic/exploded/rotated measured board & solution board from a foreground image & background image.

    Args:
        theImageSol: The source RGB image.
        theMaskSol_src: The source template image.
        explodeDis: The exploded distance setting, (xx,yy).
        moveDis: The moved distance setting, (xx,yy).
        rotateRange: The range of the rotation.
        ROTATION_ENABLED: The flag signifying rotation option.
        verbose: The flag signifying debug or not.

    Returns:
        theGridMea: The measured board.
        theGridSol: The solution board.
    """

    theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)
    theImageSol = cropImage(theImageSol, theMaskSol_src)

    # Create an improcessor to obtain the mask.
    improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                               cv2.GaussianBlur, ((3, 3), 3,),
                               cv2.Canny, (30, 200,),
                               improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

    theDet = FromSketch(improc)
    theDet.process(theMaskSol_src.copy())
    theMaskSol = theDet.getState().x

    # Create a Grid instance and explode it into a new board
    print('Running through test cases. Will take a bit.')

    theGridSol = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                                theParams=ParamGrid(areaThresholdLower=4000, areaThresholdUpper=200000,reorder=True))
    if verbose:
        cv2.imshow('theGridSol', theGridSol.toImage(ID_DISPLAY=True))
        cv2.waitKey()

    # Create a new Grid instance from the images
    _, epBoard = theGridSol.explodedPuzzle(dx=explodeDis[0], dy=explodeDis[1])

    # Randomly swap the puzzle pieces.
    _, epBoard, gt_pAssignments = epBoard.swapPuzzle()

    # Put measured pieces at the right side of the image
    for i in range(epBoard.size()):
        epBoard.pieces[i].setPlacement(r=np.array([moveDis[0], moveDis[1]]), offset=True)

    # Randomly rotate the puzzle pieces.
    if ROTATION_ENABLED:
        gt_rotation = []
        for key in epBoard.pieces:
            gt_rotation.append(np.random.randint(0, rotateRange))
            epBoard.pieces[key] = epBoard.pieces[key].rotatePiece(gt_rotation[-1])

    epImage = epBoard.toImage(CONTOUR_DISPLAY=False, BOUNDING_BOX=False)
    if verbose:
        cv2.imshow('movedPuzzle', cv2.resize(epImage,(0,0),fx=0.3,fy=0.3))
        cv2.waitKey()

    # Create a new Grid instance from the images

    # Todo: Need updates, from color may have some problems
    improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                               improcessor.basic.thresh, ((5, 255, cv2.THRESH_BINARY),),
                               cv2.dilate, (np.ones((3, 3), np.uint8),)
                               )
    theMaskMea = improc.apply(epImage)
    if verbose:
        cv2.imshow('processedMask', cv2.resize(theMaskMea,(0,0),fx=0.3,fy=0.3))
        cv2.waitKey()

    theGridMea = Gridded.buildFrom_ImageAndMask(epImage, theMaskMea,
                                                theParams=ParamGrid(areaThresholdLower=1000, reorder=True))
    print('Extracted pieces:', theGridMea.size())

    return theGridMea, theGridSol, gt_pAssignments
#
# ====================== puzzle.utils.puzzleProcessing ======================
