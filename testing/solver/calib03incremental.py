#!/usr/bin/python3
#============================= calib03incremental ============================
## @file
# @brief    Calibrated puzzle built out incrementally from another puzzle board.
#           but within a larger image.
#
# Shows how to generate a calibrated puzzle piece by incrementally building it up
# piece by piece through image snapshots after each added piece.  
#
# The full Surveillance system would use something like glove shots as the outer
# loop.  When the glove goes out of the field of view an image is taken.  That 
# image then feeds a foreground difference detector that finds the changed
# region and sends it along as a mask (with image) to the board for puzzle piece
# extraction and addition to the board's bag.
#
# A similar approach may be used for assessing puzzle progress (may be incorrect if
# there is not appearance matching with the pieces and just testing of existence
# of a piece).
#
# @ingroup  TestPuzzle_Solver
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#
# @date     2025/02/15  
#
#============================= calib03incremental ============================

#==[0] Prep the environment. From most basic to current implementation.
#
import os
import cv2
import numpy as np
import argparse
import pkg_resources
from skimage.measure import label

import improcessor.basic as improcessor
import ivapy.display_cv as display

import detector.fgmodel.differences as diffs

from puzzle.utils.imageProcessing import cropImage
from puzzle.parse.fromSketch import FromSketch
import puzzle.board as puzzle

argparser = argparse.ArgumentParser()

argparser.add_argument('--image', type=str, default='fish', 
        choices=['duck', 'earth', 'balloon', 'elsa1', 'elsa2', 'rapunzel', 
                 'dinos', 'fish'],
        help='The image to be used for the puzzle.')

argparser.add_argument('--mask', type=int, default=48, 
        choices=[15, 35, 48, 60],
        help = 'The number of pieces in the puzzle.')

opt = argparser.parse_args()

mask_dict = {
    15: 'puzzle_15p_123rf.png',
    35: 'puzzle_35p.png',
    48: 'puzzle_48p.jpg',
    60: 'puzzle_60p_AdSt408534841.png'
}

img_dict = {
    'duck': 'duck.jpg',
    'earth': 'earth.jpg',
    'balloon': 'balloon.png',
    'elsa1': 'FrozenII_Elsa_1.jpg',
    'elsa2': 'FrozenII_Elsa_2.jpg',
    'rapunzel': 'Rapunzel.jpg',
    'dinos': 'Amazon_Dinos_2.jpg',
    'fish': 'fish.jpg',
}

#==[1] Read a sketch image that needs to be processed.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')
theMask  = cv2.imread(prefix + mask_dict[opt.mask])
theMask  = cv2.resize(theMask, (640, 480))

theImage = cv2.imread(prefix + img_dict[opt.image])
theImage = cv2.cvtColor(theImage, cv2.COLOR_BGR2RGB)
theImage = cropImage(theImage, theMask)


#==[2] Instantiate inImage detector with an image processor that does
#      the thresholding.  Use it to create a puzzle board.
#
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                 improcessor.basic.thresh, ((150, 255, cv2.THRESH_BINARY),))
theDet = FromSketch(improc)

theDet.process(theMask)
theLabels = label(theDet.getState().x)

thePuzzle = puzzle.Board()
thePuzzle.fromImageAndLabels(theImage, theLabels)

thePuzzle.offset(np.array([75, 75]))

#==[3] Create the foreground detector that will identify additions
#       to the image over time and flag them.  
#
# @note Right now done as an though only change is an individual piece.  
#       Need to wrap around a multi-centroid tracker to extract multiple, 
#       just in case more get added.  In principle, should be one at a time
#       but not sure if I'll be able to track that outside of calibration
#       implementation.  Progress monitoring will have to use a different
#       approach.  Maybe image differences or puzzle piece similarity.
#
cfgDet = diffs.CfgDifferences()
cfgDet.doAccum= True

chDet = diffs.fgDifferences(cfgDet)

#==[4] Now incrementally build it up in another image and use that with
#       the differences detector to add puzzle pieces.
#

imsize = np.array(np.shape(theImage))
imsize[0] = imsize[0] + 200
imsize[1] = imsize[1] + 200
puzzImage = np.zeros(imsize, dtype=np.uint8)

newPuzzle = puzzle.Board()

chDet.process(puzzImage)
for pk in thePuzzle.pieces:
  kPiece = thePuzzle.pieces[pk]
  kPiece.placeInImage(puzzImage)

  chDet.process(puzzImage)

  newPuzzle.addPieceFromImageAndMask(puzzImage, chDet.fgIm)


newImage = np.zeros(imsize, dtype=np.uint8)
newImage = newPuzzle.toImage(newImage, CONTOUR_DISPLAY=False, BOUNDING_BOX=False)

#==[4] Visualize the output
#
print("Creating window: should see a processed mask.")
display.rgb(theImage,window_name='Input')
display.rgb(newImage, window_name='Output')
display.gray(chDet.labelI.astype(np.uint8), window_name="Label")
display.wait()

#
#============================= calib03incremental ============================
