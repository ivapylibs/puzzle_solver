# ========================= simTimeless01_usage ========================
#
# @brief    The test script for the basic timeless simulator
#
# ========================= simTimeless01_usage ========================
#
# @file     agent02_board.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/10
#
#
# ========================= simTimeless01_usage ========================

import matplotlib.pyplot as plt
import numpy as np

from puzzle.builder.board import board
from puzzle.piece.template import template
from puzzle.simulator.agent import Agent
from puzzle.simulator.lineArrange import solver_LA, manager_LA
##==[0] Prepare
# [0.1] environment
from puzzle.simulator.planner import Planner_Fix
from puzzle.simulator.simTimeless import SimTimeLess, ParamST

# ==[1] Prepare

# settings
init_piece_loc = [140, 100]
init_agent_loc = [100, 50]
target_piece_loc = [40, 100]
pick_color = np.array((0, 255, 0), dtype=np.uint8)

# Prepare the boards
init_board = board()
init_piece = template.buildSquare(20, (255, 0, 0), rLoc=init_piece_loc)
init_board.addPiece(init_piece)
sol_board = board()
sol_piece = template.buildSquare(20, (255, 0, 0), rLoc=target_piece_loc)
sol_board.addPiece(sol_piece)

# prepare the human agent 
agent = Agent.buildSphereAgent(8, (0, 0, 255), rLoc=init_agent_loc)
solver = solver_LA(sol_board, init_board)
manager = manager_LA(sol_board)
manager.set_pAssignments_board(init_board)
planner = Planner_Fix(solver, manager)
planner.setInitLoc(init_agent_loc)
agent.setPlanner(planner)

# prepare the simulator
param_sim = ParamST(
    canvas_H=200,
    canvas_W=200
)
simulator = SimTimeLess(init_board, sol_board, agent, param_sim)

# visualize
fh, axes = plt.subplots(1, 3, figsize=(15, 5))
fh.suptitle("The timeless Simulator")
# plt.pause(7)    # give me time to record the gif
simulator.visualize(mode="initBoard", title="The initial board", ax=axes[0])
simulator.visualize(mode="solBoard", title="The solution board", ax=axes[1])
simulator.visualize(mode="scene", title="The current scene", ax=axes[2])
plt.pause(1)

# ==[2] Simulate
simulator.simulate(
    vis=True,
    vis_pause_time=1,
    title="The current scene",
    ax=axes[2],
    pickColorA=pick_color
)
