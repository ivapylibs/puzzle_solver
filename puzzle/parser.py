#============================== puzzle.parser ==============================
#
# @class    puzzle.parser
#
# @brief    A basic tracking class that processes a layered image (or mask
#           and image) detection output and generates a model of the puzzle
#           pieces in the scene. Converts all accepted, isolated regions
#           into their own puzzle piece instances.
#
#
# Being a subclass of centroidMulti, this is effectively just a puzzle board
# measurement strategy.  To be a full fledged system requires integration
# with some sort of filter (e.g., temporal data association scheme).
#
#============================== puzzle.parser ==============================
#
# @file     parser.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#           Patricio A. Vela,       pvela@gatech.edu
# @date     2023/09/01 [copied from puzzle.parser.fromLayer master branch]
#
# NOTE:90 columns.
#
#============================== puzzle.parser ==============================

# ===== Environment / Dependencies
#

from dataclasses import dataclass

import cv2
import numpy as np
from copy import deepcopy

from trackpointer.centroidMulti import centroidMulti, CfgCentMulti

from puzzle.board import Board
from puzzle.piece import Piece, PieceStatus
from puzzle.utils.shapeProcessing import bb_intersection_over_union


#
#---------------------------------------------------------------------------
#==================== Configuration Node : boardMeasure ====================
#---------------------------------------------------------------------------
#

class CfgBoardMeasure(CfgCentMulti):
  '''!
  @brief  Configuration setting specifier for centroidMulti.
  '''

  #============================= __init__ ============================
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief        Constructor of configuration instance.
  
    @param[in]    cfg_files   List of config files to load to merge settings.
    '''
    if (init_dict == None):
      init_dict = CfgBoardMeasure.get_default_settings()

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
    default_dict = CfgCentMulti.get_default_settings()
    default_dict.update(dict(\
          lengthThresholdLower = 1000, \
          pieceBuilder = 'Template', pieceStatus = PieceStatus.MEASURED.value))

    return default_dict

  #========================== builtForPuzzles =========================
  #
  #
  def builtForPuzzles():
    puzzleCfg = CfgBoardMeasure();
    puzzleCfg.minArea = 60
    puzzleCfg.maxArea = float('inf')
    return puzzleCfg


#
#---------------------------------------------------------------------------
#=============================== boardMeasure ==============================
#---------------------------------------------------------------------------

class boardMeasure(centroidMulti):

  def __init__(self, theParams=CfgBoardMeasure()):
    """!
    @brief  Constructor for the puzzle piece layer parsing class.

    @param[in]  theParams   The parameters/config settings for the track pointer.
    """

    super(boardMeasure, self).__init__(None, theParams)

    self.bMeas = Board()  # @< The measured board.
    self.pieceConstructor = Piece.getBuilderFromString(theParams.pieceBuilder)


  def getState(self):
    """!
    @brief  Return the track-pointer state. Override the original one.

    @param[out] tstate  Return the board measurement track state.
    """
    tstate = self.bMeas

    return tstate

  def measure(self, I, M):
    """!
    @brief  Process the passed imagery to recover puzzle pieces and
            manage their track states.

    @param[in] I    RGB image.
    @param[in] M    Mask image.
    """

    # 1] Extract pieces based on disconnected component regions
    #    then instantiate puzzle piece instances from regions.
    #
    regions = self.mask2regions(I, M)
    pieces  = self.regions2pieces(regions)

    # 3] Package into a board.
    #
    self.bMeas.clear()
    self.bMeas.addPieces(pieces)

    # Add the pieces one by one. So the label can be managed.
    # MOVE THIS TO BOARD FUNCTION addPieces.

    self.haveMeas = len(self.bMeas.pieces) > 0

    if self.haveMeas:
      #self.tpt = self.bMeas.getPieceLocations()
      # MOVE THIS TO BOARD FUNCTION getPieceLocations() . ALREADY a pieceLocations.
      thePieces = self.bMeas.pieceLocations()
      print('The pieces ....')
      print(thePieces)
      print('---------------')
      self.tpt = []
      for id, loc in thePieces.items():
        self.tpt.append(loc)
      self.tpt = np.array(self.tpt).reshape(-1, 2).T


  def findCorrectedContours(self, mask, FILTER=True):
    """
    @brief Find the right contours given a binary mask image.

    @param[in]  mask    The input binary mask image.
    @param[in]  FILTER  Options (set to TRUE).

    @param[ou]  desired_cnts    Contour list.
        """
    # For details of options, see https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga819779b9857cc2f8601e6526a3a5bc71
    # and https://docs.opencv.org/4.5.2/d3/dc0/group__imgproc__shape.html#ga4303f45752694956374734a03c54d5ff
    # For OpenCV 4+
    cnts, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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

      print('KKKK')
      print(keep)
      print(cnts)
      cnts = np.array(cnts)
      cnts = cnts[keep]
      print('CCCC')
      print(cnts)
      print('----')
    else:
      cnts = np.array(cnts)

    desired_cnts = []

    # Filter out some contours according to area threshold
    for c in cnts:
      # Draw the contours
      # cv2.drawContours(mask, [c], -1, (0, 255, 0), 2)

      area = cv2.contourArea(c)

      # Filtered by the area threshold
      if area > self.tparams.maxArea:
        continue
      elif area > self.tparams.minArea:
        desired_cnts.append(c)
      else:
        # findContours may return a discontinuous contour which cannot compute contourArea correctly
        if cv2.arcLength(c, True) > self.tparams.lengthThresholdLower:

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
            if area > self.tparams.maxArea:
              continue
            elif area > self.tparams.minArea:
              desired_cnts.append(c)
            desired_cnts.append(c)
    
    print("DCDCDCDCDCDC")
    print(desired_cnts)
    print('RRRRRRRRRRRR')
    return desired_cnts

  def mask2regions(self, I, M, verbose=False):
    """
    @brief Convert the selection mask into a bunch of regions.
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
    if verbose:
      cv2.imshow('debug_ori_mask',mask)
      cv2.waitKey()

    desired_cnts = self.findCorrectedContours(mask)

    # In rare case, a valid contour may contain some small contours
    if len(desired_cnts) == 0:
        desired_cnts = self.findCorrectedContours(mask, FILTER=False)

    if verbose:
        print('size of desired_cnts is', len(desired_cnts))

    # # Debug only
    if verbose:
      debug_mask = np.zeros_like(mask).astype('uint8')
      for c in desired_cnts:
        cv2.drawContours(debug_mask, [c], -1, (255, 255, 255), 2)

      debug_mask = cv2.resize(debug_mask, (int(debug_mask.shape[1] / 2), int(debug_mask.shape[0] / 2)), interpolation=cv2.INTER_AREA)
      cv2.imshow('debug_after_area_thresh',debug_mask)
      cv2.waitKey()

    regions = []
    # Get the individual part
    print('DCDCDCDCDCD')
    print(desired_cnts)
    for c in desired_cnts:
      seg_img = np.zeros(mask.shape[:2], dtype="uint8")  # reset a blank image every time
      cv2.drawContours(seg_img, [c], -1, (255, 255, 255), thickness=-1)

      # # Debug only
      if verbose:
        cv2.imshow('debug_individual_seg',seg_img)
        cv2.waitKey()

      # Get ROI, OpenCV style
      x, y, w, h = cv2.boundingRect(c)

      # The area checking only count the actual area but we may have some cases where segmentation is scattered
      if w*h > self.tparams.maxArea:
        skipFlag = True
      else:
        # Double check if ROI has a large IoU with the previous ones, then discard it
        skipFlag = False
        for region in regions:
          if bb_intersection_over_union(region[3], [x, y, x + w, y + h]) > 0.5:
            skipFlag = True
            break

      # Todo: A tricky solution to skip regions of all black, which is for our real scene
      if cv2.countNonZero(cv2.threshold(cv2.cvtColor(cv2.bitwise_and(I.astype('uint8'), I.astype('uint8'), mask=seg_img.astype('uint8')), cv2.COLOR_BGR2GRAY), 50, 255, cv2.THRESH_BINARY)[1]) == 0:
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
      """!
      @brief Convert the region information into puzzle pieces.

      @param[in] regions    List of region pairs (mask, segmented image, location in the source image).

      @param[out] pieces    List of puzzle pieces instances.
      """
      pieces = []
      print(regions)
      for region in regions:
        theMask  = region[0]
        theImage = region[1]
        rLoc     = region[2]
        thePiece = self.pieceConstructor.buildFromMaskAndImage(theMask, theImage, \
                                          rLoc=rLoc, pieceStatus=self.tparams.pieceStatus)

        pieces.append(thePiece)

      return pieces


  def process(self, I, M):
    """!
    @brief  Run the tracking pipeline for image measurement.

    @param[in] I    RGB image.
    @param[in] M    Mask.
    """
    self.measure(I, M)

#
#============================== puzzle.parser ==============================
