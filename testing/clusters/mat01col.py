#!/usr/bin/python3
#============================ arg01_clusterByColor ===========================
## @file
# @brief    Test clustering methods on matrix puzzle.
#
# Loads the desired puzzle and applies process according to arguments to create a
# puzzle.  The puzzle is displayed.  If specified, the puzzle pieces will be
# clusters and a separate image will be created with cluster ID overlay.
#
#  Use the ``--help`` flag to see what the options are.  Sending no option swill
#  default to a 48 piece fish puzzle.
#
# @ingroup TestCluster
# @quitf
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/10/26  [created]
#
#============================ arg01_clusterByColor ===========================


# ==[0] Prep environment
import copy
import os

import matplotlib.pyplot as plt

from puzzle.clusters.byColor import ByColor, ParamColorCluster

import os
import cv2
import matplotlib.pyplot as plt
import numpy as np

import ivapy.display_cv as display

import improcessor.basic as improcessor
from puzzle.builder.gridded import Gridded, CfgGridded
from puzzle.parse.fromSketch import FromSketch
from puzzle.utils.imageProcessing import cropImage

import argparse
import pkg_resources

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

opt = argparser.parse_args()

# ==[1] Read the source image and template.
#

prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImageSol = cv2.imread(prefix + img_dict[opt.image])
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(prefix + mask_dict[opt.mask])
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((150, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#DEBUG
#print("Creating window: should see a processed mask.")
#import ivapy.display_cv as display
#display.rgb(theImageSol,window_name='Input')
#display.binary(theMaskSol, window_name='Output')
#display.wait()

cfgGrid = CfgGridded()
cfgGrid.tauGrid = 5000
cfgGrid.reorder=False

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, cfgGrid)
#theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=CfgGridded(areaThresholdLower=5000, removeBlack=False, reorder=True))

# Display the original board
print("board.display_mp has been updated.  Check and revise this invocation.")
theGrid.display_mp(theImageSol, None, CONTOUR_DISPLAY=False, ID_DISPLAY=True)#, TITLE='Original ID')
# Display the original board
# theGrid.display(CONTOUR_DISPLAY=True, ID_DISPLAY=True, TITLE='Original ID')

# ==[2] Create a cluster instance and process the puzzle board.
#

print(opt.with_cluster)
if opt.with_cluster:

    if opt.cluster_mode == 'number':
        theColorCluster = ByColor(theGrid, theParams=ParamColorCluster(cluster_num=opt.cluster_number, cluster_mode='number'))
    elif opt.cluster_mode == 'threshold':
        theColorCluster = ByColor(theGrid, theParams=ParamColorCluster(tauDist=opt.cluster_threshold, cluster_mode='threshold'))
    else:
        raise ValueError('Invalid cluster mode.')

    theColorCluster.process()

    for k, v in theColorCluster.feaLabel_dict.items():
        #theGrid.pieces[k].id = v
        print("this code should be correct now. Pieces need a cluster ID.")
        # @todo THE ABOVE CODE IS BAD. IT IS A KLUDGE UNTIL MERGED WITH YUNZHI.
        #       YUNZHI HAS UPDATED DISPLAY ROUTINE.
        theGrid.pieces[k].cluster_id = v

    print('The number of pieces:', len(theColorCluster.feature))
    print('The cluster label:', theColorCluster.feaLabel)

    print("board.display_mp has been updated.  Check and revise this invocation.")
    print("board.display_mp needs the ID_DISPLAY_OPTION and other flags.")
    theGrid.display_mp(theImageSol,CONTOUR_DISPLAY=True, ID_DISPLAY=True)#, ID_DISPLAY_OPTION=1, TITLE='Cluster ID')
    #theGrid.display_mp(CONTOUR_DISPLAY=True, ID_DISPLAY=True, ID_DISPLAY_OPTION=1, TITLE='Cluster ID')
    Warning("Code is incomplete.  Missing display by cluster ID.")

plt.savefig(f'{opt.image}_cluster.png', dpi=300)

plt.show()

#
#============================ arg01_clusterByColor ===========================
