#========================== puzzle.piece.matcher =========================
#
# @brief    Class for comparing puzzle pieces in support of puzzle solving and
#           puzzle piece association.  The base-type class and most of its member
#           functions will do nothing. They require overloading.  The ones that 
#           don't should be for some generic functionality.
#
# Sub-classes of this derived class branch use difference or similarity scores for 
# determining whether two puzzle pieces match.  Difference scores are interpreted as smaller
# values being more likely to be a match and bigger being less likely to be a match.  Similarity
# scores are interpreted as bigger value being more likely to be a match and smaller being less
# likely to be a match.
#
#========================== puzzle.piece.matcher =========================

# @file     matcher.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/25 [created]
#           2021/07/31 [modified]
#
#
#========================== puzzle.piece.matcher =========================

#====== Environment / Dependencies
#
# from puzzle.piece.template import template

#
#---------------------------------------------------------------------------
#================================= Matcher =================================
#---------------------------------------------------------------------------
#
class Matcher:

    def __init__(self, tau=float("NaN")):
        """
        @brief  Constructor for the matcher class.

        Args:
            tau: The comparison threshold.
        """

        # super(matcher, self).__init__(y)

        self.tau = tau  # @< Threshold to use when comparing, if given.


    def extractFeature(piece):
        """
        @brief  Process raw puzzle piece data to obtain encoded description of piece. 
                Use to recognize/associate the piece given new measurements.
                This member function should be overloaded.

        @param[in]  piece   Template instance saving a piece's info.

        @param[out] "Feature" vector.
        """
        raise NotImplementedError

    #============================== score ==============================
    #
    def score(self, piece_A, piece_B):
        """
        @brief Compute the score between two passed puzzle piece data.

        @param[in] piece_A      Template instance saving a piece's info.
        @param[in] piece_B      Template instance saving a piece's info.

        @param[out] Distance of the feature vectors. (Overload if not proper).
        """

        cent_A = self.extractFeature(piece_A)
        cent_B = self.extractFeature(piece_B)

        return np.norm(cent_A - cent_B)

    #============================= compare =============================
    #
    def compare(self, piece_A, piece_B):
        """
        @brief  Compare between two passed puzzle piece data.
                This member function should be overloaded. Currently returns false
                so that all comparisons fail.

        Args:
            piece_A: A template instance saving a piece's info.
            piece_B: A template instance saving a piece's info.

        Returns:
          Comparison result.
        """

        raise NotImplementedError

#
#---------------------------------------------------------------------------
#============================== MatchDifferent =============================
#---------------------------------------------------------------------------
#

class MatchDifferent(Matcher):
    """!
    @brief  The puzzle piece matching scores are based on differences. Lower is better.
    """

    #============================= __init__ ============================
    #
    def __init__(self, tau=-float('inf')):
        """!
        @brief Constructor for the puzzle piece matchDifferent class.

        @param[in]  tau     Threshold param to determine difference.
        """
        super(MatchDifferent, self).__init__(tau)


    #============================= compare =============================
    #
    def compare(self, piece_A, piece_B):
        """!
        @brief Compare two puzzle pieces.

        @param[in]  piece_A     First puzzle piece.
        @param[in]  piece_B     Second puzzle piece.

        @param[out] Binary indicator of similarity = not different (True = similar).
        """

        # score is to calculate the similarity while it will call the feature extraction process
        # inside
        diffScore = self.score(piece_A, piece_B)

        return diffScore < self.tau

#
#---------------------------------------------------------------------------
#======================== puzzle.piece.matchSimilar ========================
#---------------------------------------------------------------------------
#
class MatchSimilar(Matcher):

    #============================= __init__ ============================
    #
    def __init__(self, tau=float('inf')):
        """
        @brief  Constructor for the puzzle piece matchSimilar class.

        @param[in]  tau     Threshold param to determine similarity.
        """

        super(MatchSimilar, self).__init__(tau)

    #============================= compare =============================
    #
    def compare(self, piece_A, piece_B):
        """
        @brief  Compare between two passed puzzle piece data.

        @param[in]  piece_A     First puzzle piece.
        @param[in]  piece_B     Second puzzle piece.

        @param[out] Binary indicator of similarity (True = similar).
        """

        # score is to calculate the similarity while it will call the feature extraction process
        # inside
        simScore = self.score(piece_A, piece_B)

        return simScore > self.tau


#
# ========================= puzzle.piece.matcher =========================
