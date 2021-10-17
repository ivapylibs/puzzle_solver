#!/usr/bin/python3
# ============================ realSolver_basic ===========================
#
# @brief    Test script with command from the solver. (real)
#
# ============================ realSolver_basic ===========================

#
# @file     realSolver_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/10/16  [created]
#
# ============================ realSolver_basic ===========================


import glob
import os

import cv2
import imageio
# ==[0] Prep environment
import matplotlib.pyplot as plt

from puzzle.builder.gridded import gridded, paramGrid
from puzzle.manager import manager, managerParms
from puzzle.piece.sift import sift
from puzzle.simulator.basic import basic
from puzzle.solver.simple import simple
from puzzle.utils.imageProcessing import preprocess_real_puzzle

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Read the source image and template.
#
# theImageSol = cv2.imread(cpath + '/data/puzzle_real_sample/Exploded_meaBoard.png')
theImageSol = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/Exploded_mea_0.png')

theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

# theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample/ExplodedWithRotationAndExchange_meaBoard.png')
# theImageMea = cv2.imread(cpath + '/data/puzzle_real_sample/ExplodedWithRotation_meaBoard.png')
# theImageMea = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/ExplodedWithRotationAndExchange_mea_0.png')
theImageMea = cv2.imread(cpath + '/../../testing/data/puzzle_real_sample_black/ExplodedWithRotation_mea_0.png')

theImageMea = cv2.cvtColor(theImageMea, cv2.COLOR_BGR2RGB)

# ==[1.1] Create an improcessor to obtain the mask.
#
theMaskSol = preprocess_real_puzzle(theImageSol)
theMaskMea = preprocess_real_puzzle(theImageMea, verbose=False)

# ==[2] Create a Grid instance.
#
print('Running through test cases. Will take a bit.')

# cv2.imshow('debug', theMaskMea)
# cv2.waitKey()
theGrid_Sol = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol,
                                             theParams=paramGrid(areaThreshold=1000, reorder=True))
theGrid_Mea = gridded.buildFrom_ImageAndMask(theImageMea, theMaskMea,
                                             theParams=paramGrid(areaThreshold=1000, reorder=True))

# ==[3] Create a manager
#
# theManager = manager(theGrid_src, managerParms(matcher=edge()))

theManager = manager(theGrid_Sol, managerParms(matcher=sift()))
theManager.process(theGrid_Mea)

# ==[4] Create simple sovler and set up the match
#
theSolver = simple(theGrid_Sol, theGrid_Mea)

theSolver.setMatch(theManager.pAssignments, theManager.pAssignments_rotation)

# ==[5] Create a simulator for display
#
theSim = basic(theGrid_Mea)

# ==[6] Start the solver to take turns, display the updated board.
#

plt.ion()

# saveMe = True
saveMe = False

FINISHED = False
i = 0

while 1:

    # Since we use the same instance in the simulator and the solver,
    # it will update automatically
    theSim.display(ID_DISPLAY=True)

    theSim.fig.suptitle(f'Step {i}', fontsize=20)
    plt.pause(1)

    if FINISHED:
        break
    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    if saveMe:
        theSim.fig.savefig(cpath + f'/data/realSolver_step{str(i).zfill(2)}.png')

    print(f'Step {i + 1}:')
    FINISHED = theSolver.takeTurn(defaultPlan='order')

    i = i + 1

cv2.waitKey()
plt.ioff()
# plt.draw()



if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/realSolver.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/realSolver_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)

#
# ============================ realSolver_basic ===========================
