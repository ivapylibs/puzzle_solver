#============================= puzzle.piece.matcher ============================
##
# @package  puzzle.pieces.matcher
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
from puzzle.piece import Template

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

    #============================ pcaFrame =============================
    #
    @staticmethod
    def pcaFrame(piece) -> tuple[np.ndarray, np.ndarray]:
        """!
        @brief  Estimate a signed PCA frame from a puzzle piece's foreground pixels.

        @param[in] piece  Template puzzle piece.

        @return ``(center, frame)`` where ``center`` is the global pixel centroid
                and ``frame`` is a 2x2 right-handed rotation matrix whose first
                column is the major PCA axis.
        """
        if not isinstance(piece, Template):
            raise TypeError("piece must be a puzzle.piece.Template instance.")

        local_points = np.asarray(piece.y.rcoords, dtype=np.float64).T
        if local_points.ndim != 2 or local_points.shape[1] != 2 or len(local_points) < 3:
            raise ValueError("piece must contain at least three foreground pixel coordinates.")

        points       = local_points + np.asarray(piece.rLoc, dtype=np.float64)
        center       = points.mean(axis=0)
        centered     = points - center
        covariance   = centered.T @ centered / len(centered)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)

        if eigenvalues[-1] <= np.finfo(float).eps:
            raise ValueError("Cannot estimate a PCA frame from a degenerate puzzle piece.")

        major_axis = eigenvectors[:, np.argmax(eigenvalues)]

        # Eigenvectors are sign-ambiguous.  Give the major axis a repeatable
        # direction using the shape's third moment; fall back to its dominant
        # coordinate for shapes whose third moment is symmetric.  Perfectly
        # symmetric shapes retain an unavoidable 180-degree ambiguity.
        projections = centered @ major_axis
        skewness = float(np.mean(projections ** 3))
        if abs(skewness) > np.finfo(float).eps:
            if skewness < 0:
                major_axis *= -1
        else:
            dominant_coordinate = int(np.argmax(np.abs(major_axis)))
            if major_axis[dominant_coordinate] < 0:
                major_axis *= -1

        minor_axis = np.array([-major_axis[1], major_axis[0]])
        return center, np.column_stack((major_axis, minor_axis))

    #========================= estimateAffineMatch ======================
    #
    def estimateAffineMatch(self, piece_A, piece_B) -> tuple[float, np.ndarray]:
        """!
        @brief  Estimate the rigid affine transform that aligns piece A to piece B.

        The transform maps global pixel coordinates from @p piece_A into the
        global coordinate frame of @p piece_B.  Its rotation is determined by
        their signed PCA frames and its translation maps the A centroid onto
        the B centroid.

        @return ``(rotation_degrees, affine)`` where ``affine`` is a 3x3
                homogeneous rigid transform.
        """
        center_A, frame_A = self.pcaFrame(piece_A)
        center_B, frame_B = self.pcaFrame(piece_B)

        rotation = frame_B @ frame_A.T
        translation = center_B - rotation @ center_A
        affine = np.eye(3, dtype=np.float64)
        affine[:2, :2] = rotation
        affine[:2, 2] = translation

        rotation_degrees = float(np.rad2deg(np.arctan2(rotation[1, 0], rotation[0, 0])))
        return rotation_degrees, affine


    #------------------------------------------------------------------
    # Fitting (vocabulary discovery + database encoding)
    #------------------------------------------------------------------

    #======================= fitFromImageSegmented =======================
    #
    def fitFromImageSegmented(self, Irgb, Iseg, hasLabs=False) -> "Matcher":
        """!
        @brief  Given an image and a segmentation, generate fit.

        This base class does nothing. Overload as fitting.

        Permits fitting based on two images, one with all objects of interest
        in it as a color image and the second a segmentation isolating the objects.
        It should be considered binary in nature, then no labels assumed.  If it
        has labels (each unique value is the label), then snag from Iseg as labels.

        @param[in]  Irgb    Source color image.
        @param[in]  Iseg    Binary segmentation of image, or label segmentation.
        @param[in]  hasLabs Iseg has labels and is interpreted as binary. Default: False.
        """

        return self


    #================================= fit ===============================
    #
    def fit(self, groups, labels: list[str] | None = None,) -> "Matcher":
        """!
        @brief Given raw data regarding expected element instances, identify
               model to differentiate them if possible for this matcher type.

        This base class does nothing. Overload as fitting.

        @param groups  List of (3, N) RGB matrices forming the database.
        @param labels  Optional list of human-readable names, one per group.
                       Auto-generated as "group_0", "group_1", ... if None.

        @return Self, to allow method chaining (e.g., matcher.fit(groups).query(q)).
        """

        return self

    #------------------------------------------------------------------
    # Feature Extraction and Comparison
    #------------------------------------------------------------------

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

    #======================== solveMatchedPuzzle =======================
    #
    def solveMatchedPuzzle(self, puzzle, sol):

      puzIDs = [puzzle.pieces[i].id for i in range(puzzle.size())]
      puzKey = range(puzzle.size())
      puzMap = dict(zip(puzIDs, puzKey))

      solIDs = [sol.pieces[i].id for i in range(sol.size())]
      solKey = range(sol.size())
      solMap = dict(zip(solIDs, solKey))

      for pi in puzKey:
        si = solMap[puzzle.pieces[pi].id]
        puzzle.pieces[pi].setPlacement(sol.pieces[si].rLoc)


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
