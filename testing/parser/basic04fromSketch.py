#!/usr/bin/python3
#============================= basic04_fromSketch ============================
## @file
# @brief    Code to test out the simple image detector for a fairly
#           contrived scenario: threshold a grayscale image.
#
# The fromSketch python file is incomplete.  This is not a functional test.
#
# Upgrades earlier test scripts to use a depth image plus upper and lower
# depth limits to establish a detection depth zone. The "depth image" here
# is simply fictitious data placed into an array (same as fake data in
# earlier test scripts).
#
# @ingroup TestPuzzleParser
# @quitf
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/10  [created]
#
#============================= basic04_fromSketch ============================

#==[0] Prep the environment. From most basic to current implementation.
#
import os
import cv2
import numpy as np
import argparse
import pkg_resources

import improcessor.basic as improcessor
import ivapy.display_cv as display

from puzzle.parse.fromSketch import FromSketch

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

theImage = cv2.imread(prefix + img_dict[opt.image])
theImage = cv2.cvtColor(theImage, cv2.COLOR_BGR2RGB)

#==[2] Instantiate inImage detector with an image processor that does
#      the thresholding.
#
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                 improcessor.basic.thresh, ((150, 255, cv2.THRESH_BINARY),))
theDet = FromSketch(improc)

# Why is this approach taken and not one based on region labels?
# Seems really weird. Region props gives the full pixel listing of the regions.
# Ignoring for now, but may need to revisit.

#==[3] Apply and visualize.
#
theDet.process(theImage, theMask)

#==[4] Visualize the output
#
print("Creating window: should see a processed mask.")
display.rgb(theImage,window_name='Input')
display.binary(theDet.getState().x, window_name='Output')
display.wait()

#
#============================= basic04_fromSketch ============================
