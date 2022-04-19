# ========================= puzzle.piece.template =========================
#
# @brief    The base class for puzzle piece specification or description
#           encapsulation. This simply stores the template image and
#           related data for a puzzle piece in its canonical
#           orientation.
#
# ========================= puzzle.piece.template =========================
#
# @file     template.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/24 [created]
#           2021/07/28 [modified]
#
#
# ========================= puzzle.piece.template =========================

# ===== Environment / Dependencies
#
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum

import cv2
import matplotlib.pyplot as plt
import numpy as np

from puzzle.utils.imageProcessing import rotate_im


# ===== Helper Elements
#

class PieceStatus(Enum):
    """
    @brief PieceStatus used to keep track of the status of pieces.
    """

    UNKNOWN = 0 # @< The default status.
    MEASURED = 1  # @< The initial status in the current measured board (visible).
    TRACKED = 2 # @< Not present in the current measured board (including INVISIBLE & GONE).
    INHAND = 3

    INVISIBLE=4 # @< A subset of TRACKED, which is occluded.
    GONE=5 # @< A subset of TRACKED, which is not occluded. Be careful that this status may be inaccurate when piece extraction fails.



@dataclass
class PuzzleTemplate:
    size: np.ndarray = np.array([])  # @< Tight bbox size of puzzle piece image.
    rcoords: np.ndarray = np.array([])  # @< Puzzle piece linear image coordinates.
    appear: np.ndarray = np.array([])  # @< Puzzle piece linear color/appearance.
    image: np.ndarray = np.array([], dtype='uint8')  # @< Template RGB image with BG default fill.
    mask: np.ndarray = np.array([], dtype='uint8')  # @< Template binary mask image.
    contour: np.ndarray = np.array([], dtype='uint8')  # @< Template binary contour image.
    contour_pts: np.ndarray = np.array([])  # @< Template contour points.

    # Feature related
    kpFea: tuple = ()  # @< The processed keypoint feature.
    colorFea: np.ndarray = np.array([])  # @< The processed color feature.
    shapeFea: np.ndarray = np.array([])  # @< The processed shape feature.


#
# ========================= puzzle.piece.template =========================
#

class Template:

    def __init__(self, y=None, r=(0, 0), id=None, theta=0, pieceStatus=PieceStatus.UNKNOWN):
        """
        @brief  Constructor for template class.

        Args:
            y: The puzzle piece template source data, if given. It is a class instance, see puzzleTemplate.
            r: The puzzle piece location in the whole image.
            id: The puzzle piece id in the measured board. Be set up by the board.
            theta: The puzzle piece aligned angle.
            pieceStatus: The status of the puzzle pieces, including UNKNOWN, MEASURED, TRACKED, and INHAND.
        """

        self.y = y # @< A PuzzleTemplate instance.
        self.rLoc = np.array(r)  # @< The default location is the top left corner.
        self.id = id    # @< Mainly for display and user operation.
        self.status = pieceStatus  # @< To save the status of the puzzle pieces, for tracking purpose.
        self.theta = theta  # @< Should be set up later by the alignment function. For regular piece, which means the angle to rotate to its upright.

        self.tracking_life = 0 # @< For saving the life count, only useful in the tracking function

    def size(self):
        """
        @brief  Return the dimensions of the puzzle piece image.

        Returns:
            Dimensions of the puzzle piece image
        """

        return self.y.size

    @staticmethod
    def getEig(img):
        """
        @brief  To find the major and minor axes of a blob and then return the aligned rotation.
                See https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/ for details.
                PCA is our default method which does not perform very well.

        Args:
            img: A contour image.

        Returns:
            theta: The aligned angle (degree).

        """

        # @note Currently, we use the image center

        y, x = np.nonzero(img)
        # x = x - np.mean(x)
        # y = y - np.mean(y)
        #
        x = x - np.mean(img.shape[1] / 2)
        y = y - np.mean(img.shape[0] / 2)

        coords = np.vstack([x, y])
        cov = np.cov(coords)
        evals, evecs = np.linalg.eig(cov)
        sort_indices = np.argsort(evals)[::-1]
        v1 = evecs[:, sort_indices[0]]  # Eigenvector with largest eigenvalue
        v2 = evecs[:, sort_indices[1]]

        dict = {
            'x': x,
            'y': y,
            'v1': v1,
            'v2': v2,
        }

        theta = np.rad2deg(np.arctan2(dict['v1'][1], dict['v1'][0]))

        # # Debug only
        #
        # scale = 20
        # plt.plot([dict['v1'][0] * -scale * 2, dict['v1'][0] * scale * 2],
        #          [dict['v1'][1] * -scale * 2, dict['v1'][1] * scale * 2], color='red')
        # plt.plot([dict['v2'][0] * -scale, dict['v2'][0] * scale],
        #          [dict['v2'][1] * -scale, dict['v2'][1] * scale], color='blue')
        # plt.plot(x, y, 'k.')
        # plt.axis('equal')
        # plt.gca().invert_yaxis()  # Match the image system with origin at top left
        # plt.show()

        return theta

    def setPlacement(self, r, offset=False, isCenter=False):
        """
        @brief  Provide pixel placement location information.

        Args:
            r: Location of its frame origin.
            offset: Boolean indicating whether it sets the offset or not.
            isCenter: Boolean indicating r is center or not.
        """

        if isCenter:
            if offset:
                self.rLoc = np.array(self.rLoc + r - np.ceil(self.y.size / 2))
            else:
                self.rLoc = np.array(r - np.ceil(self.y.size / 2))
        else:
            if offset:
                self.rLoc = np.array(self.rLoc + r)
            else:
                self.rLoc = np.array(r)

    def getMask(self, theMask, offset=[0, 0]):
        """
        @brief Get an updated mask of the target
        Args:
            theMask: The original mask of the target.
            offset: The movement.

        Returns:
            theMask: The updated mask of the target.
        """

        rcoords = np.array(offset).reshape(-1, 1) + self.rLoc.reshape(-1, 1) + self.y.rcoords

        # Have to deal with the out of bounds situation
        # Since the hand is small, there is no chance that it will exceed the left bound and the right bound at the same time
        x_max = np.max(rcoords[0])
        y_max = np.max(rcoords[1])
        x_min = np.min(rcoords[0])
        y_min = np.min(rcoords[1])

        enlarge = [0,0]
        if x_min<0:
            enlarge[0] = x_min
        elif x_max>theMask.shape[1]:
            enlarge[0] = x_max+1-theMask.shape[1]

        if y_min<0:
            enlarge[1] = y_min
        elif y_max>theMask.shape[0]:
            enlarge[1] = y_max+1-theMask.shape[0]

        theMask_enlarged = np.zeros((theMask.shape[0]+abs(enlarge[1]), theMask.shape[1]+abs(enlarge[0])), dtype='uint8')

        if enlarge[0]<0 and enlarge[1]<0:
            theMask_enlarged[rcoords[1]+abs(enlarge[1]), rcoords[0]+abs(enlarge[0])] =1
            theMask[:, :] = theMask_enlarged[abs(enlarge[1]):theMask.shape[0]+abs(enlarge[1]), \
                            abs(enlarge[0]):theMask.shape[1]+abs(enlarge[0])]

        elif enlarge[0]>0 and enlarge[1]<0:
            theMask_enlarged[rcoords[1]+abs(enlarge[1]), rcoords[0]] =1
            theMask[:, :] = theMask_enlarged[abs(enlarge[1]):theMask.shape[0]+abs(enlarge[1]), \
                            :theMask.shape[1]]

        elif enlarge[0]<0 and enlarge[1]>0:
            theMask_enlarged[rcoords[1], rcoords[0]+abs(enlarge[0])] =1
            theMask[:, :] = theMask_enlarged[:theMask.shape[0], \
                            abs(enlarge[0]):theMask.shape[1]+abs(enlarge[0])]

        else:
            theMask_enlarged[rcoords[1], rcoords[0]] = 1
            theMask[:, :] = theMask_enlarged[:theMask.shape[0], :theMask.shape[1]]

        return theMask

    def placeInImage(self, theImage, offset=[0, 0], CONTOUR_DISPLAY=True):
        """
        @brief  Insert the puzzle piece into the image in the original location.

        Args:
            theImage: The source image to put puzzle piece into.
            offset: The offset list.
            CONTOUR_DISPLAY: The flag indicating whether to display the contours.
        """

        # Remap coordinates from own image sprite coordinates to bigger
        # image coordinates. 2*N
        rcoords = np.array(offset).reshape(-1, 1) + self.rLoc.reshape(-1, 1) + self.y.rcoords

        # Dump color/appearance information into the image (It will override the original image).
        # If rcoords is outside the image, they will not be displayed
        theImage[rcoords[1], rcoords[0], :] = self.y.appear

        # May have to re-draw the contour for better visualization
        if CONTOUR_DISPLAY:
            rcoords = list(np.where(self.y.contour))
            rcoords[0], rcoords[1] = rcoords[1], rcoords[0]
            rcoords = np.array(offset).reshape(-1, 1) + self.rLoc.reshape(-1, 1) + rcoords
            theImage[rcoords[1], rcoords[0], :] = [0, 0, 0]

    def placeInImageAt(self, theImage, rc, theta=None, isCenter=False, CONTOUR_DISPLAY=True):
        """
        @brief  Insert the puzzle piece into the image at the given location.

        Args:
            theImage: The source image to put puzzle piece into.
            rc: The coordinate location.
            theta: The orientation of the puzzle piece (default = 0).
            isCenter: The flag indicating whether the given location is for the center.
            CONTOUR_DISPLAY: The flag indicating whether to display the contours.
        """

        if theta is not None:
            thePiece = self.rotatePiece(theta)
        else:
            thePiece = self

        # If specification is at center, then compute offset to top-left corner.
        if isCenter:
            rc = rc - np.ceil(thePiece.y.size / 2)

        # Remap coordinates from own image sprite coordinates to bigger image coordinates.
        rcoords = rc.reshape(-1, 1) + thePiece.y.rcoords

        # Dump color/appearance information into the image.
        theImage[rcoords[1], rcoords[0], :] = thePiece.y.appear

        # May have to re-draw the contour for better visualization
        if CONTOUR_DISPLAY:
            rcoords = list(np.where(thePiece.y.contour))
            rcoords[0], rcoords[1] = rcoords[1], rcoords[0]
            rcoords = rc.reshape(-1, 1) + rcoords
            theImage[rcoords[1], rcoords[0], :] = [0, 0, 0]

    def toImage(self):
        """
        @brief  Return the puzzle piece image (cropped).

        Returns:
            theImage: The puzzle piece image (cropped).
        """

        theImage = np.zeros_like(self.y.image)
        theImage[self.y.rcoords[1], self.y.rcoords[0], :] = self.y.appear

        return theImage

    def display(self, fh=None):
        """
        @brief  Display the puzzle piece contents in an image window.

        Args:
            fh: The figure label/handle if available. (optional)

        Returns:
            The handle of the image.
        """

        if fh:
            # See https://stackoverflow.com/a/7987462/5269146
            fh = plt.figure(fh.number)
        else:
            fh = plt.figure()

        # See https://stackoverflow.com/questions/13384653/imshow-extent-and-aspect
        # plt.imshow(self.y.image, extent = [0, 1, 0, 1])

        theImage = self.toImage()
        plt.imshow(theImage)

        # plt.show()

        return fh

    @staticmethod
    def buildFromMaskAndImage(theMask, theImage, rLoc=None, pieceStatus=PieceStatus.MEASURED):
        """
        @brief  Given a mask (individual) and an image of same base dimensions, use to
                instantiate a puzzle piece template.

        Args:
            theMask: The individual mask.
            theImage: The source image.
            rLoc: The puzzle piece location in the whole image.

        Returns:
            The puzzle piece instance.
        """

        y = PuzzleTemplate()

        # Populate dimensions.
        # Updated to OpenCV style
        y.size = [theMask.shape[1], theMask.shape[0]]

        y.mask = theMask.astype('uint8')

        # Create a contour of the mask
        cnts = cv2.findContours(y.mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)

        y.contour_pts = cnts[0][0]
        y.contour = np.zeros_like(y.mask).astype('uint8')
        cv2.drawContours(y.contour, cnts[0], -1, (255, 255, 255), thickness=2)

        # Debug only
        # hull = cv2.convexHull(cnts[0][0])
        # aa = np.zeros_like(y.mask).astype('uint8')
        # cv2.drawContours(aa, hull, -1, (255, 255, 255), thickness=10)
        # cv2.imshow('Test', aa)
        # cv2.waitKey()

        y.rcoords = list(np.nonzero(theMask))  # 2 (row,col) x N

        # Updated to OpenCV style -> (x,y)
        y.rcoords[0], y.rcoords[1] = y.rcoords[1], y.rcoords[0]  # 2 (x;y) x N
        y.rcoords = np.array(y.rcoords)

        y.appear = theImage[y.rcoords[1], y.rcoords[0], :]

        # Store template image.
        # For now, not concerned about bad image data outside of mask.
        y.image = theImage

        if not rLoc:
            thePiece = Template(y)
        else:
            thePiece = Template(y, rLoc)

        # Set up the rotation (with theta, we can correct the rotation)
        thePiece.theta = -Template.getEig(thePiece.y.mask)

        # Set up the status of the piece
        thePiece.status = pieceStatus

        return thePiece

    def rotatePiece(self, theta):
        """
        @brief Rotate the puzzle template instance by the given angle.

        Args:
            theta: The rotated angle.

        Returns:
            A new puzzle template instance.
        """

        # Create a new instance. Without rLoc.
        thePiece = Template(y=deepcopy(self.y), id=deepcopy(self.id))

        # By default the rotation is around its center (img center)
        # thePiece.y.mask, mask_temp, M, x_pad, y_pad = rotate_im(thePiece.y.mask, theta)

        # With rLoc_relative option
        thePiece.y.mask, mask_temp, M, x_pad, y_pad, rLoc_relative = rotate_im(thePiece.y.mask, theta)
        thePiece.rLoc_relative = rLoc_relative

        # Have to apply a thresh to deal with holes caused by interpolation
        _, thePiece.y.mask = cv2.threshold(thePiece.y.mask, 5, 255, cv2.THRESH_BINARY)

        # Have to apply a filter to smooth the edges
        thePiece.y.mask = cv2.GaussianBlur(thePiece.y.mask, (3, 3), 0)

        # thePiece.y.image, _, _, _, _ = rotate_im(thePiece.y.image, theta, mask=mask_temp)

        # With rLoc_relative option
        thePiece.y.image, _, _, _, _, _ = rotate_im(thePiece.y.image, theta, mask=mask_temp)

        thePiece.y.size = [thePiece.y.mask.shape[1], thePiece.y.mask.shape[0]]

        thePiece.y.rcoords = list(np.nonzero(thePiece.y.mask))  # 2 (row;col) x N

        # Updated to OpenCV style -> (x,y)
        thePiece.y.rcoords[0], thePiece.y.rcoords[1] = thePiece.y.rcoords[1], thePiece.y.rcoords[0]  # 2 (x;y) x N
        thePiece.y.rcoords = np.array(thePiece.y.rcoords)

        thePiece.y.appear = thePiece.y.image[thePiece.y.rcoords[1], thePiece.y.rcoords[0], :]

        '''
        @todo   If we simply transform the original info, the result may be inaccurate?
                May still worth it. 
        '''

        # Create a contour of the mask
        cnts = cv2.findContours(thePiece.y.mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)

        thePiece.y.contour_pts = cnts[0][0]
        thePiece.y.contour = np.zeros_like(thePiece.y.mask).astype('uint8')
        cv2.drawContours(thePiece.y.contour, cnts[0], -1, (255, 255, 255), thickness=2)

        # Might be negative
        thePiece.rLoc = self.rLoc - np.array([np.sum(x_pad), np.sum(y_pad)])

        # Set up the new rotation
        thePiece.theta = self.theta + theta

        # Reset kpFea while colorFea & shapeFea is associated to the corrected case
        thePiece.y.kpFea = ()

        return thePiece

    @staticmethod
    def buildSquare(size, color, rLoc=None):
        """
        @brief  Build a square piece.

        Args:
            size: The side length of the square
            color: (3,). The RGB color.
            rLoc: (x, y). The puzzle piece location in the whole image. x: left-to-right. y:top-to-down

        Returns:
            The puzzle piece instance.
        """

        y = PuzzleTemplate()

        # the tight bbox is just the square itself, so size is just size
        y.size = np.array([size, size])
        y.mask = np.ones((size, size), dtype=np.uint8) * 255

        # Create a contour of the mask
        cnts = cv2.findContours(y.mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)

        y.contour_pts = cnts[0][0]
        y.contour = np.zeros_like(y.mask).astype('uint8')
        cv2.drawContours(y.contour, cnts[0], -1, (255, 255, 255), thickness=2)

        y.rcoords = list(np.nonzero(y.mask))  # 2 (row,col) x N
        # Updated to OpenCV style -> (x,y)
        y.rcoords[0], y.rcoords[1] = y.rcoords[1], y.rcoords[0]
        y.rcoords = np.array(y.rcoords)

        # y.image = np.zeros((size, size, 3), dtype=np.uint8)
        # y.image = cv2.rectangle(y.image, (0, 0), (size - 1, size - 1), color=color, thickness=-1)
        y.image = np.full((size, size, 3), color, dtype=np.uint8)

        y.appear = y.image[y.rcoords[1], y.rcoords[0], :]

        if not rLoc:
            thePiece = Template(y)
        else:
            thePiece = Template(y, rLoc)

        return thePiece

    @staticmethod
    def buildSphere(radius, color, rLoc=None):
        """
        @brief  Build a sphere piece

        Args:
            radius: The radius of the sphere.
            color: (3,). The RGB color.
            rLoc: (x, y). The puzzle piece location in the whole image. x: left-to-right. y:top-to-down
            The puzzle piece instance.
        """

        y = PuzzleTemplate()

        # the tight bbox is just the square itself, so size is just size
        y.size = np.array([radius, radius]) * 2
        y.mask = np.zeros((2 * radius, 2 * radius), dtype=np.uint8)
        y.mask = cv2.circle(y.mask, center=(radius - 1, radius - 1), radius=radius, color=(255, 255, 255), thickness=-1)

        # Create a contour of the mask
        cnts = cv2.findContours(y.mask, cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)

        y.contour_pts = cnts[0][0]
        y.contour = np.zeros_like(y.mask).astype('uint8')
        cv2.drawContours(y.contour, cnts[0], -1, (255, 255, 255), thickness=2)

        y.rcoords = list(np.nonzero(y.mask))  # 2 (row,col) x N
        # Updated to OpenCV style -> (x,y)
        y.rcoords[0], y.rcoords[1] = y.rcoords[1], y.rcoords[0]
        y.rcoords = np.array(y.rcoords)

        y.image = np.ones((2 * radius, 2 * radius, 3), dtype=np.uint8)
        y.image = cv2.circle(y.image, radius=radius, center=(radius - 1, radius - 1), color=color, thickness=-1)
        y.appear = y.image[y.rcoords[1], y.rcoords[0], :]

        if not rLoc:
            thePiece = Template(y)
        else:
            thePiece = Template(y, rLoc)

        return thePiece

#
# ========================= puzzle.piece.template =========================
