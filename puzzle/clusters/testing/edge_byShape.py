#!/usr/bin/python3
# ============================ edge_byShape ===========================
#
# @brief    Test script for basic functionality of byColor
#
# ============================ edge_byShape ===========================

#
# @file     edge_byShape.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/29  [created]
#
# ============================ edge_byShape ===========================


# ==[0] Prep environment
import os

import cv2
import improcessor.basic as improcessor
import matplotlib.pyplot as plt

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.clusters.byShape import byShape
from puzzle.parser.fromSketch import fromSketch
from puzzle.piece.edge import edge
from puzzle.piece.regular import regular
from puzzle.utils.imageProcessing import cropImage

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
# theImageSol = cv2.imread(cpath + '/../../testing/data/cocacola.jpg')
# theImageSol = cv2.imread(cpath + '/../../testing/data/church.jpg')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                         theParams=paramGrid(areaThresholdLower=5000, pieceConstructor=regular,
                                                             reorder=True))

# ==[2] Create a cluster instance and process the puzzle board.
#

theShapeCluster = byShape(theGrid, extractor=edge())
theShapeCluster.process()

# ==[3] Display the extracted features.
#

print('Should see 15 pieces of 3 different types (inside/side/corner). They are clustered into 3 groups.')
print('The number of pieces:', len(theShapeCluster.feature))
print('The cluster label:', theShapeCluster.feaLabel)

theGrid.display(ID_DISPLAY=True)
plt.show()

#
# ============================ edge_byShape ===========================
