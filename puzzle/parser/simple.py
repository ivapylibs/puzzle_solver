#========================== puzzle.parser.simple =========================
#
# @class    puzzle.parser.simple
#
# @brief    A simple parsing engine for recovering puzzle pieces from a
#           layer mask and an image. It's only job is to recover said
#           information from an image. No attempt is made to do anything
#           else, such as associate over time or anything like that.
#
#========================== puzzle.parser.simple =========================

#
# @file     simple.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   WHO ELSE?
# @date     2021/07/28  [created]
#
#========================== puzzle.parser.simple =========================

#============================== Dependencies =============================
#

# IMPORT WHAT? MOST LIKELY numpy, opencv

#
#========================== puzzle.parser.simple =========================
#

class simple(perceiver.simple):

  #=============================== simple ==============================
  #
  # @brief  Constructor for the simple puzzler parser. Lacks a filter.
  #
  def __init__(self, theDetector, theTracker, theParams = [])

    __init__(super,perceiver.simple)(theDetector, theTracker, [], theParams)
    self.board = puzzle.board()


  #============================== measure ==============================
  #
  # @brief      Process data from mask layer and image
  #
  def measure(self, I, LM)

    #--[1] Parse mask to get distinct objects from it.  Query image to
    #       get appearance information from the objects.


    #--[2] Package all of the information into individual puzzle pieces.
    #


    #--[3] Instantiate a puzzle board for the pieces.
    #


    #--[4] Copy locations to this perceiver.
    #
    self.tpts = self.board.pieceLocations()
    if self.board.size() > 0:
      self.haveObs = true
      self.haveState = true
      self.haveRun = true
      # @note   Is this right? Review meanings and correct/confirm.


  #========================= buildBasicPipeline ========================
  #
  # @brief      Creates a simple puzzle parser employing a very basic
  #             (practically trivial) processing pipeline for 
  @staticmethod
  def buildBasicPipeline:

  # @note   IGNORE THIS MEMBER FUNCTION.  It belongs elsewhere but that
  # file is not yet created for fully known at this moment.
  #
  # @todo   Figure out where to place this static factory method so that
  # test and puzzle solver code is easy to implement. It is really a
  # wrapper for a data processing scheme that leads to a (I, LM)
  # pairing.  We may not need it in the end since other processes will
  # do the equivalent.

    
#
#========================== puzzle.parser.simple =========================
