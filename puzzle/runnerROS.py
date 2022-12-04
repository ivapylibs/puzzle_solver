#!/usr/bin/python3
# ============================= puzzle.runnerROS =============================
#
# @class    puzzle.runnerROS
#
# @brief    A sub-wrapper class for deployment in the real-world cases.
#           We further add some minimal ROS support.
#
# ============================= puzzle.runnerROS =============================
#
# @file     runner.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/03/09 [created]
#
# ============================= puzzle.runnerROS =============================


# ==[0] Prep environment
from dataclasses import dataclass
import copy
import os
from tkinter import Grid
import cv2
import time
import matplotlib.pyplot as plt
import numpy as np
import glob
import rospy
from std_msgs.msg import String

from puzzle.builder.board import Board
from puzzle.builder.arrangement import Arrangement
from puzzle.builder.interlocking import Interlocking
from puzzle.builder.gridded import Gridded, ParamGrid
from puzzle.manager import Manager, ManagerParms
from puzzle.piece.sift import Sift
from puzzle.utils.dataProcessing import closestNumber, convert_dict2ROS
from puzzle.utils.imageProcessing import preprocess_real_puzzle
from puzzle.utils.puzzleProcessing import calibrate_real_puzzle
from puzzle.solver.simple import Simple
from puzzle.simulator.planner import Planner, ParamPlanner
from puzzle.piece.template import Template, PieceStatus
from puzzle.runner import RealSolver, ParamRunner

from ROSWrapper.publishers.Image_pub import Image_pub


# Publish topics
puzzle_solver_info_topic = "puzzle_solver_info"
status_history_topic = "status_history"
loc_history_topic = "loc_history"

bMeasImage_topic = "bMeasImage"
bTrackImage_topic = "bTrackImage"
bTrackImage_SolID_topic = "bTrackImage_SolID"

class RealSolverROS(RealSolver):
    def __init__(self, theParams=ParamRunner):

        super().__init__(theParams)

        # Some initializations
        self.plan = []

        # ROS support
        self.puzzle_solver_info_pub = rospy.Publisher(puzzle_solver_info_topic, String, queue_size=5)
        self.status_history_pub = rospy.Publisher(status_history_topic, String, queue_size=5)
        self.loc_history_pub = rospy.Publisher(loc_history_topic, String, queue_size=5)

        self.bMeasImage_pub = Image_pub(topic_name=bMeasImage_topic)
        self.bTrackImage_pub = Image_pub(topic_name=bTrackImage_topic)
        self.bTrackImage_SolID_pub = Image_pub(topic_name=bTrackImage_SolID_topic)

    def process_ROS(self, theImageMea, visibleMask, hTracker_BEV, run_solver=True, planOnTrack=False, verbose=False):
        """
        @brief Call the process function and publish the ROS message.

        Args:
            theImageMea: The input image (from the surveillance system).
            visibleMask: The mask image of the visible area (no hand/robot)(from the surveillance system).
            hTracker_BEV: The location of the hand in the BEV.
            run_solver: Run the solver or not.
            planOnTrack: Plan on the tracked board or not.
            verbose: If True, will display the detected measured pieces, from working or solution area.
        """
        # Save the plan
        self.plan = self.process(theImageMea, visibleMask, hTracker_BEV, run_solver=run_solver, planOnTrack=planOnTrack, verbose=verbose)

        # ROS support
        self.publish_ROS()

    def publish_ROS(self):
        """
        @brief Publish the ROS message for the runner.
        """

        # Have to process the saved information first for json
        plan_processed = []
        for command in self.plan:
            if command:
                plan_processed.append([command[0], command[1], command[2], command[3].tolist()])
            else:
                plan_processed.append(command)

        # status_history  e.g., k: [PieceStatus(Enum), PieceStatus(Enum), ...]
        status_history_processed = {}
        for k, v in self.thePlanner.status_history.items():
            status_history_processed[k] = [x.value for x in v]

        # loc_history  e.g., k: [array([x1, y1]), array([x2, y2]), ...]
        loc_history_processed = {}
        for k, v in self.thePlanner.loc_history.items():
            loc_history_processed[k] = [x.tolist() for x in v]

        # Wrap the board into a dictionary
        info_dict ={
            'plan': plan_processed,
            'solution_board_size': self.theManager.solution.size(),
            'progress': self.progress(),
        }

        # Publish the messages
        self.puzzle_solver_info_pub.publish(convert_dict2ROS(info_dict))
        self.status_history_pub.publish(convert_dict2ROS(status_history_processed))
        self.loc_history_pub.publish(convert_dict2ROS(loc_history_processed))

        # Publish the board images
        self.bMeasImage_pub.pub(self.bMeasImage)
        self.bTrackImage_pub.pub(self.bTrackImage)
        self.bTrackImage_SolID_pub.pub(self.bTrackImage_SolID)

#
# ========================== puzzle.runnerROS =========================

