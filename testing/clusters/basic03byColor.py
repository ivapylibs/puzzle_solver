#!/usr/bin/python3
#============================= basic03byColor ============================
##
# @brief    Test script for basic functionality of byColor on simulated puzzle pieces
#
#
# @ingroup  TestCluster
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/10/09  [created]
#
# @quitf
#============================= basic03byColor ============================


# ==[0] Prep environment
import copy
import os
import pkg_resources

import matplotlib.pyplot as plt

from puzzle.board import Board
from puzzle.clusters.byColor import ByColor, ParamColorCluster
from puzzle.piece import Template

import os
import pickle
from dataclasses import dataclass
import cv2
import matplotlib.pyplot as plt
import numpy as np

import improcessor.basic as improcessor
from puzzle.piece import Regular
from puzzle.builder.gridded import Gridded, CfgGridded
from puzzle.parse.fromLayer import FromLayer, ParamPuzzle
from puzzle.parse.fromSketch import FromSketch
from puzzle.utils.imageProcessing import cropImage


fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImageSol = cv2.imread(prefix + 'earth.jpg')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(prefix + 'puzzle_15p_123rf.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           improcessor.basic.thresh, ((40, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

cfgGrid = CfgGridded()
cfgGrid.update(dict(areaThresholdLower=5000))
theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, cfgGrid)

# Display the original board
# theGrid.display_mp(CONTOUR_DISPLAY=True, ID_DISPLAY=True)

# ==[2] Create a cluster instance and process the puzzle board.
#

theColorCluster = ByColor(theGrid, theParams=ParamColorCluster(cluster_num=4, cluster_mode='number'))
theColorCluster.process()

# ==[3] Display the extracted features.
#

print('Should see 15 pieces. They are clustered into 4 groups.')
print('The number of pieces:', len(theColorCluster.feature))
print('The cluster label:', theColorCluster.feaLabel)

# Copy and paste a new board but with the cluster label displayed.
theGrid2 = copy.deepcopy(theGrid)
for key in theGrid2.pieces:
    theGrid2.pieces[key].id = theColorCluster.feaLabel[key]

theGrid2.display_mp(CONTOUR_DISPLAY=True, ID_DISPLAY=True)


plt.show()

#
#============================= basic03byColor ============================
