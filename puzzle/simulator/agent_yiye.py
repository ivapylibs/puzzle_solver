# ========================= puzzle.simulator.agent ========================
#
# @class    puzzle.simulator.agent
#
# @brief    The agent simulates a subject to solve the puzzle task.
#           It takes the perceived board and the solution board,
#           and plan the next step
#
# ========================= puzzle.simulator.agent ========================
#
# @file     agent_yiye.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/08/29
#
#
# ========================= puzzle.simulator.agent ========================

from puzzle.builder.board import Board
from puzzle.piece.template import Template
from puzzle.simulator.action import Actions
from puzzle.simulator.planner import Planner_Base


class Appearance(Template):
    """
    @brief  The Appearance agent class contains the basic appearance information about the agent
            It inherit the puzzle.piece.template class so that it can be treated as a special piece
    
    TODO: so far haven't thought of features need to be added to the template. Add if needed
    """

    def __init__(self, y=None, r=(0, 0), id=None):
        super().__init__(y=y, r=r, id=id)


class Agent(Actions):

    def __init__(self, app: Appearance, planner: Planner_Base = None):
        """
        @brief  The Agent class equip the Base with the actions and the planning ability

        Args:
            app: An appearance instance.
            planner: A planner instance (like a solver)
        """
        self.app = app
        super().__init__(loc=self.app.rLoc)
        # self.app.rLoc = self.loc

        # planner
        self.planner = planner

        # the short-term memory of the actions to be executed to accomplish a plan
        self.cache_actions = []
        self.cache_action_args = []

    def setSolBoard(self, solBoard):
        """
        @brief  Set the solution board for the Agent to refer to during the puzzle solving process.
                It will update the solution board to the planner it used,
                which includes both manager and solver

        Args:
            solBoard: The solution board
        """
        self.planner.setSolBoard(solBoard)

    def setPlanner(self, planner: Planner_Base):
        self.planner = planner

    def process(self, meaBoard: Board, execute=True):
        """
        @brief  Process the current perceived board to produce the next action.

        Args:
            meaBoard: The measured board.
            execute: Execute an action or not. If not, will only attempt to plan.


        Returns:
            theSuccessFlag(Whether future actions are planned and executed) & action(The action label) & action_arg(The action arguments. If it is piece, then this will be its index in the board)
        """

        assert self.planner is not None, \
            "The planner can not be None, or the agent has no brain! \
                Please use the setPlanner function to get a planner"
        theSuccessFlag = False

        # if there are no cached actions, plan new actions
        if len(self.cache_actions) == 0:
            flag, actions, action_args = self.planner.process(meaBoard=meaBoard)
            if not flag:
                # If the planning is not successful, return False, None, None
                return theSuccessFlag, None, None
            else:
                # If the planning is successful, update cached actions
                theSuccessFlag = True
                self.cache_actions = actions
                self.cache_action_args = action_args
        # If there exists planned actions, then planning is successful
        else:
            theSuccessFlag = True

        # Execute the next action
        if execute:
            next_action, next_arg = self.execute_next(meaBoard)
            return theSuccessFlag, next_action, next_arg
        else:
            return theSuccessFlag, None, None

    def pop_action(self):
        """
        Pop out the next action and action argument WITHOUT executing them

        @param[out]  next_action         The next action label
        @param[out]  next_arg            The next action's argument
        """
        next_action = self.cache_actions.pop(0)
        next_arg = self.cache_action_args.pop(0)
        return next_action, next_arg

    def execute_next(self, meaBoard):
        """
        This function executes the next cached action

        @param[in]  next_action         The next action label
        @param[in]  next_arg            The next action's argument
        """
        next_action, next_arg = self.pop_action()
        next_arg_return = next_arg  # since next arg might be changed

        # Execute the action
        self.execute(next_action, next_arg, board=meaBoard)

        return next_action, next_arg_return

    def execute(self, action_label, action_param=None, board=None):
        """
        Execute an action given the action label and parameter

        Overwrite the execute function since we need to keep the self.app.rLoc updated
        NOTE:This is necessary only when we are using the puzzle.template as the appearance model
        """

        # if it is pick action, then get the puzzle piece as the real parameter
        if action_label == "pick":
            # sanity check. Make sure the arg is int (index)
            assert isinstance(action_param, int) and (board is not None)
            action_param = board.pieces[action_param]

        if action_param is None:
            self.ACTION_LABELS[action_label]()
        else:
            self.ACTION_LABELS[action_label](action_param)
        self.app.rLoc = self.loc

    def placeInImage(self, img, offset=[0, 0], CONTOUR_DISPLAY=True):
        self.app.placeInImage(img, offset, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

    @staticmethod
    def buildSphereAgent(radius, color, rLoc=None, planner: Planner_Base = None):
        app_sphere = Template.buildSphere(radius, color, rLoc)
        return Agent(app_sphere, planner)

    @staticmethod
    def buildSquareAgent(size, color, rLoc=None, planner: Planner_Base = None):
        app_Square = Template.buildSquare(size, color, rLoc)
        return Agent(app_Square, planner)
