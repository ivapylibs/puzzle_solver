#========================== puzzle.parser.simple =========================
#
# @class    puzzle.parser.simple
#
# @brief    A simple parsing engine for recovering puzzle pieces from a
#           layer mask and an image. It's only job is to recover said
#           information from an image. No attempt is made to do anything
#           else, such as associate over time or anything like that.
#           For flexibility, this class is a perceiver. There will be
#           many ways to instantiate a simple parser.
#
#========================== puzzle.parser.simple =========================

#
# @file     simple.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/28 [created]
#           2021/08/01 [modified]
#
#========================== puzzle.parser.simple =========================

#============================== Dependencies =============================
#

# IMPORT WHAT? MOST LIKELY numpy, opencv
import perceiver.simple as perceiverSimple
from puzzle.board import board
#
#========================== puzzle.parser.simple =========================
#

class simple(perceiverSimple.simple):

  #=============================== simple ==============================
  #
  # @brief  Constructor for the simple puzzler parser. Lacks a filter.
  #
  def __init__(self, theDetector, theTracker, theParams = []):

    super(simple, self).__init__(theDetector, theTracker, [], theParams)
    self.board = board()
    self.Mask = []


  #============================== measure ==============================
  #
  # @brief      Process data from mask layer and image
  #
  # @param[in]  I   The puzzle image source.
  # @param[in]  LM  The puzzle template mask.
  #
  def measure(self, I, LM = []):

    self.I = I
    self.Mask = LM

    #--[1] Parse image and mask to get distinct candidate puzzle objects
    #      from it. Generates mask or revises existing mask.
    #
    # @note Is process the right thing to call. Why not measure? Is it
    #       because this is a perceiver? I think so. We are decoupling
    #       the individual steps in this implementation.
    if LM:
      self.detector.process(I, LM)
    else:
      self.detector.process(I)

    detState = self.detector.getState()

    #--[2] Parse detector output to reconstitute recognized puzzle
    #      pieces into a board.
    #
    self.tracker.process(I, detState.x)

    # @todo
    # Yunzhi:
    # 1. the state obtained in the tracker (centroid or centroidMulti)
    # (self.tpt = tpt (the center point of a segmented region) & self.haveMeas = haveMeas)
    # which is different from the board instance. Should we do something else?
    # 2. A typical process should be instantiating the puzzle pieces. That is
    # something already done by puzzle.builder.fromMask?
    # So what are we doing here? What is the difference?

    self.board = self.tracker.getState()

    #--[4] Copy locations to this perceiver.
    #
    # IS LINE BELOW EVEN CORRECT BASE ON CLASS?
    self.tpts = self.board.pieceLocations()
    if self.board.size() > 0:
      self.haveObs = True
      self.haveState = True
      self.haveRun = True
      # @note   Is this right? Review meanings and correct/confirm.


  #========================= buildBasicPipeline ========================
  #
  # @brief      Creates a simple puzzle parser employing a very basic
  #             (practically trivial) processing pipeline for 
  @staticmethod
  def buildBasicPipeline():

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
#========================== puzzle.parser.simple =========================
