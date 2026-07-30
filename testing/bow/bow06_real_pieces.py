#!/usr/bin/python3
#============================ bow06_real_pieces ============================
##@file
# @brief    Test script for Bag-of-Words color matcher forcing a 1-to-1 bipartite
#           match across all pieces using the Hungarian Algorithm.
#
# @details  Connected components are extracted from pieces01_seg.png (Dataset 1)
#           to fit a multi-piece color vocabulary and model database.
#           Query connected components are extracted from pieces02_seg.png (Dataset 2).
#           An N x M cost matrix of Chi-Squared histogram distances is computed,
#           and scipy.optimize.linear_sum_assignment is used to force an exact
#           one-to-one optimal assignment between all query and database pieces.
#           A side-by-side visualization (`pieces_match_visualization_1to1.png`)
#           with arrows connecting the 1-to-1 matched piece centroids is saved.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Antigravity + Patricio A. Vela, pvela@gatech.edu
# @date     2026/07/30
#
#============================ bow06_real_pieces ============================

import os
import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

import sys
import argparse

from puzzle.pieces.BoW import ColorBoWMatcher, CfgBoW, encode_histogram, histogram_distance
import ivapy.display_cv as display

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

def test_real_pieces_1to1(doDisp=False):
    print("=" * 70)
    print("  BoW Test 06: Real Puzzle Pieces 1-to-1 Bipartite Matching")
    print("=" * 70)

    # 1. Image path setup
    img1_rgb_path = os.path.join(cpath, 'pieces01_rgb.png')
    img1_seg_path = os.path.join(cpath, 'pieces01_seg.png')
    img2_rgb_path = os.path.join(cpath, 'pieces02_rgb.png')
    img2_seg_path = os.path.join(cpath, 'pieces02_seg.png')

    assert os.path.exists(img1_rgb_path), f"Missing image: {img1_rgb_path}"
    assert os.path.exists(img1_seg_path), f"Missing image: {img1_seg_path}"
    assert os.path.exists(img2_rgb_path), f"Missing image: {img2_rgb_path}"
    assert os.path.exists(img2_seg_path), f"Missing image: {img2_seg_path}"

    # 2. Load images (convert BGR -> RGB for color processing)
    Irgb1_bgr = cv2.imread(img1_rgb_path, cv2.IMREAD_COLOR)
    Irgb1 = cv2.cvtColor(Irgb1_bgr, cv2.COLOR_BGR2RGB)
    Iseg1_bin = cv2.imread(img1_seg_path, cv2.IMREAD_GRAYSCALE)

    Irgb2_bgr = cv2.imread(img2_rgb_path, cv2.IMREAD_COLOR)
    Irgb2 = cv2.cvtColor(Irgb2_bgr, cv2.COLOR_BGR2RGB)
    Iseg2_bin = cv2.imread(img2_seg_path, cv2.IMREAD_GRAYSCALE)

    # 3. Extract connected components from pieces01 binary segmentation
    num_labels1, labels1 = cv2.connectedComponents((Iseg1_bin > 0).astype(np.uint8))
    print(f"[Dataset 1] Found {num_labels1 - 1} piece connected components in pieces01.")

    # Compute centroids for Dataset 1 pieces
    centroids1 = {}
    for pid in range(1, num_labels1):
        ys, xs = np.where(labels1 == pid)
        if len(xs) > 0:
            centroids1[str(pid)] = (int(np.mean(xs)), int(np.mean(ys)))

    # 4. Instantiate ColorBoWMatcher and fit model using labeled connected components
    cfg = CfgBoW()
    cfg.n_words = 27
    cfg.metric = "chi2"
    cfg.tau = 0.5
    matcher = ColorBoWMatcher(cfg)

    print("Fitting BoW color vocabulary on pieces01 piece components...")
    matcher.fitFromImageSegmented(Irgb1, labels1, hasLabs=True)

    print(f"[Vocabulary] Discovered {matcher.n_words} color words.")
    print(f"[Database] Model populated with {len(matcher.group_labels_)} piece histograms.")

    # 5. Extract connected components from pieces02 binary segmentation
    num_labels2, labels2 = cv2.connectedComponents((Iseg2_bin > 0).astype(np.uint8))
    print(f"\n[Dataset 2] Found {num_labels2 - 1} connected components in pieces02.")

    query_pieces = []
    query_hists = []
    query_centroids = {}

    for comp_id in range(1, num_labels2):
        mask = (labels2 == comp_id)
        pixel_count = int(np.sum(mask))

        # Filter out trivial noise components (< 10 pixels)
        if pixel_count < 10:
            continue

        ys, xs = np.where(mask)
        cx, cy = int(np.mean(xs)), int(np.mean(ys))
        query_centroids[comp_id] = (cx, cy)

        query_rgb = Irgb2[mask].T  # (3, N) RGB matrix
        q_hist = encode_histogram(query_rgb, matcher.centroids_)
        query_pieces.append((comp_id, pixel_count))
        query_hists.append(q_hist)

    N = len(query_pieces)
    M = len(matcher.histograms_)
    print(f"[Cost Matrix] Computing {N} x {M} histogram distance matrix...")

    # 6. Build N x M cost matrix
    cost_matrix = np.zeros((N, M), dtype=np.float64)
    for i in range(N):
        q_hist = query_hists[i]
        for j in range(M):
            db_hist = matcher.histograms_[j]
            cost_matrix[i, j] = histogram_distance(q_hist, db_hist, metric=matcher.metric)

    # 7. Force 1-to-1 optimal bipartite matching via Hungarian algorithm
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    print("\n[1-to-1 Matching Results] Optimal Bipartite Assignment:")
    print("-" * 70)
    print(f"  {'Query Piece ID':<16} {'Size (px)':<12} {'Matched Piece':<16} {'Chi2 Distance':<15}")
    print("-" * 70)

    assignment_results = []
    for r, c in zip(row_ind, col_ind):
        comp_id, size = query_pieces[r]
        matched_label = matcher.group_labels_[c]
        dist = cost_matrix[r, c]
        assignment_results.append((comp_id, size, matched_label, dist))
        print(f"  Piece_{comp_id:02d}          {size:<12d} Piece_{matched_label:<10s}    {dist:.6f}")

    print("-" * 70)
    total_cost = float(np.sum(cost_matrix[row_ind, col_ind]))
    unique_matched = len(np.unique(col_ind))
    print(f"[Summary] Assigned {N} query pieces to {unique_matched} unique database pieces.")
    print(f"[Global Cost] Total sum of assignment distances: {total_cost:.6f}")

    assert unique_matched == N, f"Expected 1-to-1 unique mapping for {N} pieces, got {unique_matched}"

    # 8. Side-by-Side 1-to-1 Visualization with arrows
    H, W, _ = Irgb1_bgr.shape
    canvas = np.hstack([Irgb1_bgr.copy(), Irgb2_bgr.copy()])

    np.random.seed(200)
    palette_colors = [tuple(int(c) for c in color) for color in np.random.randint(60, 255, (N + 10, 3))]

    for r, c in zip(row_ind, col_ind):
        comp_id, _ = query_pieces[r]
        matched_label = matcher.group_labels_[c]

        cx2, cy2 = query_centroids[comp_id]
        pt2 = (cx2 + W, cy2)  # Shift x by W for right panel

        if matched_label in centroids1:
            pt1 = centroids1[matched_label]
            color = palette_colors[comp_id % len(palette_colors)]

            # Draw arrow from left (database piece) to right (1-to-1 matched query piece)
            cv2.arrowedLine(canvas, pt1, pt2, color, thickness=1, tipLength=0.015)
            cv2.circle(canvas, pt1, 4, color, -1)
            cv2.circle(canvas, pt2, 4, color, -1)

    # Draw header text on canvas
    cv2.putText(canvas, "Dataset 1: Database Model (1-to-1 Match)", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
    cv2.putText(canvas, "Dataset 2: Query Pieces (Assigned)", (W + 20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

    # Save visualization output image
    vis_path = os.path.join(cpath, 'pieces_match_visualization_1to1.png')
    cv2.imwrite(vis_path, canvas)

    vocab_swatch = matcher.vocabulary_as_image(swatch_size=40)
    cv2.imwrite(os.path.join(cpath, 'pieces_vocab_swatches_1to1.png'), vocab_swatch)

    print(f"\n[Output] Saved 1-to-1 matching visualization to '{os.path.basename(vis_path)}'")
    print("[Output] Saved vocabulary swatches to 'pieces_vocab_swatches_1to1.png'")
    print("\nTest bow06_real_pieces Passed Successfully!\n")

    if doDisp:
      display.bgr(canvas, window_name="Matches")
      display.wait()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Run BoW fitting and matching on test data.")
    argparser.add_argument("--display", action='store_true', help="Display outcome in user interactive move.")
    opts = argparser.parse_args()

    test_real_pieces_1to1(opts.display)
