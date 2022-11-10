#!/usr/bin/python3
# ============================ scoreHuman_byColor ===========================
#
# @brief    Test script for basic functionality of byColor on simulated puzzle pieces.
#           Will randomly shuffle the pieces and separate them into clusters. Then score the clusters with reference to the ground truth.
#
# ============================ scoreHuman_byColor ===========================

#
# @file     scoreHuman_byColor.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/11/9  [created]
#
# ============================ scoreHuman_byColor ===========================


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
argparser.add_argument('--image', type=str, default='fish', choices=['duck', 'earth', 'balloon', 'elsa1', 'elsa2', 'rapunzel', 'dinos', 'fish'],
                       help='The image to be used for the puzzle.')
argparser.add_argument('--mask', type=int, default=48, choices=[15, 35, 48, 60],
                       help = 'The number of pieces in the puzzle.')
argparser.add_argument('--cluster_mode', type=str, default='number', choices=['number', 'threshold'],
                       help='The mode of the cluster algorithm.')
argparser.add_argument('--cluster_number', type=int, default=4,
                       help='The number of clusters to be used.')
argparser.add_argument('--cluster_threshold', type=float, default=0.5,
                       help='The threshold of the cluster algorithm.')
argparser.add_argument('--only_final_display', action='store_true',
                       help='Only display the final result.')
argparser.add_argument('--score_method', type=str, default='label', choices=['label', 'histogram'])

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

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=ParamGrid(areaThresholdLower=5000, removeBlack=False, reorder=True))

# Display the original board
theGrid.display(CONTOUR_DISPLAY=True, ID_DISPLAY=True, TITLE='Original ID')

# ==[2] Create a cluster instance and process the puzzle board.
#

if opt.cluster_mode == 'number':
    theColorCluster = ByColor(theGrid, theParams=ParamColorCluster(cluster_num=opt.cluster_number, cluster_mode='number'))
elif opt.cluster_mode == 'threshold':
    theColorCluster = ByColor(theGrid, theParams=ParamColorCluster(tauDist=opt.cluster_threshold, cluster_mode='threshold'))
else:
    raise ValueError('Invalid cluster mode.')

theColorCluster.process()

# Initialize the reference cluster id
for k, v in theColorCluster.feaLabel_dict.items():
    theGrid.pieces[k].cluster_id = v

print('The number of pieces:', len(theColorCluster.feature))
print('The cluster label:', theColorCluster.feaLabel)

theGrid.display(CONTOUR_DISPLAY=True, ID_DISPLAY=True, ID_DISPLAY_OPTION=1, TITLE='Cluster ID')

# ==[3.1] Simulate randomly clustering the pieces.

_, epBoard = theGrid.explodedPuzzle(dx=250, dy=250)

epBoard = Gridded(epBoard, ParamGrid(areaThresholdLower=5000, removeBlack=False))

# ==[3.2] Randomly swap the puzzle pieces.
#

# Set up the random seed to make sure we have the same initial state.
np.random.seed(0)
_, epBoard, _ = epBoard.swapPuzzle()

epImage = epBoard.toImage(CONTOUR_DISPLAY=True, ID_DISPLAY=True, ID_DISPLAY_OPTION=1, BOUNDING_BOX=False)

# ==[4] Simulate the human performance. We separate the puzzle pieces into 4 groups.

# Create the desired cluster2region id map, cluster_id: region_id
# We may have different desired map (random)
region_id_list = np.arange(4)
np.random.seed()
np.random.shuffle(region_id_list)
cluster_region_dict = {i:v for i,v in enumerate(region_id_list)}
print('The desired cluster id to region id map:', cluster_region_dict)

x_mid = epImage.shape[1]//2
y_mid = epImage.shape[0]//2

# Create the region_dict
region_dict = {
    0: [0,0,x_mid,y_mid],
    1: [x_mid,0,x_mid*2,y_mid],
    2: [0,y_mid,x_mid,y_mid*2],
    3: [x_mid,y_mid,x_mid*2,y_mid*2],
}

# Compute the cluster id of each piece (based on the region)
piece_human_cluster_dict = {}
for piece_id in epBoard.pieces:

    piece = epBoard.pieces[piece_id]
    piece_center = piece.rLoc + np.array(piece.y.size)//2

    if piece_center[0] < x_mid and piece_center[1] < y_mid:
        piece_human_cluster_dict[piece.id] = 0
    elif piece_center[0] > x_mid and piece_center[1] < y_mid:
        piece_human_cluster_dict[piece.id] = 1
    elif piece_center[0] < x_mid and piece_center[1] > y_mid:
        piece_human_cluster_dict[piece.id] = 2
    elif piece_center[0] > x_mid and piece_center[1] > y_mid:
        piece_human_cluster_dict[piece.id] = 3
    else:
        # Maybe on the lines
        piece_human_cluster_dict[piece.id] = 0

score = theColorCluster.score(piece_human_cluster_dict, method=opt.score_method)
print('Score:', score)

# Add two lines to split the pieces into clusters.
cv2.line(epImage, (0, epImage.shape[0]//2), (epImage.shape[1], epImage.shape[0]//2), (255, 255, 255), 5)
cv2.line(epImage, (epImage.shape[1]//2, 0), (epImage.shape[1]//2, epImage.shape[0]), (255, 255, 255), 5)

plt.figure()
plt.imshow(epImage)
plt.title(f'Randomly clustered pieces/Score: {score:.3f}')

fh = plt.figure()
# Force to change the epBoard according to the reference clustering (one by one).
for idx, piece_id in enumerate(epBoard.pieces):
    if piece_human_cluster_dict[piece_id] != cluster_region_dict[epBoard.pieces[piece_id].cluster_id]:

        def random_place(rectangle_list):
            # Todo: we may need to check if the new location is valid.
            return np.array([np.random.randint(rectangle_list[0]+300, rectangle_list[2]-300), np.random.randint(rectangle_list[1]+300, rectangle_list[3]-300)])

        epBoard.pieces[piece_id].rLoc = random_place(region_dict[cluster_region_dict[epBoard.pieces[piece_id].cluster_id]])

        # Update piece_human_cluster_dict
        piece_human_cluster_dict[piece_id] = cluster_region_dict[epBoard.pieces[piece_id].cluster_id]

        if not opt.only_final_display or idx==len(epBoard.pieces)-1:

            print(f"Step {idx}:")
            epImage = epBoard.toImage(theImage=np.zeros(epImage.shape) ,CONTOUR_DISPLAY=True, ID_DISPLAY=True, ID_DISPLAY_OPTION=1)

            # Add two lines to split the pieces into clusters.
            cv2.line(epImage, (0, epImage.shape[0] // 2), (epImage.shape[1], epImage.shape[0] // 2), (255, 255, 255), 5)
            cv2.line(epImage, (epImage.shape[1] // 2, 0), (epImage.shape[1] // 2, epImage.shape[0]), (255, 255, 255), 5)

            score = theColorCluster.score(piece_human_cluster_dict, method=opt.score_method)
            print('Score:', score)

            plt.imshow(epImage)
            plt.title(f"Step {idx}/Score: {score:.3f}")
            plt.pause(1)

            plt.savefig(f'{opt.image}_cluster_Step_{idx}.png', dpi=300)

plt.show()

#
# ============================ scoreHuman_byColor ===========================
