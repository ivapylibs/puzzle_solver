#================================ puzzle.piece code ==================================
##
# @package  puzzle.piece
# @brief    Classes for puzzle piece specification or description encapsulation. 
# @ingroup  PuzzleSolver
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#
# @date     2024/10/20 [merged from Percevier branch]
# @date     2021/07/28 [modified]
# @date     2021/07/24 [created]
#

#================================ puzzle.piece code ==================================
# NOTES:
#   95 columns.
#   indent is 4 spaces.
#
#================================ puzzle.piece code ==================================

# ===== Environment / Dependencies
#
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np

from puzzle.utils.imageProcessing import rotate_im

import matplotlib.pyplot as plt
import ivapy.display_cv as display

# ===== Helper Elements
#

class PieceStatus(Enum):
    '''!
    @ingroup    PuzzleSolver
    @brief PieceStatus used to keep track of the status of pieces.
    '''

    UNKNOWN  = 0    # @< The default status.
    MEASURED = 1    # @< The initial status in the current measured board (visible).
    TRACKED  = 2    # @< Not present in the current measured board (including INVISIBLE & GONE).

    INHAND   = 3    # @< Presumably in player's/worker's hand.
    INVISIBLE = 4   # @< A subset of TRACKED, which is occluded.
    GONE = 5        # @< A subset of TRACKED, which is not occluded. Be careful that this status
                    #       may be inaccurate when piece extraction fails.



#
#================================= PuzzleTemplate ================================
#
@dataclass
class PuzzleTemplate:
    '''!
    @ingroup    PuzzleSolver
    @brief  Data class containing puzzle piece information.
    '''

    pcorner:        np.ndarray = np.array([])   # @< The top left corner (x,y) of puzzle piece bbox.
    size:           np.ndarray = np.array([])   # @< Tight bbox size (width, height) of puzzle piece image.
    rcoords:        np.ndarray = np.array([])   # @< Puzzle piece linear image coordinates.
    appear:         np.ndarray = np.array([])   # @< Puzzle piece vectorized color/appearance.
    image:          np.ndarray = np.array([], dtype='uint8')    # @< Image w/BG (original).
    mask:           np.ndarray = np.array([], dtype='uint8')    # @< Binary mask image.
    contour:        np.ndarray = np.array([], dtype='uint8')    # @< Binary contour image.
    contour_pts:    np.ndarray = np.array([])   # @< Template contour points.

#
#==================================== Template ===================================
#

class Template:
    '''!
    @ingroup    PuzzleSolver
    @brief  Stores and encapsulates a template instance of a visual puzzle piece.

    The language here is general, but the fact that it lives in the puzzle.piece namespace
    indicates that this class is strictly associated to puzzle pieces.  As the base class,
    it probably implements the simplest, no frills version of a template puzzle piece.

    '''

    #================================ __init__ ===============================
    #
    def __init__(self, y:PuzzleTemplate=None, r=None, id=None, theta=0, pieceStatus=PieceStatus.UNKNOWN):
        '''!
        @brief  Constructor for template class.

        Args:
            y: The puzzle piece template source data, if given. It is a class instance, see puzzleTemplate.
            r: The puzzle piece location in the whole image.
            id: The puzzle piece id in the measured board. Be set up by the board.
            theta: The puzzle piece aligned angle.
            pieceStatus: The status of the puzzle pieces, including UNKNOWN, MEASURED, TRACKED, and INHAND.
        '''

        self.y = y                  # @< A PuzzleTemplate instance.
        if (r is None):
          self.rLoc = y.pcorner     # @< The default location is the top left corner.
        else:
          self.rLoc = np.array(r)     
        # @todo Might actually be the centroid.
        # @todo Why is the location stored here when PuzzleTemplate has it too?
        # @todo What benefit occurs from the duplicate given that there is potentialy for
        #       mismatch? Is mismatch useful?
        # @todo Good news is that only location is included outside of PuzzleTemplate
        #       which means that update can take care of it as needed without getting
        #       too complex. Just gotta work out what will be needed.
        #

        self.id = id                # @< Unique ID for piece (assist with data association).
        self.status = pieceStatus   # @< Status of the puzzle pieces, for tracking purpose.
        self.theta  = theta         # @< Should be set up later by the alignment function. For
                                    # regular piece, which means the angle to rotate to its upright.

        self.lifespan = 0           # @< Save life count, only useful in the tracking function.
        self.featVec  = None        # @< If assigned, feature descriptor vector of puzzle piece.

    #================================== size =================================
    #
    def size(self):
        """!
        @brief  Return the dimensions of the puzzle piece image.

        Returns:
            Dimensions of the puzzle piece image
        """

        return self.y.size

    #============================== setPlacement =============================
    #
    def setPlacement(self, r, isOffset=False, isCenter=False):
        """!
        @brief  Provide pixel placement location information.

        @param[in]  r           Location of puzzle piece "frame origin."
        @param[in]  isOffset    Boolean flag indicating whether placement is an offset (= Delta r).
        @param[in]  isCenter    Boolean flag indicating if r is center reference.
        """

        if isOffset:
            self.rLoc = np.array(self.rLoc + r)
            self.y.pcorner = np.array(self.y.pcorner + r)
        else:
            if isCenter:
                self.rLoc = np.array(r - np.ceil(self.y.size / 2))
            else:
                self.cLoc = np.array(self.y.pcorner + r - self.y.pcorner) #todo Need to double check.
                self.rLoc = np.array(r)

    #    if isCenter:        # Specifying center and not top-left corner.
    #        if isOffset:
    #            self.rLoc = np.array(self.rLoc + r - np.ceil(self.y.size / 2))
    #        else:
    #            self.rLoc = np.array(r - np.ceil(self.y.size / 2))
    #    else:
    #        if isOffset:
    #            self.rLoc = np.array(self.rLoc + r)
    #        else:
    #            self.rLoc = np.array(r)

    #================================ displace ===============================
    #
    def displace(self, dr):
        """!
        @brief  Displace puzzle piece.

        @param[in]  dr          Displacement to apply.
        @param[in]  isCenter    Boolean flag indicating if r is center reference.
        """

        self.setPlacement(dr, True, False)

    #=============================== genFeature ==============================
    #
    def genFeature(self, theMatcher):

        self.featVec = theMatcher.extractFeature(self)

    #=============================== getFeature ==============================
    #
    def getFeature(self, theMatcher = None):
        """!
        @brief  Get the feature vector of the puzzle piece. Assign if not
                defined based on passed matcher.

        @param[in] theMatcher   Optional but recommended argument that specifies
                                the feature matching implementation.
        """

        if self.featVec is not None:
            return self.featVec 
        else:
            if theMatcher is None:
                return None
            else:
                self.genFeature(theMatcher)
                return self.featVec

    #=============================== setStatus ===============================
    #
    def setStatus(self, theStatus):

        self.status = theStatus

    #================================ getMask ================================
    #
    def getMask(self, theMask, offset=[0, 0]):
        """!
        @brief Get an updated mask of the target.

        @param[in] theMask  Original mask of the target.
        @param[in] offset   Movement.

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

    #============================== placeInImage =============================
    #
    def placeInImage(self, theImage, offset=[0, 0], CONTOUR_DISPLAY=True):
        """!
        @brief  Insert the puzzle piece into the image in the original location.

        @param[in] theImage     Source image to put puzzle piece into.
        @param[in] offset       Offset coordinates.

        @param[in] CONTOUR_DISPLAY  Flag indicating whether to display the contours.
        """

        # Remap coordinates based on internal model of location. See comment below.
        #DEBUG
        #print(offset)
        #print(type(self.y.pcorner))
        #print(type(self.y.rcoords))
        #print(self.y.pcorner)
        #print(self.y.rcoords)
        #print(self.y.size)
        rcoords = np.array(offset).reshape(-1, 1) + self.rLoc.reshape(-1, 1) + self.y.rcoords
        # @todo @WHY ADDING pcorner AND rcoords ???? WHAT IS GOING ON ???
        # @todo WHAT ABOUT OFFSET??? WHAT DOES THAT DO??

        #DEBUG
        #print(np.array(offset))
        #print(np.array(self.rLoc))
        #print(self.y.rcoords)
        #print(rcoords)

        # Dump color/appearance information into the image (override original image).
        # If rcoords is outside the image, they will not be displayed.  Automatically
        # corrected by class implementation.
        #DEBUG
        #print("==========PIM")
        #print(np.shape(self.y.appear))
        #print(np.shape(rcoords))
        theImage[rcoords[1], rcoords[0], :] = self.y.appear

        # May have to re-draw the contour for better visualization
        if CONTOUR_DISPLAY:
            rcoords = list(np.where(self.y.contour))
            rcoords[0], rcoords[1] = rcoords[1], rcoords[0]
            rcoords = np.array(offset).reshape(-1, 1) + self.rLoc.reshape(-1, 1) + rcoords
            theImage[rcoords[1], rcoords[0], :] = [0, 0, 0]

    #============================= placeInImageAt ============================
    #
    def placeInImageAt(self, theImage, rc, theta=None, isCenter=False, CONTOUR_DISPLAY=True):
        """!
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

    #================================ toImage ================================
    #
    def toImage(self):
        """!
        @brief  Return the puzzle piece image (cropped).

        Returns:
            theImage: The puzzle piece image (cropped).
        """

        theImage = np.zeros_like(self.y.image)
        theImage[self.y.rcoords[1], self.y.rcoords[0], :] = self.y.appear

        return theImage

    #================================ display ================================
    #
    def display(self, fh=None):
        """!
        @brief  Display the puzzle piece contents in an image window.

        Args:
            fh: The figure label/handle if available. (optional)

        Returns:
            fh: The handle of the image.
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

    #========================= buildFromMaskAndImage =========================
    #
    @staticmethod
    def buildFromMaskAndImage(theMask, theImage, cLoc=None, rLoc=None, pieceStatus=PieceStatus.MEASURED):
        """!
        @brief  Given a mask (individual) and an image of same base dimensions, use to
                instantiate a puzzle piece template.  Usually passed as cropped.

        This can be run in a few different ways.  First, assumiong that the puzzle
        piece has been cropped along with the mask.  Then providing cLoc is important
        for it to be placed in correct part of the original (uncropped) image.  If the
        placement should change for whatever reason, then specifying rLoc will do
        that.  Otherwise, cLoc and rLoc are set to be the same.

        A less common implementation is to provide the whole image and an image-wide
        mask for recovering a single piece.  Then cLoc is not needed. rLoc can still
        be used.

        Not implemented is the case of a whole image plus a cropped mask with cLoc.
        That is on the todo list.

        @param[in] theMask      Mask of individual piece.
        @param[in] theImage     Source image with puzzle piece.
        @param[in] cLoc         Corner location of puzzle piece [optional: None].
        @param[in] rLoc         Alternative puzzle piece location [optional: None].
        @param[in] pieceStatus  Status of the puzzle piece [optional, def:MEASURED]

        @param[in] thePiece     Puzzle piece instance.

        @todo   Include option to have cropped mask but full image and use cLoc.
        """

        #DEBUG CODE: DELETE LATER
        #display.rgb_binary(theImage,theMask,window_name='Puzzle Image')
        #display.wait()

        y = PuzzleTemplate()

        # Populate dimensions.
        # Updated to OpenCV style
        y.size    = [theMask.shape[1], theMask.shape[0]]        # width then height
        if cLoc is None:
          cy, cx = np.nonzero(theMask)
          cLoc = np.array([np.min(cx), np.min(cy)])
          print(cLoc)
        
        y.pcorner = cLoc
        # I originally though that setting cLoc manually was weird.  Why should it be
        # given externally?   Why isn't it just the min of rcoords?
        # But then it made sense if the mask and image were cropped, at which point
        # not sending cLoc was weird.  Then I ran across a case where the mask was of
        # the size of the uncropped image but only captured a single piece.  Made
        # sense and was set to be optional, with code updated to support either
        # verison.  - 10/05/2024 - PAV.
        #
        # The role of rLoc is to support moving the piece to a new location.
        # In general, it looks like the puzzle piece retains its original cLoc.
        # Then changes are made to rLoc and that is what is used for display purpsoes.
        # The two version seem useful, so keeping that old/new corner location
        # implementation.  An earlier message noted that it was to support initial
        # and changed corner locations.  Makes sense. - 10/05/2024 - PAV.
        #

        y.mask = theMask.astype('uint8')

        # Create a contour of the mask.  Find version gets the contour/boundary.
        # Draw version creates binary contour mask.
        cnts = cv2.findContours(y.mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        y.contour_pts = cnts[0][0]
        y.contour = np.zeros_like(y.mask).astype('uint8')
        cv2.drawContours(y.contour, cnts[0], -1, 255, thickness=2)

        # Debug only
        # hull = cv2.convexHull(cnts[0][0])
        # aa = np.zeros_like(y.mask).astype('uint8')
        # cv2.drawContours(aa, hull, -1, (255, 255, 255), thickness=10)
        # cv2.imshow('Test', aa)
        # cv2.waitKey()

        y.rcoords = list(np.nonzero(theMask))  # 2 (row,col) x N

        # Get individual pixel colors from image patch.  Updated to OpenCV style -> (x,y)
        y.rcoords[0], y.rcoords[1] = y.rcoords[1], y.rcoords[0] # 2 (x;y) x N
        y.rcoords = np.array(y.rcoords)

        y.appear = theImage[y.rcoords[1], y.rcoords[0], :]      # Vectorized appearance.

        # Store template image.
        # For now, not concerned about bad image data outside of mask.
        y.image = theImage

        if rLoc is None:
            thePiece = Template(y, cLoc)
        else:
            thePiece = Template(y, rLoc)

        # Set up the rotation (with theta, we can correct the rotation)
        thePiece.theta = -Template.getEig(thePiece.y.mask)

        # Set up the status of the piece
        thePiece.status = pieceStatus

        return thePiece

    #================================= update ================================
    #
    def update(self, matchedPiece):
        """!
        @brief  Update template board puzzle piece based on association.

        Performs the simplest of updates.

        @param[in]  matchedPiece    Latest matched measurement of a piece.
        """

        # Should update self (own properties) and (feature vector properties).
        # How to do this has high variation, especially given that the feature
        # vector derives from the piece properties.  Updating the piece properties
        # may require non-trivial updates to the feature vector.  The degrees
        # of freedom here are "high."
        #
        # What is right way to code?  Try to dump many options into the base
        # template, or use sub-classes?   More complex case is to perform a
        # mix of the two.
        #
        self.featVec = matchedPiece.featVec


    #============================== rotatePiece ==============================
    #
    def rotatePiece(self, theta):
        """!
        @brief Rotate the puzzle template instance by the given angle.

        Args:
            theta: The rotated angle.

        Returns:
            thePiece: A new puzzle template instance.
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
        #thePiece.y.kpFea = ()
        # @todo Remove kpFea, colorFea, and shapeFea code.

        return thePiece

    #================================= getEig ================================
    #
    @staticmethod
    def getEig(img):
        """!
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

    #============================== buildSquare ==============================
    #
    @staticmethod
    def buildSquare(size, color, rLoc=[0,0]):
        """!
        @brief  Build a square piece.

        @param[in] size     Side length of the square
        @param[in] color    The RGB color [size: (3,)]
        @param[in] rLoc     Puzzle piece location whole image [(x,y) - x: left-to-right. y:top-to-down]

        @return Puzzle piece instance.
        """

        y = PuzzleTemplate()

        # the tight bbox is just the square itself, so size is just size
        y.size = np.array([size, size])
        y.mask = np.ones((size, size), dtype=np.uint8) * 255
        y.pcorner = np.array(rLoc)

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
            thePiece = Template(y, np.array(rLoc))

        return thePiece

    #============================== buildSphere ==============================
    #
    @staticmethod
    def buildSphere(radius, color, rLoc=[0,0]):
        """!
        @brief  Build a sphere piece.

        Args:
            radius: The radius of the sphere.
            color: (3,). The RGB color.
            rLoc: (x, y). The puzzle piece location in the whole image. x: left-to-right. y:top-to-down
            The puzzle piece instance.

        Returns:
            The puzzle piece instance.
        """

        y = PuzzleTemplate()

        # the tight bbox is just the square itself, so size is just size
        y.size = np.array([radius, radius]) * 2
        y.mask = np.zeros((2 * radius, 2 * radius), dtype=np.uint8)
        y.mask = cv2.circle(y.mask, center=(radius - 1, radius - 1), radius=radius, color=(255, 255, 255), thickness=-1)
        y.pcorner = np.array(rLoc)

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
            thePiece = Template(y, np.array(rLoc))

        return thePiece


class Piece:
  '''!
  @brief    Bad code here.  Created a dummy Piece class rather than use the Template
            class for defining the static method getBuilderFromString.

  @todo     When have time, need to integrate into Template or have be generic
            function available through the Piece package. Piece.getBuilderFromString.
            or Piece.Template, Piece.Regular, etc.  For now leaving until have time
            to make correction and ensure code + unit tests work.
  '''
  staticmethod
  def getBuilderFromString(theStr):

    if (theStr == 'Template'):
      return Template
    elif (theStr == 'Regular'):
      return Regular
    else:
      return Template

#
#============================== puzzle.piece.template ==============================

#=============================== puzzle.piece.regular ==============================
#
# @brief    Establish a regular puzzle piece (4 sides with locks)
#
#=============================== puzzle.piece.regular ==============================
#
# @file     regular.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/17 [created]
#
#
#=============================== puzzle.piece.regular ==============================

#===== Environment / Dependencies
#

from puzzle.utils.sideExtractor import sideExtractor


# ===== Helper Elements
#
class EdgeType(Enum):
    """!
    @brief EdgeType used to keep track of the type of edges
    """

    UNDEFINED = 0
    IN = 1
    OUT = 2
    FLAT = 3


# Todo: May need to upgrade to other forms when we have rotations
class EdgeDirection(Enum):
    """!
    @brief EdgeDirection used to keep track of the direction of edges
    """

    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3


class EdgeDes:
    # Here we save the rotated edges
    etype: int = EdgeType.UNDEFINED  # To save the type: in/out/flat.
    image: np.ndarray = np.array([])  # To save the whole image of the edge.
    mask: np.ndarray = np.array([])  # To save the mask image of the edge.

    colorFea: np.ndarray = np.array([])  # @< The processed color feature.
    shapeFea: np.ndarray = np.array([])  # @< The processed shape feature.


#
#============================== puzzle.piece.regular =============================
#
class Regular(Template):
    '''!
    @brief  A puzzle has Regular pieces when they are all of a consistent sizing such
            that their edge structure can be compared in a standard North, South,
            East, West approach. Usually Regular pieces are part of a Gridded puzzle.
    '''

    #============================= __init__ Regular ============================
    #
    def __init__(self, y:PuzzleTemplate=None, r=(0, 0), id=None, theta=0, pieceStatus=PieceStatus.UNKNOWN):
        '''!
        @brief  Constructor for the regular puzzle piece.  Arguments are optional.

        @param[in]  y           Puzzle template instance.
        @param[in]  r           Location of the puzzle piece (top-left corner).
        @param[in]  theta       Orientation of the piece.
        @param[in]  pieceStatus Measurement status.
        '''

        super(Regular, self).__init__(y, r, id, theta, pieceStatus)

        # Assume the order 0, 1, 2, 3 correspond to left, right, top, bottom
        self.edge = [EdgeDes() for i in range(4)]

        # Debug only
        self.class_image            = None
        self.rectangle_pts          = None
        self.filtered_harris_pts    = None
        self.simple_harris_pts      = None
        self.theta = None

        if theta == 0:
            self._process(enable_rotate=False)
        else:
            self._process()

    #================================= _process ================================
    #
    def _process(self, enable_rotate=True):
        '''!
        @brief Run the sideExtractor.
        '''

        # @todo     Enable rotate should be a param flag.
        # @note     All of the work is done in sideExtractor.  Why have it be separate?

        # d_thresh is related to the size of the puzzle piece
        out_dict = sideExtractor(self.y, scale_factor=1,
                                 harris_block_size=5, harris_ksize=5,
                                 corner_score_threshold=0.7, corner_minmax_threshold=100,
                                 shape_classification_nhs=3, 
                                 d_thresh=(self.y.size[0] + self.y.size[1]) / 5,
                                 enable_rotate=enable_rotate)

        # Set up the type/img of the chosen edge
        for direction in EdgeDirection:
            self.setEdgeType(direction.value, out_dict['inout'][direction.value])
            self.edge[direction.value].image = out_dict['class_image']
            self.edge[direction.value].mask = out_dict['side_images'][direction.value]

        # @note Just for display for now
        self.class_image = out_dict['class_image']  # with four edges
        self.theta = out_dict['rotation_angle']

        # Not rotated yet
        self.rectangle_pts = out_dict['rectangle_pts']
        self.filtered_harris_pts = out_dict['filtered_harris_pts']
        self.simple_harris_pts = out_dict['simple_harris_pts']

    #=============================== setEdgeType ===============================
    #
    def setEdgeType(self, direction, etype):
        '''!
        @brief  Set up the type of the chosen edge.

        @param[in]  direction   The edge to be set up.
        @param[in]  etype       The edge type.

        @todo   Shouldn't this be a private or protected member function?
        '''

        self.edge[direction].etype = etype

    #============================== printEdgeType ==============================
    #
    def printEdgeType(self):
        """
        @brief  Display the edge type of the piece.
        """

        for direction in EdgeDirection:
            print(f'{direction.name}:', self.edge[direction.value].etype)


    #=============================== rotatePiece ===============================
    #
    def rotatePiece(self, theta):
        """
        @brief  Rotate the regular puzzle piece

        Args:
            theta: The rotation angle.

        Returns:
            theRegular: The rotated regular piece.
        """

        # @todo May need to change from redo everything to focus on transformation.
        thePiece = super().rotatePiece(theta)

        # Hacked to disable rotation operation
        thePiece.theta = 0
        theRegular = Regular(thePiece)

        return theRegular

    #========================== buildFromMaskAndImage ==========================
    #
    @staticmethod
    def buildFromMaskAndImage(theMask, theImage, cLoc, rLoc=None, pieceStatus=PieceStatus.MEASURED):
        '''!
        @brief  Given a mask (individual) and an image of same base dimensions, use to
                instantiate a puzzle piece template.

        @param[in]  theMask     Individual mask.
        @param[in]  theImage    Source image.
        @param[in]  rLoc        Puzzle piece (corner) location in the whole image.

        @param[in]  theRegular  Puzzle piece instance as a Regular piece.
        '''

        thePiece = Template.buildFromMaskAndImage(theMask, theImage, cLoc, rLoc=rLoc, \
                                                                     pieceStatus=pieceStatus)
        #DEBUG
        #print("MI -- Made Template just fine.")
        theRegular = Regular.upgradeTemplate(thePiece)
        #print("MI -- Upgrade to Regular just fine.")

        return theRegular


    #============================= upgradeTemplate =============================
    #
    @staticmethod
    def upgradeTemplate(thePiece):
        '''!
        @brief  Given a Template instance, transfer to a Regular instance.

        @param[in]  thePiece    Puzzle piece as a Template instance.
        @param[out]             Puzzle piece as a Regular instance.
        '''

        thePiece = Regular(thePiece.y, thePiece.rLoc, thePiece.id, 
                                                      thePiece.theta, thePiece.status)
        return thePiece

#
#============================== puzzle.piece.regular =============================

#
#================================ puzzle.piece code ==================================
