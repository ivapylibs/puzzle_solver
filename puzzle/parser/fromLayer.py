# ======================== puzzle.parser.fromLayer ========================
#
# @class    puzzle.parser.fromLayer
#
# @brief    A basic detector class that processes a layered image
#           (or mask and image) detection output. Converts all isolated
#           regions into their own puzzle piece instances.
#
# ======================== puzzle.parser.fromLayer ========================
#
# @file     fromLayer.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/29 [created]
#           2021/08/01 [modified]
#
#
# ======================== puzzle.parser.fromLayer ========================

# ===== Environment / Dependencies
#

from dataclasses import dataclass

import cv2
import numpy as np
from copy import deepcopy

from trackpointer.centroidMulti import centroidMulti

from puzzle.builder.board import Board
from puzzle.piece.template import Template, PieceStatus
from puzzle.utils.shapeProcessing import bb_intersection_over_union


# ===== Helper Elements
#

@dataclass
class ParamPuzzle:
    areaThresholdLower: float = 20
    areaThresholdUpper: float = float('inf')
    lengthThresholdLower: float = 1000
    pieceConstructor: any = Template
    pieceStatus: int = PieceStatus.MEASURED


#
# ======================== puzzle.parser.fromLayer ========================
#

class FromLayer(centroidMulti):

    def __init__(self, theParams=ParamPuzzle):
        """
        @brief  Constructor for the puzzle piece layer parsing class.

        Args:
            theParams: The parameters.
        """

        super(FromLayer, self).__init__()

        self.bMeas = Board()  # @< The measured board.

        self.params = theParams

        self.pieceConstructor = theParams.pieceConstructor  # @< The basic constructor for pieces: template or regular

    def getState(self):
        """
        @brief  Return the track-pointer state. Override the original one.

        Returns:
            tstate(The board measurement)
        """
        tstate = self.bMeas

        return tstate

    def measure(self, I, M):
        """
        @brief  Process the passed imagery to recover puzzle pieces and
                manage their track states.

        Args:
            I:  RGB image.
            M:  Mask image.
        """

        # 1] Extract pieces based on disconnected component regions
        #
        regions = self.mask2regions(I, M)

        # 2] Instantiate puzzle piece elements from extracted data
        #
        pieces = self.regions2pieces(regions)

        # 3] Package into a board.
        #
        self.bMeas.clear()

        # Add the pieces one by one. So the label can be managed.
        for piece in pieces:
            self.bMeas.addPiece(piece)

        if len(self.bMeas.pieces) == 0:
            self.haveMeas = False
        else:
            # Todo: Eventually, tpt should be updated with a dict or class instance
            self.tpt = []
            for id, loc in self.bMeas.pieceLocations().items():
                self.tpt.append(loc)
            self.tpt = np.array(self.tpt).reshape(-1, 2).T

            self.haveMeas = True

    def findCorrectedContours(self, mask, FILTER=True):
        """
        @brief Find the right contours given a binary mask image.

        Args:
            mask: The input binary mask image.

        Returns:
            desired_cnts: Contour list.
        """

        # For details of options, see https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga819779b9857cc2f8601e6526a3a5bc71
        # and https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga4303f45752694956374734a03c54d5ff
        # For OpenCV 4+
        cnts, hierarchy = cv2.findContours(mask, cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) == 0:
            return []

        hierarchy = hierarchy[0]

        if FILTER:
            # Filter out the outermost contour
            # See https://docs.opencv.org/master/d9/d8b/tutorial_py_contours_hierarchy.html
            keep = []
            for i in range(hierarchy.shape[0]):
                # We assume a valid contour should not contain too many small contours
                if hierarchy[i][3] == -1 and np.count_nonzero(hierarchy[:, 3] == i) >= 2:

                    # # Debug only
                    # temp_mask = np.zeros_like(mask).astype('uint8')
                    # cv2.drawContours(temp_mask, cnts[i], -1, (255, 255, 255), 2)
                    # _, temp_mask = cv2.threshold(temp_mask, 10, 255, cv2.THRESH_BINARY)
                    # cv2.imshow('temp_mask', temp_mask)
                    # cv2.waitKey()

                    pass
                else:
                    keep.append(i)

            cnts = np.array(cnts)
            cnts = cnts[keep]
        else:
            cnts = np.array(cnts)

        desired_cnts = []

        # Filter out some contours according to area threshold
        for c in cnts:
            # Draw the contours
            # cv2.drawContours(mask, [c], -1, (0, 255, 0), 2)

            area = cv2.contourArea(c)

            # Filtered by the area threshold
            if area > self.params.areaThresholdUpper:
                continue
            elif area > self.params.areaThresholdLower:
                desired_cnts.append(c)
            else:

                # findContours may return a discontinuous contour which cannot compute contourArea correctly
                if cv2.arcLength(c, True) > self.params.lengthThresholdLower:

                    temp_mask = np.zeros_like(mask).astype('uint8')
                    cv2.drawContours(temp_mask, [c], -1, (255, 255, 255), 2)
                    _, temp_mask = cv2.threshold(temp_mask, 10, 255, cv2.THRESH_BINARY)
                    # Debug only
                    # debug_mask = copy.deepcopy(temp_mask)
                    # debug_mask = cv2.resize(debug_mask, (int(debug_mask.shape[1] / 2), int(debug_mask.shape[0] / 2)),
                    #                         interpolation=cv2.INTER_AREA)
                    # cv2.imshow('debug', debug_mask)
                    # cv2.waitKey()
                    desired_cnts_new = self.findCorrectedContours(temp_mask)
                    for c in desired_cnts_new:
                        if area > self.params.areaThresholdUpper:
                            continue
                        elif area > self.params.areaThresholdLower:
                            desired_cnts.append(c)
                        desired_cnts.append(c)

        return desired_cnts

    def mask2regions(self, I, M):
        """
        @brief      Convert the selection mask into a bunch of regions.
                    Mainly based on findContours function.

        Args:
            I:  RGB image.
            M:  Mask image.

        Returns:
            regions: A list of regions (mask, segmented image, location in the source image).
        """
        # Convert mask to an image
        mask = M.astype('uint8')

        # # Debug only
        # cv2.imshow('debug',mask)
        # cv2.waitKey()

        desired_cnts = self.findCorrectedContours(mask)

        # In rare case, a valid contour may contain some small contours
        if len(desired_cnts) == 0:
            desired_cnts = self.findCorrectedContours(mask, FILTER=False)

        # print('size of desired_cnts is', len(desired_cnts))

        # # Debug only
        # debug_mask = np.zeros_like(mask_enlarged).astype('uint8')
        # for c in desired_cnts:
        #   cv2.drawContours(debug_mask, [c], -1, (255, 255, 255), 2)
        #
        # debug_mask = cv2.resize(debug_mask, (int(debug_mask.shape[1] / 2), int(debug_mask.shape[0] / 2)), interpolation=cv2.INTER_AREA)
        # cv2.imshow('after area thresh',debug_mask)
        # cv2.waitKey()

        regions = []
        # Get the individual part
        for c in desired_cnts:
            seg_img = np.zeros(mask.shape[:2], dtype="uint8")  # reset a blank image every time
            cv2.drawContours(seg_img, [c], -1, (255, 255, 255), thickness=-1)

            # # Debug only
            # cv2.imshow('debug',seg_img)
            # cv2.waitKey()

            # Get ROI, OpenCV style
            x, y, w, h = cv2.boundingRect(c)

            # The area checking only count the actual area but we may have some cases where segmentation is scattered
            if w*h > self.params.areaThresholdUpper:
                skipFlag = True
            else:
                # Double check if ROI has a large IoU with the previous ones, then discard it
                skipFlag = False
                for region in regions:
                    if bb_intersection_over_union(region[3], [x, y, x + w, y + h]) > 0.5:
                        skipFlag = True
                        break

            # Todo: A tricky solution to skip regions of all black, which is for our real scene
            if cv2.countNonZero(cv2.threshold(cv2.cvtColor(cv2.bitwise_and(I, I, mask=seg_img.astype('uint8')),
                                                           cv2.COLOR_BGR2GRAY), 50, 255, cv2.THRESH_BINARY)[1]) == 0:
                # Debug only
                # cv2.imshow('seg_img', seg_img)
                # cv2.imshow('I', I)
                # cv2.waitKey()
                continue

            if not skipFlag:
                # Add theMask, theImage, rLoc, the region
                regions.append((seg_img[y:y + h, x:x + w], I[y:y + h, x:x + w, :], [x, y], [x, y, x + w, y + h]))

        return regions

    def regions2pieces(self, regions):
        """
        @brief  Convert the region information into puzzle pieces.

        Args:
            regions: A list of region pairs (mask, segmented image, location in the source image).

        Returns:
            pieces: A list of puzzle pieces instances.
        """
        pieces = []
        for region in regions:
            theMask = region[0]
            theImage = region[1]
            rLoc = region[2]
            thePiece = self.pieceConstructor.buildFromMaskAndImage(theMask, theImage, rLoc=rLoc,
                                                                   pieceStatus=self.params.pieceStatus)

            pieces.append(thePiece)

        return pieces

    # ============================== correct ==============================
    #
    # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

    # =============================== adapt ===============================
    #
    # DEFINE ONLY IF OVERLOADING. OTHERWISE REMOVE.

    def process(self, I, M):
        """
        @brief  Run the tracking pipeline for image measurement.

        Args:
            I: RGB image.
            M: Mask image.
        """
        self.measure(I, M)

#
# ======================== puzzle.parser.fromLayer ========================
