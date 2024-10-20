#============================= puzzle.piece.matcher ============================
##
# @package  PuzzlePieceMatcher
#
# @brief    Classes for comparing puzzle pieces in support of puzzle solving and
#           puzzle piece association.  The base-type class and most of its member
#           functions will do nothing. They require overloading.  The ones that 
#           don't should be for some generic functionality.
#
# Sub-classes of this derived class branch use difference or similarity scores
# for determining whether two puzzle pieces match.  Difference scores are
# interpreted as smaller values being more likely to be a match and bigger
# being less likely to be a match.  Similarity scores are interpreted as
# bigger value being more likely to be a match and smaller being less likely
# to be a match.
#
# @ingroup  Puzzle_Tracking
#
# @author   Patricio A. Vela,       pvela@gatech.edu
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#
# @date     2024/10/20 [merged from Perceiver branch, updating documentation]
# @date     2021/07/31 [modified]
# @date     2021/07/25 [created]
#


#============================= puzzle.piece.matcher ============================
#
# NOTE
#   Using 2 space indents. 84+ column width viewing.
#
#============================= puzzle.piece.matcher ============================

#====== Environment / Dependencies
#
# from puzzle.piece.template import template

import numpy as np
from detector.Configuration import AlgConfig

#
#---------------------------------------------------------------------------
#================================= Matcher =================================
#---------------------------------------------------------------------------
#

#
#-------------------------------- CfgMatcher -------------------------------
#

class CfgMatcher(AlgConfig):
  '''!
  @ingroup  Puzzle_Tracking
  @brief  Configuration setting specifier for puzzle piece matcher class.
  '''

  #============================= __init__ ============================
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief      Constructor of configuration instance.
  
    @param[in]  init_dict   Dictionary to use that expands default one. Usually not given.
    @param[in]  key_list    Unsure.
    @param[in]  new_allowed Are new entries allowed. Default is yes.
    '''
    if (init_dict == None):
      init_dict = CfgMatcher.get_default_settings()

    super().__init__(init_dict, key_list, new_allowed)


  #========================= get_default_settings ========================
  #
  # @brief    Return the default settings for this configuration class.
  #
  # @param[out] default_dict    The default settings dictionary.
  #
  @staticmethod
  def get_default_settings():
    '''!
    @brief  Defines default configuration parameter for Matcher class.

    @param[out] default_dict  Dictionary populated with minimal set of
                              default settings.
    '''
    default_dict = dict( tau = None ) 
    return default_dict


#
#--------------------------------- Matcher ---------------------------------
#

class Matcher:
  """!
  @ingroup  Puzzle_Tracking
  @brief    Generic puzzle piece matching class.  Actual instances should use
            similarity of difference matching sub-classes.
  """

    #============================== __init__ =============================
    #
    def __init__(self, theParams=CfgMatcher): 
        """!
        @brief  Constructor for the matcher class.

        @param[in]  theParams   The matcher configuration (optional).
        """

        self.params = theParams  # @< Parameters to use when building and comparing features.


    #=========================== extractFeature ==========================
    #
    def extractFeature(self, piece):
        """!
        @brief  Process raw puzzle piece data to obtain encoded description of piece. 
                Use to recognize/associate the piece given new measurements.
                This member function should be overloaded.

        @param[in]  piece   Template instance saving a piece's info.

        @param[out] featVec The "feature" vector.
        """
        raise NotImplementedError

    #============================== score ==============================
    #
    def score(self, piece_A, piece_B):
        """!
        @brief Compute the score between two passed puzzle piece data.

        @param[in] piece_A      Template instance saving a piece's info.
        @param[in] piece_B      Template instance saving a piece's info.

        @param[out] Distance of the feature vectors. (Overload if not proper).
        """

        cent_A = piece_A.getFeature(self) 
        cent_B = piece_B.getFeature(self)

        return np.linalg.norm(cent_A - cent_B)

    #============================= compare =============================
    #
    def compare(self, piece_A, piece_B):
        """!
        @brief  Compare between two passed puzzle piece data.
                This member function should be overloaded. 

        @param[in]  piece_A     Puzzle piece A instance.
        @param[in]  piece_B     Puzzle piece B instance.

        @param[out] Outcome of matching classification, when function overloaded.
        """

        raise NotImplementedError

#
#---------------------------------------------------------------------------
#============================== MatchDifferent =============================
#---------------------------------------------------------------------------
#

#
#------------------------------- CfgDifferent ------------------------------
#

class CfgDifferent(CfgMatcher):
  """!
  @ingroup  Puzzle_Tracking
  @brief  Configuration setting specifier for difference matcher class.
  """

  #============================= __init__ ============================
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    """!
    @brief      Constructor of different matcher configuration instance.
  
    @param[in]  init_dict   Dictionary to use that expands default one. Usually not given.
    @param[in]  key_list    Unsure.
    @param[in]  new_allowed Are new entries allowed. Default is yes.
    """
    if (init_dict == None):
      init_dict = CfgDifferent.get_default_settings()

    super().__init__(init_dict, key_list, new_allowed)


  #========================= get_default_settings ========================
  #
  # @brief    Recover the default settings in a dictionary.
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Defines default configuration parameter for difference matcher class.

    @param[out] default_dict  Dictionary populated with minimal set of
                              default settings.
    """
    default_dict = CfgMatcher.get_default_settings()
    default_dict.update(dict( tau = float('inf') ))
    return default_dict

#
#------------------------------ MatchDifferent -----------------------------
#

class MatchDifferent(Matcher):
    """!
    @ingroup  Puzzle_Tracking
    @brief  The puzzle piece matching scores are based on differences. Lower is better.
    """

    #============================= __init__ ============================
    #
    def __init__(self, theParams=CfgDifferent()):
        """!
        @brief  Constructor for the difference matcher class.

        @param[in]  theParams   The matcher configuration (optional).
        """
        super(MatchDifferent, self).__init__(theParams)


    #============================= compare =============================
    #
    def compare(self, piece_A, piece_B):
        """!
        @brief Compare two puzzle pieces.

        @param[in]  piece_A     First puzzle piece.
        @param[in]  piece_B     Second puzzle piece.

        @param[out] Binary indicator of similarity = not different (True = similar).
        """

        # Score function call is to calculate the difference, which will call the feature 
        # extraction process internally.
        diffScore = self.score(piece_A, piece_B)

        return diffScore < self.params.tau

#
#---------------------------------------------------------------------------
#======================== puzzle.piece.matchSimilar ========================
#---------------------------------------------------------------------------
#

#
#-------------------------------- CfgSimilar -------------------------------
#

class CfgSimilar(CfgMatcher):
  '''!
  @ingroup  Puzzle_Tracking
  @brief  Configuration setting specifier for similar matcher class.
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
      init_dict = CfgSimilar.get_default_settings()

    super().__init__(init_dict, key_list, new_allowed)


  #========================= get_default_settings ========================
  #
  # @brief    Recover the default settings in a dictionary.
  #
  @staticmethod
  def get_default_settings():
    '''!
    @brief  Defines default configuration parameter for similarity matcher class.

    @param[out] default_dict  Dictionary populated with minimal set of
                              default settings.
    '''
    default_dict = CfgMatcher.get_default_settings()
    default_dict.update(dict( tau = float(0.0) )) 
    return default_dict

#
#------------------------------- MatchSimilar ------------------------------
#

class MatchSimilar(Matcher):
  """!
  @ingroup  Puzzle_Tracking
  @brief    Similarity matching.
  """

    #============================= __init__ ============================
    #
    def __init__(self, theParams = CfgSimilar()):
        """
        @brief  Constructor for the puzzle piece matchSimilar class.

        @param[in]  tau     Threshold param to determine similarity.
        """

        super(MatchSimilar, self).__init__(theParams)

    #============================= compare =============================
    #
    def compare(self, piece_A, piece_B):
        """
        @brief  Compare between two passed puzzle piece data.

        @param[in]  piece_A     First puzzle piece.
        @param[in]  piece_B     Second puzzle piece.

        @param[out] Binary indicator of similarity (True = similar).
        """

        # Score function call is to calculate the similarity, which will call the feature 
        # extraction process internally.
        simScore = self.score(piece_A, piece_B)

        return simScore > self.params.tau


#
#========================== puzzle.piece.matcher =========================
