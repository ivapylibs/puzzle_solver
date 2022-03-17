# ========================= puzzle.simulator.simTime ========================
#
# @class    puzzle.simulator.SimTime
#
# @brief    The simulator that also simulates the time effect.
#           Each simulation step will have a fixed time length,
#           and the speed of the agent movement and the length
#           of the agent's pause will be simulated.
#
# ========================= puzzle.simulator.simTime ========================
#
# @file     simTime_yiye.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/10
#
#
# ========================= puzzle.simulator.simTime ========================


import math
from dataclasses import dataclass

import numpy as np

from puzzle.builder.board import Board
from puzzle.simulator.agent_yiye import Agent
from puzzle.simulator.simTimeless_yiye import SimTimeLess, ParamST


@dataclass
class ParamSTL(ParamST):
    """
    @param  canvas_H            The height of the whole scene
    @param  canvas_W            The width of the whole scene
    ------------------ Below are related to time ---------------------
    @param  delta_t             Unit: s(econd). The time length for a simulation step.
    @param  speed               Unit: pixel/s. The speed of the agent movement
    @param  static_duration     Unit: s(econd). The duration of the static actions
    """
    delta_t: float = 0.01
    speed: float = 200
    static_duration: float = 0.5


class SimTime(SimTimeLess):
    """
    @brief: The time-aware simulator that simulate the time effects

    On top of the timeless simulator,this simulator simulates the time when
    executing the agent action. To be more specific:
    1. Each simulation step is assumed to have a fixed time length
    2. The agent dynamic actions (e.g. Move) is assumed to have a fixed speed
    3. The agent static actions (e.g. Pause, Pick, Place) are assumed to have a fixed
        duration

    @param[in]  init_board          The initial board
    @param[in]  sol_board           The solution board
    @param[in]  agent               The puzzle solving agent
    @param[in]  param               ParamST instance. It stores the parameters
                                    related to the time effect
    """

    def __init__(self, init_board: Board, sol_board: Board, agent: Agent,
                 param: ParamSTL = ParamSTL()):
        super().__init__(init_board, sol_board, agent, param=param)
        # store the parameters
        self.param = param

        # cached action, argument, and time
        self.cache_action = None  # The next action to execute
        self.cache_arg = None  # The next action argument
        self.timer = -1  # The timer

    def simulate_step(self):
        """
        Overwrite the simulate_step function
        """

        SUCCESS = True  # < Whether the simulation is still successfully running
        finishFlag = False  # < Whether the current cached action has been finishFlag

        if self.cache_action is None:
            # if no more stored action, meaning the last action has been executed.
            # Then will let the agent plan again (if has unfinishFlag plans then will simply do nothign)
            # and pop out the new action
            SUCCESS, _, _ = self.agent.process(self.cur_board, execute=False)
            if SUCCESS:
                self.cache_action, self.cache_arg = self.agent.pop_action()

                # If the next action to executed is static, then start the timer.
                if self.cache_action != "move":
                    self.timer = self.param.static_duration
            else:
                return False

        elif self.cache_action == "move":
            # The move action
            finishFlag = self._move_step(self.cache_arg)
        else:
            # The static actions
            finishFlag = self._pause_step()

        # if the cached action is finishFlag, reset the cache and the timer
        if finishFlag:
            self.reset_cache()

        return SUCCESS

    def _move_step(self, target_loc):
        """
        Move a step given the target location
        Note that the target location might not be reachable within a step's time length

        @param[in]  target_loc          The target location of the "move"

        @param[out] finishFlag        Binary. Indicator of whether the target location
                                        has been reached
        """
        # distance
        delta_x = target_loc[0] - self.agent.loc[0]
        delta_y = target_loc[1] - self.agent.loc[1]
        distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

        # determine where to end up
        step_loc = np.array([-1, -1])
        if distance >= self.param.delta_t * self.param.speed:
            x_step = delta_x * (self.param.delta_t * self.param.speed) / distance
            y_step = delta_y * (self.param.delta_t * self.param.speed) / distance
            step_loc[0] = self.agent.loc[0] + x_step
            step_loc[1] = self.agent.loc[1] + y_step
            finishFlag = False
        else:
            step_loc[0] = target_loc[0]
            step_loc[1] = target_loc[1]
            finishFlag = True

        # execute
        self.agent.execute("move", step_loc)

        return finishFlag

    def _pause_step(self):
        assert self.cache_action != "move"

        # if have not been executed, then execute first before pause there
        if self.timer == self.param.static_duration:
            self.agent.execute(self.cache_action, self.cache_arg, board=self.cur_board)

            # continue to run the timer
        self.timer -= self.param.delta_t

        # if timer is below zero, then it is up!
        if self.timer <= 0:
            finishFlag = True
        else:
            finishFlag = False

        return finishFlag

    def reset_cache(self):
        self.cache_arg = None
        self.cache_action = None
        self.timer = -1