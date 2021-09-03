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

from puzzle.piece.template import template
from puzzle.simulator.action import Actions
from puzzle.simulator.planner import Base as planner_base

class Apperance(template):
    """
    @brief  The Appearance agent class contains the basic appearance information about the agent
            It inherit the puzzle.piece.template class so that it can be treated as a special piece
    
    TODO: so far haven't thought of features need to be added to the template. Add if needed
    """
    def __init__(self, y= None, r = (0, 0), id = None):
        super().__init__(y=y, r=r, id=id)


class Agent(Actions):
    """
    The Agent class equip the Base with the actions and the planning ability
    """

    def __init__(self, app:Apperance, planner:planner_base):
        self.app = app
        super().__init__(loc=self.app.rLoc)

        # the short-term memory of the actions to be executed to accomplish a plan
        self.cache_actions = None
    
    def setSolBoard(self):
        """
        Set the solution board for the Agent to refer to during the puzzle solving process
        """
        pass
    
    def process(self, meaBoard):
        """
        Process the current perceived board to produce the next action
        """
        actions = None
        self.cache_actions = actions
        pass

    def placeInImage(self, img, offset, CONTOUR_DISPLAY):
        self.app.placeInImage(img, offset, CONTOUR_DISPLAY=CONTOUR_DISPLAY)
    
    @staticmethod
    def buildSphereAgent(radius, color, rLoc=None):
        app_sphere = template.buildSphere(radius, color, rLoc)
        return Agent(app_sphere)

    @staticmethod
    def buildSquareAgent(size, color, rLoc=None):
        app_Square = template.buildSquare(size, color, rLoc)
        return Agent(app_Square)