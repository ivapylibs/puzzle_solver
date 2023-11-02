#======================= puzzle.piece.matchDifferent =======================
#
# @brief    Sub-classes of this derived class branch use difference
#           scores for determining whether two puzzle pieces match.
#
# Difference scores are interpreted as smaller being more likely to be a
# match and bigger being less likely to be a match. There will usually
# be lower and upper limits for the difference score.
#
#======================= puzzle.piece.matchDifferent =======================

# @file     matchDifferent.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/24 [created]
#           2021/07/30 [modified]
#
#
#======================= puzzle.piece.matchDifferent =======================

#====== Environment / Dependencies
#
import numpy as np
import cv2
import math
from puzzle.pieces.matcher import MatchDifferent
from puzzle.pieces.matcher import CfgDifferent
from puzzle.piece import Template



#
#---------------------------------------------------------------------------
#================================= Distance ================================
#---------------------------------------------------------------------------
#

#------------------------------ CfgDistance ------------------------------
#

class CfgDistance(CfgDifferent):
  '''!
  @brief  Configuration setting specifier for distance matcher class.
  '''

  #============================= __init__ ============================
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief      Constructor of different matcher configuration instance.
  
    @param[in]  init_dict   Dictionary to use that expands default one. Usually not given.
    @param[in]  key_list    Unsure.
    @param[in]  new_allowed Are new entries allowed. Default is yes.
    '''
    if (init_dict == None):
      init_dict = CfgDistance.get_default_settings()

    super().__init__(init_dict, key_list, new_allowed)


  #========================= get_default_settings ========================
  #
  # @brief    Recover the default settings in a dictionary.
  #
  @staticmethod
  def get_default_settings():
    '''!
    @brief  Defines default configuration parameter for distance matcher class.

    @param[out] default_dict  Dictionary populated with minimal set of
                              default settings.
    '''
    default_dict = CfgDifferent().get_default_settings()
    default_dict.update( dict( tau = 35) )      # What is this about?? Why this value?
    return default_dict



#-------------------------------- Distance -------------------------------
#

class Distance(MatchDifferent):

  #============================= __init__ ============================
  #
  def __init__(self, theParams = CfgDistance()):
    """!
    @brief  Constructor for the puzzle piece histogram class.

    @param[in]  tau     Threshold param to determine difference.
    """
    super(Distance, self).__init__(theParams)

  #========================== extractFeature =========================
  #
  # @todo   Should it really be a static method? Might there ever be a need for configuration
  #         specifications that would dictate being a member function???
  # @todo   0203/11/02 PAV - Yes!  When the feature extraction process has variable
  #             parameters.  Almost always the case for non-trivial features.
  #             Modifying code to reflect as much. Remove this todo once the modifications
  #             are done, the code works, and the documentation supports this understanding.
  #
  def extractFeature(self, piece):
    """
    @brief Get the puzzle centroid value.

    @param[in]  piece   Puzzle piece to use.

    @param[out]  Centroid "feature" vector.
    """

    if issubclass(type(piece), Template):
      return piece.rLoc
    else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')


  #========================== buildFromConfig ==========================
  #
  @staticmethod
  def buildFromConfig(matchConfig):

    matcher = Distance(matchConfig)
    return matcher


#
#---------------------------------------------------------------------------
#================================ Histogram ================================
#---------------------------------------------------------------------------
#

class CfgHistogramCV(CfgDifferent):
  '''!
  @brief  Configuration setting specifier for Histogram puzzle comparator class.
  '''

  #============================= __init__ ============================
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief        Constructor of configuration instance.
  
    @param[in]    cfg_files   List of config files to load to merge settings.
    '''
    if (init_dict == None):
      init_dict = CfgHistogramCV.get_default_settings()

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
    default_dict = CfgDifferent.get_default_settings()
    default_dict.update( dict( tau = 0.3 , colorSpace = 'toHSV', bins = [36, 32], \
                                                                 ranges = [0, 180, 0, 256]) )
    return default_dict

  #============================ build_for_RGB ============================
  #
  # @brief    Recover the default settings in a dictionary.
  #
  @staticmethod
  def build_for_RGB():
    '''!
    @brief  Defines canned settings for RGB histogram matching. Prioritizes a bit efficiency
            over accuracy.  16 bins per channel = 4096 bins, if using Cartesian product and not
            separating coordinate-wise, in which case it would be 48 bins.

    @param[out] theParams   Default parameters instance for RGB case.
    '''

    theParams = CfgHistogramCV()
    default_dict = dict( tau = 0.3 , colorSpace = 'RGB', bins = [16, 16, 16],\
                         range = [0, 256, 0, 256, 0, 256]) 
    theParams.merge(default_dict)   # @todo Untested.
    return default_dict

#
#-------------------------------- Histogram --------------------------------
#

class HistogramCV(MatchDifferent):

  #============================= __init__ ============================
  #
  def __init__(self, theParams=CfgHistogramCV()):
    """
    @brief  Constructor for the puzzle piece histogram class.

    @param[in]  tau     Threshold param to determine difference.
    """

    super(HistogramCV, self).__init__(theParams)

  #========================== extractFeature =========================
  #
  def extractFeature(self, piece): 
    """
    @brief Compute histogram from the raw puzzle data.
           See https://opencv-tutorial.readthedocs.io/en/latest/histogram/histogram.html

    @param[in]  piece   Puzzle piece to use.

    @param[out] Puzzle piece histogram.
    """

    if not issubclass(type(piece), Template):
    #  if len(piece.y.colorFea) > 0:
    #    return piece.y.colorFea
    #else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

    #DEBUG
    #cv2.imshow('demo', piece.y.mask)
    #cv2.waitKey()

    # Convert to HSV space for comparison, see https://theailearner.com/tag/cv2-comparehist/
    if (self.params.colorSpace == 'toHSV'):
      img_hsv = cv2.cvtColor(piece.y.image.astype('uint8'), cv2.COLOR_RGB2HSV)
      hist = cv2.calcHist([img_hsv], [0, 1], piece.y.mask, self.params.bins,\
                                                           self.params.ranges) 
      cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
      # @todo   Why is MINMAX the one to choose.  Seems weird.  I think this may affect
      #         how Bhattacharya works and converts it to a difference type.  Normally
      #         Bhattacharya is a similarity score, not a difference score.  what is up?
    
    return hist
    #@todo   Remove because not applicable.
    #piece.y.colorFea = hist

  #============================== score ==============================
  #
  def score(self, piece_A, piece_B):
    """
    @brief Compute the score between two passed puzzle piece data.

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] Distance of the feature vectors. (Overload if not proper).
    """

    hist_A = piece_A.getFeature(self)
    hist_B = piece_B.getFeature(self) 

    # Range from 0-1, smaller means closer
    theScore =  cv2.compareHist(hist_A, hist_B, cv2.HISTCMP_BHATTACHARYYA)
    return theScore

#
#---------------------------------------------------------------------------
#================================= Moments =================================
#---------------------------------------------------------------------------
#

class CfgMoments(CfgDifferent):
  '''!
  @brief  Configuration setting specifier for Moments class.
  '''

  #============================= __init__ ============================
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief        Constructor of configuration instance.
  
    @param[in]    cfg_files   List of config files to load to merge settings.
    '''
    if (init_dict == None):
      init_dict = CfgMoments.get_default_settings()

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
    default_dict = dict(num = 20)

    return default_dict




class Moments(MatchDifferent):
  """! 
  @brief    Uses shape moments to establish similarity.
  """

  #============================= __init__ ============================
  #
  def __init__(self, tau=5):
    """
    @brief  Constructor for the puzzle piece moments class.

    @param[in]  tau     Threshold param to determine difference.
    """

    super(Moments, self).__init__(tau)

  #========================== extractFeature =========================
  #
  def extractFeature(self, piece):
    """
    @brief  Compute moments from the raw puzzle data.


    See https://learnopencv.com/shape-matching-using-hu-moments-c-python/

    @param[in]  piece   Puzzle piece to use.

    @param[out]  huMoments: A list of huMoments value.
    """

    if issubclass(type(piece), Template):
      if len(piece.y.shapeFea) > 0:
        return piece.y.shapeFea
    else:
      raise ('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

    moments = cv2.moments(piece.y.contour)
    huMoments = cv2.HuMoments(moments)
    for i in range(7):
      huMoments[i] = -1 * math.copysign(1.0, huMoments[i]) * math.log10(1e-06 + abs(huMoments[i]))

    piece.y.shapeFea = huMoments
    return huMoments

  #============================== score ==============================
  #
  def score(self, piece_A, piece_B):
    """
    @brief Compute the score between two passed puzzle piece data.

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] Distance of the feature vectors. (Overload if not proper).
    """

    huMoments_A = piece_A.getFeature(self)
    huMoments_B = piece_B.getFeature(self)

    distance = np.sum(np.abs(huMoments_B - huMoments_A))

    return distance

#
#---------------------------------------------------------------------------
#=================================== PCA ===================================
#---------------------------------------------------------------------------
#
class PCA(MatchDifferent):
  """!
  @brief    Uses pca to calculate rotation.

  WHAT IS GOING ON HERE???  WHAT IS THE POINT OF THIS PARTICULAR MATCHER??
  """

  #============================= __init__ ============================
  #
  def __init__(self, tau=-float('inf')):
    """!
    @brief  Constructor for the puzzle piece histogram class.

    @param[in]  tau     Threshold param to determine difference.
    """
    super(PCA, self).__init__(tau)

  #========================== extractFeature =========================
  #
  def extractFeature(self, piece):
    """
    @brief Get the puzzle centroid value.

    @param[in]  piece   Puzzle piece to use.

    @param[out]  The rotation of the main vector.
    """
    if issubclass(type(piece), Template):
      yfeature = PCA.getEig(piece.y.contour)
      theta = np.arctan2(yfeature['v1'][1], yfeature['v1'][0])

      return theta
    else:
      raise TypeError('Input type is wrong. Need template instance or puzzleTemplate instance.')

  #============================== score ==============================
  #
  def score(self, piece_A, piece_B):
    """
    @brief Compute the score between two passed puzzle piece data.

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] The degree distance between passed puzzle piece data and stored puzzle piece. (counter-clockwise)
    """

    theta_A = piece_A.getFeature(self)
    theta_B = piece_B.getFeature(self) 

    return np.rad2deg(theta_B - theta_A)

  #=============================== getEig ==============================
  #
  @staticmethod
  def getEig(img):
    """
    @brief  To find the major and minor axes of a blob.


    See https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/ for details.

    Args: img: A mask image.

    Returns: dict: A dict saving centerized points, main vectors.
    """
    y, x = np.nonzero(img)
    x = x - np.mean(x)
    y = y - np.mean(y)
    coords = np.vstack([x, y])
    cov = np.cov(coords)
    evals, evecs = np.linalg.eig(cov)
    sort_indices = np.argsort(evals)[::-1]
    v1 = evecs[:, sort_indices[0]]  # Eigenvector with largest eigenvalue
    v2 = evecs[:, sort_indices[1]]

    dict = {
            'x': x,
            'y': y,
            'v1': v1,
            'v2': v2,
        }

    return dict

#
#======================= puzzle.piece.matchDifferent =======================
