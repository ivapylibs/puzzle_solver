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
# @file     simTime.py
#
# @author   Yiye Chen,               yychen2019@gatech.edu
#           Yunzhi Lin,              yunzhi.lin@gatech.edu
# @date     2021/09/10 [created]
#           2021/11/25 [modified]
#
#
# ========================= puzzle.simulator.simTime ========================

import math
import sys
from copy import deepcopy
from dataclasses import dataclass

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pygame

from puzzle.simulator.simTimeless import SimTimeLess, ParamSTL


@dataclass
class ParamST(ParamSTL):
    """
    @param  canvas_H            The height of the whole scene
    @param  canvas_W            The width of the whole scene
    ------------------ Below are related to time ---------------------
    @param  delta_t             Unit: s(econd). The time length for a simulation step.
    @param  speed               Unit: pixel/s. The speed of the agent movement
    @param  static_duration     Unit: s(econd). The duration of the static actions
    """
    delta_t: float = 0.1
    speed: float = 100
    static_duration: float = 0.1


class SimTime(SimTimeLess):
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

    @param[in]  thePuzzle           The current board
    @param[in]  agent               The puzzle solving agent
    @param[in]  param               The parameters
    """

    def __init__(self, thePuzzle, theHand, thePlanner=None, thePlannerHand=None, theFig=None, shareFlag=True,
                     theParams=ParamST()):

        super(SimTime, self).__init__(thePuzzle, theHand, thePlanner=thePlanner, thePlannerHand=thePlannerHand,
                                      theFig=theFig, shareFlag=shareFlag, theParams=theParams)

        self.timer = self.param.static_duration  # The timer

        # Setting up FPS
        self.FPS = 60
        self.FramePerSec = pygame.time.Clock()

        # To save the display window
        self.DISPLAYSURF = None

    def _move_step(self, param):
        """
        @brief  Move a step given the target location.
                Note that the target location might not be reachable within a step's time length.
        Args:
            target_loc: The target location of the "move"

        Returns:
            flag_finish(Indicator of whether the target location has been reached)
        """

        # offset has been adjusted in advance
        if isinstance(param, tuple):
            targetLoc = param[0]
            # offset = param[1]
        elif isinstance(param, list) or isinstance(param, np.ndarray):
            targetLoc = param
            # offset = False

        delta_x = targetLoc[0] - self.hand.app.rLoc[0]
        delta_y = targetLoc[1] - self.hand.app.rLoc[1]

        distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

        # determine where to end up
        step_loc = np.array([-1, -1])
        if distance >= self.param.delta_t * self.param.speed:
            x_step = delta_x * (self.param.delta_t * self.param.speed) / distance
            y_step = delta_y * (self.param.delta_t * self.param.speed) / distance
            step_loc[0] = self.hand.app.rLoc[0] + x_step
            step_loc[1] = self.hand.app.rLoc[1] + y_step
            flag_finish = False
        else:
            step_loc[0] = targetLoc[0]
            step_loc[1] = targetLoc[1]
            flag_finish = True

        # Todo: May update the bounds later. Could be slightly off.
        if step_loc[0] < 0 or step_loc[1] < 0 \
                or step_loc[0] + self.hand.app.size()[0] >= self.canvas.shape[1] \
                or step_loc[1] + self.hand.app.size()[1] >= self.canvas.shape[0]:
            print('Out of the bounds!')
            flag_finish = True
        else:
            # Execute
            self.hand.execute(self.puzzle, "move", step_loc)

        # self.hand.execute(self.puzzle, "move", step_loc)

        return flag_finish

    def _pause_step(self, action):

        # Have to be pick or place for now
        assert action[0] != "move"

        # If have not been executed, then execute first before pause there
        if abs(self.timer - self.param.static_duration) < 1e-04:
            if self.shareFlag == False and action[0] == "pick":
                _, piece_index = self.translateAction(self.plannerHand.manager.pAssignments, action[1])
                action[1] = piece_index
                self.hand.execute(self.puzzle, action[0], piece_index)
            else:
                self.hand.execute(self.puzzle, action[0], action[1])


        # Continue to run the timer
        self.timer -= self.param.delta_t

        # If timer is below zero, then it is up!
        if self.timer < 0:
            flag_finish = True
        else:
            flag_finish = False

        return flag_finish

    def reset_cache(self):
        self.cache_action = []
        self.timer = self.param.static_duration

    def simulate_step(self, robot_only=False, ID_DISPLAY=True, CONTOUR_DISPLAY=True):

        cache_image = self.puzzle.toImage(np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY,
                                          BOUNDING_BOX=False)

        while 1:

            # Only related to the hand movement
            finish_flag = self.simulate_step_small()

            if finish_flag is not None or robot_only:
                if finish_flag is True or robot_only:
                    cache_image = self.puzzle.toImage(np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY,
                                                      BOUNDING_BOX=False)

                theImage = deepcopy(cache_image)
                self.hand.placeInImage(theImage, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

                # pygame APIs to update the figure
                theImage_demo = cv2.resize(theImage, (0, 0), fx=0.5, fy=0.5)
                background = pygame.surfarray.make_surface(np.moveaxis(theImage_demo, 0, 1))
                self.DISPLAYSURF.blit(background, (0, 0))
                pygame.display.update()
                self.FramePerSec.tick(self.FPS)

                if finish_flag is True or robot_only:
                    break
            else:
                break

    def simulate_step_small(self):
        """
        Overwrite the simulate_step function
        """

        if len(self.cache_action) > 0:
            action = self.cache_action[0]

            if action[0] == "move":

                if isinstance(action[1], tuple) and action[1][1] is True:
                    # We have to recompute & reset the action for offset case
                    self.cache_action[0][1] = action[1][0] + self.hand.app.rLoc
                    action = self.cache_action[0]

                flag_finish = self._move_step(action[1])
            else:
                flag_finish = self._pause_step(action)
        else:
            return None

        # if the cached action is finished, reset the cache and the timer
        if flag_finish:  # < Whether the current cached action has been finished
            self.cache_action.pop(0)
            self.reset_cache()

        return flag_finish

    def display(self, ID_DISPLAY=True, CONTOUR_DISPLAY=True):
        """
        @brief  Displays the current puzzle board.

        Args:
            ID_DISPLAY: Flag indicating ID_DISPLAY or not.
            CONTOUR_DISPLAY: Flag indicating CONTOUR_DISPLAY or not.
        """

        def press_handle(key):

            if key[pygame.K_UP]:
                self.cache_action.append(["move", np.array([0, -self.param.displacement]) + self.hand.app.rLoc])
            elif key[pygame.K_LEFT]:
                self.cache_action.append(["move", np.array([-self.param.displacement, 0]) + self.hand.app.rLoc])
            elif key[pygame.K_DOWN]:
                self.cache_action.append(["move", np.array([0, self.param.displacement]) + self.hand.app.rLoc])
            elif key[pygame.K_RIGHT]:
                self.cache_action.append(["move", np.array([self.param.displacement, 0]) + self.hand.app.rLoc])
            elif key[pygame.K_z]:
                self.cache_action.append(["pick", None])
            elif key[pygame.K_c]:
                self.cache_action.append(["place", None])
            elif key[pygame.K_o]:
                print('The robot executes a move.')

                # Let the robot plays
                if self.planner is None:
                    print('planner has not been set up yet.')
                else:
                    if self.shareFlag == True:
                        # Complete plan is only meaningful when the puzzle board is not changed
                        plan = self.planner.process(self.puzzle, COMPLETE_PLAN=True)
                    else:
                        plan = self.planner.process(
                            self.toImage(ID_DISPLAY=False, CONTOUR_DISPLAY=False, BOUNDING_BOX=False),
                            COMPLETE_PLAN=False)

                    self.takeAction(plan)

                    self.simulate_step(robot_only=True, ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY)
            elif key[pygame.K_p]:
                print('The hand executes a move.')

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

            else:
                return

            self.simulate_step(ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

        if not self.fig:
            self.fig = plt.figure()

        theImage = self.puzzle.toImage(np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY, BOUNDING_BOX=False)
        self.hand.placeInImage(theImage, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

        theImage_demo = cv2.resize(theImage, (0, 0), fx=0.5, fy=0.5)
        background = pygame.surfarray.make_surface(np.moveaxis(theImage_demo, 0, 1))

        # Initializing
        pygame.init()

        # Create a white screen
        BLACK = (0, 0, 0)
        self.DISPLAYSURF = pygame.display.set_mode((theImage_demo.shape[1], theImage_demo.shape[0]))
        self.DISPLAYSURF.fill(BLACK)
        pygame.display.set_caption("Puzzle Solver")
        self.DISPLAYSURF.blit(background, (0, 0))

        # Game Loop
        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pressed_keys = pygame.key.get_pressed()
            press_handle(pressed_keys)

            pygame.display.update()
            self.FramePerSec.tick(self.FPS)

#
# ========================= puzzle.simulator.simTime ========================
