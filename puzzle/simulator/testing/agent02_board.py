# ========================= agent02_board ========================
#
# @brief    The test script for the agent functions on the board
#       
#           On top of the agent01_piece that verifies the funcionality 
#           of the atomic actions, this script test the planner.
#           The planner will use a customized manager and solver 
#           (namely the manager&solver for the lineArrangement)
#           to plan the action according to the solution board,
#           so those will also be tested
#           
#
# ========================= agent02_board ========================

#
# @file     agent02_board.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/02
#
#
# ========================= agent02_board ========================

from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np

from puzzle.board import board
from puzzle.piece.template import template
from puzzle.simulator.agent import Agent
from puzzle.simulator.lineArrange import solver_LA, manager_LA
##==[0] Prepare
# [0.1] environment
from puzzle.simulator.planner import Planner_Fix


# [0.2 utility function]
def vis_scene(board, canvas, agent=None, agent_color=None, title=None, ax=None):
    """
    @param[in]  agent_color         allow overwrite the agent's color, which is temporary and will not be saved after visualization
    """
    if ax is None:
        ax = plt.gca()
    canvas_vis = deepcopy(canvas)
    # add the board
    for piece in board.pieces:
        piece.placeInImage(canvas_vis)

    # add the agent
    if agent is not None:
        # change color?
        if agent_color is not None:
            appear_cache = deepcopy(agent.app.y.appear)
            new_appear = np.repeat(pick_color[np.newaxis, :], repeats=agent.app.y.appear.shape[0], axis=0)
            agent.app.y.appear = new_appear
        # visualize
        agent.placeInImage(canvas_vis, CONTOUR_DISPLAY=False)

    # show
    ax.imshow(canvas_vis)
    ax.set_title(title)

    # restore the color
    if (agent is not None) and (agent_color is not None):
        agent.app.y.appear = appear_cache


# ==[1] Prepare

# Prepare the boards and the canvas(visualization)
init_piece_loc = [140, 100]
init_agent_loc = [100, 50]
target_piece_loc = [40, 100]
pick_color = np.array((0, 255, 0), dtype=np.uint8)

canvas = np.ones((200, 200, 3), dtype=np.uint8) * 255
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

# visualize
fh, axes = plt.subplots(1, 2, figsize=(10, 5))
fh.suptitle("The puzzle to solve")
# plt.pause(7)    # give me time to record the gif
canvs_vis = canvas
vis_scene(init_board, canvas, title="Initial board", ax=axes[0])
vis_scene(sol_board, canvas, title="Solution board", ax=axes[1])
plt.pause(1)

# ==[2] Agent observe and plan

plt.figure()

succ, _, _ = agent.process(init_board, execute=False)
# verify the manager function
assigns = manager.pAssignments
assert all([np.all(assign == np.array((idx, idx))) for idx, assign in enumerate(assigns)])
print("The mea-to-sol assignment: {}, which is correct!".format(assigns))

# visualize
ax = plt.gca()
vis_scene(init_board, canvas, agent=agent, title="Initial Scene", ax=ax)
plt.pause(1)

# plt.pause(7)    #<- give me time to setup for the gif recording.


# ==[3] Agent execute the action until finishing the puzzle

succ = True
while succ:
    # plan and execute
    succ, action, action_arg = agent.process(init_board, execute=True)
    if not succ:
        # if not success, will lead to termination
        continue

    # visualize
    if action == 'pick':
        title = "Actions: {}. Argument: the piece of index {}".format(action, action_arg)
    else:
        title = "Action: {}. Argument: {}".format(action, action_arg)
    ax = plt.gca()
    if agent.cache_piece is not None:
        vis_scene(init_board, canvas, agent=agent, agent_color=pick_color, title=title, ax=ax)
    else:
        vis_scene(init_board, canvas, agent=agent, title=title, ax=ax)
    plt.pause(1)
