#!/usr/bin/python3
# ============================ 15pExplode_simple ===========================
#
# @brief    Test script for solving a explodedPuzzle in a col-wise manner.
#           (15p img)
#
# ============================ 15pExplode_simple ===========================

#
# @file     15pExplode_simple.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/23  [created]
#
# ============================ 15pExplode_simple ===========================


import glob
import os

import cv2
import imageio
import improcessor.basic as improcessor
# ==[0] Prep environment
import matplotlib.pyplot as plt

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager
from puzzle.parser.fromLayer import FromLayer, ParamPuzzle
from puzzle.parser.fromSketch import FromSketch
from puzzle.solver.simple import Simple

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')

# ==[1.1] Create an improcessor to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                           cv2.GaussianBlur, ((3, 3), 0,),
                           cv2.Canny, (30, 200,),
                           improcessor.basic.thresh, ((10, 255, cv2.THRESH_BINARY),))

theDet = FromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

# ==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer(ParamPuzzle(areaThresholdLower=5000))

theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[1.3] Display the solution board
#
f, axarr = plt.subplots(1, 2)
bSource = theBoardSol.toImage(ID_DISPLAY=True)
axarr[0].imshow(bSource)
axarr[0].title.set_text('Source solution board')

# ==[2] Create an Grid instance and explode it
#

print('Running through test cases. Will take a bit.')

theGrid = Gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=ParamGrid(areaThresholdLower=5000))

epImage, epBoard = theGrid.explodedPuzzle(dx=100, dy=100)

axarr[1].imshow(epImage)
axarr[1].title.set_text('Exploded view')

# ==[3] Create match by manager
#
theManager = Manager(theBoardSol)
theManager.process(epBoard)

# ==[4] Create simple solver and set up the match
#
theSolver = Simple(Gridded(theBoardSol), Gridded(epBoard))

theSolver.setMatch(theManager.pAssignments)

# ==[5] Start the solver to take turns, display the updated board.
#

plt.ion()
fh = plt.figure()

# saveMe = True
saveMe = False

if saveMe:
    f.savefig(cpath + f'/data/theBoardExplode.png')

finishFlag = False
i = 0

while 1:

    # Since we use the same instance in the simulator and the solver,
    # it will update automatically
    theSolver.current.display(fh=fh, ID_DISPLAY=True)
    fh.suptitle(f'Step {i}', fontsize=20)
    plt.pause(1)

    if finishFlag:
        break
    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    if saveMe:
        fh.savefig(cpath + f'/data/15pExplode_step{str(i).zfill(2)}.png')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='order')

    if plan[0] is None:
        print('All the matched puzzle pieces have been in position. No move.')
        finishFlag = True
    else:

        piece_id = plan[0][0]
        piece_index = plan[0][1]
        action_type = plan[0][2]
        action = plan[0][3]

        if action_type == 'rotate':
            print(f'Rotate piece {piece_id} by {int(action)} degree')
            theSolver.current.pieces[piece_index] = theSolver.current.pieces[piece_index].rotatePiece(
                action)
        elif action_type == 'move':
            print(f'Move piece {piece_id} by {action}')
            theSolver.current.pieces[piece_index].setPlacement(action, offset=True)

    i = i + 1
plt.ioff()
# plt.draw()

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/15pExplode.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/15pExplode_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)

#
# ============================ 15pExplode_simple ===========================
