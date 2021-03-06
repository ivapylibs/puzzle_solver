# ================================ puzzle.piece.regular ================================
#
# @brief    Establish a regular puzzle piece (4 sides with locks)
#
# ================================ puzzle.piece.regular ================================
#
# @file     regular.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/17 [created]
#
#
# ================================ puzzle.piece.regular ================================

# ===== Environment / Dependencies
#

from enum import Enum

import numpy as np

from puzzle.piece.template import Template, PieceStatus
from puzzle.utils.sideExtractor import sideExtractor


# ===== Helper Elements
#
class EdgeType(Enum):
    """
    @brief EdgeType used to keep track of the type of edges
    """

    UNDEFINED = 0
    IN = 1
    OUT = 2
    FLAT = 3


# Todo: May need to upgrade to other forms when we have rotations
class EdgeDirection(Enum):
    """
    @brief EdgeDirection used to keep track of the direction of edges
    """

    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3


class EdgeDes:
    # Here we save the rotated edges
    type: int = EdgeType.UNDEFINED  # To save the type: in/out/flat.
    image: np.ndarray = np.array([])  # To save the whole image of the edge.
    mask: np.ndarray = np.array([])  # To save the mask image of the edge.

    colorFea: np.ndarray = np.array([])  # @< The processed color feature.
    shapeFea: np.ndarray = np.array([])  # @< The processed shape feature.


#
# ================================ puzzle.piece.regular ================================
#
class Regular(Template):

    def __init__(self, *argv):
        """
        @brief  Constructor for the regular puzzle piece.

        Args:
            *argv: Input params.
        """

        y = None
        r = (0, 0)
        id = None
        theta = None
        status = PieceStatus.UNKNOWN

        if len(argv) == 1:
            if isinstance(argv[0], Template):
                y = argv[0].y
                r = argv[0].rLoc
                id = argv[0].id
                theta = argv[0].theta
                status = argv[0].status
            else:
                y = argv[0]
        elif len(argv) == 2:
            y = argv[0]
            r = argv[1]
        elif len(argv) >= 3 and len(argv) <= 4:
            y = argv[0]
            r = argv[1]
            id = argv[2]
        elif len(argv) > 4:
            raise TypeError('Too many parameters!')

        super(Regular, self).__init__(y=y, r=r, id=id, theta=theta, pieceStatus=status)

        # Assume the order 0, 1, 2, 3 correspond to left, right, top, bottom
        self.edge = [EdgeDes() for i in range(4)]

        # Debug only
        self.class_image = None
        self.rectangle_pts = None
        self.filtered_harris_pts = None
        self.simple_harris_pts = None
        self.theta = None

        if theta == 0:
            self._process(enable_rotate=False)
        else:
            self._process()

    def setEdgeType(self, direction, type):
        """
        @brief  Set up the type of the chosen edge.

        Args:
            direction: The edge to be set up.
            type: The type.
        """

        self.edge[direction].type = type

    def displayEdgeType(self):
        """
        @brief  Display the edge type of the piece.
        """

        for direction in EdgeDirection:
            print(f'{direction.name}:', self.edge[direction.value].type)

    def _process(self, enable_rotate=True):
        """
        @brief Run the sideExtractor.
        """

        # d_thresh is related to the size of the puzzle piece
        out_dict = sideExtractor(self.y, scale_factor=1,
                                 harris_block_size=5, harris_ksize=5,
                                 corner_score_threshold=0.15, corner_minmax_threshold=100,
                                 shape_classification_nhs=3, d_thresh=(self.y.size[0] + self.y.size[1]) / 5,
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
            theRegular: The puzzle piece instance.
        """

        thePiece = Template.buildFromMaskAndImage(theMask, theImage, rLoc=rLoc, pieceStatus=pieceStatus)
        theRegular = Regular(thePiece)

        return theRegular
#
# ================================ puzzle.piece.regular ================================
