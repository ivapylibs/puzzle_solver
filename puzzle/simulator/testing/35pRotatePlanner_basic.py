#!/usr/bin/python3
# ============================ 35pRotatePlanner_basic ===========================
#
# @brief    Test script with command from the planner. Test for success rate. (35p img)
#
# ============================ 35pRotatePlanner_basic ===========================

#
# @file     35pRotatePlanner_basic.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/1/26  [created]
#
# ============================ 35pRotatePlanner_basic ===========================

# Change the Settings here

ROTATION_ENABLED = True
# ROTATION_ENABLED = False

NUM = 50

# ==[0] Prep environment
import glob
import os
import cv2
import imageio
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift
from puzzle.simulator.basic import Basic, ParamBasic
from puzzle.solver.simple import Simple
from puzzle.utils.puzzleProcessing import create_synthetic_puzzle
from puzzle.simulator.planner import Planner

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# Debug only
# np.random.seed(100)

Image_list = ['balloon.png', 'church.jpg', 'cocacola.jpg', 'duck.jpg', 'map.jpg']
Res = np.zeros(len(Image_list))

for trial_index in range(NUM):

    print(f'Trial {trial_index}:')

    # ==[1] Read the source image and template.
    #
    # theImageSol = cv2.imread(cpath + '/../../testing/data/' + Image_list[np.random.randint(0,len(Image_list))])

    # NUM/len(Image_list) for each image
    theImageSol = cv2.imread(cpath + '/../../testing/data/' + Image_list[trial_index%len(Image_list)])

    theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_35p.png')
    # theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')

    theGridMea, theGridSol, gt_pAssignments = create_synthetic_puzzle(theImageSol=theImageSol, theMaskSol_src=theMaskSol_src,
                                                     ROTATION_ENABLED=ROTATION_ENABLED,verbose=False)

    # ==[2] Create a manager & simple solver and integrate them into a planner
    #

    theManager = Manager(theGridSol, ManagerParms(matcher=Sift()))
    theSolver = Simple(theGridSol, theGridMea)
    thePlanner = Planner(theSolver, theManager, ParamGrid(areaThresholdLower=1000))

    # ==[3] Create a simulator for display
    #
    theSim = Basic(theGridMea, thePlanner=thePlanner, theParams=ParamBasic(3000,6000))

    # ==[4] Start the solver to take turns, execute the plan, and display the updated board.
    #

    plt.ion()

    # saveMe = True
    saveMe = False

    if saveMe:
        filename_list = glob.glob(cpath + f'/data/35pRotatePlanner_step*.png')
        for filename in filename_list:
            os.remove(filename)

    finishFlag = False
    i = 0

    while 1:

        # Since we use the same instance in the simulator and the solver,
        # it will update automatically.
        theSim.display(ID_DISPLAY=True, BOUNDING_BOX=False)

        theSim.fig.suptitle(f'Step {i}', fontsize=20)
        plt.pause(1)

        if finishFlag:
            break
        if i == 0:
            # Display the original one at the very beginning
            print(f'The original measured board')

        if saveMe:
            theSim.fig.savefig(cpath + f'/data/35pRotatePlanner_step{str(i).zfill(3)}.png')

        print(f'Step {i + 1}:')

        # One Step
        plan = thePlanner.process(theSim.puzzle, COMPLETE_PLAN=True, SAVED_PLAN=False)

        # Step by step
        # plan = thePlanner.process(theSim.puzzle, COMPLETE_PLAN=False)

        finishFlag = theSim.takeAction(plan)

        i = i + 1

    # Call the progress to compare rLoc
    thePercent = theSim.progress(gt_pAssignments)
    print('Progress:', thePercent)

    Res[trial_index%len(Image_list)]+=float(thePercent.split('%')[0])/100.0

    plt.ioff()
    # plt.show()
    # plt.draw()
    plt.pause(1)
    plt.close()

    if saveMe:
        # Build GIF
        with imageio.get_writer(cpath + f'/data/35pRotatePlanner.gif', mode='I', fps=1) as writer:
            filename_list = glob.glob(cpath + f'/data/35pRotatePlanner_step*.png')
            filename_list.sort()
            for filename in filename_list:
                image = imageio.imread(filename)
                writer.append_data(image)

# ==[5] Print final result
Res = Res/(NUM/len(Image_list))
print('\nAverage result:\n')
for i in range(len(Image_list)):
    print(f'Average success rate for Image {i}:', '{:.1%}'.format(Res[i]))

#
# ============================ 35pRotatePlanner_basic ===========================
