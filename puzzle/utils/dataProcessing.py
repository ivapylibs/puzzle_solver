# ====================== puzzle.utils.dataProcessing ======================
#
# @brief    Some data processing functions.
#
# ====================== puzzle.utils.dataProcessing ======================
#
# @file     dataProcessing.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/09 [created]
#
#
# ====================== puzzle.utils.dataProcessing ======================

# ===== Environment / Dependencies
#
import types
import cv2
import numpy as np


#=============================== updateLabel ===============================
#
def updateLabel(x_list, x_label):
    """!
    @brief  Update the label according to the ranking of all the elements'
            (with the same label) mean value.
            E.g., x_list = [28,137,263,269,33,151] / x_label = [2,3,1,1,2,3] ->
            x_label_updated = [0,1,2,2,0,1]
    
    @param[in]  x_list  Value list.
    @param[in]  x_label Original label.

    @param[out] x_label_updated     The updated label.
    """

    x_mean = []
    for label in range(1, 1 + len(set(x_label))):
        x_mean.append(np.mean(x_list[np.where(x_label == label)]))
    x_rank = np.array(x_mean).argsort().argsort()

    x_zip = dict(zip(list(range(1, 1 + len(x_mean))), x_rank))

    x_label_updated = list(map(x_zip.get, x_label))

    return x_label_updated

#============================== copyAttributes =============================
#
class copyAttributes(object):

    def __init__(self, source):
        """
        @brief  Class constructor.

        Args:
            source: The source class instance.
        """

        self.source = source

    def __call__(self, target):
        """
        @brief  Copy attributes from a source class to a target class.
                See https://stackoverflow.com/a/12014625/5269146.

        Args:
            target: The target class instance.

        Returns:
            target: The updated target class instance.
        """

        for attr, value in self.source.__dict__.items():
            if attr.startswith('__'):
                continue
            if isinstance(value, (property, types.FunctionType)):
                continue
            setattr(target, attr, value)
        return target


#============================= calculateMatches ============================
#
def calculateMatches(des1, des2, ratio_threshold=0.7):
    """!
    @brief  Calculate the matches based on KNN

    For premise behind this approach, see
    https://github.com/adumrewal/SIFTImageSimilarity/blob/master/SIFTSimilarityInteractive.ipynb

    @param[in]  des1        First descriptor.
    @param[in]  des2        Second descriptor.

    @param[in] topResults   Final matches.
    """
    bf = cv2.BFMatcher()
    try:
        # First match keypoint descriptors from 1 to 2.
        matches = bf.knnMatch(des1, des2, k=2)

        # Then match keypoint descriptors from 2 to 1.
        matches = bf.knnMatch(des2, des1, k=2)

        # Keep only matches are closer than next best option
        topResults1 = []
        topResults2 = []
        for m, n in matches:
            if m.distance < ratio_threshold * n.distance:
                topResults1.append([m])
    
        for m, n in matches:
            if m.distance < ratio_threshold * n.distance:
                topResults2.append([m])

    except:
        print('No matches')
        return []

    # Cross-compare matches and retain symmetric ones.
    #
    topResults = []
    for match1 in topResults1:
        match1QueryIndex = match1[0].queryIdx
        match1TrainIndex = match1[0].trainIdx

        for match2 in topResults2:
            match2QueryIndex = match2[0].queryIdx
            match2TrainIndex = match2[0].trainIdx

            # Symmetry of keypoint matches test.
            if (match1QueryIndex == match2TrainIndex) and (match1TrainIndex == match2QueryIndex):
                topResults.append(match1)


    return topResults


#================================= checkKey ================================
#
def checkKey(dict1, dict2, value):
    """
    @brief Check the key & value pairs between two dicts given a query value.

    Args:
        dict1: Query dict 1.
        dict2:  Query dict 2.
        value:  Query value.

    Returns:
        Whether the keys found are the same.
    """

    key1 = list(dict1.keys())[list(dict1.values()).index(value)]
    key2 = list(dict2.keys())[list(dict2.values()).index(value)]

    return key1 == key2

#============================== closestNumber ==============================
#
def closestNumber(num, basis=50, lower=True):
    """
    @brief Get the closest number to the basis target for the input number.
    e.g., 580 with 50 -> 550

    Args:
        num: The input number.
        basis: The basis target number.
        lower: The direction.

    Returns:
        The integar of the closest number.

    """
    if lower:
        return int(num-num%basis)
    else:
        return int(num-num%basis+basis)

#
# ====================== puzzle.utils.dataProcessing ======================
