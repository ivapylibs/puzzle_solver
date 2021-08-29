#========================= puzzle.simulator.agent ========================
#
# @class    puzzle.simulator.agent
#
# @brief    The agent simulates a subject to solve the puzzle task.
#           It takes the perceived board and the solution board,
#           and plan the next step
#
#========================= puzzle.simulator.agent ========================

#
# @file     agent.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/08/29
#
#
#========================= puzzle.simulator.agent ========================



class Base():
    """
    The base defines all the atomic actions that an agent can execute.
    """
    def __init__(self):
        pass

    def move(self, targetLoc):
        pass

    def pick(self, piece):
        pass
    
    def place(self, piece):
        pass

    def pause(self):
        pass

class Agent(Base):
    """
    In addition to the atomic actions, the 
    """
    def __init__(self):
        super().__init__()

        # the short-term memory of the actions to be executed to accomplish a plan
        self.memory = None
    
    def plan(self, board):
        """
        Plan according to the perceived board and the solution board.
        It outputs a sequence of action labels
        """
        pass
    
    def process(self, board):
        """
        Process the current perceived board to produce the next action
        """
        action = None
        return action