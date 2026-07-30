#!/usr/bin/python3
#============================== bow03_segmented ==============================
##@file
# @brief    Test script for fitFromImageSegmented method supporting binary and
#           labeled image segmentations.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Antigravity + Patricio A. Vela, pvela@gatech.edu
# @date     2026/07/30
#
#============================== bow03_segmented ==============================

import numpy as np
from puzzle.pieces.BoW import ColorBoWMatcher

def test_fit_from_image_segmented():
    print("=" * 60)
    print("  BoW Test 03: Fit From Segmented Image")
    print("=" * 60)

    # 1. Synthesise synthetic color image and segmentation mask
    np.random.seed(42)
    img = np.random.randint(0, 256, (120, 120, 3), dtype=np.uint8)

    # Labeled segmentation with 3 object regions
    seg_labs = np.zeros((120, 120), dtype=np.int32)
    seg_labs[10:40, 10:40] = 101
    seg_labs[50:80, 50:80] = 102
    seg_labs[90:110, 90:110] = 103

    # Binary segmentation mask
    seg_bin = (seg_labs > 0).astype(np.uint8) * 255

    # 2. Test Labeled Segmentation (hasLabs=True)
    matcher_labs = ColorBoWMatcher(n_words=10)
    matcher_labs.fitFromImageSegmented(img, seg_labs, hasLabs=True)

    print(f"[Labeled Mode] Extracted {len(matcher_labs.group_labels_)} groups with labels: {matcher_labs.group_labels_}")
    assert matcher_labs.group_labels_ == ['101', '102', '103'], f"Expected labels ['101', '102', '103'], got {matcher_labs.group_labels_}"
    assert len(matcher_labs.histograms_) == 3, f"Expected 3 histograms, got {len(matcher_labs.histograms_)}"

    # 3. Test Binary Segmentation (hasLabs=False)
    matcher_bin = ColorBoWMatcher(n_words=10)
    matcher_bin.fitFromImageSegmented(img, seg_bin, hasLabs=False)

    print(f"[Binary Mode] Extracted {len(matcher_bin.group_labels_)} group with labels: {matcher_bin.group_labels_}")
    assert matcher_bin.group_labels_ == ['group_0'], f"Expected label ['group_0'], got {matcher_bin.group_labels_}"
    assert len(matcher_bin.histograms_) == 1, f"Expected 1 histogram, got {len(matcher_bin.histograms_)}"

    print("\nTest bow03_segmented Passed Successfully!\n")

if __name__ == "__main__":
    test_fit_from_image_segmented()
