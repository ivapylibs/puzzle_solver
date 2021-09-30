# ====================== puzzle.utils.shapeProcessing ======================
#
# @brief    Some shape processing functions.
#
# ====================== puzzle.utils.dataProcessing ======================
#
# @file     shapeProcessing.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/10 [created]
#
#
# ====================== puzzle.utils.shapeProcessing ======================


# ============================== Dependencies =============================

# ====================== puzzle.utils.shapeProcessing ======================

def bb_intersection_over_union(boxA, boxB):
    """
    @brief  Compute the intersection of two boundingboxes.
            See https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc

    Args:
        boxA: A list representing a bounding box.
        boxB: A list representing a bounding box.

    Returns:
        The intersection over union value.
    """
    # Determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # Compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0

    # Compute the area of both the prediction and ground-truth rectangles
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    # Compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # Return the intersection over union value
    return iou

#
# ====================== puzzle.utils.shapeProcessing ======================
