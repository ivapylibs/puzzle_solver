#========================= puzzle.simulator.simTime ========================
#
# @class    puzzle.simulator.SimTime
#
# @brief    The simulator that also simulates the time effect.
#           Each simulation step will have a fixed time length,
#           and the speed of the agent movement and the length
#           of the agent's pause will be simulated.
#
#========================= puzzle.simulator.simTime ========================

#
# @file     simTime.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/09/10
#
#
#========================= puzzle.simulator.simTime ========================


from dataclasses import dataclass
from puzzle.board import board
from puzzle.simulator.agent import Agent
from puzzle.simulator.simTimeless import SimTimeLess

@dataclass
class ParamST:
    pass

class SimTime(SimTimeLess):
    """
    @brief: The time-aware simulator that simulate the time effects

    On top of the timeless simulator,this simulator simulates the speed when 
    executing the agent action 

    @param[in]  init_board          The initial board
    @param[in]  sol_board           The solution board
    @param[in]  agent               The puzzle solving agent
    @param[in]  param               ParamST instance. It stores the parameters
                                    related to the time effect
    """
    def __init__(self, init_board:board, sol_board:board, agent:Agent, 
                param: ParamST=ParamST()):
        super().__init__(init_board, sol_board, agent)
        # store the parameters
        self.param = param
    
    def simulate(self):
        """
        Overwrite the simulation step function
        """
        pass
