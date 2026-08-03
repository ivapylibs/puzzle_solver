#!/usr/bin/python3
#================================= bow01_fit =================================
##@file
# @brief    Test script for basic fitting and histogram encoding of Bag-of-Words
#           color matching system.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Antigravity + Patricio A. Vela, pvela@gatech.edu
# @date     2026/07/30
#
# @quit
#================================= bow01_fit =================================

import numpy as np
from puzzle.pieces.BoW import ColorBoWMatcher, CfgBoW, _make_demo_groups

def test_fit():
    print("=" * 60)
    print("  BoW Test 01: Vocabulary Fitting and Encoding")
    print("=" * 60)

    # 1. Synthesise synthetic groups
    groups, labels = _make_demo_groups(n_groups=5, n_pixels_per_group=500, n_true_colors=20)
    print(f"[Data] Created {len(groups)} groups with {groups[0].shape[1]} pixels each.")

    # 2. Instantiate with default CfgBoW configuration
    cfg = CfgBoW()
    cfg.n_words = 15
    matcher = ColorBoWMatcher(cfg)

    # 3. Fit model
    matcher.fit(groups, labels=labels)

    # 4. Verify outputs
    assert matcher.centroids_ is not None, "Centroids should not be None after fit."
    assert matcher.centroids_.shape == (15, 3), f"Expected centroids shape (15, 3), got {matcher.centroids_.shape}"
    assert len(matcher.histograms_) == 5, f"Expected 5 histograms, got {len(matcher.histograms_)}"
    assert len(matcher.group_labels_) == 5, f"Expected 5 labels, got {len(matcher.group_labels_)}"

    # Check histogram normalization (sum to 1)
    for i, hist in enumerate(matcher.histograms_):
        h_sum = float(np.sum(hist))
        assert abs(h_sum - 1.0) < 1e-5, f"Histogram {i} sum should be 1.0, got {h_sum}"

    print(f"[Vocabulary] Discovered {matcher.n_words} cluster centroids.")
    print(f"[Histograms] Encoded {len(matcher.histograms_)} normalized histograms.")
    print("Test bow01_fit Passed Successfully!\n")

if __name__ == "__main__":
    test_fit()
