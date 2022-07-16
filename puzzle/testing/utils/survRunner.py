"""

    @brief          Surveillance runner that wraps the basic functionality of the surveillance system
                    required for examining the puzzle solving.

                    Is a copy and simplification of the surveillance ros deployment runner for the unit test purpose:
                    https://github.gatech.edu/VisMan/Mary_ROS/blob/master/ros/surveillance/script/surv_runner.py

    @author         Yiye Chen,          yychen2019@gatech.edu
    @date           07/14/2022

"""
import numpy as np
import os
import yaml
import time
import matplotlib.pyplot as plt
import copy

# Surveillance system
from Surveillance.deployment.Base import BaseSurveillanceDeploy
from Surveillance.deployment.Base import Params as bParams


class SurvRunner():
    """
    Args
        test_rgb_tpic (str):        The topic name for publishing the rgb data
        test_dep_topic (str):       The topic name for publishing the depth data
        calib_data_name (str):      The rosbag name for storing the calibration data
        mary_control (bool):        Whether want to control the robot
    """
    def __init__(self, surv_args) -> None:

        # args
        surv_args = self._parse_record_args(surv_args)
        self.rgb_topic = surv_args["rgb_topic"]
        self.dep_topic = surv_args["dep_topic"]

        self.calib_bag_path = surv_args["calib_data_path"]

        ### build the surveillance
        configs = bParams(
            markerLength = 0.075,
            W = 1920,               # The width of the frames
            H = 1080,                # The depth of the frames
            reCalibrate = False,
            ros_pub = False,         # Publish the test data to the ros or not
            test_rgb_topic = self.rgb_topic,
            test_depth_topic = self.dep_topic,
            # activity_topic= test_activity_topic,
            visualize = True,
            run_system= True,        
            # activity_label = args.act_collect
            # Postprocessing
            bound_limit = [200,60,50,50], # @< The ignored region area. Top/Bottom/Left/Right. E.g., Top: 200, 0-200 is ignored.
            mea_mode = 'test', # @< The mode for the postprocessing function, 'test' or 'sol'.
            mea_test_r = 150,  # @< The circle size in the postprocessing for the measured board.
        )
        self.surv = BaseSurveillanceDeploy.buildPub(configs, bag_path=self.calib_bag_path)

        bg_seg = self.surv.scene_interpreter.bg_seg


        print("\n=========== The Surveillance Calibration finished===========")
        print("\n")

    def _parse_record_args(self, surv_args):

        # If no existing calib data, report error 
        calib_data_path = surv_args["calib_data_path"]
        assert os.path.exists(calib_data_path), "The surveillance calibration data is not found: {}".format(surv_args["calib_data_path"])

        return surv_args


    def run(self):
        """NOTE: a run function here might not be a good idea.
        Loses flexibility
        """
        while(True):
            # obtain and store the data
            rgb, dep = self.get_data()

            # process the data
            self.process(rgb, dep)

    
    def get_data(self):
        rgb, dep, status = self.surv.imgSource()
        self.surv.test_rgb = rgb
        self.surv.test_depth = dep

        return rgb, dep
    
    def process(self, rgb, dep):
        self.surv.process(rgb, dep, puzzle_postprocess=True)

