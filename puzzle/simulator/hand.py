# ========================= puzzle.simulator.hand ========================
#
# @class    puzzle.simulator.hand
#
# @brief    The agent simulates a subject to solve the puzzle task.
#           It takes the measured board and the solution board,
#           and plan the next step
#
# ========================= puzzle.simulator.hand ========================
#
# @file     hand.py
#
# @author   Yiye Chen,               yychen2019@gatech.edu
#           Yunzhi Lin,              yunzhi.lin@gatech.edu
# @date     2021/08/29 [created]
#           2021/11/25 [modified]
#
# ========================= puzzle.simulator.hand ========================

import numpy as np
import cv2

from puzzle.piece.template import Template

# ========================= puzzle.simulator.hand ========================

class Hand:

    def __init__(self, app, arm_image=None, arm_mask=None):
        """
        @brief  The Agent class equip the Base with the actions and the planning ability

        Args:
            app: A Template instance.
        """
        self.app = app
        self.arm_image = arm_image # @< The image for the arm part
        self.arm_mask = arm_mask  # @< The mask for the arm part
        self.arm_region = None
        self.cache_piece = None  # @< A piece instance in hand

    def move(self, param):

        if isinstance(param, tuple):
            targetLoc = param[0]
            offset = param[1]
        elif isinstance(param, list) or isinstance(param, np.ndarray):
            targetLoc = param
            offset = False

        self.app.setPlacement(targetLoc, offset=offset)

        if self.cache_piece is not None:
            self.cache_piece.setPlacement(targetLoc, offset=offset)

        return (True, None)

    def pieceInHand(self, rLoc):

        theDist = np.linalg.norm(np.array(rLoc) - np.array(self.app.rLoc))

        return theDist < 80

    def pick(self, puzzle, piece_id=None):
        """
        @brief Pick up a puzzle piece (can be specified).

        Args:
            puzzle: A puzzle instance.
            piece_id: The index of the puzzle.

        Returns:
            Whether have successfully performed the operation.

        """
        if piece_id is None:
            theDists = {}
            pLocTrue = puzzle.pieceLocations()

            for id in pLocTrue.keys():
                theDists[id] = np.linalg.norm(np.array(pLocTrue[id]) - np.array(self.app.rLoc))

            piece_id = min(theDists, key=theDists.get)

        try:
            piece = puzzle.pieces[piece_id]
        except:
            print('s')

        if self.pieceInHand(piece.rLoc):

            print('Pick the piece.')

            # Align the rLoc
            piece.rLoc = self.app.rLoc
            self.cache_piece = piece

            puzzle.rmPiece(piece_id)

            return (True, None)

        else:
            print('No piece is nearby.')

            return (False, None)

    def place(self, puzzle):
        """
        @brief Place a puzzle piece to where the hand is.

        Args:
            puzzle: A puzzle board.

        Returns:
            Whether have successfully performed the operation.
        """
        if self.cache_piece is not None:

            print('Place the piece.')

            old_id = self.cache_piece.id

            # Todo: Maybe with the original id?
            puzzle.addPiece(self.cache_piece)
            self.cache_piece = None

            return (True, old_id)
        else:
            print('No piece is hand.')

            return (False, None)

    # Todo: To be implemented
    def pause(self):
        return (True, None)

    def rotate(self, action_param):

        if self.cache_piece is None:
            raise RuntimeError('There is no piece in hand')

        self.cache_piece = self.cache_piece.rotatePiece(
            action_param)

        return (True, None)

    def execute(self, puzzle, action_type, action_param=None):
        """
        Execute an action given the action label and parameter

        Overwrite the execute function since we need to keep the self.app.rLoc updated
        NOTE:This is necessary only when we are using the puzzle.template as the appearance model
        """

        # if it is pick action, then get the puzzle piece as the real parameter
        if action_type == "pick":
            return self.pick(puzzle, action_param)
        elif action_type == "rotate":
            return self.rotate(action_param)
        elif action_type == "move":
            return self.move(action_param)
        elif action_type == "place":
            return self.place(puzzle)
        elif action_type == "pause":
            return self.pause()

    def placeInImage(self, img, offset=[0, 0], CONTOUR_DISPLAY=False):
        """
        @brief  Insert the hand into the image in the original location.

        Args:
            img: The source image to put puzzle piece into.
            offset: The offset list.
        """

        # Note that tl & br are for hand not arm

        # Top left corner
        tl = np.array(offset) + self.app.rLoc

        # Bottom right corner
        br = np.array([self.app.y.image.shape[1] + tl[0], self.app.y.image.shape[0] + tl[1]])

        # Todo: We assume the hand cannot pass the top border

        # The enlarged (x,y)
        enlarge = [0, 0]
        if br[1] > img.shape[0]:
            enlarge[1] = br[1] - img.shape[0]
        elif tl[1] < 0:
            enlarge[1] = tl[1]

        # The hand has a small width so it can not cover the whole image width
        if br[0] > img.shape[1]:
            enlarge[0] = br[0] - img.shape[1]
        elif tl[0] < 0:
            enlarge[0] = tl[0]


        img_enlarged = np.zeros((img.shape[0] + abs(enlarge[1]), img.shape[1] + abs(enlarge[0]), 3),
                                     dtype='uint8')

        rcoords = np.array(offset).reshape(-1, 1) + self.app.rLoc.reshape(-1, 1) + self.app.y.rcoords

        if enlarge[0] >= 0 and enlarge[1] >= 0:
            # Bottom right region

            img_enlarged[:img.shape[0], :img.shape[1], :] = img
            img_enlarged[rcoords[1], rcoords[0], :] = self.app.y.appear

            if self.arm_image is not None and self.arm_image is not None and img_enlarged.shape[0] > br[1]:
                set_height = img_enlarged.shape[0] - br[1]

                self.arm_image = cv2.resize(self.arm_image,(self.arm_image.shape[1],set_height))
                self.arm_mask = cv2.resize(self.arm_mask,(self.arm_mask.shape[1], set_height))

                # Todo: The images are not perfectly aligned, have to be manually adjusted
                left = int(br[0] / 2 + tl[0] / 2 - self.arm_image.shape[1] / 2)-11
                img_enlarged[br[1]:img_enlarged.shape[0],left:left+self.arm_image.shape[1],:] = self.arm_image

                # Todo: Need double-check
                # tl, br
                self.arm_region = [ (min(left, img.shape[1]), min(br[1], img.shape[0])),(min(left+self.arm_image.shape[1], img.shape[1]), img.shape[0])]

            img[:, :, :] = img_enlarged[:img.shape[0], :img.shape[1], :]

        elif enlarge[0] < 0 and enlarge[1] >= 0:
            # Bottom left region

            img_enlarged[:img.shape[0], abs(enlarge[0]):img.shape[1] + abs(enlarge[0]), :] = img
            img_enlarged[rcoords[1], rcoords[0] + abs(enlarge[0]), :] = self.app.y.appear

            if self.arm_image is not None and self.arm_image is not None and img_enlarged.shape[0] > br[1]:
                set_height = img_enlarged.shape[0] - br[1]

                self.arm_image = cv2.resize(self.arm_image, (self.arm_image.shape[1], set_height))
                self.arm_mask = cv2.resize(self.arm_mask, (self.arm_mask.shape[1], set_height))

                # Todo: The images are not perfectly aligned, have to be manually adjusted
                left = int(br[0] / 2 + tl[0] / 2 - self.arm_image.shape[1] / 2) - 11 + abs(enlarge[0])
                img_enlarged[br[1]:img_enlarged.shape[0], left:left + self.arm_image.shape[1], :] = self.arm_image

                # Todo: Need double-check
                # tl, br
                self.arm_region = [(max(left-abs(enlarge[0]),0), min(br[1],img.shape[0])), (max(left+self.arm_image.shape[1]-abs(enlarge[0]), 0), img.shape[0])]

            # cv2.imshow('debug',img_enlarged)
            # cv2.waitKey()

            img[:, :, :] = img_enlarged[:img.shape[0],
                                abs(enlarge[0]):img.shape[1] + abs(enlarge[0]), :]

        elif enlarge[0] >= 0 and enlarge[1] < 0:
            # Top right region

            img_enlarged[abs(enlarge[1]):img.shape[0] + abs(enlarge[1]), :img.shape[1], :] = img
            img_enlarged[rcoords[1], rcoords[0], :] = self.app.y.appear
            # Add arm image if it is needed
            if self.arm_image is not None and self.arm_image is not None and img_enlarged.shape[0] > br[1]:
                set_height = img_enlarged.shape[0] - br[1]

                self.arm_image = cv2.resize(self.arm_image, (self.arm_image.shape[1], set_height))
                self.arm_mask = cv2.resize(self.arm_mask, (self.arm_mask.shape[1], set_height))

                # Todo: The images are not perfectly aligned, have to be manually adjusted
                left = int(br[0] / 2 + tl[0] / 2 - self.arm_image.shape[1] / 2) - 11
                img_enlarged[br[1]:img_enlarged.shape[0], left:left + self.arm_image.shape[1], :] = self.arm_image

                # Todo: Need double-check
                # tl, br
                self.arm_region = [ (min(left, img.shape[1]), min(br[1]-abs(enlarge[1]), 0)),(min(left+self.arm_image.shape[1]-abs(enlarge[0]), 0), img.shape[0])]

            img[:, :, :] = img_enlarged[abs(enlarge[1]):img.shape[0] + abs(enlarge[1]),
                                :img.shape[1], :]
        else:
            # top left region

            img_enlarged[abs(enlarge[1]):img.shape[0] + abs(enlarge[1]),
            abs(enlarge[0]):img.shape[1] + abs(enlarge[0]), :] = img
            img_enlarged[rcoords[1], rcoords[0], :] = self.app.y.appear
            # Add arm image if it is needed
            if self.arm_image is not None and self.arm_image is not None and img_enlarged.shape[0] > br[1]:
                set_height = img_enlarged.shape[0] - br[1]

                self.arm_image = cv2.resize(self.arm_image, (self.arm_image.shape[1], set_height))
                self.arm_mask = cv2.resize(self.arm_mask, (self.arm_mask.shape[1], set_height))

                # Todo: The images are not perfectly aligned, have to be manually adjusted
                left = int(br[0] / 2 + tl[0] / 2 - self.arm_image.shape[1] / 2) - 11
                img_enlarged[br[1]:img_enlarged.shape[0], left:left + self.arm_image.shape[1], :] = self.arm_image

                # Todo: Need double-check
                # tl, br
                self.arm_region = [ (min(left-abs(enlarge[0]), 0), min(br[1]-abs(enlarge[1]), 0)),(min(left+self.arm_image.shape[1], img.shape[1]), img.shape[0])]

            img[:, :, :] = img_enlarged[abs(enlarge[1]):img.shape[0] + abs(enlarge[1]),
                                abs(enlarge[0]):img.shape[1] + abs(enlarge[0]), :]



        # # 0. pixel check too slow
        # rcoords = np.array(offset).reshape(-1, 1) + self.app.rLoc.reshape(-1, 1) + self.app.y.rcoords
        # aa = np.where(rcoords[0] < img.shape[1])[0]
        # bb = np.where(rcoords[0] >= 0)[0]
        # cc = np.where(rcoords[1] < img.shape[0])[0]
        # dd = np.where(rcoords[1] >= 0)[0]
        # index_filtered = list(set(aa) & set(bb) & set(cc) & set(dd))
        # rcoords = rcoords[:, index_filtered]
        # img[rcoords[1], rcoords[0], :] = self.app.y.appear[index_filtered,:]

        # # 1. blending too slow
        # img2 = np.zeros_like(img)
        # alpha = np.zeros(img.shape)
        #
        # alpha[tl[1]:br[1],tl[0]:br[0],:] = np.tile(self.app.y.mask[:br[1]-tl[1],:br[0]-tl[0]][:, :, None], [1, 1, 3])
        #
        # alpha = alpha.astype(float)/255
        #
        # img2[tl[1]:br[1],tl[0]:br[0]] = self.app.y.image[:br[1]-tl[1],:br[0]-tl[0]]
        #
        # outImage = alpha * img2.astype(float) + (1.0 - alpha)* img.astype(float)
        # outImage = outImage.astype('uint8')
        # img[:,:,:] = outImage[:,:,:]


    @staticmethod
    def buildSphereAgent(radius, color, rLoc=None):
        app_sphere = Template.buildSphere(radius, color, rLoc)
        return Hand(app_sphere)

    @staticmethod
    def buildSquareAgent(size, color, rLoc=None):
        app_Square = Template.buildSquare(size, color, rLoc)
        return Hand(app_Square)

#
# ========================= puzzle.simulator.hand ========================
