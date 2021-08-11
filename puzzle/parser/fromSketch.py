# ======================== puzzle.parser.fromSketch ========================
#
# @class    puzzle.parser.fromSketch
#
# @brief    A derived detector class that can processe an image & mask image to create
#           a binary mask.
#
#           @ todo
#           Not fully developed yet.
#
#
# ======================== puzzle.parser.fromSketch ========================

#
# @file     fromSketch.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/10 [created]
#
# !NOTE:
# !  Indent is set to 2 spaces.
# !  Tab is set to 4 spaces with conversion to spaces.
#
# ======================== puzzle.parser.fromSketch ========================

# ==== Imports
#

import cv2
import numpy as np

from detector.inImage import inImage

# ==== Helper
#

#
# ======================== puzzle.parser.fromSketch ========================
#

class fromSketch(inImage):

  def __init__(self, processor=None):
    super(fromSketch, self).__init__(processor)

  def predict(self):
    pass

  def measure(self, I, LM = None):
    # We may still need some simple image processing at the very beginning
    if self.processor is not None:
      if LM is not None:
        # Preferred to work on the mask
        self.Ip = self.processor.apply(LM)
      else:
        self.Ip = self.processor.apply(I)


  def process(self, I, LM = None):
    self.predict()
    self.measure(I, LM)
    self.correct()
    self.adapt()



#
# ======================== puzzle.parser.fromSketch ========================
