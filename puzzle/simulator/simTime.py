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
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pygame
from dataclasses import dataclass
from collections import defaultdict

from puzzle.simulator.simTimeless import SimTimeLess, ParamSTL
from puzzle.utils.imageProcessing import extract_region, find_nonzero_mask
from puzzle.utils.pygameProcessing import multiLineSurface

@dataclass
class ParamST(ParamSTL):
    delta_t: float = 0.1  # <- Unit: s. The time length for a simulation step.
    speed: float = 100  # <- Unit: pixel/s. The speed of the agent movement.
    static_duration: float = 0.1  # <- Unit: s. The duration of the static actions.
    FPS: int = 60  # <- Flash rate for the simulator.

    fx: float = 0.5  # <- The x scale of display.
    fy: float = 0.5  # <- The y scale of display.

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
        self.FPS = self.param.FPS
        self.FramePerSec = pygame.time.Clock()

        # To save the display window
        self.pygameFig = None

        # To save the regions for cluster
        self.cluster_region_list = []

        self.cluster_piece_dict = dict()

    def _move_step(self, param):
        """
        @brief  Move a step given the target location.
                Note that the target location might not be reachable within a step's time length.
        Args:
            target_loc: The target location of the "move"

        Returns:
            finishFlag(Indicator of whether the target location has been reached)
        """

        opParam = (False, None)

        # offset has been adjusted in advance
        if isinstance(param, tuple):
            targetLoc = param[0]
        elif isinstance(param, list) or isinstance(param, np.ndarray):
            targetLoc = param

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
            finishFlag = False
        else:
            step_loc[0] = targetLoc[0]
            step_loc[1] = targetLoc[1]
            finishFlag = True

        # Todo: May update the bounds later. Could be slightly off.
        if step_loc[0] < 0 or step_loc[1] < 0 \
                or step_loc[0] + self.hand.app.size()[0] >= self.canvas.shape[1] \
                or step_loc[1] + self.hand.app.size()[1] >= self.canvas.shape[0]:
            print('Out of the bounds!')
            finishFlag = True
        else:
            # Execute
            opParam = self.hand.execute(self.puzzle, "move", step_loc)

        # self.hand.execute(self.puzzle, "move", step_loc)

        return finishFlag, opParam

    def _pause_step(self, action):

        # Have to be pick or place for now
        assert action[0] != "move"

        opParam = (False, None)

        # If have not been executed, then execute first before pause there
        if abs(self.timer - self.param.static_duration) < 1e-04:
            if self.shareFlag == False and action[0] == "pick":
                piece_id = self.translateAction(self.plannerHand.manager.pAssignments, action[1])
                action[1] = piece_id
                opParam = self.hand.execute(self.puzzle, action[0], piece_id)
            else:
                opParam = self.hand.execute(self.puzzle, action[0], action[1])

        # Continue to run the timer
        self.timer -= self.param.delta_t

        # If timer is below zero, then it is up!
        if self.timer < 0:
            finishFlag = True
        else:
            finishFlag = False

        return finishFlag, opParam

    def reset_cache(self):
        self.cache_action = []
        self.timer = self.param.static_duration

    def simulate_step(self, robot_only=False, ID_DISPLAY=True, CONTOUR_DISPLAY=True):

        cache_image = self.puzzle.toImage(theImage=np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY,
                                          BOUNDING_BOX=False)

        while 1:

            # Only related to the hand movement
            finish_flag = self.simulate_step_small()

            if finish_flag is not None or robot_only:
                if finish_flag is True or robot_only:
                    cache_image = self.puzzle.toImage(theImage=np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY,
                                                      BOUNDING_BOX=False)

                theImage = deepcopy(cache_image)
                self.hand.placeInImage(theImage, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

                # pygame APIs to update the figure
                theImage_demo = cv2.resize(theImage, (0, 0), fx=self.param.fx, fy=self.param.fy)
                background = pygame.surfarray.make_surface(np.moveaxis(theImage_demo, 0, 1))
                self.pygameFig.blit(background, (0, 0))
                pygame.display.update()
                self.FramePerSec.tick(self.FPS)

                if finish_flag is True or robot_only:
                    break
            else:
                break

    def instruction(self):

        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)

        # Instruction
        font = pygame.font.SysFont('chalkduster.ttf', 72)
        rect = pygame.Rect((0, 0), (int(self.canvas.shape[1] * self.param.fx),
                                    int(self.canvas.shape[0] * self.param.fy)))

        insFig = multiLineSurface('Welcome to the Puzzle Solver!\n\n'
                                  'Key board instruction:\n'
                                  '- Up: Move the hand up\n'
                                  '- Down: Move the hand down\n'
                                  '- Left: Move the hand left\n'
                                  '- Right: Move the hand right\n'
                                  '- z: Pick the puzzle piece\n'
                                  '- c: Place the puzzle piece if there is one in the hand\n'
                                  '- o: Run the puzzle solver for the robot\n'
                                  '- p: Run the puzzle solver for the hand\n\n'
                                  'Use you mouse to segment the solution board for a calibration!\n\n'
                                  'Press any key to continue!',
                                  font, rect, WHITE, BLACK)
        self.pygameFig.blit(insFig, (0, 0))
        pygame.display.update()

        insFlag = True
        while insFlag:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    insFlag = False
                    break

    def calibrate(self, ID_DISPLAY=True):

        drawing = False
        mouse_position = (0, 0)
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        last_pos = None

        # Display solution board
        theImage = self.planner.manager.solution.toImage(ID_DISPLAY=ID_DISPLAY, BOUNDING_BOX=False)
        background = pygame.surfarray.make_surface(np.moveaxis(theImage, 0, 1))
        self.pygameFig = pygame.display.set_mode((int(theImage.shape[1]), int(theImage.shape[0])))
        self.pygameFig.blit(background, (0, 0))

        # With white background
        theMask = np.ones_like(theImage, 'uint8') * 255

        # Calibration
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEMOTION:
                    if (drawing):
                        mouse_position = pygame.mouse.get_pos()
                        if last_pos is not None:
                            # For display
                            pygame.draw.line(self.pygameFig, WHITE, last_pos, mouse_position, 10)

                            # # For calibration
                            cv2.line(theMask, last_pos, mouse_position, BLACK, 5)
                        last_pos = mouse_position
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_position = (0, 0)
                    drawing = False
                    last_pos = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    drawing = True

            pressed_keys = pygame.key.get_pressed()

            if pressed_keys[pygame.K_f]:
                try:
                    self.cluster_region_list = extract_region(theMask)

                    self.cluster_piece_dict = defaultdict(list)

                    print('Segmentation successful.')
                    print(f'{len(self.cluster_region_list)} regions in total.')

                    break
                except:
                    print('Segmentation not successful. Please try again.')

            pygame.display.update()

        if len(self.cluster_region_list) > 0:

            for piece in self.planner.manager.solution.pieces:

                # Mask with 0 and 1
                mask_piece = np.zeros((theMask.shape[:2]), 'uint8')
                mask_piece = piece.getMask(mask_piece)

                # Count the number of pixels
                mask_piece_count = np.count_nonzero(mask_piece == 1)

                for idx, cluster_region in enumerate(self.cluster_region_list):
                    mask_combine = mask_piece + cluster_region

                    mask_combine_count = np.count_nonzero(mask_combine == 2)

                    # Calculate the ratio
                    ratio = mask_combine_count / mask_piece_count

                    if ratio > 0.5:
                        self.cluster_piece_dict[idx].append(piece.id)
                        break

            print(self.cluster_piece_dict)

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

                finishFlag, opParam = self._move_step(action[1])
            else:
                finishFlag, opParam = self._pause_step(action)
        else:
            return None

        # If the cached action is finishFlag, reset the cache and the timer
        if finishFlag:  # < Whether the current cached action has been finishFlag
            self.cache_action.pop(0)
            self.reset_cache()

        # Todo: Maybe too slow, have to be updated later
        # finishFlag is only about the animation, opParam is about the implementation
        if action[0] == "place" and opParam[0] == True:
            # Update self.matchSimulator

            # Remove the old association
            temp = self.matchSimulator[opParam[1]]
            del self.matchSimulator[opParam[1]]

            # Add the new one
            # Todo: Note that here we assume the placed puzzle has a new id
            self.matchSimulator[self.puzzle.id_count - 1] = temp

        return finishFlag

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

                        # Enable hand occlusion
                        if self.param.HAND_OCCLUSION == True:
                            # Get the hand mask
                            theMask = np.zeros((self.canvas.shape[:2])).astype('bool')
                            theMask = self.hand.app.getMask(theMask)

                            # Invert to work on the other region
                            theMask = np.invert(theMask)
                        else:
                            theMask = None

                        plan = self.plannerHand.process(
                            self.toImage(theImage=np.zeros_like(self.canvas), theMask=theMask,
                                         ID_DISPLAY=False, CONTOUR_DISPLAY=False, BOUNDING_BOX=False), self.hand,
                            COMPLETE_PLAN=False)

                    # print(plan)
                    for action in plan:
                        if action is None:
                            break
                        self.cache_action.append(action)

                        self.simulate_step(ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

            else:
                return

            self.simulate_step(ID_DISPLAY=ID_DISPLAY, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

        # Step 0: Initialization
        pygame.init()

        WHITE = (255,255,255)
        BLACK = (0, 0, 0)

        # with a black screen
        self.pygameFig = pygame.display.set_mode((int(self.canvas.shape[1]*self.param.fx),
                                                    int(self.canvas.shape[0]*self.param.fy)))
        self.pygameFig.fill(BLACK)
        pygame.display.set_caption("Puzzle Solver")

        # Step 1: Instruction screen
        self.instruction()

        # # Step 2: Calibration process
        # self.calibrate(ID_DISPLAY=ID_DISPLAY)

        # Step 3: Game screen
        theImage = self.puzzle.toImage(theImage=np.zeros_like(self.canvas), ID_DISPLAY=ID_DISPLAY, BOUNDING_BOX=False)
        self.hand.placeInImage(theImage, CONTOUR_DISPLAY=CONTOUR_DISPLAY)

        theImage_demo = cv2.resize(theImage, (0, 0), fx=self.param.fx, fy=self.param.fy)
        background = pygame.surfarray.make_surface(np.moveaxis(theImage_demo, 0, 1))
        self.pygameFig = pygame.display.set_mode((int(self.canvas.shape[1]*self.param.fx),
                                                    int(self.canvas.shape[0]*self.param.fy)))

        self.pygameFig.blit(background, (0, 0))

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
