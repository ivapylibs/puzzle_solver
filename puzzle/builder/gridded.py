#=========================== puzzle.builder.gridded ==========================
##
# @package  puzzle.builder.gridded
# @brief    An interlocking puzzle for which the pieces are arranged in a nice
#           gridded manner with a rectangular shape when complete.
#
# @ingroup  Puzzle_Types
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2022/07/15 [modified]
# @date     2021/08/05 [modified]
# @date     2021/08/04 [created]
#

#=========================== puzzle.builder.gridded ==========================
#
# NOTE
#   85 columns, 2 spaces indent.
#
#=========================== puzzle.builder.gridded ==========================

#===== Environment / Dependencies =====
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
from puzzle.board import Board
from puzzle.builder.interlocking import Interlocking, CfgInterlocking
from puzzle.utils.dataProcessing import updateLabel, partition_even


#
#-----------------------------------------------------------------------------
#======================== Configuration Node : Gridded =======================
#-----------------------------------------------------------------------------
#

class CfgGridded(CfgInterlocking):
  '''!
  @ingroup  Puzzle_Types
  @brief  Configuration setting specifier for gridded puzzle.

  '''

  #=============================== __init__ ==============================
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief        Constructor of configuration instance.
  
    @param[in]    cfg_files   List of config files to load to merge settings.
    '''
    if (init_dict == None):
      init_dict = CfgGridded.get_default_settings()

    super().__init__(init_dict, key_list, new_allowed)

  #========================= get_default_settings ========================
  #
  # @brief    Recover the default settings in a dictionary.
  #
  @staticmethod
  def get_default_settings():
    '''!
    @brief  Defines most basic, default settings for RealSense D435.

    @param[out] default_dict  Dictionary populated with minimal set of
                              default settings.
    '''
    default_dict = super(CfgGridded,CfgGridded).get_default_settings()
    default_dict.update(dict(tauGrid = float('inf'),    # Threshold on size of puzzle piece.
                        reorder = False,                # Reorder pieces based on grid.
                        grid = (None, None) ),          # Not sure. kmeans?
                        gridding = 'rectangular'        # Default grid estimation method.
                        )

    return default_dict

#
#-----------------------------------------------------------------------------
#=========================== puzzle.builder.Gridded ==========================
#-----------------------------------------------------------------------------
#

class Gridded(Interlocking):
  '''!
  @ingroup  Puzzle_Types
  @brief    Puzzle type that is a set of interlocking puzzle pieces that get put
            together in a grid structure.  All rows/columns have same number of pieces.

  This class is an organized version of the interlocking class. Since the interlocking
  pieces lie on a regular grid, we can establish a relative ordering. If needed, it can
  be used for evaluating or interpreting a puzzle board and its correctness. 
  
  It also includes a scoring mechanism to indicate how "close" a current
  solution would be to the calibrated solution.
  '''

  #=========================== __init__ Gridded ==========================
  def __init__(self, theBoard=[], theParams=CfgGridded):
    '''!
    @brief Constructor for the puzzle.builder.adjacent class.

    @param[in]  theBoard    Input board instance.
    @param[in]  theParams   Gridded puzzle configuration instance.
    '''

    super(Gridded, self).__init__(theBoard, theParams)

    if isinstance(theBoard, Board):
      # Store the calibrated grid location of the puzzle piece, e.g., [x; y]
      # We do not have to worry about the index or id here since they are the same in
      # the solution board.
      self.gc = np.zeros((2, theBoard.size()))      # @< Puzzle piece grid locations.
      self.pshape = []                              # @< Puzzle grid dims (width x height)
    else:
      raise TypeError('Not initialized properly')

    # @todo Need to figure out what this does.  PAV 10/05/2024.
    # @note Creates the puzzle grid ordering.
    self.__processGrid(verbose = False)


  #============================= _processGrid ============================
  #
  def __processGrid(self, verbose=False):
    '''!
    @brief  Process the solution board and determine what pieces interlock with
            which others and the grid ordering. Grid ordering helps to determine
            adjacency.

    Since the puzzle pieces are marked by their top-left corner coordinate, it should
    be possible to discern the puzzle piece gridding by enumerating through this
    listing in the right way. In particular, the top row will have consistent
    y-coordinate locations.  The left column with also have consistent x-coordinate
    locations.  Between these, it should be possible to split all the other pieces up.
    A good start is to use the top row pieces to establish an x-ordering, and the left
    column pieces to establish a y-ordering.  Then pieces closest to one of the (x,y)
    grid approximations should give the right answer.
    '''

    pLoc = self.pieceLocations()

    if self.params.gridding == 'rectangular':
      # Code below works for a rectangular gridding of the puzzle based on assumption
      # in the documentation above.
      x_list = np.array([rLoc[0] for _, rLoc in pLoc.items()]).reshape(-1, 1)
      y_list = np.array([rLoc[1] for _, rLoc in pLoc.items()]).reshape(-1, 1)

      #DEBUG
      #print(x_list)
      #print(y_list)

      # Use rectangular shape assumptions to get no. of rows and columns.
      # Store in pshape.
      xMin = np.min(x_list)
      yMin = np.min(y_list)
      self.pshape = [ np.count_nonzero(y_list == yMin) , np.count_nonzero(x_list == xMin) ]

      #DEBUG
      #print(self.pshape)

      # Use known row and column quantities to get the x, y labels of the puzzle
      # pieces by partitioning in vertical and horizontal so that each partition
      # has the same number of elements in it.  That gets the answer.
      x_labels, x_parts = partition_even(x_list, partition_num=self.pshape[0], order="ascend")
      y_labels, y_parts = partition_even(y_list, partition_num=self.pshape[1], order="ascend")

    elif self.params.gridding == 'arrangedbox':

      x_list = np.array([rLoc[0] for _, rLoc in pLoc.items()]).reshape(-1, 1)
      y_list = np.array([rLoc[1] for _, rLoc in pLoc.items()]).reshape(-1, 1)

      x_labels, y_labels = self.__processGrid_rectangular(x_list, y_list)

    else:
      # The puzzle need not be rectangular.  That would be problematic.
      # Uncomment if statement when ready.  Push other options to else.
      # They won't be developed at this moment.
      warning("This code not developed.  Will fail downstream.")

    # If verbose, plot the coordinates and provide visuals that show correct processing.
    # Here there are three scatter plots.  One is of the puzzle piece corner
    # coordinates. The other two are of the puzzle piece x-ordering and then the
    # y-ordering.  The marker hues should change in x and in y, respectively.
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
    if self.params.reorder:
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
        self.gc[:, ii] = x_labels[ii], y_labels[ii]
        # TODO  Eventually, this has to be upgraded to a dict? 
        # TODO  Does it? Why? - PAV - 10/06/2024.



  #======================== __processGrid_cluster ========================
  #
  def __processGrid_cluster(self, x_list, y_list, kmeans_cluster=(None, None),
    tauPiece=float('inf')):
    '''!
    @brief  Unsure what is going on here.

    @param[in]  x_list          
    @param[in]  y_list          
    @param[in]  kmeans_cluster  Unsure.
    @param[in]  tauPiece        Threshold for both x,y.
    '''
    # @note
    # Check the puzzle shape size to determine the thresh here.
    # It is based on the assumption that all the puzzle pieces are of similar sizes.

    if kmeans_cluster[0] is None:
      x_thresh = np.mean([self.pieces[key].y.size[0] for key in self.pieces]) / 3
      x_thresh = min(x_thresh, tauPiece)
      x_label = hcluster.fclusterdata(x_list, x_thresh, criterion="distance")  # from 1
      x_labels = updateLabel(x_list, x_label)  # from 0
    else:
      x_kmeans = KMeans(n_clusters=kmeans_cluster[0], random_state=0).fit(x_list)
      x_labels = x_kmeans.labels_

    if kmeans_cluster[1] is None:
      y_thresh = np.mean([self.pieces[key].y.size[1] for key in self.pieces]) / 3
      y_thresh = min(y_thresh, tauPiece)
      y_label = hcluster.fclusterdata(y_list, y_thresh, criterion="distance")
      y_labels = updateLabel(y_list, y_label)  # from 0
    else:
      y_kmeans = KMeans(n_clusters=3, random_state=0).fit(y_list)
      y_labels = y_kmeans.labels_


    return np.array(x_labels), np.array(y_labels)
    
  #======================== __processGrid_rectangular ========================
  #
  def __processGrid_rectangular(self, x_list, y_list):
    '''!
    @brief  Generate grid based on assumption that grid is rectangular.
            The method is to check all the two number combinations that multiply to the
            piece number.
            The two number will be treated as the maximum grid coordinate along x and y
            directions.  For number, assign the x_list and y_list evenly, and finally
            choose the one with the least mean square error.

    NOTE: In my(Yiye) tests the assumption holds. And the cluster-based method is prone
          to error.

    @param[in] x_list   The x coordinates ((N, 1))
    @param[in] y_list   The y coordinates ((N, 1))

    @params[out] x_labels   Grid coordinates in x-direction ((N, 1))
    @params[out] y_labels   Grid coordinates in y-direction ((N, 1))
    '''
    print("Processing rectangular.")
    print(x_list)
    print(y_list)
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
        

  #============================= assert_gc =============================
  #
  def assert_gc(self, verbose=False):
    '''!
    @brief    Assert the assigned grid coordinates are correct.

    Criteria for correctness of the gridding:
      1. The distinct coordinate number is equal to the solution board piece number
      2. The max grid coordinate number is equal to the solution board piece number

    @return   flag (bool) True if grid cooridnates are correct, else False.
    '''
    flag = True       #! Set flag to true, returns false when testing fails.

    # 1. Check the unique of the gc
    gc_unique = np.unique(self.gc, axis=1)
    num_unique = gc_unique.shape[1]

    if num_unique != self.size():
      flag = False
      if verbose:
        Warning("Grid coordinate is wrong. The assigned number does not equal to" +
                "the piece number")

    # 2. check the max grid coordinate number.
    elif (np.max(self.gc[0, :])+1) * (np.max(self.gc[1,:]) + 1)  != self.size():
      flag = False
      if verbose:
        Warning(\
          "The max grid coordinate number does not equal to the piece number." \
          "Either grid coordinates are wrong, or solution board does not form a square.")
    elif verbose:
        print("Grid coordinate assignment passes the check.") 
          
    return flag

  #============================== swapPuzzle =============================
  def swapPuzzle(self, num=100):
    '''!
    @brief  Randomly swap rLoc of two puzzle pieces for num times.

    @param[in] num  The number of times to swap.

    @param[out] epImage     Generated puzzle image.
    @param[out] epBoard     Generated puzzle board.
    @param[out] change_map  Ground truth change dict mapping (Old -> New).
    '''

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
    epBoard.pieces[pieceKeysList[target_list[0]]].rLoc, \
    epBoard.pieces[pieceKeysList[target_list[1]]].rLoc =  \
                    epBoard.pieces[pieceKeysList[target_list[1]]].rLoc, \
                    epBoard.pieces[pieceKeysList[target_list[0]]].rLoc

    epImage = epBoard.toImage(CONTOUR_DISPLAY=False)

    # Invert mapping
    # New -> old(solution board order)
    change_dict = {v: k for k, v in change_dict.items()}
    return epImage, epBoard, change_dict

  #============================ explodedPuzzle ===========================
  #
  def explodedPuzzle(self, dx=100, dy=50, bgColor=(0, 0, 0)):
    '''!
    @brief  Create an exploded version of the puzzle. It is an image with no touching
            pieces.

    The value for an exploded puzzle image is that it can be used to generate a
    simulated puzzle scenario that can be passed to a puzzle solver. It can also be
    used to define a quasi-puzzle problem, where the objective is to place the pieces
    in grid ordering like the exploded view (without needing to interlock). Doing see
    keeps puzzle piece well separated for simple puzzle interpretation algorithms to
    rapidly parse.

    Currently, it is just explode but without changing the order.  Otherwise, gc has to
    be updated too.  Both the exploded puzzle image & the exploded puzzle board.

    @param[in]  dx          Horizontal offset when exploding.
    @param[in]  dy          Vertical offset when exploding.
    @param[in]  bgColor     Background color to use in new regions.

    @param[out] epImage     Image of exploded puzzle.
    @param[out] epBoard     Board instance with exploded puzzle pieces.
    '''

    #--[1] First figure out how big the exploded image should be based
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

    #--[2] Place image data into the exploded puzzle image.
    #

    # Work on the epBoard
    epBoard = deepcopy(self)
    for idx, key in enumerate(epBoard.pieces):
      piece = epBoard.pieces[key]
      r_new = -r_origin + piece.rLoc + np.array([dx, dy]) * self.gc[:, idx].flatten()
      r_new = r_new.astype('int')

      piece.placeInImageAt(epImage, rc=r_new)
      piece.setPlacement(r_new)

    # @todo Doesn't seem to have copied the piece IDs.  Need to double check that.

    return epImage, epBoard
    
  #=============================== getGc ===============================
  #
  def getGc(self):
    '''!
    @brief    Obtain the solution board pieces' grid coordinates

    @param[out]   gc  Grid coordinates assigned to each pieces, (2, N_pieces).
    '''

    return self.gc

  #======================== buildFromFile_Puzzle =======================
  #
  @staticmethod
  def buildFromFile_Puzzle(fileName, theParams=None):
    '''!
    @brief Load a saved arrangement calibration/solution puzzle board.

    @param[in]    fileName    Python file to load.
    @param[in]    theParams   Gridded configuration instance.

    @return   thePuzzle   Gridded puzzle board instance.
    '''

    aPuzzle = Arrangement.buildFromFile_Puzzle(fileName, theParams)

    with open(fileName, 'rb') as fp:
      data = pickle.load(fp)

    if theParams is None and hasattr(data, 'tauGrid'):  # DELETE WHEN CODE FIXED.
      theParams = CfgGridded()                        # BAD SAVE/LOAD PROCESS.
      theParams.tauGrid = data.tauGrid

    thePuzzle = Gridded(aPuzzle, theParams)
    #TODO: WHAT IS THIS? DELETE IF ABOVE WORKS.
    #if hasattr(theParams, 'tauGrid'):
    #    thePuzzle = Gridded(aPuzzle, theParams)
    #else:
    #    thePuzzle = Gridded(aPuzzle)

    return thePuzzle

  #===================== buildFromFile_ImageAndMask ====================
  #
  @staticmethod
  def buildFromFile_ImageAndMask(fileName, theParams=None):
    '''!
    @brief Load a saved arrangement calibration/solution stored as an image and a mask.

    The python file contains the puzzle board mask and image source data. It gets
    processed into an arrangement instance. If a threshold variable ``tauDist`` is
    found, then it is applied to the arrangement instance.

    @param[in]    fileName    Python file to load.
    @param[in]    theParams   Gridded configuration instance.

    @return   thePuzzle   Gridded puzzle board instance.
    '''
    aPuzzle = Arrangement.buildFromFile_ImageAndMask(fileName, theParams)

    if hasattr(theParams, 'tauGrid'):
      thePuzzle = Gridded(aPuzzle, theParams)
    else:
      thePuzzle = Gridded(aPuzzle)

    return thePuzzle

  #==================== buildFromFiles_ImageAndMask ====================
  #
  @staticmethod
  def buildFromFiles_ImageAndMask(imFile, maskFile, theParams=None):
    '''!
    @brief Load a saved arrangement calibration/solution stored as
           separate image and mask files.

    The source file contain the puzzle board image and mask data. It gets processed
    into an arrangement instance. If a threshold variable ``tauDist`` is found, then
    it is applied to the arrangement instance.

    @param[in]    imFile      Image file to load.
    @param[in]    maskFile    Mask file to load.
    @param[in]    theParams   Gridded configuration instance.

    @return   thePuzzle   Gridded puzzle board instance.
    '''

    aPuzzle = Arrangement.buildFromFiles_ImageAndMask(imFile, maskFile, theParams)

    if hasattr(theParams, 'tauGrid'):
      thePuzzle = Gridded(aPuzzle, theParams)
    else:
      thePuzzle = Gridded(aPuzzle)

    return thePuzzle

  #======================= buildFrom_ImageAndMask ======================
  #
  @staticmethod
  def buildFrom_ImageAndMask(theImage, theMask, theParams=CfgGridded()):
    '''!
    @brief Given an image and an image mask, parse both to recover the puzzle
           calibration/solution.

    Instantiates a puzzle parser that gets applied to the submitted data to create a
    puzzle board instance. That instance is the calibration/solution.

    @param[in]    theImage    Puzzle image data.
    @param[in]    theMask     Puzzle mask data.
    @param[in]    theParams   Gridded configuration instance.

    @return   thePuzzle   Gridded puzzle board instance.
    '''

    aPuzzle   = Arrangement.buildFrom_ImageAndMask(theImage, theMask, theParams)

    aPuzzle.display_mp()
    plt.show()

    thePuzzle = Gridded(aPuzzle, theParams)

    return thePuzzle

  #====================== buildFrom_ImageProcessing ======================
  #
  @staticmethod
  def buildFrom_ImageProcessing(theImage, theProcessor=None, theDetector=None, 
                                                                        theParams=None):
    '''
    @brief  Given an image with regions clearly separated by some color or threshold,
            parse it to recover the puzzle calibration/solution. Can source alternative
            detector.

    Instantiates a puzzle parser that gets applied to the submitted data to create a
    puzzle board instance. That instance is the calibration/solution.

    @param[in]  theImage: The puzzle image data.
    @param[in]  theProcessor: The processing scheme.
    @param[in]  theDetector: The detector scheme.
    @param[in]  theParams   Gridded configuration instance.

    @return   thePuzzle   Gridded puzzle board instance.
    '''

    aPuzzle = Arrangement.buildFrom_ImageProcessing(theImage, theProcessor, 
                                                              theDetector , theParams)

    if hasattr(theParams, 'tauGrid'):
      thePuzzle = Gridded(aPuzzle, theParams)
    else:
      thePuzzle = Gridded(aPuzzle)

    return thePuzzle

  #=========================== buildFrom_Sketch ==========================
  #
  @staticmethod
  def buildFrom_Sketch(theImage, theMask, theProcessor=None, theDetector=None, theParams=None):
    '''
    @brief  Given an image with regions clearly separated by some color or threshold,
            parse it to recover the puzzle calibration/solution. Can source alternative
            detector.

    Instantiates a puzzle parser that gets applied to the submitted data to create a
    puzzle board instance. That instance is the calibration/solution.

    @param[in]  theImage:       Puzzle image data.
    @param[in]  theMask:        Puzzle mask data.
    @param[in]  theProcessor    Processing scheme.
    @param[in]  theDetector     Detector scheme.
    @param[in]  theParams       Gridded configuration instance.

    @return     thePuzzle   Gridded puzzle board instance.
    '''
    aPuzzle = Arrangement.buildFrom_Sketch(theImage, theMask, theProcessor, theDetector, theParams)

    if hasattr(theParams, 'tauGrid'):
      thePuzzle = Gridded(aPuzzle, theParams)
    else:
      thePuzzle = Gridded(aPuzzle)

    return thePuzzle

#
#=========================== puzzle.builder.gridded ==========================
