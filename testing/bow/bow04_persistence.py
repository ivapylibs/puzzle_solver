#!/usr/bin/python3
#============================= bow04_persistence =============================
##@file
# @brief    Test script for YAML configuration and HDF5 model persistence in BoW.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Antigravity + Patricio A. Vela, pvela@gatech.edu
# @date     2026/07/30
#
#============================= bow04_persistence =============================

import os
import tempfile
import numpy as np
from puzzle.pieces.BoW import ColorBoWMatcher, CfgBoW, _make_demo_groups

def test_persistence():
    print("=" * 60)
    print("  BoW Test 04: YAML & HDF5 Persistence")
    print("=" * 60)

    # 1. Test YAML Config Save and Load
    cfg = CfgBoW()
    cfg.n_words = 12
    cfg.tau = 0.35
    cfg.metric = "hellinger"
    matcher_yaml = ColorBoWMatcher(cfg)

    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp_yaml:
        yaml_path = tmp_yaml.name

    try:
        matcher_yaml.saveToYAML(yaml_path)
        loaded_yaml_matcher = ColorBoWMatcher.loadFromYAML(yaml_path)

        print(f"[YAML Test] Loaded configuration: n_words={loaded_yaml_matcher.n_words}, tau={loaded_yaml_matcher.params.tau}, metric={loaded_yaml_matcher.metric}")
        assert loaded_yaml_matcher.n_words == 12, f"Expected n_words=12, got {loaded_yaml_matcher.n_words}"
        assert abs(loaded_yaml_matcher.params.tau - 0.35) < 1e-5, f"Expected tau=0.35, got {loaded_yaml_matcher.params.tau}"
        assert loaded_yaml_matcher.metric == "hellinger", f"Expected metric='hellinger', got {loaded_yaml_matcher.metric}"
    finally:
        if os.path.exists(yaml_path):
            os.remove(yaml_path)

    # 2. Test HDF5 Model Save and Load
    groups, labels = _make_demo_groups(n_groups=4, n_pixels_per_group=400)
    matcher_hdf5 = ColorBoWMatcher(n_words=10, tau=0.2)
    matcher_hdf5.fit(groups, labels=labels)

    with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as tmp_hdf5:
        hdf5_path = tmp_hdf5.name

    try:
        matcher_hdf5.save(hdf5_path)
        loaded_hdf5_matcher = ColorBoWMatcher.load(hdf5_path)

        print(f"[HDF5 Test] Loaded model: n_words={loaded_hdf5_matcher.n_words}, labels={loaded_hdf5_matcher.group_labels_}")
        assert loaded_hdf5_matcher.n_words == 10, f"Expected n_words=10, got {loaded_hdf5_matcher.n_words}"
        assert loaded_hdf5_matcher.group_labels_ == labels, f"Expected labels {labels}, got {loaded_hdf5_matcher.group_labels_}"
        assert np.allclose(matcher_hdf5.centroids_, loaded_hdf5_matcher.centroids_), "Centroids matrix mismatch after HDF5 load."
        assert len(loaded_hdf5_matcher.histograms_) == 4, f"Expected 4 histograms, got {len(loaded_hdf5_matcher.histograms_)}"
    finally:
        if os.path.exists(hdf5_path):
            os.remove(hdf5_path)

    print("\nTest bow04_persistence Passed Successfully!\n")

if __name__ == "__main__":
    test_persistence()
