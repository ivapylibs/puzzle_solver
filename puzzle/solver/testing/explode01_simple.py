#!/usr/bin/python3
#============================ explode01_simple ===========================
#
# @brief    Test script for solving a explodedPuzzle in a col-wise manner.
#           (6 shapes img)
#
#============================ explode01_simple ===========================

#
# @file     explode01_simple.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/16  [created]
#
#============================ explode01_simple ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import imageio
import glob

from puzzle.manager import manager
from puzzle.solver.simple import simple

from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.builder.gridded import gridded, paramGrid

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.cvtColor(theImageSol,cv2.COLOR_BGR2GRAY)
_ , theMaskSol = cv2.threshold(theMaskSol,10,255,cv2.THRESH_BINARY)

#==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()

#==[1.2] Display the solution board
#
f, axarr = plt.subplots(1,2)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0].imshow(bSource)
axarr[0].title.set_text('Source Board')

#==[2] Create an Grid instance and explode it
#

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol)

epImage, epBoard = theGrid.explodedPuzzle()

axarr[1].imshow(epImage)
axarr[1].title.set_text('Exploded View')

#==[3] Create match by manager
#
theManager = manager(theBoardSol)
theManager.process(epBoard)

#==[4] Create simple sovler and set up the match
#
theSolver = simple(theBoardSol, epBoard)

theSolver.setMatch(theManager.pAssignments)

#==[5] Start the solver to take turns, display the updated board.
#

plt.ion()
fh = plt.figure()

saveMe = True
# saveMe = False

if saveMe:
  f.savefig(cpath + f'/data/theBoardExplode.png')

# num of size() actions at most
for i in range(1+theSolver.desired.size()):

  theSolver.current.display(fh=fh, ID_DISPLAY=True)
  fh.suptitle(f'Step {i}', fontsize=20)
  plt.pause(1)

  if i==0:
    # Display the original one at the very beginning
    print(f'The original measured board')

  if saveMe:
    fh.savefig(cpath + f'/data/explode01_simple_step{str(i).zfill(2)}.png')

  if i < theSolver.desired.size():
    print(f'Step {i+1}:')
    theSolver.takeTurn(defaultPlan='order')

plt.ioff()
# plt.draw()

if saveMe:
  # Build GIF
  with imageio.get_writer(cpath + f'/data/demo_simple_explode01.gif', mode='I', fps=1) as writer:
      filename_list = glob.glob(cpath + f'/data/explode01_simple_step*.png')
      filename_list.sort()
      for filename in filename_list:
          image = imageio.imread(filename)
          writer.append_data(image)

#
#============================ explode01_simple ===========================
