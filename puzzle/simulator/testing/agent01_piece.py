# ========================= agent01_piece ========================
#
# @brief    The test script for the agent functions on the pieces.
#           It tests the atomic actions on a single puzzle piece
#
# ========================= agent01_piece ========================

#
# @file     agent01_piece.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/02
#
#
# ========================= agent01_piece ========================

from copy import deepcopy

# ==[0] Prepare
# [0.1] environment
import matplotlib.pyplot as plt
import numpy as np

from puzzle.piece.template import template
from puzzle.simulator.agent import Agent


# [0.2 utility function]
def vis_scene(piece, agent, canvas, agent_color=None, title=None, ax=None):
    """
    @param[in]  agent_color         allow overwrite the agent's color, which is temporary and will not be saved after visualization
    """
    if ax is None:
        ax = plt.gca()
    canvas_vis = deepcopy(canvas)
    # change color?
    if agent_color is not None:
        appear_cache = deepcopy(agent.app.y.appear)
        new_appear = np.repeat(pick_color[np.newaxis, :], repeats=agent.app.y.appear.shape[0], axis=0)
        agent.app.y.appear = new_appear
    # visualize
    piece.placeInImage(canvas_vis)
    agent.placeInImage(canvas_vis, CONTOUR_DISPLAY=False)
    ax.imshow(canvas_vis)
    ax.set_title(title)
    # restore the color
    if agent_color is not None:
        agent.app.y.appear = appear_cache


# ==[1] Prepare

# Prepare the piece, agent, and the canvas
init_piece_loc = [140, 100]
init_agent_loc = [100, 50]
target_piece_loc = [40, 100]
pick_color = np.array((0, 255, 0), dtype=np.uint8)

canvas = np.ones((200, 200, 3), dtype=np.uint8) * 255
piece = template.buildSquare(20, (255, 0, 0), rLoc=init_piece_loc)
agent = Agent.buildSphereAgent(8, (0, 0, 255), rLoc=init_agent_loc)

# visualize
plt.figure()
# plt.pause(7)    # give me time to record the gif
ax = plt.gca()
vis_scene(piece, agent, canvas, title="Initial scene", ax=ax)
plt.pause(1)

# ==[2] move to the piece location
agent.execute("move", piece.rLoc)
vis_scene(piece, agent, canvas, title="Reach to the piece", ax=ax)
plt.pause(1)

# ==[3] pick the piece
agent.execute("pick", piece)
agent.pick(piece)
vis_scene(piece, agent, canvas, agent_color=pick_color, title="Pick the piece up", ax=ax)
plt.pause(1)

# ==[4] move to another location
agent.execute("move", target_piece_loc)
vis_scene(piece, agent, canvas, agent_color=pick_color, title="Move to the target location", ax=ax)
plt.pause(1)

# ==[5] place the piece
agent.execute("place")
vis_scene(piece, agent, canvas, title="Place the piece", ax=ax)
plt.pause(1)

# ==[6] move away
agent.execute("move", init_agent_loc)
vis_scene(piece, agent, canvas, title="Move back to the initial location", ax=ax)
plt.pause(1)

plt.show()
