#!/usr/bin/python3
#================================== corr01sift =================================
## @file
# @brief    Test the SIFT data association for various puzzle configurations.
#
# Loads the desired puzzle and applies process according to arguments to create a
# puzzle.  The exploded and shuffled puzzle pieces are then matched against the
# original extracted puzzle.  If all went well, the associations should be 
# correct.
#
#  Use the ``--help`` flag to see what the options are.  Sending no option swill
#  default to a 48 piece fish puzzle.
#
# Since the original puzzle shuffle member function did not work, this script
# performs the shuffling process.  The next iteration runs from within the
# shuffle member function.
#
# @ingroup TestCluster
#
# @author   Devesh Nath
# @author   Patricio A. Vela,   pvela@gatech.edu
# @date     2024/12/06  [created]
#
# @quitf
#
#================================== corr01sift =================================


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
    'earth': 'earth.jpg',
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

#==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((150, 255, cv2.THRESH_BINARY),))

#==[1.2] Create Gridded Board
theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

cfgGrid = CfgGridded()
cfgGrid.tauGrid = 5000
cfgGrid.reorder = False

theGridSol = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, cfgGrid)

# DEBUG VISUAL 
theGridSol.display_mp(ID_DISPLAY=True)  # Display the original board 


#==[2] Explode the board, randomize orientations, randomize locations
#       Not using the Gridded.swapPuzzle
epImage, theGridMea = theGridSol.explodedPuzzle(dx=200, dy=200) # Explode

#DEBUG VISUAL
#theGridMea.display_mp(ID_DISPLAY=True) # Exploded Board

keyOrig = list(theGridMea.pieces)
keyShuf = keyOrig.copy()
random.shuffle(keyShuf)

pieceLocations = theGridMea.pieceLocations()
pieceLocations = np.transpose(np.array([value for value in pieceLocations.values()]))
pieceLocations = pieceLocations[:,np.array(keyShuf)]

pieceIDs = np.array([theGridMea.pieces[i].id for i in range(theGridMea.size())])
shuffIDs = pieceIDs[keyShuf]
key2id = dict(zip(keyOrig, shuffIDs))
idMap  = dict(zip(pieceIDs, shuffIDs))

for key in theGridMea.pieces.keys():
    piece = theGridMea.pieces[key]
    piece.setPlacement(pieceLocations[:,key]) # Randomize Locations
    rotatedPiece = piece.rotatePiece(random.uniform(10, 10)) # Random reorientation
    rotatedPiece.id = key2id[key]
    theGridMea.pieces[key] = rotatedPiece

#DEBUG VISUAL
#theGridMea.display_mp(ID_DISPLAY=True) 

#==[3] Correspondences

CfgTrack   = board.CfgCorrespondences()
CfgTrack.matcher = 'SIFTCV'  
CfgTrack.matchParams = None
CfgTrack.forceMatches = opt.forceMatches
theTracker = board.Correspondences(CfgTrack, theGridSol)

theTracker.process(theGridMea)
theGridMea.display_mp(ID_DISPLAY=True)
print(idMap)
plt.show()

#
#================================== corr01sift =================================
