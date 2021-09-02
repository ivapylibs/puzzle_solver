#!/usr/bin/python3
#============================ basic02_withSolver ===========================
#
# @brief    Test script with command from the solver. (15p img)
#
#============================ basic02_withSolver ===========================

#
# @file     basic02_withSolver.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/30  [created]
#
#============================ basic02_withSolver ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import imageio
import glob

from puzzle.manager import manager
from puzzle.solver.simple import simple

import improcessor.basic as improcessor
from puzzle.parser.fromSketch import fromSketch
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.builder.gridded import gridded, paramGrid

from puzzle.simulator.basic import basic

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')


#==[1.1] Create an improcesser to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                  cv2.GaussianBlur, ((3, 3), 0,),
                  cv2.Canny, (30, 200,),
                  improcessor.basic.thresh, ((10,255,cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000))

theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()


#==[1.3] Display the solution board
#
f, axarr = plt.subplots(1,2)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0].imshow(bSource)
axarr[0].title.set_text('Source solution board')

#==[2] Create an Grid instance and explode it
#

print('Running through test cases. Will take a bit.')

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=paramGrid(areaThreshold=5000))

epImage, epBoard = theGrid.explodedPuzzle(dx=100,dy=100)

axarr[1].imshow(epImage)
axarr[1].title.set_text('Exploded view')

#==[2.1] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

theMaskSol_new = cv2.cvtColor(epImage,cv2.COLOR_BGR2GRAY)
_ , theMaskSol_new = cv2.threshold(theMaskSol_new,5,255,cv2.THRESH_BINARY)

theGrid_new = gridded.buildFrom_ImageAndMask(epImage, theMaskSol_new, theParams=paramGrid(areaThreshold=1000))

axarr[1].imshow(epImage)
axarr[1].title.set_text('Exploded view')

#==[3] Create match by manager
#
theManager = manager(theBoardSol)
# theManager.process(epBoard)
theManager.process(theGrid_new.solution)

#==[4] Create simple sovler and set up the match
#
theSolver = simple(theBoardSol, theGrid_new.solution)

theSolver.setMatch(theManager.pAssignments)

#==[5] Create a simulator for display
#
theSim = basic(theGrid_new.solution)

#==[6] Start the solver to take turns, display the updated board.
#

plt.ion()

# saveMe = True
saveMe = False

if saveMe:
  f.savefig(cpath + f'/data/theBoardExplode.png')

# num of size() actions at most
for i in range(1+theSolver.desired.size()):

  # Since we use the same instance in the simulator and the solver,
  # it will update automatically
  theSim.display(ID_DISPLAY=True)

  theSim.fig.suptitle(f'Step {i}', fontsize=20)
  plt.pause(1)

  if i==0:
    # Display the original one at the very beginning
    print(f'The original measured board')

  if saveMe:
    theSim.fig.savefig(cpath + f'/data/explode02_simple_step{str(i).zfill(2)}.png')

  if i < theSolver.desired.size():
    print(f'Step {i+1}:')
    theSolver.takeTurn(defaultPlan='order')

plt.ioff()
# plt.draw()

if saveMe:
  # Build GIF
  with imageio.get_writer(cpath + f'/data/demo_simple_explode02.gif', mode='I', fps=1) as writer:
      filename_list = glob.glob(cpath + f'/data/explode02_simple_step*.png')
      filename_list.sort()
      for filename in filename_list:
          image = imageio.imread(filename)
          writer.append_data(image)

#
#============================ basic02_withSolver ===========================