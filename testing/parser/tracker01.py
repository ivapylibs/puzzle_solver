#!/usr/bin/python3
#=============================== tracker01 ===============================
#
# @brief    Pack detector + trackpointer into a perceiver instance and 
#           test out functionality.
#
# In this test, there is no data association going on.  See the next 
# tracker test script.
#
#=============================== tracker01 ===============================

#
# @file     tracker01.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2024/09/15  [created]
#
#
# NOTE:
#   indent is 2 spaces.
#   80 columns
#
#=============================== tracker01 ===============================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import time
import cv2

import detector.inImage as detector
import improcessor.basic as improcessor
from puzzle.parser import boardPerceive
from puzzle.parser import boardMeasure, CfgBoardMeasure


from puzzle.piece import Template

#==[1] Create a start image.
#
squarePiece = Template.buildSquare(20, color=(160, 160, 0), rLoc=(80, 40))
spherePiece = Template.buildSphere(10, color=(0, 255, 0), rLoc=(80, 140))

bigImage = np.zeros((200, 200, 3)).astype('uint8')

squarePiece.placeInImage(bigImage)
spherePiece.placeInImage(bigImage)

plt.ion()
fh = plt.figure()
plt.title("Test builder of basic-shape puzzle pieces: red square and green sphere")
plt.imshow(bigImage)
plt.show()
plt.pause(0.2)

#==[2] Create perceiver.
#
improc   = improcessor.basic(
                cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                improcessor.basic.thresh, ((40, 255, cv2.THRESH_BINARY),) )
binDet   = detector.inImage(improc)
theLayer = boardMeasure()

boardPer = boardPerceive(None, binDet, theLayer)


#==[3] Move pieces in image.
#
shiftSq = np.array([2, 2])
shiftSp = np.array([-2, 3])

for i in range(6):
  bigImage = np.zeros((200, 200, 3)).astype('uint8')
  squarePiece.setPlacement(shiftSq, True) 
  spherePiece.setPlacement(shiftSp, True) 

  squarePiece.placeInImage(bigImage)
  spherePiece.placeInImage(bigImage)

  boardPer.process(bigImage)

  outImage = np.zeros((200, 200, 3)).astype('uint8')

  plt.cla()
  boardPer.tracker.bMeas.display_mp(outImage, fh, ID_DISPLAY=True)
  plt.pause(0.2)

#
#=============================== tracker01 ===============================
