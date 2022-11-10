# ========================= puzzle.builder.gridded ========================
#
# @class    puzzle.builder.gridded
#
# @brief    This type of puzzle is simply a set of interlocking puzzle
#           pieces that get put together in a grid structure.
#
# This class is an organized version of the interlocking class. Since
# the interlocking pieces lie on a regular grid, we can establish a
# relative ordering. If needed, it can be used for evaluating or
# interpreting a puzzle board and its correctness. 
#
# It also includes a scoring mechanism to indicate how "close" a current
# solution would be to the calibrated solution.
#
# ========================= puzzle.builder.gridded ========================
#
# @file     gridded.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
#           Yiye Chen,              yychen2019@gatech.edu
# @date     2021/08/04 [created]
#           2021/08/05 [modified]
#           2022/07/15 [modified]
#
# ========================= puzzle.builder.gridded ========================

# ===== Environment / Dependencies
#

import pickle
import math
from copy import deepcopy
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import numpy as np
import scipy.cluster.hierarchy as hcluster
from sklearn.cluster import KMeans

from puzzle.builder.arrangement import Arrangement
from puzzle.builder.board import Board
from puzzle.builder.interlocking import Interlocking, ParamInter
from puzzle.utils.dataProcessing import updateLabel, partition_even


# ===== Helper Elements
#

@dataclass
class ParamGrid(ParamInter):
    tauGrid: float = float('inf')  # The threshold size of the puzzle piece.
    reorder: bool = False
    grid: tuple = (None, None)
    gcMethod: str = "rectangle"       # The method to obtain the grid coordinates. 
                                    # Choices: ["rectangle", "cluster"]


#
# ====================== puzzle.builder.interlocking ======================
#

class Gridded(Interlocking):
    def __init__(self, theBoard=[], theParams=ParamGrid):
        """
        @brief Constructor for the puzzle.builder.adjacent class.

        Args:
            theBoard: The input board instance.
            theParams: The params.
        """

        super(Gridded, self).__init__(theBoard, theParams)

        if isinstance(theBoard, Board):
            # Store the calibrated grid location of the puzzle piece.
            # e.g., [x; y]
            # We do not have to worry about the index or id here since they are the same in the solution board.
            self.gc = np.zeros((2, theBoard.size()))
        else:
            raise TypeError('Not initialized properly')

        self.__processGrid(theParams.reorder, theParams.tauGrid, theParams.grid, verbose=False)

    def __processGrid(self, reorder=False, piece_thresh=float('inf'), kmeans_cluster=(None, None), verbose=False):
        """
        @brief  Process the solution board and determine what pieces are
                interlocking and the grid ordering. Grid ordering helps to
                determine adjacency.

        Note that if the pieces are close to each other, this function may fail when the location of a piece is not computed properly.

        Args:
            reorder: The flag signaling whether to reorder the piece id according to the location.
            piece_thresh: The threshold for both x,y.
            kmeans_cluster: The desired grid numbers for the puzzle.
        """

        pLoc = self.pieceLocations()

        x_list = np.array([rLoc[0] for _, rLoc in pLoc.items()]).reshape(-1, 1)
        y_list = np.array([rLoc[1] for _, rLoc in pLoc.items()]).reshape(-1, 1)


        # get the x, y labels
        if self.params.gcMethod == "cluster":
            x_labels, y_labels = self.__processGrid_cluster(x_list, y_list, kmeans_cluster, piece_thresh)
        elif self.params.gcMethod == "rectangle":
            x_labels, y_labels = self.__processGrid_rectangle(x_list, y_list)

        # For debug. Plot the coordinates 
        if verbose:
            colors_x_all = cm.rainbow(np.linspace(0, 1, x_labels.max() + 1)) 
            colors_y_all = cm.rainbow(np.linspace(0, 1, y_labels.max() + 1)) 
            fh, (ax1, ax2, ax3) = plt.subplots(1, 3)
            ax1.scatter(x_list, y_list)
            ax1.set_title("The piece coordinates")
            colors_x = np.array([colors_x_all[l, :] for l in x_labels])
            ax2.scatter(x_list, y_list, color=colors_x)
            ax2.set_title("The gc x coordinate assignment")
            colors_y = np.array([colors_y_all[l] for l in y_labels])
            ax3.scatter(x_list, y_list, color=colors_y)
            ax3.set_title("The gc y coordinate assignment")
            plt.show()

        # Reorder the pieces, so the id will correspond to the grid location
        if reorder:
            pieces_src = deepcopy(self.pieces)
            pieceKeysList = list(self.pieces.keys())

            num = 0

            # Save the changes, {new:old}
            dict_conversion = {}

            for jj in range(max(y_labels) + 1):
                for ii in range(max(x_labels) + 1):
                    for idx, pts in enumerate(zip(x_labels, y_labels)):
                        if pts[0] == ii and pts[1] == jj:
                            self.pieces[num] = pieces_src[pieceKeysList[idx]]
                            dict_conversion[num] = pieceKeysList[idx]
                            self.pieces[num].id = num
                            self.gc[:, num] = ii, jj
                            num = num + 1
                            break

            # Have to re-compute adjMat/ilMat
            adjMat_src = deepcopy(self.adjMat)
            for ii in range(self.size()):
                for jj in range(ii + 1, self.size()):
                    self.adjMat[ii, jj] = adjMat_src[dict_conversion[ii], dict_conversion[jj]]
                    self.adjMat[jj, ii] = self.adjMat[ii, jj]

            self.ilMat = self.adjMat

        else:
            for ii in range(self.size()):
                # The order is in line with the one saving in self.pieces

                # Todo: Eventually, this has to be upgraded to a dict?
                self.gc[:, ii] = x_labels[ii], y_labels[ii]
            

    def __processGrid_cluster(self, x_list, y_list, kmeans_cluster=(None, None), piece_thresh=float('inf')):
        # @note
        # Check the puzzle shape size to determine the thresh here.
        # It is based on the assumption that all the puzzle pieces are of similar sizes.

        if kmeans_cluster[0] is None:
            x_thresh = np.mean([self.pieces[key].y.size[0] for key in self.pieces]) / 3
            x_thresh = min(x_thresh, piece_thresh)
            x_label = hcluster.fclusterdata(x_list, x_thresh, criterion="distance")  # from 1
            x_labels = updateLabel(x_list, x_label)  # from 0
        else:
            x_kmeans = KMeans(n_clusters=kmeans_cluster[0], random_state=0).fit(x_list)
            x_labels = x_kmeans.labels_

        if kmeans_cluster[1] is None:
            y_thresh = np.mean([self.pieces[key].y.size[1] for key in self.pieces]) / 3
            y_thresh = min(y_thresh, piece_thresh)
            y_label = hcluster.fclusterdata(y_list, y_thresh, criterion="distance")
            y_labels = updateLabel(y_list, y_label)  # from 0
        else:
            y_kmeans = KMeans(n_clusters=3, random_state=0).fit(y_list)
            y_labels = y_kmeans.labels_


        return np.array(x_labels), np.array(y_labels)
    
    def __processGrid_rectangle(self, x_list, y_list):
        """Generate the grid based on the assumption that the grid is a rectangle.
        The method is to check all the two number combinations that multiply to the piece number
        The two number will be treated as the maximum grid coordinate along x and y directions.
        For number, assign the x_list and y_list evenly, and finally choose the one with the least mean square error.

        NOTE: In my(Yiye) tests the assumption holds. And the cluster-based method is prone to error.

        Args:
            x_list ((N, 1)):    The x coordinates
            y_list ((N, 1)):    The y coordinates

        Returns:
            x_labels ((N, 1)):          The x-direction grid coordinates
            y_labels ((N, 1)):          The y-direction grid coordinates
        """
        N_piece = x_list.shape[0]

        # the result cache
        x_labels = None
        y_labels = None
        error_min = float('inf')

        # go through all possible combinations
        for i in range(math.ceil(N_piece**0.5) + 1):
            if (i == 0) or (N_piece % i != 0):
                continue
            factor1 = i
            factor2 = int(N_piece / i)

            for x_num, y_num in zip((factor1, factor2), (factor2, factor1)):
                x_labels_this, x_parts = partition_even(x_list, partition_num=x_num, order="ascend")    
                y_labels_this, y_parts = partition_even(y_list, partition_num=y_num, order="ascend")

                # get the error. x_parts and y_parts are (x/y_num, data_num)
                x_avgs = np.mean(x_parts, axis=1, keepdims=True)
                y_avgs = np.mean(y_parts, axis=1, keepdims=True)
                x_errors = x_parts - x_avgs
                y_errors = y_parts - y_avgs
                error_this = (np.mean(np.abs(x_errors)) + np.mean(np.abs(y_errors))) / 2.

                # print("The x_num: {}, y_num: {}".format(x_num, y_num))
                # print("The error: {} \n".format(error_this))

                # update the result if small error
                if error_this < error_min:
                    x_labels = x_labels_this.copy()
                    y_labels = y_labels_this.copy()
                    error_min = error_this

        return x_labels, y_labels
        

    # OTHER CODE / MEMBER FUNCTIONS

    def assert_gc(self, verbose=False):
        """Assert the assigned grid coordinates are correct.
        The criteria:
            1. The distinct coordinate number is equal to the solution board piece number
            2. The max grid coordinate number is equal to the solution board piece number

        Return:
            flag (bool):        True if the grid cooridnates are correct, else False
        """
        flag = True

        # 1. Check the unique of the gc
        gc_unique = np.unique(self.gc, axis=1)
        num_unique = gc_unique.shape[1]
        if num_unique != self.size():
            flag = False
            if verbose:
                Warning("Grid coordinate is wrong. The assigned number does not equal to the piece number")
        # 2. check the max grid coordinate number.
        elif (np.max(self.gc[0, :])+1) * (np.max(self.gc[1,:]) + 1)  != self.size():
            flag = False
            if verbose:
                Warning(
                    "The max grid coordinate number does not equal to the piece number."
                    "Either the grid coordinate is wrong, or the solution board does not form a square."
                )
        else:
            if verbose:
                print("Grid coordinate assignment passes the check.") 
            
        return flag

    def swapPuzzle(self, num=100):
        """
        @brief  Randomly swap rLoc of two puzzle pieces for num times.

        Args:
            num:  The number of times to swap.

        Returns:
            epImage: Generated puzzle image.
            epBoard: Generated puzzle board.
            change_dict: The ground truth change dict (Old -> New).
        """

        # Note: We do not care about id in this function.
        epBoard = deepcopy(self)

        pieceKeysList = list(epBoard.pieces.keys())

        # Initialize a change dict
        # Old -> New
        change_dict = {}
        for key in pieceKeysList:
            change_dict[key]=key

        for i in range(num):
            target_list = np.random.randint(0, epBoard.size(), 2)

            # Exchange values
            change_dict[target_list[0]],change_dict[target_list[1]] = change_dict[target_list[1]],change_dict[target_list[0]]

            # Exchange rLoc
            epBoard.pieces[pieceKeysList[target_list[0]]].rLoc, epBoard.pieces[pieceKeysList[target_list[1]]].rLoc = \
                epBoard.pieces[pieceKeysList[target_list[1]]].rLoc, epBoard.pieces[pieceKeysList[target_list[0]]].rLoc

        epImage = epBoard.toImage(CONTOUR_DISPLAY=False)

        # Invert mapping
        # New -> old(solution board order)
        change_dict = {v: k for k, v in change_dict.items()}
        return epImage, epBoard, change_dict

    def explodedPuzzle(self, dx=100, dy=50, bgColor=(0, 0, 0)):
        """
        @brief  Create an exploded version of the puzzle. It is an image
        with no touching pieces.

        The value for an exploded puzzle image is that it can be used to
        generate a simulated puzzle scenario that can be passed to a puzzle
        solver. It can also be used to define a quasi-puzzle problem, where
        the objective is to place the pieces in grid ordering like the
        exploded view (without needing to interlock). Doing see keeps puzzle
        piece well separated for simple puzzle interpretation algorithms to
        rapidly parse.

        Args:
            dx: The horizontal offset when exploding.
            dy: The vertical offset when exploding.
            bgColor: The background color to use.
            Exploded puzzle image & Exploded puzzle board.

        Returns:
            epImage: The image of the exploded puzzle pieces.
            epBoard: The board instance of the exploded puzzle pieces.
        """

        # --[1] First figure out how big the exploded image should be based
        #      on the puzzle image dimensions, the number of puzzle pieces
        #      across rows and columns, and the chosen spacing.
        [nc, nr] = self.extents()
        bbox = self.boundingBox()
        r_origin = bbox[0]

        # The max index of pieces for x,y
        x_max = np.max(self.gc[0, :])
        y_max = np.max(self.gc[1, :])

        nr = int(nr + y_max * dy)
        nc = int(nc + x_max * dx)

        epImage = np.zeros((nr, nc, 3), dtype='uint8')
        epImage[:, :, :] = bgColor

        # --[2] Place image data into the exploded puzzle image.
        #

        # Work on the epBoard
        epBoard = deepcopy(self)
        for idx, key in enumerate(epBoard.pieces):
            piece = epBoard.pieces[key]
            r_new = -r_origin + piece.rLoc + np.array([dx, dy]) * self.gc[:, idx].flatten()
            r_new = r_new.astype('int')
            piece.placeInImageAt(epImage, rc=r_new)
            # epBoard.pieces[idx].setPlacement(r_new)
            piece.setPlacement(r_new)
        # epImage = epBoard.toImage(CONTOUR_DISPLAY=False)

        """
        Todo: Currently, it is just explode but without changing the order.
        Otherwise, gc has to be updated too.
        """

        return epImage, epBoard
    
    def getGc(self):
        """
        Obtained the solution board pieces' grid coordinates

        Returns:
            gc (2, N_pieces):       The grid coordinates assigned to each pieces
        """
        return self.gc

    @staticmethod
    def buildFromFile_Puzzle(fileName, theParams=None):
        """
        @brief Load a saved arrangement calibration/solution puzzle board.

        Args:
            fileName: The python file to load.
            theParams: The params.

        Returns:
            thePuzzle: The gridded puzzle board instance.
        """

        aPuzzle = Arrangement.buildFromFile_Puzzle(fileName, theParams)

        with open(fileName, 'rb') as fp:
            data = pickle.load(fp)

        if theParams is None and hasattr(data, 'tauGrid'):
            theParams = ParamGrid(data.tauGrid)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = Gridded(aPuzzle, theParams)
        else:
            thePuzzle = Gridded(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFromFile_ImageAndMask(fileName, theParams=None):
        """
        @brief Load a saved arrangement calibration/solution stored as an image and a mask.

        The python file contains the puzzle board mask and image source
        data. It gets processed into an arrangement instance. If a threshold
        variable ``tauDist`` is found, then it is applied to the arrangement
        instance.

        Args:
            fileName: The python file to load.
            theParams: The params.

        Returns:
            thePuzzle: The gridded puzzle board instance.
        """

        aPuzzle = Arrangement.buildFromFile_ImageAndMask(fileName, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = Gridded(aPuzzle, theParams)
        else:
            thePuzzle = Gridded(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFromFiles_ImageAndMask(imFile, maskFile, theParams=None):
        """
        @brief Load a saved arrangement calibration/solution stored as
               separate image and mask files.

        The source file contain the puzzle board image and mask data. It
        gets processed into an arrangement instance. If a threshold variable
        ``tauDist`` is found, then it is applied to the arrangement instance.

        Args:
            imFile: The image file to load.
            maskFile: The mask file to load.
            theParams: The params.

        Returns:
            thePuzzle: The gridded puzzle board instance.
        """

        aPuzzle = Arrangement.buildFromFiles_ImageAndMask(imFile, maskFile, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = Gridded(aPuzzle, theParams)
        else:
            thePuzzle = Gridded(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFrom_ImageAndMask(theImage, theMask, theParams=None):
        """
        @brief Given an image and an image mask, parse both to recover
               the puzzle calibration/solution.

        Instantiates a puzzle parser that gets applied to the submitted data
        to create a puzzle board instance. That instance is the calibration/solution.

        Args:
            theImage: The puzzle image data.
            theMask: The puzzle mask data.
            theParams: The params.

        Returns:
            thePuzzle: The gridded puzzle board instance.
        """

        aPuzzle = Arrangement.buildFrom_ImageAndMask(theImage, theMask, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = Gridded(aPuzzle, theParams)
        else:
            thePuzzle = Gridded(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFrom_ImageProcessing(theImage, theProcessor=None, theDetector=None, theParams=None):
        """
        @brief Given an image with regions clearly separated by some
               color or threshold, parse it to recover the puzzle
               calibration/solution. Can source alternative detector.

        Instantiates a puzzle parser that gets applied to the submitted data
        to create a puzzle board instance. That instance is the calibration/solution.

        Args:
            theImage: The puzzle image data.
            theProcessor: The processing scheme.
            theDetector: The detector scheme.
            theParams: The params.

        Returns:
            thePuzzle: The gridded puzzle board instance.
        """

        aPuzzle = Arrangement.buildFrom_ImageProcessing(theImage, theProcessor, theDetector, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = Gridded(aPuzzle, theParams)
        else:
            thePuzzle = Gridded(aPuzzle)

        return thePuzzle

    @staticmethod
    def buildFrom_Sketch(theImage, theMask, theProcessor=None, theDetector=None, theParams=None):
        """
        @brief Given an image with regions clearly separated by some
               color or threshold, parse it to recover the puzzle
               calibration/solution. Can source alternative detector.

        Instantiates a puzzle parser that gets applied to the submitted data
        to create a puzzle board instance. That instance is the calibration/solution.

        Args:
            theImage: The puzzle image data.
            theMask: The puzzle mask data.
            theProcessor: The processing scheme.
            theDetector: The detector scheme.
            theParams: The params.

        Returns:
            thePuzzle: The gridded puzzle board instance.
        """

        aPuzzle = Arrangement.buildFrom_Sketch(theImage, theMask, theProcessor, theDetector, theParams)

        if hasattr(theParams, 'tauGrid'):
            thePuzzle = Gridded(aPuzzle, theParams)
        else:
            thePuzzle = Gridded(aPuzzle)

        return thePuzzle

#
# ========================= puzzle.builder.gridded ========================
