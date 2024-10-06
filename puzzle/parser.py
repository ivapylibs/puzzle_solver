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
# 1] boardMeasure
#
# Being a subclass of centroidMulti, this is effectively just a puzzle board
# measurement strategy.  To be a full fledged system requires integration
# with some sort of filter (e.g., temporal data association scheme).
#
#
# 2] boardTracker
#
# Performs the data association code for keeping track of puzzle pieces over
# time.
#
# 3] boardActivity
#
# Monitors the tracker associations and recovers the atomic actions or activities
# inferred from the track states over time.
#
#============================== puzzle.parser ==============================
#
# @file     parser.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#           Patricio A. Vela,       pvela@gatech.edu
# @date     2023/09/01 [copied from puzzle.parser.fromLayer master branch]
#
# NOTE:
#   90 columns.
#   indent is 2 spaces.
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

from camera.utils import display

import perceiver.perceiver as Perceiver 

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
    default_dict['minArea'] = 1
    default_dict.update(dict(measProps = True,  #override
          lengthThresholdLower = 1000,  \
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
#

class boardMeasure(centroidMulti):

  #============================== __init__ =============================
  #
  def __init__(self, params=CfgBoardMeasure()):
    """!
    @brief  Constructor for the puzzle piece layer parsing class.

    @param[in]  theParams   The parameters/config settings for the track pointer.
    """

    if params is None:
      params = CfgBoardMeasure()

    super(boardMeasure, self).__init__(None, params)

    self.bMeas = Board()  # @< The measured board.
    self.pieceConstructor = Piece.getBuilderFromString(params.pieceBuilder)

  #============================== getState =============================
  #
  def getState(self):
    """!
    @brief  Return the track-pointer state. Override the original one.

    @param[out] tstate  Return the board measurement track state.
    """
    tstate = self.bMeas

    return tstate

  #============================== measure ==============================
  #
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
    self.bMeas = Board()                # Get a new measured board.
    super(boardMeasure, self).measure(M)


    # DEBUG
    #print("boardMeasure : measure.")
    #print("Made it through here fine.")
    self._regions2board(I)

    # Override since some regions might be too small or large. Check again.
    # Also regenerate the list of "track points."
    self.haveMeas = len(self.bMeas.pieces) > 0  

    if self.haveMeas:
      #self.tpt = self.bMeas.getPieceLocations()
      # MOVE THIS TO BOARD FUNCTION getPieceLocations() . ALREADY a pieceLocations.
      # The function returns a dict. Ugly but possibly sensible given the implementation.
      # Yucky though.  
      # @todo   Consider how to implement some form of getPieceLocations or maybe
      #         should be getPieceTrackpoint.  Who knows.  Moving on.
      thePieces = self.bMeas.pieceLocations()
      self.tpt = []
      for id, loc in thePieces.items():
        self.tpt.append(loc)
      self.tpt = np.array(self.tpt).reshape(-1, 2).T
      #DEBUG
      #print(self.tpt)


  #=========================== _regions2board ==========================
  #
  def _regions2board(self, I):
    '''!
    @brief  Extract piece information from identified regions. Add to
            board measurement.

    The process packages up the region mask, the region image data, the
    centroid, and the puzzle piece status.  These get added to the board
    measurement.
    '''

    #--[0] Pre-processing. Reshape image for faster recovery of 
    #       content.
    self.bMeas.clear()  # Clear board.

    imdims = np.shape(I)
    #vI = I.reshape(-1, imdims[2])        # Vectorized image.

    for ri in self.trackProps:
      #--[1] Region label process recovers bounding box mask and sliced image coords.
      #      Extract the color image patch from mask, and vectorized image data
      #      based on mask and region pixel coords.
      #
      #DEBUG
      #print(self.tparams)
      pImage = I[ri.slice]
      pMask  = ri.image
      pImage = pImage.reshape( np.append(np.shape(pMask), imdims[2]) )

      #DEBUG VISUAL
      #print("Image and Mask shapes.")
      #print(pImage.shape)
      #print(pMask.shape)
      #print("Theta??")
      #print(ri.orientation)
      #@todo    orientation part may be worth keeping if it is consistently computed.
      #         then can use for placing in proper orientation. - PAV 10/04/2024.
     
      #--[3] Collect other information.
      #
      pCorn  = np.array([ri.bbox[1], ri.bbox[0]])
      pCent  = np.round(ri.centroid).astype(int)[::-1]      # (x,y) coords.
      pStat  = self.tparams.pieceStatus

      #--[4] Instantiate piece and add to measured board.
      #
      ##
      ## Gridded: buildFrom_ImageAndMask (theParams = custom CfgGridded) 
      ## Arrangement: buildFrom_ImageAndMask (theParams)
      ##
      #DEBUG 
      #print('-----')
      #print(ri.area)
      #print(self.tparams.minArea)
      #print((ri.bbox[2]-ri.bbox[0])*(ri.bbox[3]-ri.bbox[1]))
      #print(np.shape(pMask))
      #print(np.shape(pImage))
      #print(pCorn)
      #print(pCent)
      #print(pStat)
      #print('EEEEE')
      if (ri.area > self.tparams.minArea):
        thePiece = self.pieceConstructor.buildFromMaskAndImage(pMask, pImage, 
                                                               pCorn, None, pStat)
        # @todo I was sending the centroid as a coordinate. Why was that??
        #       Why do we need the centroid?  Is it to better test for proximity?
        #       Otherwise, the corner may not be a great way to do so? PAV 10/04/2024.
        #       May need to fix this downstream.

        #thePiece = self.pieceConstructor.buildFromPropsAndImage(ri, pImage, pStat)
        # @todo   Maybe should just work directly from region props info plus cropped image.
        #         Let builder extract what it needs to.
        # @todo   Revisit once working.
        self.bMeas.addPiece(thePiece)

        #DEBUG
        #display.rgb_cv(pImage)
        #display.binary_cv(ri.image)
        #display.wait_cv()
      # @todo   Appears to miss outer pixel boundary during piece plotting. But here
      #         that is not the case.  Something happens elsewhere. Maybe in the
      #         plot/display or place in image routine.  Need to double check code.
      #         09/08: Confirmed that place in image is weird. Push to later.
      #         09/15: There are weird adjustments to image size. Badly commented.


  #xxxxxxxxxxxxxxxxxxxxxxx findCorrectedContours xxxxxxxxxxxxxxxxxxxxxxx
  #
  # MOST LIKELY NO LONGER NEEDED. KEEP UNTIL NEW IMPLEMENTATION DONE.
  #
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

      #DEBUG
      #print('KKKK')
      #print(keep)
      #print(cnts)
      cnts = np.array(cnts)
      cnts = cnts[keep]
      #print('CCCC')
      #print(cnts)
      #print('----')
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
    
    #DEBUG
    #print("DCDCDCDCDCDC")
    #print(desired_cnts)
    #print('RRRRRRRRRRRR')
    return desired_cnts

  #xxxxxxxxxxxxxxxxxxxxxxxxxxxx mask2regions xxxxxxxxxxxxxxxxxxxxxxxxxxx
  #
  # To be deprecated.  Seems to use an inefficient OpenCV scheme.
  # Replicating functionality elsewhere as I decipher the code.
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

  #xxxxxxxxxxxxxxxxxxxxxxxxxxx regions2pieces xxxxxxxxxxxxxxxxxxxxxxxxxx
  #
  # to be deprecated.  Appears to use weird OpenCV implementation.
  # the process seems contorted relative to how Matlab would do it.
  # Shifting gears to skimage until can figure out OpenCV equivalent
  # that isn't contour-based, or that better utilizes the contour-based
  # approach.
  #
  # The process is more sensible when based on pixel regions (not
  # boundaries).
  #
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
#---------------------------------------------------------------------------
#============================== boardPerceive ==============================
#---------------------------------------------------------------------------
#

#
# @todo Missing algorithm configuration node for the Perceiver.
# @todo What would the configuration node even have?
#
# @note Moved from earlier version in parser/simple.py
#

class boardPerceive(Perceiver.Perceiver):
  """!  
  @brief  A simple perceiver for recovering puzzle pieces from a
          layer mask and an image. If desired, can do piece association.

  Being a perceiver, there is flexibility in the implementation.
  There will be many ways to instantiate a simple puzzle perceiver.

  @todo   Create complete implementation with track filter.
  """

  #============================= __init__ ============================
  #
  def __init__(self, theParams=None, theDetector=None, theTracker=None, theFilter=None):
    """!
    @brief  Constructor for the simple puzzler parser. 

    @note   Lacks filter implementation.

    @param[in]  theParams       Perceiver parameters.
    @param[in]  theDetector     Detector instance.
    @param[in]  theTracker      Tracker instance.
    @param[in]  theFilter       Filter instance (puzzle piece data association).
        """

    super(boardPerceive, self).__init__(theParams, theDetector, theTracker, theFilter)

    self.board = Board()
    self.Mask  = None

  #============================= measure =============================
  #
  def measure(self, I, M=None):
    """!
    @brief Process data from mask layer and image.

    @param[in]  I   Puzzle image source.
    @param[in]  M   Puzzle template mask.
    """

    self.I = I
    self.Mask = M

    #--[1] Parse image and mask to get distinct candidate puzzle objects
    #      from it. Generates mask or revises existing mask.
    #
    # @note Is process the right thing to call. Why not measure? Is it
    #       because this is a perceiver? I think so. We are decoupling
    #       the individual steps in this implementation.
    if self.Mask is not None:
      self.detector.process(I, self.Mask)
    else:
      self.detector.process(I)

    detState = self.detector.getState()

    #DEBUG
    #display.binary_cv(detState.x)
    #display.wait_cv()

    #--[2] Parse detector output to reconstitute recognized puzzle
    #      pieces into a board.

    # Here detState.x is a mask
    self.tracker.process(I, detState.x)

    self.board = self.tracker.getState()

    if self.board.size() > 0:
      self.haveObs = True
      self.haveState = True
      self.haveRun = True

    else:
      self.haveState = False

  #============================== correct ==============================
  #
  def correct(self):
    """!
    @brief  Preserve temporal consistency of track labels via data association. 

    """

    if self.haveState and (self.filter is not None):
      self.filter.process(self.tracker.getState())
      # IAMHERE
      # @note   Not sure when stopped working on this code. - 09/17/2024 - PAV.
      #         The test script for this craps out.  Maybe not fully revised.



  #============================== process ==============================
  #
  def process(self, I, M=None):
    """
    @brief  Process the passed imagery.

    Args:
      I:  The puzzle image source.
      M:  The puzzle template mask.
    """

    self.predict()
    self.measure(I, M)
    self.correct()
    self.adapt()

    #======================== buildBasicPipelne ========================
    #
    @staticmethod
    def buildBasicPipeline():
      """
      @brief      Creates a simple puzzle parser employing a very basic
                  (practically trivial) processing pipeline for
      """

      # @note   IGNORE THIS MEMBER FUNCTION.  It belongs elsewhere but that
      # file is not yet created for fully known at this moment.
      #
      # @todo   Figure out where to place this static factory method so that
      # test and puzzle solver code is easy to implement. It is really a
      # wrapper for a data processing scheme that leads to a (I, LM)
      # pairing.  We may not need it in the end since other processes will
      # do the equivalent.

      # @note The preference over the above, for the moment is to create a
      # set of static methods here that perform simple image processing
      # operations to extract the mask.  Options include:
      #
      # imageToMask_Threshold
      # imageToMask_GrowSelection
      #
      # These should work for most of the basic images to be used for
      # testing purposes.
      #
      # If needed, some outer class can be made to automatically implement
      # these, then pass on the image and mask.  Otherwise, just rely on the
      # calling scope to properly implement.  Calling scope makes sense
      # since immediate anticipated use is for test scripts more so than
      # actual operation and final solution.
      #

      pass

#
#============================== puzzle.parser ==============================
