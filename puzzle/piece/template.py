#========================= puzzle.piece.template =========================
#
# @brief    The base class for puzzle piece specification or description
#           encapsulation. This simply stores the template image and
#           related data for a puzzle piece in its canonical
#           orientation.
#
#========================= puzzle.piece.template =========================

#
# @file     template.m
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @date     2021/07/24
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================= puzzle.piece.template =========================

#============================= Dependencies ==============================

import numpy as np
from dataclasses import dataclass

#=========================== Helper Components ===========================

@dataclass
class puzzleTemplate:
  icoords: list[int]    # @< Linear index coordinates.
  rcoords: np.ndarray   # @< Puzzle piece linear image coordinates 
  rcolors: np.ndarray   # @< Puzzle piece linear color/appearance 
  image: np.ndarray     # @< Template image with BG default fill.


#
#========================= puzzle.piece.template =========================
#

class template:

  #================================ base ===============================
  #
  # @brief  Constructor for the puzzle.piece.base class.
  #
  def __init__(self, y = [], r = [], p = []):
    self.y = y          # @< The puzzle piece template source data, if given.
    self.rLoc = r       # @< The puzzle piece location in pixels, if given.
    self.pLoc = p       # @< The puzzle piece discrete grid piece coordinates.

    # @note     Excluding orientation for now. Can add later.

  #============================== setSource ============================
  #
  # @brief  Pass along the source data describing the puzzle piece.
  #
  def setSource(self, y, r):
    self.y = y

  #============================ setPlacement ===========================
  #
  # @brief  Provide pixel placement location information.
  #
  def setPlacement(self, r, p = []):
    self.r = r
    self.p = p

  #============================ placeInImage ===========================
  #
  # @brief  Insert the puzzle piece into the image at the given location.
  #         
  # @param[in]  theImage    The source image to put puzzle piece into.
  # @param[in]  rc          The coordinate location
  # @param[in]  theta       The orientation of the puzzle piece (default = 0)
  #
  def placeInImage(self, theImage, rc, theta = 0)

    # FOR NOW JUST PROGRAM WITHOUT ORIENTATION CHANGE. LATER, INCLUDE THAT
    # OPTION.  IT WILL BE A LITTLE MORE INVOLVED.

    pass    # REPLACE WITH ACTUAL CODE.

  #============================== display ==============================
  #
  # @brief  Display the puzzle piece contents.
  #
  def display(self):
    pass
    # Need to figure this out.  Should a figure label/handler be given?
    # If not given, then create a new handle, display data and
    # return the handle?
    # Sounds reasonable.
    # What about some kind of display plot scaling parameter?
    
    # Should the template class have an optional parms structure that
    # indicates how much to scale, with default value of 2 or 3x
    # upscaling?  How does matplotlibs plot things? Can the plot be
    # opened in such a way that it is not native resolution?
    # I think so. We want outcome like in Matlab where small things are
    # still plotted reasonably large for easy visualization.

#
#========================= puzzle.piece.template =========================
