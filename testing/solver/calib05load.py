#!/usr/bin/python3
#================================ calib05load ================================
## @file
# @brief    Load Calibrated puzzle test script.
#
# @ingroup  TestPuzzle_Solver
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#
# @date     2025/02/15  
#
# @quitf
#================================ calib05load ================================

#==[0] Prep the environment. From most basic to current implementation.
#
import os
import cv2
import numpy as np
import argparse
import pkg_resources

import ivapy.display_cv as display

import puzzle.builder.calibrate as puzzle


#==[1] Load calibrated puzzle solution.
#
solPuzzle = puzzle.Calibrate.load("calib04save.hdf5")


#==[2] Confirm data correctly obtained by visualizing it.
#
print("There are " + str(solPuzzle.size()) + " pieces.");

display.rgb(solPuzzle.puzzIm,window_name='Input')
display.gray(solPuzzle.puzzLb.astype(np.uint8), window_name="Label")
solPuzzle.display_cv(window_name='Puzzle')
display.wait()

#
#================================ calib05load ================================
