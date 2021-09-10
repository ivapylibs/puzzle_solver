#========================= puzzle.simulator.simTimeless ========================
#
# @class    puzzle.simulator.SimTimeless
#
# @brief    The simulator that simulate the puzzle solving process
#           without any time effect.
#           The agent will observe the board and attempt to solve it until finished
#
#========================= puzzle.simulator.simTimeless ========================

#
# @file     simTimeless.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/10
#
#
#========================= puzzle.simulator.simTimeless ========================

from puzzle.board import board
from puzzle.simulator.agent import Agent

class SimTimeLess():
    """
    @brief: The timeless simulator class that simulates the puzzle solving progress.

    The class stores an initial board, a solution board, and an agent instance.
    During the simulation, the simulator will execute the following process:
    1. Let the agent observe the board
    2. Let the agent process the board, which means:
        2.1 Plan actions if don't know what to do (no more stored actions)
        2.2 Execute the next planned actions
    3. If no more process result, meaning no more plans or actions to be executed,
        then end the simulation. Otherwise repreat the above process

    @param[in]  init_board          The initial board
    @param[in]  sol_board           The solution board
    @param[in]  agent               The puzzle solving agent
    """
    def __init__(self, init_board:board, sol_board:board, agent:Agent):
        self.meaBoard = init_board  # the initial measured board is the init_board
        self.sol_board = sol_board
        self.agent = agent

        # let the agent be aware of the solution board
        self.agent.setSolBoard(sol_board)
    
    def simulate(self):
        pass

    def visualize(self):
        pass