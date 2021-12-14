# ========================= puzzle.simulator.simTimeless ========================
#
# @class    puzzle.simulator.SimTimeless
#
# @brief    The simulator that simulate the puzzle solving process
#           without any time effect.
#           The agent will observe the board and attempt to solve it until finished
#
# ========================= puzzle.simulator.simTimeless ========================
#
# @file     simTimeless.py
#
# @author   Yiye Chen,               yychen2019@gatech.edu
#           Yunzhi Lin,              yunzhi.lin@gatech.edu
# @date     2021/09/10 [created]
#           2021/11/25 [modified]
#
#
# ========================= puzzle.simulator.simTimeless ========================

import sys
from copy import deepcopy
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np

from puzzle.simulator.basic import Basic


# from puzzle.simulator.agent import Agent

@dataclass
class ParamSTL:
    """
    @param canvas_H             The height of the whole scene
    @param canvas_W             The width of the whole scene
    """
    canvas_H: int = 2500  # <- The height of the scene
    canvas_W: int = 3500  # <- The width of the scene
    displacement: int = 100  # <- The unit movement of the agent


class SimTimeLess(Basic):
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
    @param[in]  param               The parameters
    """

    def __init__(self, thePuzzle, theHand, thePlanner=None, thePlannerHand=None, theFig = None, shareFlag = True, theParams=ParamSTL()):
        super(SimTimeLess, self).__init__(thePuzzle=thePuzzle, thePlanner=thePlanner, theFig=theFig, shareFlag=shareFlag)

        self.hand = theHand
        self.param = theParams

        self.canvas = np.zeros(
            (self.param.canvas_H, self.param.canvas_W, 3),
            dtype=np.uint8
        )

        # Todo: Currently, the planner is with the simulator.
        #       Not sure if we should go with the hand.

        self.plannerHand = thePlannerHand

        # cached action, argument, and time
        self.cache_action = []  # The next action to execute

        # For display
        self.im = None

    def simulate_step(self, ID_DISPLAY=True, CONTOUR_DISPLAY=True):

        if len(self.cache_action) > 0:
            action = self.cache_action.pop(0)

            if self.shareFlag == False:

                # FixMe: Need to fix the index change bug
                if action[0] == "pick":
                    _, piece_index = self.translateAction(self.plannerHand.manager.pAssignments, action[1])
                    action[1] = piece_index


                opFlag = self.hand.execute(self.puzzle, action[0], action[1])

                # if action[0] == "pick" and opFlag == True:
                #     # Record the index to be changed
                #     self.changeIndex = action[1]
                #
                # if action[0] == "place" and opFlag == True:
                #     # Update self.matchInit
                #     for match in self.matchInit:
                #         if match[0]
            else:
                self.hand.execute(self.puzzle, action[0], action[1])
            # self.hand.execute(self.puzzle, action[0], action[1])

        cache_image = self.puzzle.toImage(np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY,
                                          BOUNDING_BOX=False)

        theImage = deepcopy(cache_image)
        self.hand.placeInImage(theImage, CONTOUR_DISPLAY=CONTOUR_DISPLAY)
        plt.pause(0.001)

        self.im.set_data(theImage)
        self.fig.canvas.draw()

    def display(self, ID_DISPLAY=True, CONTOUR_DISPLAY=True):
        """
        @brief  Displays the current puzzle board.

        Args:
            ID_DISPLAY: Flag indicating ID_DISPLAY or not.
            CONTOUR_DISPLAY: Flag indicating CONTOUR_DISPLAY or not.
        """

        if not self.fig:
            self.fig = plt.figure()

        theImage = self.puzzle.toImage(np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY, BOUNDING_BOX=False)
        self.hand.placeInImage(theImage, CONTOUR_DISPLAY=CONTOUR_DISPLAY)
        self.im = plt.imshow(theImage)

        def press_handle(event):
            print('press', event.key)
            sys.stdout.flush()

            if event.key == 'up':
                self.cache_action.append(["move", np.array([0, -self.param.displacement]) + self.hand.app.rLoc])
            elif event.key == 'left':
                self.cache_action.append(["move", np.array([-self.param.displacement, 0]) + self.hand.app.rLoc])
            elif event.key == 'down':
                self.cache_action.append(["move", np.array([0, self.param.displacement]) + self.hand.app.rLoc])
            elif event.key == 'right':
                self.cache_action.append(["move", np.array([self.param.displacement, 0]) + self.hand.app.rLoc])
            elif event.key == 'z':
                self.cache_action.append(["pick", None])
            elif event.key == 'c':
                self.cache_action.append(["place", None])
            elif event.key == 'o':
                # Let the robot plays
                print('The robot executes a move')

                if self.planner is None:
                    print('planner has not been set up yet.')
                else:
                    if self.shareFlag == True:
                        # Complete plan is only meaningful when the puzzle board is not changed
                        plan = self.planner.process(self.puzzle, COMPLETE_PLAN=True)
                    else:
                        plan = self.planner.process(self.toImage(ID_DISPLAY=False,CONTOUR_DISPLAY=False, BOUNDING_BOX=False), COMPLETE_PLAN=False)

                    self.takeAction(plan)

            elif event.key == 'p':
                print('The hand executes a move')
                # Let the hand plays
                if self.plannerHand is None:
                    print('plannerHand has not been set up yet.')
                else:
                    if self.shareFlag == True:
                        plan = self.plannerHand.process(self.puzzle, self.hand, COMPLETE_PLAN=True)
                    else:
                        plan = self.plannerHand.process(self.toImage(ID_DISPLAY=False,CONTOUR_DISPLAY=False, BOUNDING_BOX=False), self.hand, COMPLETE_PLAN=False)

                    # print(plan)
                    for action in plan:
                        if action is None:
                            break
                        self.cache_action.append(action)
                        self.simulate_step(ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

            self.simulate_step(ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

        # Debug only
        # class Event:
        #     key = None
        #
        # event = Event()
        # event.key = 'o'
        # while 1:
        #     press(event)

        self.fig.canvas.mpl_connect('key_press_event', press_handle)

        plt.show()

#
# ========================= puzzle.simulator.simTimeless ========================
