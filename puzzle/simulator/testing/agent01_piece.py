#========================= agent01_piece ========================
#
# @brief    The test script for the agent functions on the pieces
#
#========================= agent01_piece ========================

#
# @file     agent01_piece.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/02
#
#
#========================= agent01_piece ========================

#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
from copy import deepcopy

from puzzle.parser.fromLayer import fromLayer
from puzzle.simulator.basic import basic

#==[1] Prepare the piece, agent, and the canvas
