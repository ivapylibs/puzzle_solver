#=========================== puzzle.builder.matrix ===========================
##
# @package  puzzle.builder.matrix
# @brief    An adjacent puzzle for which the pieces are rectangular or square
#           so as to arranged neatly into rows and columns. 
#
# @ingroup  Puzzle_Types
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#
# @date     2024/01/11 [modified]
#

#=========================== puzzle.builder.matrix ===========================
#
# NOTE
#   85 columns, 2 spaces indent.
#
#=========================== puzzle.builder.matrix ===========================

#===== Environment / Dependencies =====
#
import pickle
import math
import random

from copy import deepcopy
from dataclasses import dataclass

import numpy as np
import scipy.cluster.hierarchy as hcluster
from   sklearn.cluster import KMeans

import cv2
import ivapy.display_cv as display

from puzzle.builder.arrangement import Arrangement
from puzzle.board import Board
from puzzle.builder.adjacent import Adjacent, CfgAdjacent
from puzzle.utils.dataProcessing import updateLabel, partition_even

import matplotlib.pyplot as plt
import matplotlib.cm as cm

#
#-----------------------------------------------------------------------------
#======================== Configuration Node : Matrix ========================
#-----------------------------------------------------------------------------
#

class CfgMatrix(CfgAdjacent):
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
      init_dict = CfgMatrix.get_default_settings()

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
    default_dict = super(CfgMatrix,CfgMatrix).get_default_settings()
    default_dict.update(dict(tauGrid = float('inf'),    # Threshold on size of puzzle piece.
                        reorder = False,                # Reorder pieces based on grid.
                        psize = [None, None],           # Puzzle matrix size (width, height).
                        isize = [None, None],           # Puzzle image size  (width, height).
                        minArea = 0 )
                        )

    return default_dict

#
#-----------------------------------------------------------------------------
#=========================== puzzle.builder.Matrix ===========================
#-----------------------------------------------------------------------------
#

class Matrix(Adjacent):
  '''!
  @ingroup  Puzzle_Types
  @brief    Puzzle type that is a set of adjacent, rectangular puzzle pieces 
            that get put together in a matrix/2D array shape.  All rows/columns have
            same number of pieces.

  This class is an organized version of the Adjacent class. Since the adjacent
  pieces lie on a regular grid, we can establish a relative ordering. If needed, 
  it can be used for evaluating or interpreting a puzzle board and its correctness. 
  
  It also includes a scoring mechanism to indicate how "close" a current
  solution would be to the calibrated solution.
  '''

  #=========================== __init__ Matrix ===========================
  def __init__(self, theBoard=[], theParams=CfgMatrix):
    '''!
    @brief Constructor for the puzzle.builder.adjacent class.

    @param[in]  theBoard    Input board instance.
    @param[in]  theParams   Matrix puzzle configuration instance.
    '''

    super(Matrix, self).__init__(theBoard, theParams)

    if isinstance(theBoard, Board):
      # Store the calibrated grid location of the puzzle piece, e.g., [x; y]
      # We do not have to worry about the index or id here since they are the same in
      # the solution board.
      self.gc = np.zeros((2, theBoard.size()))      # @< Puzzle piece grid locations.
      #!self.pshape = []                            # @< Puzzle grid dims (width x height)
    else:
      raise TypeError('Not initialized properly')

    # @todo Running but does not seem needed for Matrix puzzle. - PAV 01/11/2025.
    self.xcoords = []
    self.ycoords = []
    self.shape   = []
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
    x_list = np.array([rLoc[0] for _, rLoc in pLoc.items()]).reshape(-1, 1)
    y_list = np.array([rLoc[1] for _, rLoc in pLoc.items()]).reshape(-1, 1)

    #!  # Use known row and column quantities to get the x, y labels of the puzzle
    #!  # pieces by partitioning in vertical and horizontal so that each partition
    #!  # has the same number of elements in it.  That gets the answer.
    x_labels, x_parts = partition_even(x_list, partition_num=self.params.psize[0], 
                                                                        order="ascend")
    y_labels, y_parts = partition_even(y_list, partition_num=self.params.psize[1], 
                                                                        order="ascend")

    self.xcoords = x_parts[:,1]
    self.ycoords = y_parts[:,1]

    self.shape = self.params.psize

    #!if self.params.gridding == 'rectangular':
    #!  # Code below works for a rectangular gridding of the puzzle based on assumption
    #!  # in the documentation above.
    #!  x_list = np.array([rLoc[0] for _, rLoc in pLoc.items()]).reshape(-1, 1)
    #!  y_list = np.array([rLoc[1] for _, rLoc in pLoc.items()]).reshape(-1, 1)

    #!  # Use rectangular shape to get no. of rows and columns. Store in pshape.
    #!  xMin = np.min(x_list)
    #!  yMin = np.min(y_list)
    #!  self.pshape = [ np.count_nonzero(y_list == yMin) , np.count_nonzero(x_list == xMin) ]

    #!  #DEBUG
    #!  #print(self.pshape)

    #!  # Use known row and column quantities to get the x, y labels of the puzzle
    #!  # pieces by partitioning in vertical and horizontal so that each partition
    #!  # has the same number of elements in it.  That gets the answer.
    #!  x_labels, x_parts = partition_even(x_list, partition_num=self.pshape[0], order="ascend")
    #!  y_labels, y_parts = partition_even(y_list, partition_num=self.pshape[1], order="ascend")

    #!elif self.params.gridding == 'arrangedbox':

    #!  x_list = np.array([rLoc[0] for _, rLoc in pLoc.items()]).reshape(-1, 1)
    #!  y_list = np.array([rLoc[1] for _, rLoc in pLoc.items()]).reshape(-1, 1)

    #!  x_labels, y_labels = self.__processMatrix(x_list, y_list)

  #============================= __processMatrix =============================
  #
  def __processMatrix(self, x_list, y_list):
    '''!
    @brief  Generate matrix organization given that puzzle is rectangular.
            Check all the two number combinations that multiply to the piece number.
            The two number will be treated as the maximum grid coordinate along x and y
            directions.  For number, assign the x_list and y_list evenly, and finally
            choose the one with the least mean square error.

    @note   Per Yiye, this form of processing works decently.  It would be better if
            the code actually did a factoring, then only processed the different
            factor combinations. Use sympy.factorint or equivalent.

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
        

  #============================== getCoordinates =============================
  #
  def getCoordinates(self):
    '''!
    @brief  Obtain solution board coordinates for the pieces.

    @param[out]   gc  Grid coordinates assigned to each pieces, (2, N_pieces).
    '''

    # @todo Doesn't seem to be populated for Matrix.  Need to resolve this.
    #       Fornow going with default row, col approach: data row-wise.
    return self.gc

  #============================== sub2ind ==============================
  #
  def sub2ind(self, theSubs):
    '''!
    @brief  Uses puzzle shape to convert puzzle piece subscripts to linear index/key.

    Assumes that pieces are ordered according to their matrix placement.
    Normally gc would permit some kind of re-indexing/re-keying, but it doesn't
    seem to be implemented.  Chugging through for now.

    @param[in]  theSubs   Given in (i,j) subscripting coordinates.

    @todo   Make sure not impacted by other operations.  Right now depends on outer
            scope to figure that out or to not disturb piece ordering.
    '''

    return np.ravel_multi_index( theSubs, self.shape[::-1]) 

  #============================= coord2ind =============================
  #
  def coord2ind(self, theCoords):
    '''!
    @brief  Uses puzzle shape to convert puzzle piece coordinate to linear index/key.

    Assumes that pieces are ordered according to their matrix placement.
    Normally gc would permit some kind of re-indexing/re-keying, but it doesn't
    seem to be implemented.  Chugging through for now.

    @param[in]  theCoords   Given in (x,y) coordinates.

    @todo   Make sure not impacted by other operations.  Right now depends on outer
            scope to figure that out or to not disturb piece ordering.
    '''

    if (len(theCoords) == 0):
      return []

    theSubs = []
    for coords in theCoords:
      #! DEBUG
      #!print(coords)
      theSubs.append(coords[::-1])

    return np.ravel_multi_index( np.transpose(theSubs), self.shape[::-1]) 

  #============================== shuffle ==============================
  #
  def shuffle(self, numPieces=None, reorient=False):
    '''!
    @brief  Randomly shuffle location of puzzle pieces of the puzzle.

    Basically takes random mapping of puzzle pieces to each other, then swaps
    locations and IDs.  That should shuffle everything up.

    # @todo The numPieces argument does nothing as of now.  Should address.
    # @todo Rotation should just be 90 degree increments (0,90,180,270).

    @param[in]  numPieces   Number of pieces to shuffle (default: None = All pieces).
    @param[in]  reorient    Also apply random rotation (default: False).

    @param[out] idMap       The ground truth shuffling as a dict [oldId -> newId]
    '''

    keyOrig = list(self.pieces)
    keyShuf = keyOrig.copy()
    random.shuffle(keyShuf)

    pieceLocations = self.pieceLocations()
    pieceLocations = np.transpose(np.array([value for value in pieceLocations.values()]))
    pieceLocations = pieceLocations[:,np.array(keyShuf)]

    pieceIDs = np.array([self.pieces[i].id for i in range(self.size())])
    shuffIDs = pieceIDs[keyShuf]
    key2id = dict(zip(keyOrig, shuffIDs))
    idMap  = dict(zip(pieceIDs, shuffIDs))

    for key in self.pieces.keys():
      piece = self.pieces[key]

      if reorient:
        piece = piece.rotatePiece(random.uniform(rotRange[0], rotRange[1]))    # Random reorientation

      piece.setPlacement(pieceLocations[:,key])             # shuffled location.
      piece.id = key2id[key]

      self.pieces[key] = piece

    return idMap


  #============================ swapByCoords ===========================
  #
  def swapByCoords(self, swapCoords):
    '''!
    @brief  Specify puzzle piece coordinates that should be swapped.

    Given a list of coordinate pairs, apply the swap. Each list entry consists
    of a tuple of swap coordinates. Invalid coordinates with result in no swap.

    @param[in]  swapCoords  List of swap tuples. 
    @param[out] idMap       The ground truth swap as a dict [oldId -> newId]
    '''

    # loop over list length
    theswap = np.empty( (len(swapCoords),2) )
    si = 0
    for cSwap in swapCoords:
      theswap[si,:] = [self.coord2ind(cSwap[0]), self.coord2ind(cSwap[1])]
      si = si+1

    #! DEBUG
    #! print(theswap)
    self.swap(theswap.astype('int'))

  #================================ swap ===============================
  #
  def swap(self, theswap=None, reorient=False):
    '''!
    @brief  Randomly shuffle location of puzzle pieces of the puzzle.

    Basically takes random mapping of puzzle pieces to each other, then swaps
    locations and IDs.  That should shuffle everything up.

    # @todo The numPieces argument does nothing as of now.  Should address.
    # @todo Rotation should just be 90 degree increments (0,90,180,270).

    @param[in]  theswap     Array of swaps (row-wise) as from to (col-wise). None = no swap.
    @param[in]  reorient    Also apply random (0,90,180,270) rotation (default: False).

    @param[out] idMap       The ground truth swap as a dict [oldId -> newId]
    '''

    # @todo This is a copy of shuffle.  Need to redo the code so it swaps only
    #       those specified.  Basically just remap according to theswap.
    #
    #!print('Hello')
    keyOrig = list(self.pieces)
    keySwap = keyOrig.copy()
    numSwaps = theswap.shape[0]
    for ii in range(numSwaps):
      keySwap[theswap[ii,0]] = theswap[ii,1]
      keySwap[theswap[ii,1]] = theswap[ii,0]

    # @note Currently doing a brute force swap over all.  Not the cleanest
    #       Should be able to do only subset affected.

    pieceLocations = self.pieceLocations()
    pieceLocations = np.transpose(np.array([value for value in pieceLocations.values()]))
    pieceLocations = pieceLocations[:,np.array(keySwap)]

    pieceIDs = np.array([self.pieces[i].id for i in range(self.size())])
    shuffIDs = pieceIDs[keySwap]
    key2id = dict(zip(keyOrig, shuffIDs))
    idMap  = dict(zip(pieceIDs, shuffIDs))

    for key in self.pieces.keys():
      piece = self.pieces[key]

      if reorient:
        piece = piece.rotatePiece(random.uniform(rotRange[0], rotRange[1]))    # Random reorientation

      piece.setPlacement(pieceLocations[:,key])             # shuffled location.
      piece.id = key2id[key]

      self.pieces[key] = piece

    return idMap

  #================================ retile ===============================
  #
  def retile(self, dx=150, dy=150, inOrder = True):
    '''!
    @brief  Organize puzzle pieces according to gridding.

    Takes the puzzle pieces as ordered in the list and attaches them to
    a gridding respecting the puzzle shape. If there are not enough
    puzzle pieces, then it will stop at last one.  If there are too many,
    then these will be dumped below the gridding with extra vertical offset.

    @param[in]  dx          Horizontal step increment of grid.
    @param[in]  dy          Vertical   step increment of grid.
    @param[in]  inOrder     Sort by puzzle piece ID.
    '''

    pSize = self.pshape[0]*self.pshape[1]

    if (inOrder):
      pieceIDs = list(enumerate([self.pieces[i].id for i in range(self.size())]))
      sortIDs = sorted(pieceIDs, key=lambda x:x[1])
      sortInd = [index for index, _ in sortIDs]
    else:
      sortInd = list(range(0,self.size()))

    pcnt  = 0;
    for py in range(self.pshape[1]):
      for px in range(self.pshape[0]):
        self.pieces[sortInd[pcnt]].setPlacement(np.array([px*dx, py*dy]))
        pcnt = pcnt + 1

        if (pcnt >= pSize):
          break

      if (pcnt >= pSize):
        break
    
    if (pcnt < pSize):
      numLeft = (self.size() - pcnt)

      numRows, numRem = divmod(numLeft, self.pshape[0])
      if (numRem > 0):
        numRows = numRows + 1

      for py in range(self.pshape[1]+2,self.pshape[1]+2+numRows):
        for px in range(self.pshape[0]):
          self.pieces[sortInd[pcnt]].setPlacement(np.array([px*dx, py*dy]))
          pcnt = pcnt + 1

          if (pcnt >= self.size()):
            break

        if (pcnt >= self.size()):
          break
    
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
    

  #======================== buildFromFile_Puzzle =======================
  #
  @staticmethod
  def buildFromFile_Puzzle(fileName, theParams=None):
    '''!
    @todo   NOT UPDATED!!!!

    @brief  Load a saved arrangement calibration/solution puzzle board.

    @param[in]    fileName    Python file to load.
    @param[in]    theParams   Matrix configuration instance.

    @return   thePuzzle   Matrix puzzle board instance.
    '''

    aPuzzle = Arrangement.buildFromFile_Puzzle(fileName, theParams)

    with open(fileName, 'rb') as fp:
      data = pickle.load(fp)

    if theParams is None and hasattr(data, 'tauGrid'):  # DELETE WHEN CODE FIXED.
      theParams = CfgMatrix()                        # BAD SAVE/LOAD PROCESS.
      theParams.tauGrid = data.tauGrid

    thePuzzle = Matrix(aPuzzle, theParams)
    #TODO: WHAT IS THIS? DELETE IF ABOVE WORKS.
    #if hasattr(theParams, 'tauGrid'):
    #    thePuzzle = Matrix(aPuzzle, theParams)
    #else:
    #    thePuzzle = Matrix(aPuzzle)

    return thePuzzle

  #===================== buildFromFile_ImageAndMask ====================
  #
  @staticmethod
  def buildFromFile_ImageAndMask(fileName, theParams=None):
    '''!
    @todo   NOT UPDATED!!!!

    @brief Load a saved arrangement calibration/solution stored as an image and a mask.

    The python file contains the puzzle board mask and image source data. It gets
    processed into an arrangement instance. If a threshold variable ``tauDist`` is
    found, then it is applied to the arrangement instance.

    @param[in]    fileName    Python file to load.
    @param[in]    theParams   Matrix configuration instance.

    @return   thePuzzle   Matrix puzzle board instance.
    '''
    aPuzzle = Arrangement.buildFromFile_ImageAndMask(fileName, theParams)

    if hasattr(theParams, 'tauGrid'):
      thePuzzle = Matrix(aPuzzle, theParams)
    else:
      thePuzzle = Matrix(aPuzzle)

    return thePuzzle

  #==================== buildFromFiles_ImageAndMask ====================
  #
  @staticmethod
  def buildFromFiles_ImageAndMask(imFile, maskFile, theParams=None):
    '''!
    @todo   NOT UPDATED!!!!

    @brief Load a saved arrangement calibration/solution stored as
           separate image and mask files.

    The source file contain the puzzle board image and mask data. It gets processed
    into an arrangement instance. If a threshold variable ``tauDist`` is found, then
    it is applied to the arrangement instance.

    @param[in]    imFile      Image file to load.
    @param[in]    maskFile    Mask file to load.
    @param[in]    theParams   Matrix configuration instance.

    @return   thePuzzle   Matrix puzzle board instance.
    '''

    aPuzzle = Arrangement.buildFromFiles_ImageAndMask(imFile, maskFile, theParams)

    if hasattr(theParams, 'tauGrid'):
      thePuzzle = Matrix(aPuzzle, theParams)
    else:
      thePuzzle = Matrix(aPuzzle)

    return thePuzzle

  #===== buildFrom_ImageAndSpecs =====
  #
  @staticmethod 
  def buildFrom_ImageAndSpecs(theImage, theParams):
    '''!
    @brief  Given a fully specific Matrix puzzle and an image, instantiate
            a Matrix puzzle.

    The image and the puzzle specification need not agree.  The image will
    be reshaped to the nearest possible size compatible with the Matrix
    specifications.  It may be that the puzzle sizing has to change to 
    match that aspect ratio of the original image, or the image has to be
    cropped. This routine tries to minimize how much the specifications are
    adjusted to make a puzzle from the source image.

    What is important about the puzzle specification is that the number of
    columns and rows (width and height) of the puzzle matrix should be given.
    The target image size should be given too.  If not, then the source image
    will be used for the initial target image size, which may be adjusted or 
    cropped for compatiblity with the puzzle sizing. 

    @param[in]  theImage    The source image.
    @param[in]  theParams   The Matrix puzzle configuration (should be complete).

    @return     thePuzzle   A Matrix puzzle board instance.
    @return     theImage    The modified source image.
    '''

    #! Be careful because specifications are WxH but python does HxWxD.
    #! Indices will not agree.  Make sure to index properly.
    imsize = np.shape(theImage)
    imcols = imsize[1]
    imrows = imsize[0]

    #! DEBUG
    #!print('======================')
    #!print(imsize)
    #!print(theParams.psize)
    #!print(theParams.isize)

    #! Step 1 : Adjust the target image size to match the target puzzle size
    #!          in terms of rows and columns.  We need for target image size
    #!          to be divisible by puzzle size.


    #! Step 2 : Work out the target image size if not fully specified.
    #!
    if (theParams.isize[0] is None) and (theParams.isize[1] is None):
      #! Use image size.
      theParams.isize = (imcols, imrows)
    elif (theParams.isize[0] is None):
      #! Use image aspect ratio to set size.
      rowTarg = int((imrows*theParams.isize[1])/imcols)
      theParams.isize[0] = rowTarg
    elif (theParams.isize[1] is None):
      #! Use image aspect ratio to set size.
      colTarg = int((imcols*theParams.isize[0])/imrows)
      theParams.isize[1] = colTarg

    #! Step 3 : Get image size and target image size to align by resizing.
    #!          Do not crop since alignment to puzzle size may adjust these
    #!          values somewhat.  Need as much image as possible for that.
    #!
    spRatio  = theParams.isize[0]/theParams.isize[1]    #! Width/height.
    imRatio  = imcols / imrows

    if (np.all(theParams.isize != [imsize[i] for i in (1,0)])):
      #! Need to modify imagery only if the sizes differ.

      if (spRatio > imRatio):
        #! Specification is wide, while image is tall.  Need to resize.
        #! Resizing will be such that image is as wide as specification,
        #! which means it ends up being taller than the specified size.
        #! Downstream adjustments should correct for that (hopefully).

        #! DEBUG
        #!print('Wide vs Tall')
        imFact   = theParams.isize[0] / imcols
        theImage = cv2.resize(theImage, None, fx=imFact, fy=imFact)

        imsize = theImage.shape
        imcols = imsize[0]
        imrows = imsize[1]

      else:
        #! Specification is tall, while image is wide.  Need to resize.
        #! Or they might work out just right.
        #! Resizing will be such that image is as tall as specification,
        #! which means it ends up being wide than the specified size.
        #! Downstream adjustments should correct for that (hopefully).

        #! DEBUG
        #!print('Tall vs Wide')
        imFact   = theParams.isize[1] / imrows
        theImage = cv2.resize(theImage, None, fx=imFact, fy=imFact)

        imsize = theImage.shape
        imcols = imsize[0]
        imrows = imsize[1]

    #! Step 4 : Get image size and puzzle size to align by resizing and cropping.
    #!          It may mostly crop for now. Solution is not unique.
    #!

    dc = int(imsize[1] / theParams.psize[0])
    dr = int(imsize[0] / theParams.psize[1])

    ticols = dc * theParams.psize[0]
    tirows = dr * theParams.psize[1]

    #! DEBUG
    #!print('New size (HxW):')
    #!print(imsize)
    #!print((dr, dc))
    #!print((tirows, ticols))

    #! @todo If image size is strict then should crop!!! Add strict flag.
    #!       Adjust to minimum of either value, which crops.
    #!       Add coff and roff to correct so that crop is from middle.
    #!       That may not be necessary. Not implementing for now.
    #!coff  = ((imsize[1] - ticols)/2)
    #!roff  = ((imsize[0] - tirows)/2)
    #!print((ticols,tirows))
    #!print((coff,roff))

    theImage = theImage[0:tirows, 0:ticols, :]
    imsize = np.shape(theImage)
    imcols = imsize[1]
    imrows = imsize[0]

    theParams.isize = (None, None)      #! Image will determine image size.

    #! Step 5: For now make a mask. Later do by region labeling.
    #!
    theMask = np.ones([imrows, imcols])
    for ci in range(theParams.psize[0]) :
      theMask[:,ci*dc] = 0;

    for ri in range(theParams.psize[1]) :
      theMask[ri*dr,:] = 0;

    thePuzzle = Matrix.buildFrom_ImageAndMask(theImage, theMask, theParams)

    return thePuzzle, theImage


  #===================== buildFrom_ImageAndRegions =====================
  #
  def buildFrom_ImageAndRegions(theImage, theRegions, theParams=CfgMatrix()):

    thePuzzle = None
    return thePuzzle

  #======================= buildFrom_ImageAndMask ======================
  #
  @staticmethod
  def buildFrom_ImageAndMask(theImage, theMask, theParams=CfgMatrix(), show_grid=False):
    '''!
    @todo   NOT UPDATED!!!!

    @brief Given an image and an image mask, parse both to recover the puzzle
           calibration/solution.

    Instantiates a puzzle parser that gets applied to the submitted data to create a
    puzzle board instance. That instance is the calibration/solution.

    @param[in]    theImage    Puzzle image data.
    @param[in]    theMask     Puzzle mask data.
    @param[in]    theParams   Matrix configuration instance.

    @return   thePuzzle   Matrix puzzle board instance.
    '''

    aPuzzle   = Arrangement.buildFrom_ImageAndMask(theImage, theMask, theParams)

    if show_grid:
      aPuzzle.display_mp()
      plt.show()

    thePuzzle = Matrix(aPuzzle, theParams)

    return thePuzzle

  #====================== buildFrom_ImageProcessing ======================
  #
  @staticmethod
  def buildFrom_ImageProcessing(theImage, theProcessor=None, theDetector=None, 
                                                                        theParams=None):
    '''
    @todo   NOT UPDATED!!!!

    @brief  Given an image with regions clearly separated by some color or threshold,
            parse it to recover the puzzle calibration/solution. Can source alternative
            detector.

    Instantiates a puzzle parser that gets applied to the submitted data to create a
    puzzle board instance. That instance is the calibration/solution.

    @param[in]  theImage: The puzzle image data.
    @param[in]  theProcessor: The processing scheme.
    @param[in]  theDetector: The detector scheme.
    @param[in]  theParams   Matrix configuration instance.

    @return   thePuzzle   Matrix puzzle board instance.
    '''

    aPuzzle = Arrangement.buildFrom_ImageProcessing(theImage, theProcessor, 
                                                              theDetector , theParams)

    if hasattr(theParams, 'tauGrid'):
      thePuzzle = Matrix(aPuzzle, theParams)
    else:
      thePuzzle = Matrix(aPuzzle)

    return thePuzzle

  #=========================== buildFrom_Sketch ==========================
  #
  @staticmethod
  def buildFrom_Sketch(theImage, theMask, theProcessor=None, theDetector=None, theParams=None):
    '''
    @todo   NOT UPDATED!!!!

    @brief  Given an image with regions clearly separated by some color or threshold,
            parse it to recover the puzzle calibration/solution. Can source alternative
            detector.

    Instantiates a puzzle parser that gets applied to the submitted data to create a
    puzzle board instance. That instance is the calibration/solution.

    @param[in]  theImage:       Puzzle image data.
    @param[in]  theMask:        Puzzle mask data.
    @param[in]  theProcessor    Processing scheme.
    @param[in]  theDetector     Detector scheme.
    @param[in]  theParams       Matrix configuration instance.

    @return     thePuzzle   Matrix puzzle board instance.
    '''
    aPuzzle = Arrangement.buildFrom_Sketch(theImage, theMask, theProcessor, theDetector, theParams)

    if hasattr(theParams, 'tauGrid'):
      thePuzzle = Matrix(aPuzzle, theParams)
    else:
      thePuzzle = Matrix(aPuzzle)

    return thePuzzle

#
#=========================== puzzle.builder.matrix ===========================
