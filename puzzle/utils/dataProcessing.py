# ====================== puzzle.utils.dataProcessing ======================
#
# @brief    Some data processing functions.
#
# ====================== puzzle.utils.dataProcessing ======================
#
# @file     dataProcessing.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
#           Yiye Chen,              yychen2019@gatech.edu
# @date     2021/08/09 [created]
#           2022/07/18 [updated]
#
#
# ====================== puzzle.utils.dataProcessing ======================

# ===== Environment / Dependencies
#
import types
import cv2
import numpy as np
from std_msgs.msg import String
import json
from rospy_message_converter import message_converter, json_message_converter

from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering

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
        The integer of the closest number.

    """
    if lower:
        return int(num-num%basis)
    else:
        return int(num-num%basis+basis)
    
def partition_even(data_list, partition_num, order="ascend"):
    """Partition a list of numbers evenly into a number of sets based on their values
    e.g. data = [4, 11, 14, 3, 32, 35], partition_number = 3, order=ascend.
    result: labels = [0, 1, 1, 0, 2, 2]

    Args:
        data_list ((N, )):              The list of data
        partition_num (int):            The partition numebr
        order (str):                    ascend or descend. THe partition is based on increase order or decrease order
                                        (i.e. The numbers in the first set is the lowest or the highest)
    Returns:
        labels ((N, 1)):                                                The partition label
        part_results ((partition_num, N/partition_num)):                The partition results
    """
    data_list = np.array(data_list).squeeze()
    assert data_list.size % partition_num == 0, "Please make sure the data number is divisible by the partition number"
    partition_ppl = int(data_list.size / partition_num)
    
    # the partition labels after sorting
    labels_sort = np.repeat(np.arange(partition_num), partition_ppl)

    # data sort index
    if order == "ascend":
        idx_sort = np.argsort(data_list)
        data_sort = np.sort(data_list)
    elif order == "descend":
        idx_sort = np.argsort(data_list)[::-1]
        data_sort = np.sort(data_list)[::-1]

    # get the partition data and labels
    part_results = np.array(np.split(data_sort, partition_num))
    labels = np.zeros_like(data_list, dtype=int)
    for i in range(labels_sort.size):
        labels[idx_sort[i]] = labels_sort[i] 

    return labels, part_results

def kmeans_id_2d(dict_id_2d, kmeans_num):
    """
    @brief  Kmeans clustering for a dict of id: 2D data.

    Args:
        dict_id_2d: The dictionary of id: 2D data.
        kmeans_num: The number of clusters.

    Returns:
        dict_id_label: The updated dictionary of 2D data.
    """

    kmeans_model = KMeans(n_clusters=kmeans_num).fit(list(dict_id_2d.values()))
    dict_id_label = dict(zip(dict_id_2d.keys(), kmeans_model.labels_))

    return dict_id_label

def agglomerativeclustering_id_2d(dict_id_2d, cluster_num):
    """
    @brief  Agglomerative clustering for a dict of id: 2D data.

    Args:
        dict_id_2d: The dictionary of id: 2D data.

    Returns:
        dict_id_label: The updated dictionary of 2D data.
    """

    clustering = AgglomerativeClustering(n_clusters=cluster_num).fit(list(dict_id_2d.values()))
    dict_id_label = dict(zip(dict_id_2d.keys(), clustering.labels_))

    return dict_id_label


def convert_serializable(input):
    """
    @brief Convert the object to a serializable object.

    Args:
        input: the input object.

    Returns:
        The serializable object.
    """

    if isinstance(input, np.int64):
        return int(input)
    else:
        raise TypeError(f"Problem with {input}")

def convert_dict2ROS(info_dict):
    """
    @brief Convert the dict to ROS string. See https://github.com/uos/rospy_message_converter

    Args:
        info_dict: the input dict.

    Returns:
        json_str: the ROS string.
    """

    message_json = json.dumps(info_dict, indent=4, default=convert_serializable)
    message = String(data=f'{message_json}')
    json_str = json_message_converter.convert_ros_message_to_json(message)

    return json_str

def convert_ROS2dict(message):
    """
    @brief Convert the ROS string to dict.

    Args:
        message: the input ROS string.

    Returns:
        info_dict: the obtained dict.
    """

    info_dict = json.loads(json.loads(message.data)['data'])

    return info_dict

#
# ====================== puzzle.utils.dataProcessing ======================

if __name__ == "__main__":
    # # Test partition_even
    # data = np.array([4, 11, 14, 3, 32, 35])
    # print(partition_even(data, 3, order="ascend"))

    # # Test kmeans_id_2d
    # dict_id_2d = {0: [0, 0], 1: [1, 1], 2: [0.4, 0.4], 3: [3, 3], 4: [4, 4], 5: [5, 5], 6: [0.6, 0.6], 7: [7, 7], 8: [8, 8], 9: [0.9, 0.9]}
    # print(kmeans_id_2d(dict_id_2d, 3))

    # Test agglomerativeclustering_id_2d
    dict_id_2d = {0: [0, 0], 1: [1, 1], 2: [0.4, 0.4], 3: [3, 3], 4: [4, 4], 5: [5, 5], 6: [0.6, 0.6], 7: [7, 7], 8: [8, 8], 9: [0.9, 0.9]}
    print(agglomerativeclustering_id_2d(dict_id_2d))
