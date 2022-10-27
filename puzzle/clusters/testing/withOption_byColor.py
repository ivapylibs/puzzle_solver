#!/usr/bin/python3
# ============================ withOption_byColor ===========================
#
# @brief    Test script for basic functionality of byColor on simulated puzzle pieces. Provide mroe options to the user.
#
# ============================ withOption_byColor ===========================

#
# @file     withOption_byColor.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/10/26  [created]
#
# ============================ withOption_byColor ===========================


# ==[0] Prep environment
import copy
import os

import matplotlib.pyplot as plt

from puzzle.clusters.byColor import ByColor, ParamColorCluster

import os
import cv2
import matplotlib.pyplot as plt
import numpy as np

import improcessor.basic as improcessor
from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.parser.fromSketch import FromSketch
from puzzle.utils.imageProcessing import cropImage

import argparse

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

argparser = argparse.ArgumentParser()
argparser.add_argument('--image', type=str, default='duck', choices=['duck', 'earth', 'balloon', 'elsa1', 'elsa2', 'rapunzel', 'dinos'])
argparser.add_argument('--mask', type=int, default=15, choices=[15, 35, 60])
argparser.add_argument('--with_cluster', action='store_true')
argparser.add_argument('--cluster_mode', type=str, default='number', choices=['number', 'threshold'])
argparser.add_argument('--cluster_number', type=int, default=4)
argparser.add_argument('--cluster_threshold', type=float, default=0.5)

opt = argparser.parse_args()

img_dict = {
    'duck': 'duck.jpg',
    'earth': 'earth.jpg',
    'balloon': 'balloon.png',
    'elsa1': 'FrozenII_Elsa_1.jpg',
    'elsa2': 'FrozenII_Elsa_2.jpg',
    'rapunzel': 'Rapunzel.jpg',
    'dinos': 'Amazon_Dinos_2.jpg'
}

mask_dict = {
    15: 'puzzle_15p_123rf.png',
    35: 'puzzle_35p.png',
    60: 'puzzle_60p_AdSt408534841.png'
}

# ==[1] Read the source image and template.
#

prefix = cpath + '/../../testing/data/'

theImageSol = cv2.imread(prefix + img_dict[opt.image])
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(prefix + mask_dict[opt.mask])
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           cv2.dilate, (np.ones((3, 3), np.uint8),),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=ParamGrid(areaThresholdLower=5000,reorder=True))

# Display the original board
theGrid.display(CONTOUR_DISPLAY=True, ID_DISPLAY=True)

# ==[2] Create a cluster instance and process the puzzle board.
#

if opt.with_cluster:

    if opt.cluster_mode == 'number':
        theColorCluster = ByColor(theGrid, theParams=ParamColorCluster(cluster_num=opt.cluster_number, cluster_mode='number'))
    elif opt.cluster_mode == 'threshold':
        theColorCluster = ByColor(theGrid, theParams=ParamColorCluster(tauDist=opt.cluster_threshold, cluster_mode='threshold'))
    else:
        raise ValueError('Invalid cluster mode.')

    theColorCluster.process()

    # ==[3] Display the extracted features.
    #

    print('The number of pieces:', len(theColorCluster.feature))
    print('The cluster label:', theColorCluster.feaLabel)

    # Copy and paste a new board but with the cluster label displayed.
    theGrid2 = copy.deepcopy(theGrid)
    for key in theGrid2.pieces:
        theGrid2.pieces[key].id = theColorCluster.feaLabel[key]

    theGrid2.display(CONTOUR_DISPLAY=True, ID_DISPLAY=True)

plt.show()

#
# ============================ withOption_byColor ===========================
