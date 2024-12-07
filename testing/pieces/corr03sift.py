#!/usr/bin/python3
#================================== corr03sift =================================
## @file
# @brief    Test the SIFT data association for various puzzle configurations.
#
# Loads the desired puzzle and applies process according to arguments to create a
# puzzle.  The exploded and shuffled puzzle pieces are then matched against the
# original extracted puzzle with an attempt to recreate the puzzle proper.
# If all went well, the puzzle should have been reconstituted.
#
#  Use the ``--help`` flag to see what the options are.  Sending no option swill
#  default to a 48 piece fish puzzle.
#
# @ingroup TestCluster
#
# @author   Devesh Nath
# @author   Patricio A. Vela,   pvela@gatech.edu
# @date     2024/12/06  [created]
#
# @quitf
#
#================================== corr03sift =================================


#==[0] Prep environment
import os
from copy import deepcopy
import random 

import matplotlib.pyplot as plt

from puzzle.clusters.byColor import ByColor, ParamColorCluster

import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import random

import ivapy.display_cv as display
from distutils.util import strtobool 

import improcessor.basic as improcessor
from puzzle.builder.gridded import Gridded, CfgGridded
from puzzle.parse.fromSketch import FromSketch
from puzzle.utils.imageProcessing import cropImage
import puzzle.board as board

import argparse
import pkg_resources


fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

argparser = argparse.ArgumentParser()
argparser.add_argument('--image', type=str, default='fish', choices=['duck', 'earth', 'balloon', 'elsa1', 'elsa2', 'rapunzel', 'dinos', 'fish'],
                       help='The image to be used for the puzzle.')
argparser.add_argument('--mask', type=int, default=48, choices=[15, 35, 48, 60],
                       help = 'The number of pieces in the puzzle.')
argparser.add_argument('--with_cluster', action='store_true',
                       help='Whether to use the cluster algorithm to separate the pieces.')
argparser.add_argument('--cluster_mode', type=str, default='number', choices=['number', 'threshold'],
                       help='The mode of the cluster algorithm.')
argparser.add_argument('--cluster_number', type=int, default=4,
                       help='The number of clusters to be used.')
argparser.add_argument('--cluster_threshold', type=float, default=0.5,
                       help='The threshold of the cluster algorithm.')
argparser.add_argument('--forceMatches', type=strtobool, default='True', 
                       choices=[True, False],
                       help='Chooses whether to force matches or not.')

opt = argparser.parse_args()

img_dict = {
    'duck': 'duck.jpg',
    'balloon': 'balloon.png',
    'elsa1': 'FrozenII_Elsa_1.jpg',
    'elsa2': 'FrozenII_Elsa_2.jpg',
    'rapunzel': 'Rapunzel.jpg',
    'dinos': 'Amazon_Dinos_2.jpg',
    'fish': 'fish.jpg',
}

mask_dict = {
    15: 'puzzle_15p_123rf.png',
    35: 'puzzle_35p.png',
    48: 'puzzle_48p.jpg',
    60: 'puzzle_60p_AdSt408534841.png'
}

#==[1] Read the source image and template.
#

prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImageSol = cv2.imread(prefix + img_dict[opt.image])
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(prefix + mask_dict[opt.mask])
theImageSol = cropImage(theImageSol, theMaskSol_src)

#==[2] Create an improcessor to obtain the mask from which to obtain a
#       puzzle solution.  Display the puzzle solution with ID overlay.
#
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((150, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

cfgGrid = CfgGridded()
cfgGrid.tauGrid = 5000
cfgGrid.reorder = False

theGridSol = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, cfgGrid)


#==[3] Explode then shuffle the board to create a new board image "measurement."
#        Process the image to get the measured board.
epImage, theGridExp = theGridSol.explodedPuzzle(dx=200, dy=200) # Explode

idMap   = theGridExp.shuffle(reorient=True, rotRange=[40, 40])
shImage = theGridExp.toImage(CONTOUR_DISPLAY=False, BOUNDING_BOX=False)

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))
theDet = FromSketch(improc)
theDet.process(shImage)
shMask = theDet.getState().x

theGridMea = Gridded.buildFrom_ImageAndMask(shImage, shMask, cfgGrid)

#DEBUG VISUAL
#theGridMea.display_mp(ID_DISPLAY=True) 

#==[3] Correspondences

CfgTrack   = board.CfgCorrespondences()
CfgTrack.matcher = 'SIFTCV'  
CfgTrack.matchParams = None
CfgTrack.forceMatches = opt.forceMatches
theTracker = board.Correspondences(CfgTrack, theGridSol)

theTracker.process(theGridMea)

#DEBUG VISUAL
#theGridMea.display_mp(ID_DISPLAY=True)

theGridMea.pshape = theGridSol.pshape
theGridMea.retile(300,300)
#theGridMea.display_mp(ID_DISPLAY=True)

theTracker.matcher.solveMatchedPuzzle(theGridMea, theGridSol)

#for pi in range(0,theGridMea.size()):
#  cout = theTracker.matcher.compare(theGridMea.pieces[pi], theGridSol.pieces[pi])
#  #print([theGridMea.pieces[pi].theta, theGridSol.pieces[pi].theta])
#  thetaDiff = theGridSol.pieces[pi].theta - theGridMea.pieces[pi].theta
#  rotPiece = theGridMea.pieces[pi].rotatePiece(0)#thetaDiff))
#  rotPiece.id = theGridMea.pieces[pi].id
#  solvePuzzle.addPiece(rotPiece)
#  #print(cout)

# DEBUG VISUAL 
theGridSol.display_mp(ID_DISPLAY=True)  # Display the original board 
theGridMea.display_mp(ID_DISPLAY=True)
plt.show()

#
#================================== corr03sift =================================
