#!/usr/bin/python3
#============================ matrix01perturb ============================
##
# @brief    Tests construction of a puzzle piece from a shifted version of 
#           image patch as obtained from the source image.
#
# Loads the desired puzzle (from set of puzzles) and applies process according to
# arguments to create a puzzle.  A piece is chosen and a perturbed location is used
# to snag a new puzzle template. 
#
#  Use the ``--help`` flag to see what the options are.  Sending no option swill
#  default to a 8x6 = 48 piece puzzle with a fish puzzle image.
#
# @ingroup TestBuilder
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2024/01/11 [created]
#
# @quitf
#
#============================ matrix01perturb ============================

#==[0] Prep environment.
#
import argparse
import pkg_resources
import os
import numpy as np

import cv2

import ivapy.display_cv as display
import puzzle.builder.matrix as pzzl

img_dict = {
    'duck': 'duck.jpg',
    'earth': 'earth.jpg',
    'balloon': 'balloon.png',
    'elsa1': 'FrozenII_Elsa_1.jpg',
    'elsa2': 'FrozenII_Elsa_2.jpg',
    'rapunzel': 'Rapunzel.jpg',
    'dinos': 'Amazon_Dinos_2.jpg',
    'fish': 'fish.jpg',
    'gradient' : 'Buhah_GradientPuzzle.jpg'
}

psize_dict = {15: [5,3], 35: [7,5], 48: [8,6], 60: [10,6], 100: [10,10]}
isize_dict = {15: [500,300], 35: [700,500], 48: [800,600], 60: [800,800]}


#==[1] Parse command line arguments or set to default specs if none.
#
fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

argparser = argparse.ArgumentParser()
argparser.add_argument('--image', type=str, default='fish', choices=list(img_dict.keys()),
                       help='The image to be used for the puzzle.')
argparser.add_argument('--size', type=int, default=48, choices=list(psize_dict.keys()),
                       help = 'Number of pieces in the puzzle. Implicitly its shape too.')

opt = argparser.parse_args()

#==[2] Read the source image.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImage = cv2.imread(prefix + img_dict[opt.image])
theImage = cv2.cvtColor(theImage, cv2.COLOR_BGR2RGB)
theImage = np.array(theImage)

#==[3] Generate the Matrix puzzle specifications.
#
specPuzzle = pzzl.CfgMatrix()
specPuzzle.psize = psize_dict[opt.size]
specPuzzle.isize = isize_dict[opt.size]
specPuzzle.lengthThresholdLower = 0

(thePuzzle, srcImage) = pzzl.Matrix.buildFrom_ImageAndSpecs(theImage, specPuzzle)

shiftPiece = thePuzzle.pieces[20].replaceSourceData(srcImage, np.array([10, 10]))
thePuzzle.pieces[20] = shiftPiece

thePuzzle.display_cv()
display.wait()

#
#============================ matrix01perturb ============================
