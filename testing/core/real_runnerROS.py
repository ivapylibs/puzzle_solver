#!/usr/bin/python
"""

    @brief:             Test and update the puzzle solver runner in a ROS wrapper.
                        Currently we only accept the option 3 in https://github.com/ivapylibs/Surveillance/blob/yunzhi/Surveillance/deployment/ROS/rosbag_runner.py

    @author:            Yunzhi Lin,          yunzhi.lin@gatech.edu
    @date:              11/24/2022[created]

"""

# ==[0] Prep environment
from dataclasses import dataclass
import copy
import os
from tkinter import Grid
import subprocess
import cv2
import time
import matplotlib.pyplot as plt
import message_filters
import numpy as np
import glob
import argparse
import threading
from std_msgs.msg import String

import rospy
import rosgraph

from puzzle.piece.template import Template, PieceStatus
from puzzle.runner import ParamRunner
from puzzle.runnerROS import RealSolverROS
from puzzle.utils.dataProcessing import convert_ROS2dict

from ROSWrapper.subscribers.Images_sub import Images_sub
from ROSWrapper.subscribers.String_sub import String_sub

from camera.utils.display import display_images_cv


# configs
postImg_topic = "/postImg"
visibleMask_topic = "/visibleMask"
hTracker_BEV_topic = "/hTracker_BEV"

# preparation
lock = threading.Lock()

def get_args():
    parser = argparse.ArgumentParser(description="puzzle solver runner")
    parser.add_argument("--puzzle_solver_SolBoard", default='caliSolBoard.obj',
                        help="The saving path to a .obj instance")
    parser.add_argument("--verbose", action='store_true',
                        help="Whether to debug the system.")
    args = parser.parse_args()

    return args

class ImageListener:
    def __init__(self, opt):

        self.opt = opt

        # Data captured
        self.RGB_np = None
        self.Mask_np = None
        self.hTracker_BEV = None

        self.rgb_frame_stamp = None
        self.rgb_frame_stamp_prev = None

        self.init_solution_flag = True

        # Build up the puzzle solver
        configs_puzzleSolver = ParamRunner(
            areaThresholdLower=1000,  # @< The area threshold (lower) for the individual puzzle piece.
            areaThresholdUpper=8000,  # @< The area threshold (upper) for the individual puzzle piece.
            pieceConstructor=Template,
            lengthThresholdLower=1000,
            BoudingboxThresh=(20, 100),  # @< The bounding box threshold for the size of the individual puzzle piece.
            tauDist=100,  # @< The radius distance determining if one piece is at the right position.
            hand_radius=200,  # @< The radius distance to the hand center determining the near-by pieces.
            tracking_life_thresh=15,
            # @< Tracking life for the pieces, it should be set according to the processing speed.
            # solution_area=[600,800,400,650], # @< The solution area, [xmin, xmax, ymin, ymax]. We will perform frame difference in this area to locate the touching pieces.
            # It is set by the calibration result of the solution board.
        )
        self.puzzleSolverROS = RealSolverROS(configs_puzzleSolver)

        # Initialize a subscriber for images
        Images_sub([postImg_topic, visibleMask_topic], callback_np=self.callback_rgbMask)

        # Initialize a subscriber for other info
        String_sub(hTracker_BEV_topic, String, callback_np=self.callback_hTracker_BEV)

        print("Initialization ready, waiting for the data...")

    def callback_rgbMask(self, arg_list):

        if self.opt.verbose:
            print("Get to the callback")

        RGB_np = arg_list[0]
        Mask_np = arg_list[1]
        rgb_frame_stamp = arg_list[2].to_sec()

        with lock:
            self.RGB_np = RGB_np.copy()
            self.Mask_np = Mask_np.copy()
            self.rgb_frame_stamp = copy.deepcopy(rgb_frame_stamp)

    def callback_hTracker_BEV(self, msg):

        info_dict = convert_ROS2dict(msg)
        hTracker_BEV = info_dict['hTracker_BEV']

        with lock:
            self.hTracker_BEV = hTracker_BEV if hTracker_BEV is None else np.array(hTracker_BEV)

    def run_system(self):

        with lock:

            if self.RGB_np is None:
                return

            rgb_frame_stamp = copy.deepcopy(self.rgb_frame_stamp)

            # Skip images with the same timestamp as the previous one
            if rgb_frame_stamp != None and self.rgb_frame_stamp_prev == rgb_frame_stamp:

                time.sleep(0.001)
                # if self.opt.verbose:
                #     print('Same timestamp')
                return
            else:
                self.rgb_frame_stamp_prev = rgb_frame_stamp
                RGB_np = self.RGB_np.copy()
                Mask_np = self.Mask_np.copy()
                hTracker_BEV = copy.deepcopy(self.hTracker_BEV)

                # Display
                display_images_cv([RGB_np[:, :, ::-1]], ratio=0.5, window_name="Source RGB")
                # cv2.waitKey(1)

                if  self.init_solution_flag:
                    print('Initializing the solution board...')
                    self.puzzleSolverROS.setSolBoard(RGB_np, self.opt.puzzle_solver_SolBoard)
                    self.init_solution_flag = False

                # Run the puzzle solver ROS
                self.puzzleSolverROS.process_ROS(RGB_np, Mask_np, hTracker_BEV)

                # Display
                display_images_cv(
                    [self.puzzleSolverROS.bMeasImage[:, :, ::-1], self.puzzleSolverROS.bTrackImage_SolID[:, :, ::-1],
                     self.puzzleSolverROS.bSolImage[:, :, ::-1]],
                    ratio=0.5, window_name="Measured/Tracked/Solution board")

                cv2.waitKey(1)

if __name__ == "__main__":

    args = get_args()

    # Start the roscore if not enabled
    if not rosgraph.is_master_online():
        roscore_proc = subprocess.Popen(['roscore'], shell=True)
        # wait for a second to start completely
        time.sleep(1)

    # Initialize the ROS node
    rospy.init_node('puzzle_solver')

    listener = ImageListener(args)

    while not rospy.is_shutdown():
        listener.run_system()