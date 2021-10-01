#!/usr/bin/python3
# ============================ rotate_regular ===========================
#
# @brief    Test script for the rotation function of the puzzle piece.
#           (60p img)
#
# ============================ rotate_regular ===========================

#
# @file     rotate_regular.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/30  [created]
#
# ============================ rotate_regular ===========================


import os

import cv2
import improcessor.basic as improcessor
# ==[0] Prep environment
import matplotlib.pyplot as plt

from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.parser.fromSketch import fromSketch
from puzzle.piece.regular import regular
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_60p_AdSt408534841.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcesser to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[1.2] Extract info from theImage & theMask to obtain a board instance.
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000))

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[1.3] Focus on a single puzzle piece.
#

thePiece_A = theBoardSol.pieces[36]

# ==[1.4] Rotate the puzzle piece.
#

theRotate = thePiece_A.rotatePiece(65)

theRegular = regular(theRotate)

# ==[2] Display the puzzle piece and the extracted info.
#
print('Should see [2,1,2,2], which means LEFT: OUT, RIGHT: IN, TOP: OUT, BOTTOM: OUT')
theRegular.displayEdgeType()

theImage = theRegular.toImage()

f, axarr = plt.subplots(1, 2)

axarr[0].imshow(theImage)
axarr[0].title.set_text('The segmented puzzle piece')

axarr[1].imshow(theRegular.class_image, cmap='rainbow')
axarr[1].title.set_text('The segmented 4 edges')

print(f'The corrected rotation angle: {int(theRegular.theta)} degree')

plt.show()

#
# ============================ rotate_regular ===========================
