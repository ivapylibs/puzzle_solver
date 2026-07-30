#!/usr/bin/python3
#================================ bow02_query ================================
##@file
# @brief    Test script for query similarity matching across distance metrics
#           in Bag-of-Words color matching.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Antigravity + Patricio A. Vela, pvela@gatech.edu
# @date     2026/07/30
#
#================================ bow02_query ================================

import numpy as np
from puzzle.pieces.BoW import ColorBoWMatcher, CfgBoW, _make_demo_groups

def test_query():
    print("=" * 60)
    print("  BoW Test 02: Similarity Query and Metric Comparison")
    print("=" * 60)

    # 1. Synthesise synthetic groups
    groups, labels = _make_demo_groups(n_groups=5, n_pixels_per_group=600, n_true_colors=20)
    
    matcher = ColorBoWMatcher(n_words=20, metric="chi2", tau=0.25)
    matcher.fit(groups, labels=labels)

    # 2. Query using group_0 itself (RGB matrix query)
    results = matcher.query(groups[0])
    
    # Self-match check
    top_match = results[0]
    print(f"[Query Result] Top match for group_0: {top_match['label']} with distance {top_match['distance']:.6f}")
    assert top_match["label"] == "group_0", f"Expected top match group_0, got {top_match['label']}"
    assert top_match["distance"] < 1e-5, f"Self-match distance should be near 0, got {top_match['distance']}"

    # 3. Test across all supported distance metrics
    metrics = ["chi2", "intersection", "hellinger", "l2", "cosine"]
    print("\n[Metric Check] Testing query across metrics:")
    for m in metrics:
        matcher.metric = m
        res = matcher.query(groups[0], top_k=2)
        assert len(res) == 2, f"Expected top_k=2 results, got {len(res)}"
        print(f"  Metric: {m:12s} -> Rank 1: {res[0]['label']} (dist={res[0]['distance']:.4f}), Rank 2: {res[1]['label']} (dist={res[1]['distance']:.4f})")

    # 4. Test pre-computed histogram query
    q_hist = matcher.histograms_[0]
    hist_results = matcher.query_histogram(q_hist, top_k=2)
    assert hist_results[0]["label"] == "group_0", "query_histogram should identify group_0 as top match."

    print("\nTest bow02_query Passed Successfully!\n")

if __name__ == "__main__":
    test_query()
