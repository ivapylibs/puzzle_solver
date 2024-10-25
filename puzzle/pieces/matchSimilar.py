#========================== puzzle.piece.matchSimilar ==========================
##
# @package  puzzle.pieces.matchSimilar
# @brief    Sub-classes of this derived class branch use similarity
#           scores for determining wheter two puzzle pieces match.
#
# Similarity scores are interpreted as bigger being more likely to be a
# match and smaller being less likely to be a match. There will usually
# be lower and upper limits for the similarity score.
#
# @ingroup  Puzzle_Tracking
#
#
# @file     matchSimilar.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
#
# @date     2021/07/24 [created]
#           2023/11/03 [modified]
#
#

#========================== puzzle.piece.matchSimilar ==========================
#
# NOTE
#   indent is 2 spaces.  column width is 100 due to wide comments.
#
#========================== puzzle.piece.matchSimilar ==========================

#===== Environment / Dependencies
#
# Tricks to pickle cv2.keypoint objects https://stackoverflow.com/a/48832618/5269146
# @note Appears to be unused here but may be used externally.
import copyreg

#-- Standard numerical and image processing imports.
import cv2
import numpy as np
from skimage.measure    import ransac               # Not used. Commented and to be deleted.
from skimage.transform  import AffineTransform      # Will be deleted or moved at some point.

#-- Puzzle processing imports.
from puzzle.pieces.matcher   import CfgSimilar, MatchSimilar
from puzzle.piece  import Template
from puzzle.utils.dataProcessing    import calculateMatches

import ivapy.display_cv as display


#
#---------------------------------------------------------------------------
#=================================== SIFT ==================================
#---------------------------------------------------------------------------

def _pickle_keypoints(point):
    return cv2.KeyPoint, (*point.pt, point.size, point.angle,
                          point.response, point.octave, point.class_id)

copyreg.pickle(cv2.KeyPoint().__class__, _pickle_keypoints)

#
#-------------------------------- CfgSIFTCV --------------------------------
#

class CfgSIFTCV(CfgSimilar):
  '''!
  @ingroup  Puzzle_Tracking
  @brief  Configuration setting specifier for OpenCV SIFT matcher class.
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
      init_dict = CfgSIFTCV.get_default_settings()

    super().__init__(init_dict, key_list, new_allowed)


  #========================= get_default_settings ========================
  #
  # @brief    Recover the default settings in a dictionary.
  #
  # Parameters are:
  # tau             Threshold to determine similarity for SIFT feature.
  # slambda         Proximity scaling factor, relative to second closest, used to identify matches (0-1).
  #
  # custSettings    Flag indicating whether to use custom SIFT parameter settings or not.
  # custParams      Dictionary consisting of the revised settings (initially set to SIFT defaults).
  #
  # detKP       Flag indicating the detection of keypoints should be performed.
  # useKP       If detKP flag is false, then use these keypoint offsets relative to center.
  #
  # @todo   useKP not yet implemented.  Want to get basic version coded first, then add options.
  #
  @staticmethod
  def get_default_settings():
    '''!
    @brief  Defines default configuration parameter for similarity matcher class.

    @param[out] default_dict  Dictionary populated with minimal set of
                              default settings.
    '''
    default_dict = CfgSimilar.get_default_settings()
    default_dict.update(dict(tau = float(15.0) , slambda = 0.6 , custSettings = False,
                custParams = dict(nfeatures = 0, nOctaveLayers = 3, 
                                tauContrast = 0.04, tauEdge = 10, sigma = 1.6),
                detKP = True, useKP = None) ) 

    return default_dict


#
#---------------------------------- SIFTCV ---------------------------------
#

class SIFTCV(MatchSimilar):
  """!
  @ingroup  Puzzle_Tracking
  @brief    Uses sift features to establish similarity.
  """

  #================================ __init__ ===============================
  #
  def __init__(self, theParams=CfgSIFTCV()): #, tau=10, theThreshMatch=0.5):
    """!
    @brief  Constructor for the puzzle piece sift class.

    """
    super(SIFTCV, self).__init__(theParams)

  #============================= extractFeature ============================
  #
  def extractFeature(self, piece):
    """!
    @brief  Compute SIFT features from the raw puzzle data.

    This function just extracts the SIFT features from the piece information.
    The calling scope needs to deal with the feature storage and matching part.

    @param[in]  piece   Puzzle piece to use.

    @return     (kp, des)   Image patch keypoints and SIFT descriptors.
    """

    #if issubclass(type(piece), Template):
    #  if piece.y.kpFea:
    #    return piece.y.kpFea
    #else:
    if not issubclass(type(piece), Template):
      raise ('The input type is wrong. Need a template instance.')

    # https://stackoverflow.com/questions/60065707/cant-use-sift-in-python-opencv-v4-20
    # For opencv-python
    if self.params.custSettings:
      sift_builder = cv2.SIFT_create(self.params.customParams.nfeatures,
                                     self.params.customParams.nOctaveLayers,
                                     self.params.customParams.tauContrast,
                                     self.params.customParams.tauEdge,
                                     self.params.customParams.sigma)
    else:
      sift_builder = cv2.SIFT_create()

    # Focus on the puzzle piece image with mask. Code below reconstitutes the puzzle piece
    # visual information with zeros in the background region.  
    #
    # @note Why is the masked image not stored upon creation of puzzle piece template?
    #
    theImage = np.zeros_like(piece.y.image)
    theImage[piece.y.rcoords[1], piece.y.rcoords[0], :] = piece.y.appear

    # VISUAL DEBUG
    #display.rgb(theImage)
    #display.wait();

    if self.params.detKP:
      kp, des = sift_builder.detectAndCompute(theImage, None)
      theFeat = (kp, des)
    else:
      # @todo   Need to provide scheme for keypoints.  This might be a bad idea since
      #         the rotation is unknown.  The keypoints would have to have some kind
      #         of rotational symmetry, which makes things harder.  The alternative is
      #         to use a single keypoint at the center spanning multiple octaves. Is that
      #         what SIFT does anyhow?  Need to review.
      # @note   Per https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html,
      #         > Each keypoint is a special structure which has many attributes like its (x,y)
      #         > coordinates, size of the meaningful neighbourhood, angle which specifies its
      #         > orientation, response that specifies strength of keypoints etc.
      #         If we knew how to control, these could be preset as needed.  Rotation is one
      #         issue.  We'd have to identify some global way to define the rotation from the
      #         visual content of the puzzle piece using some kind of consistent scheme that is
      #         relatively robust to lighting. Can't use geometry due to discrete rotation symmetry.
      #         What are the options here?
      #
      #         Or should SIFT be used only when it makes sense?  Would need to test each piece
      #         in the calibration phase.
      #
      #theKP = piece.center + self.params.useKP
      #theFeat = sift_builder.Compute(theImage, theKP)
      Warning("detKP is set to False.  The option is not coded out yet.")
      pass

    return theFeat

  #============================== score ==============================
  #
  def score(self, piece_A, piece_B):
    """!
    @brief Compute the score between two passed puzzle piece data.

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] Distance of the feature vectors. (Overload if not proper).
    """

    # Get feature descriptors as tuple of (keypoints, descriptors)
    feat_A = piece_A.getFeature(self)   
    feat_B = piece_B.getFeature(self) 

    # Check that descriptor sets are non-empty.
    if feat_A[1] is None or feat_B[1] is None:  
      return 0

    # Compute matches and use percentage relative to max possible matches as the "distance" score.
    # Should be close to 100 if the pieces are similar. Of course, some image variation or skewing
    # of puzzle pieces may impact achieving a perfect match.
    matches = calculateMatches(feat_A[1], feat_B[1], self.params.slambda)
    distance = 100 * (len(matches) / min(len(feat_A[0]), len(feat_B[0])))

    return distance

  #============================= compare =============================
  #
  def compare(self, piece_A, piece_B):
    """!
    @brief  Compare between two passed puzzle piece data.

    Note that this code has additional calculations that estimate the transformation
    that will register or align the puzzle pieces.

    See references for idea behind this comparison:

    https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_matcher/py_matcher.html
    and https://scikit-image.org/docs/dev/auto_examples/transform/plot_matching.html

    @todo   Establish whether the registration code should be here or elsewhere.  The reason for
            being here is that it takes advantage of matching computations made to prevent
            additional computations.
    @todo   Yet, these are done whether it is a match or not.  Better to not bother if not even
            a match. Going to go with that by rearranging the code [2023/11/03]. Delete note
            if acceptable.

    @param[in] piece_A      Template instance saving a piece's info.
    @param[in] piece_B      Template instance saving a piece's info.

    @param[out] Comparison result & rotation angle(degree) & other params.
    """

    # Normally should just call score rather than have duplicate code.  But this
    # function takes advantage of intermediate data created during processing to
    # support puzzle piece registrations.
    #
    # Get feature descriptors as tuple of (keypoints, descriptors)
    feat_A = piece_A.getFeature(self)
    feat_B = piece_B.getFeature(self)

    # Check that descriptor sets are non-empty. If any empty, then no match.
    # Else try matching.
    #
    # Compute matches and use percentage relative to max possible matches as
    # the "distance" score.  Should be close to 100 if the pieces are similar.
    # Of course, some image variation or skewing of puzzle pieces may impact
    # achieving a perfect match.
    if feat_A[1] is None or feat_B[1] is None:  
      distance = 0
    else:
      matches = calculateMatches(feat_A[1], feat_B[1], self.params.slambda)
      distance = 100 * (len(matches) / min(len(feat_A[0]), len(feat_B[0])))

    # DEBUG
    print(f"Distance = {distance} ?? {self.params.tau} from {matches}")
    print(f"{len(feat_A[0])} vs {len(feat_B[0])}")
    isaMatch = distance > self.params.tau

    # If not a match then don't bother with additional calculations.
    if not isaMatch:
      return False, None, None

    # If a match, then continue with additional calculations: estimate affine
    # transform model using keypoint coordinates and matched descriptors.
    # Being a match means that there are sufficient matched keypoints.

    src = []
    dst = []

    for match in matches:
      src.append(feat_A[0][match[0].queryIdx].pt)
      dst.append(feat_B[0][match[0].trainIdx].pt)

    src = np.array(src)
    dst = np.array(dst)

    # It only makes sense for translation if both piece images have the same origin
    src = np.array(src) + piece_A.rLoc
    dst = np.array(dst) + piece_B.rLoc

    model = AffineTransform()
    model.estimate(src, dst)

    # Note: model.translation is not 100% consistent with what we want. Use pieceLocation instead.

    return True, np.rad2deg(model.rotation), model.params
    # @todo Why converted to degrees?  Seems superfluous. Review subsequent code to see if needed.

    # NOT NEEDED TESTED EARLIER.
    # @todo Delete when done and verified to work.
    #else:
    #  return False, None, None

    # @note Yikes, why was RANSAC even tried?  Since pieceLocation is preferred for the
    #       translational match, then a better scheme would be to center the keypoints
    #       then robustly estimate a single rotation parameter from the matches.
    #       I suspect that there is a fast, robust scheme to do so in the complex plane.
    #       Something as simple as individual estimates followed by some kind of voting
    #       or clustering process with mode recovery. 
    #
    # @note I just realized that registration is really not worth doing until there is
    #       an attempt to actually move the piece into place. If that is the case, then
    #       registration can be done at a later stage.  It also saves time when performing
    #       the matching.  
    #
    # @todo Honestly, registration maybe even should be separated from the matching process.  If
    #       truly needed simultaneous with matching, then can go ahead and define a different member
    #       function that does both.  Some of the decision making that went into this code
    #       was pretty bad.
    #
    #       2023/11/03 - PAV.

    ## Robustly estimate affine transform model with RANSAC. However, too slow
    # if len(src) > 3:
    #     model_robust, inliers = ransac((src, dst), AffineTransform, min_samples=3,
    #                                    residual_threshold=2, max_trials=100)
    #     outliers = inliers == False
    #
    #     # # Debug only
    #     # fig, ax = plt.subplots(nrows=1, ncols=1)
    #     # inlier_idxs = np.nonzero(inliers)[0]
    #     # src2 = np.array([[i[1]-piece_A.rLoc[1], i[0]-piece_A.rLoc[0]] for i in src])
    #     # dst2 = np.array([[i[1]-piece_B.rLoc[1], i[0]-piece_B.rLoc[0]] for i in dst])
    #     #
    #     # # Follow row, col order in plot_matches
    #     # plot_matches(ax, piece_A.y.image, piece_B.y.image, src2, dst2,
    #     #              np.column_stack((inlier_idxs, inlier_idxs)), matches_color='b')
    #     #
    #     # plt.show()
    #
    #     return distance > self.tau, np.rad2deg(model_robust.rotation), model_robust.params
    # else:
    #     return distance > self.tau, np.rad2deg(model.rotation), model.params


#
#========================== puzzle.piece.matchSimilar ==========================
