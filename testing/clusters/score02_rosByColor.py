#!/usr/bin/python3
#=========================== score02_rosByColor ===========================
## @file
# @brief    Basic functionality of byColor clustering on simulated puzzle pieces
#           with progress output to ROS. Builds on score01.
#
# This test script is a bit more complicated than typical ones, as it permits
# command line arguments to change the source image and puzzle gridding.  The
# default puzzle image is the fish puzzle, and the default gridding leads to
# 48 pieces. 
#
# The ROS output consists of a score topic (float) and a cluster information topic
# (JSON).  The output can probably be done differently (as matrix/list) to avoid
# JSON serialization and deserialization.  After all ROS already has tools to do
# that if the topic type is known.  This test script will remain this way, but a
# later one will use the reporting scheme to output the score and assignments
# using a cleaner pipeline (needing less prep-work). For now, this one is good.
#
# The test script is important because the robot (Mary) will know what the cluster
# assignments are from a previous calibration process. Knowing the assignment will
# provide Mary with the information needed to assist with the clustering process.
#
# For full listing of source puzzle options and other settings use the ``--help`` 
# flag. 
#
# ### Outcome ###
#
# Upon execution, the solution clustering is provided by overlaying a labeling of
# the puzzle solution over the gridded image.  The randomly placed and exploded
# pieces are displayed in another figure.  From there, the system starts to
# cluster them and output the clustering core against the ground truth for each
# cycle.
#
# At the end the score should be 1 (indicating perfect match against ground truth
# clusters).
#
#
# @ingroup TestCluster
# @quitf
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/11/17  [created]
#
#
# NOTE:
#   Indent is 4 spaces w/conversion.  Width is 90 columns.
#
#=========================== score02_rosByColor ===========================


#==[0] Prep environment
import copy
import os
import argparse
import pkg_resources

import matplotlib.pyplot as plt

from puzzle.clusters.byColor import ByColor, ParamColorCluster

import os
import cv2
import matplotlib.pyplot as plt
import numpy as np

import improcessor.basic as improcessor
from puzzle.builder.gridded import Gridded, CfgGridded
from puzzle.parse.fromSketch import FromSketch
from puzzle.utils.imageProcessing import cropImage
from puzzle.utils.shapeProcessing import bb_intersection_over_union
from puzzle.utils.dataProcessing import convert_serializable

import rospy
from rospy_message_converter import message_converter, json_message_converter
import rosgraph
import subprocess
import time
from std_msgs.msg import String, Int32, Float64
import json


#==[0.1] Argument parser.
#
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


#==[0.3] ROS support
#        Start the roscore if not enabled
#
if not rosgraph.is_master_online():
    roscore_proc = subprocess.Popen(['roscore'], shell=True)
    # wait for a second to start completely
    time.sleep(1)

# Initialize the node
# TODO: If necessary, we can create custom message types later.
rospy.init_node("score_cluster")
cluster_info_pub = rospy.Publisher('cluster_info', String, queue_size=10)
score_info_pub   = rospy.Publisher('score_info', Float64, queue_size=5) 

#==[1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImageSol = cv2.imread(prefix + img_dict[opt.image])
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(prefix + mask_dict[opt.mask])
theImageSol = cropImage(theImageSol, theMaskSol_src)

#==[1.1] Create an improcessor to obtain the puzzle piece mask.
#
# TODO: This step can probably be made cleaner.  Not worrying for now. PAV 10/04/24.
improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((80, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#==[1.2] Use puzzle template image to synthesize a gridded puzzle.
#        Display the original board for viewing with piece ID overlay.
#
cfgGrid = CfgGridded()
cfgGrid.update(dict(minArea=1000, reorder=True, pieceBuilder='Regular'))
theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, cfgGrid)

#DEBUG VISUAL
#theGrid.display(CONTOUR_DISPLAY=True, ID_DISPLAY=True, TITLE='Original ID')

#==[2] Create a cluster instance and process the puzzle board.
#      Display image with cluster ID overlay.
#
if opt.cluster_mode == 'number':
    theColorCluster = ByColor(theGrid, theParams=ParamColorCluster(cluster_num=opt.cluster_number, cluster_mode='number'))
elif opt.cluster_mode == 'threshold':
    theColorCluster = ByColor(theGrid, theParams=ParamColorCluster(tauDist=opt.cluster_threshold, cluster_mode='threshold'))
else:
    raise ValueError('Invalid cluster mode.')

theColorCluster.process()

# Generate cluster label vs puzzle piece ID mapping.
for k, v in theColorCluster.feaLabel_dict.items():
    theGrid.pieces[k].cluster_id = v

print('No. of pieces :', len(theColorCluster.feature))
print('Cluster labels:', theColorCluster.feaLabel)

#DEBUG VISUAL
#theGrid.display(CONTOUR_DISPLAY=True, ID_DISPLAY=True, ID_DISPLAY_OPTION=1, TITLE='Cluster ID')

#==[3.1] Simulate randomly clustering the pieces.
#        First explode the puzzle to make space for clustering.
#        
_, epBoard = theGrid.explodedPuzzle(dx=500, dy=500)

cfgGrid = CfgGridded()
cfgGrid.update(dict(minArea=1000, pieceBuilder='Regular'))
epBoard = Gridded(epBoard, cfgGrid)

#==[3.2] Randomly swap the puzzle pieces.
#        Set fixed random seed for repeatable execution. 
#
np.random.seed(0)
_, epBoard, _ = epBoard.swapPuzzle()

#DEBUG VISUAL
epImage = epBoard.toImage(CONTOUR_DISPLAY=True, ID_DISPLAY=True) 
                                                #ID_DISPLAY_OPTION=1, BOUNDING_BOX=False)

#==[3.3] Define image quadrant regions.

x_mid = epImage.shape[1]//2
y_mid = epImage.shape[0]//2

# Create the region_dict based on (x,y) coordinate ranges.
region_dict = {
    0: [0,0,x_mid,y_mid],
    1: [x_mid,0,x_mid*2,y_mid],
    2: [0,y_mid,x_mid,y_mid*2],
    3: [x_mid,y_mid,x_mid*2,y_mid*2],
}

#==[3.4] Rather than have the cluster regions be ordered from top-left clockwise
#        around, create a random assignment of quadrant region to cluster ID.
#
#        This is a cluster2region id map, cluster_id -> region_id
#
region_id_list = np.arange(4)
np.random.seed()
np.random.shuffle(region_id_list)
cluster_region_dict = {i:v for i,v in enumerate(region_id_list)}
print('cluster id to quadrant region map:', cluster_region_dict)


#==[4] Simulate the human clustering by separating the puzzle pieces into 4 groups.

# Compute the cluster id of each piece (based on the initial region)
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

message_dict ={
    'Step': 0,
    'Score': score,
    'Reference': theColorCluster.feaLabel_dict,
    'Human': piece_human_cluster_dict,
}

fh = plt.figure()
for idx, piece_id in enumerate(epBoard.pieces):

    # If piece_human_cluster is not aligned with the computer computed one,
    # we force to change the epBoard according to the reference clustering (one by one).
    if piece_human_cluster_dict[piece_id] != cluster_region_dict[epBoard.pieces[piece_id].cluster_id]:

        def random_place(rectangle_list):

            return np.array([np.random.randint(rectangle_list[0] + 300, rectangle_list[2] - 300),
                      np.random.randint(rectangle_list[1] + 300, rectangle_list[3] - 300)])

        rLoc_valid = False
        new_rLoc = None

        while not rLoc_valid:
            new_rLoc = random_place(region_dict[cluster_region_dict[epBoard.pieces[piece_id].cluster_id]])

            num_success = 0

            # Check if the new location is valid (do not overlap with other pieces).
            for piece_id_other in epBoard.pieces:
                if piece_id == piece_id_other:
                    continue

                query_bb = [new_rLoc[0], new_rLoc[1], new_rLoc[0] + epBoard.pieces[piece_id].y.size[0],
                            new_rLoc[1] + epBoard.pieces[piece_id].y.size[1]]
                target_bb = [epBoard.pieces[piece_id_other].rLoc[0], epBoard.pieces[piece_id_other].rLoc[1],
                             epBoard.pieces[piece_id_other].rLoc[0] + epBoard.pieces[piece_id_other].y.size[0], epBoard.pieces[piece_id_other].rLoc[1]+epBoard.pieces[piece_id_other].y.size[1]]

                if bb_intersection_over_union(query_bb, target_bb) > 0:
                    rLoc_valid = False
                    break
                else:
                    num_success += 1

            if num_success == len(epBoard.pieces) - 1:
                rLoc_valid = True

        epBoard.pieces[piece_id].rLoc = new_rLoc

        # Update piece_human_cluster_dict
        piece_human_cluster_dict[piece_id] = cluster_region_dict[epBoard.pieces[piece_id].cluster_id]

        if not opt.only_final_display or idx==len(epBoard.pieces)-1:

            print(f"Step {idx}:")
            epImage = epBoard.toImage(theImage=np.zeros(epImage.shape) ,CONTOUR_DISPLAY=True, ID_DISPLAY=True)#, ID_DISPLAY_OPTION=1)

            # Add two lines to split the pieces into clusters.
            cv2.line(epImage, (0, epImage.shape[0] // 2), (epImage.shape[1], epImage.shape[0] // 2), (255, 255, 255), 5)
            cv2.line(epImage, (epImage.shape[1] // 2, 0), (epImage.shape[1] // 2, epImage.shape[0]), (255, 255, 255), 5)

            score = theColorCluster.score(piece_human_cluster_dict, method=opt.score_method)
            print('Score:', score)

            # Update the message dict
            message_dict['Step'] = idx
            message_dict['Score'] = score
            message_dict['Human'] = piece_human_cluster_dict

            message_json = json.dumps(message_dict, indent=4, default = convert_serializable)

            message = String(data=f'{message_json}')
            json_str = json_message_converter.convert_ros_message_to_json(message)

            # ROS publish
            cluster_info_pub.publish(json_str)
            score_info_pub.publish(float(score))

            plt.imshow(epImage)
            plt.title(f"Step {idx}/Score: {score:.3f}")
            plt.pause(1)

            # plt.savefig(f'{opt.image}_cluster_Step_{idx}.png', dpi=300)

plt.show()

#
#============================ scoreHumanROS_byColor ===========================
