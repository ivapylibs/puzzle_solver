# ====================== puzzle.utils.simProcessing ======================
#
# @brief    Some processing functions for the simulator.
#
# ====================== puzzle.utils.simProcessing ======================
#
# @file     simProcessing.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2022/01/11 [created]
#
#
# ====================== puzzle.utils.simProcessing ======================


# ============================== Dependencies =============================
import cv2
import os

from puzzle.piece.template import Template
from puzzle.simulator.hand import Hand

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ====================== puzzle.utils.simProcessing ======================

def setHand(init_agent_loc, fsize=1):
    """
    @brief  Set up the hand appearance

    Args:
        init_agent_loc: The initial location.
        fsize: The scale of the hand image.

    Returns:
        theHand: A hand instance.
    """

    fsize = 3
    aa = cpath
    theImageHand = cv2.imread(cpath + '/../testing/data/hand.png', cv2.IMREAD_UNCHANGED)
    theMaskHand = theImageHand[:, :, -1]
    theImageHand = cv2.cvtColor(theImageHand[:, :, :3], cv2.COLOR_BGR2RGB)
    theImageHand = cv2.resize(theImageHand, (0, 0), fx=fsize, fy=fsize)
    theMaskHand = cv2.resize(theMaskHand, (0, 0), fx=fsize, fy=fsize)

    theHandAppearance = Template.buildFromMaskAndImage(theMaskHand, theImageHand)

    theHandAppearance.setPlacement(r=init_agent_loc)

    theImageArm = cv2.imread(cpath + '/../testing/data/arm.png', cv2.IMREAD_UNCHANGED)
    theMaskArm  = theImageArm[:, :, -1]
    theImageArm = cv2.cvtColor(theImageArm[:, :, :3], cv2.COLOR_BGR2RGB)
    theImageArm = cv2.resize(theImageArm, (0, 0), fx=fsize, fy=fsize)
    theMaskArm = cv2.resize(theMaskArm, (0, 0), fx=fsize, fy=fsize)

    theHand = Hand(theHandAppearance, arm_image=theImageArm, arm_mask= theMaskArm)

    return theHand
#
# ====================== puzzle.utils.simProcessing ======================
