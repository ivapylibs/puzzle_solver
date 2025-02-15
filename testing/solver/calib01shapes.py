#!/usr/bin/python3
#============================= calib01shapes =============================
##@file
# @brief    Test image differences calibration script. 
#
# Using image differences from snapshots of the camera stream is the easiest
# way to calibrate a puzzle.  If done right, I think we can snag a pretty
# tight puzzle board from the accumulated differences.  This is a simple
# test with shapes.
#
# @ingroup  TestPuzzle_Solver
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#
# @date     2025/02/14  
#
# @quitf
#============================= calib01shapes =============================

#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.piece import Template
import puzzle.board as puzzle
import detector.fgmodel.differences as diffs

#==[1] Create empty image, instantiate differences FG detector.
#
bigImage = np.zeros((200, 200, 3))

cfgDet = diffs.CfgDifferences()
cfgDet.doAccum= True

chDet = diffs.fgDifferences(cfgDet)

chDet.process(bigImage)

#==[2] Add shapes to image and generate difference.
#
squarePiece = Template.buildSquare(20, color=(255, 0, 0), rLoc=(80, 40))
squarePiece.placeInImage(bigImage)

chDet.process(bigImage)

squarePiece = Template.buildSquare(20, color=(0, 0, 255), rLoc=(102, 42))
squarePiece.placeInImage(bigImage)

chDet.process(bigImage)

spherePiece = Template.buildSphere(10, color=(0, 255, 0), rLoc=(80, 140))
spherePiece.placeInImage(bigImage)

chDet.process(bigImage)


#==[3] Test puzzle (solution) builder from label image.
#
pShapes = puzzle.Board()
pShapes.fromImageAndLabels(bigImage, chDet.labelI)


#==[4] Confirm that puzzle pieces were extracted.
#
puzzImage = np.zeros((200, 200, 3))

puzzImage = pShapes.toImage(puzzImage, CONTOUR_DISPLAY=False, BOUNDING_BOX=False)

plt.figure()
plt.imshow(bigImage)

plt.figure()
plt.imshow(puzzImage)

print("Close all windows to end test.")
plt.show()


#
#============================= calib01shapes =============================
