#======================== puzzle.parser.fromSketch ========================
##
# @package  puzzle.parser.fromSketch
# @brief    A derived detector class that can process an image & mask
#           image to create a binary mask.
#
# @todo     Not fully developed yet.
#
# @ingroup  PuzzleSolver
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#
# @date     2021/08/10 [created]
#

#======================== puzzle.parser.fromSketch ========================
#
#
#======================== puzzle.parser.fromSketch ========================

# ===== Environment / Dependencies
#

from detector.inImage import inImage


# ===== Helper Elements
#

#
# ======================== puzzle.parser.fromSketch ========================
#

class FromSketch(inImage):
    """!
    @ingroup PuzzleSolver
    @brief   What is FromSketch??
    """

    def __init__(self, processor=None):
        super(FromSketch, self).__init__(processor)

    def predict(self):
        pass

    def measure(self, I, M=None):
        """!
        @brief Process the passed imagery to get the mask.

        Args:
            I:  RGB image.
            M:  Mask image.
        """

        # We may still need some simple image processing at the very beginning
        if self.processor is not None:
            if M is not None:
                # Preferred to work on the mask
                self.Ip = self.processor.apply(M)
            else:
                self.Ip = self.processor.apply(I)

    def process(self, I, M=None):
        """!
        @brief Process the passed imagery.

        Args:
            I:  RGB image.
            M:  Mask image.
        """

        self.predict()
        self.measure(I, M)
        self.correct()
        self.adapt()

#
#======================== puzzle.parser.fromSketch ========================
