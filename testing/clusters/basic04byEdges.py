#!/usr/bin/python3
#============================= basic04byEdges ============================
##
# @brief    Test script for basic functionality of byColor
#
#
# @ingroup  TestCluster
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/29  [created]
#
# @quitf
#============================= basic04byEdges ============================


# ==[0] Prep environment
import os
import pkg_resources

import cv2
import improcessor.basic as improcessor
import matplotlib.pyplot as plt

from puzzle.builder.gridded import Gridded, CfgGridded
from puzzle.clusters.byShape import ByShape
from puzzle.parse.fromSketch import FromSketch
from puzzle.pieces.edge import Edge
from puzzle.piece import Regular
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
prefix = pkg_resources.resource_filename('puzzle', '../testing/data/')

theImageSol = cv2.imread(prefix + 'balloon.png')
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
cfgGrid.update(dict(areaThresholdLower=5000, pieceBuilder='Regular', reorder=True))

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, cfgGrid)

#==[2] Create a cluster instance and process the puzzle board.
#

theShapeCluster = ByShape(theGrid, extractor=Edge())
theShapeCluster.process()

print(theGrid.pieces[0].edge[0].etype)

#==[3] Display the extracted features.
#

print('Should see 15 pieces of 3 different types (inside/side/corner). They are clustered into 3 groups.')
print('The number of pieces:', len(theShapeCluster.feature))
print('The cluster label:', theShapeCluster.feaLabel)

theGrid.display_mp(ID_DISPLAY=True)
plt.show()

#
#============================= basic04byEdges ============================
