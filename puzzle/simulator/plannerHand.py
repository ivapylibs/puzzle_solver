# ========================= puzzle.simulator.plannerHand ========================
#
# @class    puzzle.simulator.plannerHand
#
# @brief    The planner for producing the action sequence to solve the puzzle.
#           Hand needs to have more interpretations.
# @note     Yunzhi: more like a wrapper of solver & manager in the test script.
#
# ========================= puzzle.simulator.plannerHand ========================
#
# @file     plannerHand.py
#
# @author   Yiye Chen,               yychen2019@gatech.edu
#           Yunzhi Lin,              yunzhi.lin@gatech.edu
# @date     2021/09/02 [created]
#           2021/11/25 [modified]
#
#
# ========================= puzzle.simulator.plannerHand ========================

from puzzle.simulator.planner import Planner
from puzzle.builder.board import Board
from puzzle.builder.gridded import ParamGrid


class PlannerHand(Planner):
    def __init__(self, solver, manager, theParams=ParamGrid):
        """
        @brief  Define the general planner planning process.

        Args:
            solver: The solver instance responsible for plan the execution order.
            manager: The manager instance responsible for determining the
                    association between the measured board and the solution board
        """
        super(PlannerHand, self).__init__(solver, manager, theParams=theParams)

    def process(self, input, hand, COMPLETE_PLAN=True):
        """
        @brief  Draft the action plan given the measured board.

        Args:
            input: A measured board or an RGB image.
            hand: The hand instance.
            COMPLETE_PLAN: Whether to plan the whole sequence.

        Returns:
            plan_new(The updated plan for hand)
        """

        if issubclass(type(input), Board):
            meaBoard = input
        else:
            # Remove the hand area
            meaBoard = self.measure(input)

        plan = self.adapt(meaBoard, COMPLETE_PLAN=COMPLETE_PLAN)

        # Interpretations for hand, more like ants moving
        plan_new = []

        for i, action in enumerate(plan):
            if action is None:
                plan_new.append(action)
            else:
                piece_id = action[0]
                # piece_index = action[1]
                action_type = action[2]
                action_param = action[3]

                # Todo: We always assume rotate first then move
                if action_type == 'rotate':

                    # move to the puzzle piece
                    plan_new.append(['move', meaBoard.pieces[piece_id].rLoc])

                    # # pick the nearby piece
                    # plan_new.append(['pick', None])

                    # pick the target piece
                    plan_new.append(['pick', piece_id])

                    # Rotate the piece in hand
                    plan_new.append(['rotate', action_param])

                    # Check if the next action is to move the same piece
                    if i + 1 < len(plan) and plan[i + 1] is not None \
                            and plan[i + 1][0] == piece_id and plan[i + 1][2] == 'move':
                        pass
                    else:
                        # if not, place the piece
                        plan_new.append(['place', None])

                elif action_type == 'move':

                    # move to the puzzle piece
                    plan_new.append(['move', meaBoard.pieces[piece_id].rLoc])

                    # Todo: Currently, we assume there is only one piece in hand at one time
                    if hand.cache_piece is None:
                        # # pick the nearby piece
                        # plan_new.append(['pick', None])

                        # pick the target piece
                        plan_new.append(['pick', piece_id])

                    # move the piece to the target loc
                    plan_new.append(['move', (action_param, True)])

                    plan_new.append(['place', None])

        return plan_new
