#!/usr/bin/python3
# ============================ lineArrange01 ===========================
#
# @brief    Test script for the basic functions of the lineArrange simulator
#
#
# ============================ lineArrange01 ===========================

#
# @file     linArrange01.py
#
# @author   Yiye Chen,             yychen2019@gatech.edu
# @date     2021/08/29
#
# ============================ lineArrange ===========================


import os
from copy import deepcopy

# ==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.board import board
from puzzle.piece.template import template
from puzzle.simulator.agent import Agent
from puzzle.simulator.lineArrange import lineArrange

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Create the simulator
# parameters
canvas_size = 200
num_pieces = 4
init_x = 140
target_x = 40
init_agent_loc = [100, 50]

canvas = np.ones((canvas_size, canvas_size, 3), dtype=np.uint8) * 255

# [1.1] initBoard 
num_pieces = 4
init_board = board()
for i in range(num_pieces):
    piece = template.buildSquare(20, (255, 0, 0), rLoc=(140, int((i + 1) / (num_pieces + 1) * canvas_size)))
    init_board.addPiece(piece)

# ==[2] Create a simulatior
#
agent = Agent.buildSphereAgent(8, (0, 0, 255), rLoc=init_agent_loc)
lineArrange_simulator = lineArrange.buildSameX(target_x, init_board, initHuman=agent)

# ==[3] Verify the target locations
#

# ==[3.1] Display the original board
#
f, axes = plt.subplots(1, 2)
init_scene = deepcopy(canvas)
for i in range(num_pieces):
    lineArrange_simulator.initBoard.pieces[i].placeInImage(init_scene)
axes[0].imshow(init_scene)
axes[0].set_title("The initial scene")

# ==[3.2] Display the target board
#
sol_scene = deepcopy(canvas)
for i in range(num_pieces):
    lineArrange_simulator.solBoard.pieces[i].placeInImage(sol_scene)
axes[1].imshow(sol_scene)
axes[1].set_title("The solution scene")

plt.show()

#
# ============================ basic01_usage ===========================
