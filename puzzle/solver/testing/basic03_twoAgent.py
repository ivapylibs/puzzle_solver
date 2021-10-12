#!/usr/bin/python3
# ============================ basic03_twoAgent ===========================
#
# @brief    Test script for the most basic functionality of simple class.
#           Display a visual sequence of the puzzle being solved. Played
#           by two agents.
#
# ============================ basic03_twoAgent ===========================

#
# @file     basic03_twoAgent.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/15  [created]
#
# ============================ basic03_twoAgent ===========================


# ==[0] Prep environment
import glob
import os

import cv2
import imageio
import matplotlib.pyplot as plt

from puzzle.builder.gridded import gridded
from puzzle.manager import manager
from puzzle.parser.fromLayer import fromLayer
from puzzle.solver.twoAgent import twoAgent

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png', cv2.IMREAD_GRAYSCALE)
_, theMaskSol = cv2.threshold(theMaskSol, 10, 255, cv2.THRESH_BINARY)

# ==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[2] Create image & mask for measurement
#
theImageMea = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image.png')
theMaskMea = cv2.imread(cpath + '/../../testing/data/shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

# ==[2.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer()
theLayer.process(theImageMea, theMaskMea)
theBoardMea = theLayer.getState()

# ==[3] Display the current & solution board
#
f, axarr = plt.subplots(1, 2)

theBoardMea_img = theBoardMea.toImage(ID_DISPLAY=True)
theBoardSol_img = theBoardSol.toImage()
axarr[0].imshow(theBoardMea_img)
axarr[0].title.set_text('Original measured board')

axarr[1].imshow(theBoardSol_img)
axarr[1].title.set_text('Solution board')

# ==[4] Create match by manager
#
theManager = manager(theBoardSol)
theManager.process(theBoardMea)

# ==[5] Create simple instance and set up the match
#
thetwoAgent = twoAgent(gridded(theBoardSol), gridded(theBoardMea))

thetwoAgent.setMatch(theManager.pAssignments)

# ==[6] Start the solver to take turns, display the updated board.
#

plt.ion()
fh = plt.figure()

# saveMe = True
saveMe = False

if saveMe:
    f.savefig(cpath + f'/data/theBoard.png')

# num of size() actions at most
for i in range(1 + thetwoAgent.desired.size()):

    thetwoAgent.current.display(fh=fh, ID_DISPLAY=True)
    fh.suptitle(f'Step {i}, Agent {thetwoAgent.iMove}\'s turn', fontsize=20)
    plt.pause(1)

    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    if saveMe:
        fh.savefig(cpath + f'/data/theBoardMea_twoAgent_step{i}.png')

    if i < thetwoAgent.desired.size():
        print(f'Step {i + 1}:')
        thetwoAgent.takeTurn()

plt.ioff()
# plt.draw()

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/demo_twoAgent.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/theBoardMea_twoAgent_*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)

#
# ============================ basic03_twoAgent ===========================
