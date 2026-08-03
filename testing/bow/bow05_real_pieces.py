#!/usr/bin/python3
#============================ bow05_real_pieces ============================
##@file
# @brief    Test script for Bag-of-Words color matcher using real puzzle piece
#           images (pieces01_rgb.png, pieces01_seg.png, pieces02_rgb.png, pieces02_seg.png).
#
# @details  Connected components are extracted from the binary segmentation mask
#           pieces01_seg.png to fit a multi-piece color vocabulary and model database.
#           Individual connected component pieces extracted from pieces02_seg.png and
#           their corresponding RGB pixels from pieces02_rgb.png are then queried against
#           the learned model to find piece-to-piece color matches.
#           A side-by-side visualization (`pieces_match_visualization.png`) with arrows
#           connecting matched piece centroids is saved as output.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Antigravity + Patricio A. Vela, pvela@gatech.edu
# @date     2026/07/30
#
# @quit
#============================ bow05_real_pieces ============================

import os
import cv2
import numpy as np

import sys
import argparse

from puzzle.pieces.BoW import ColorBoWMatcher, CfgBoW
import ivapy.display_cv as display

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

def test_real_pieces(doDisp=False):
    print("=" * 60)
    print("  BoW Test 05: Real Puzzle Pieces Connected Components Matching")
    print("=" * 60)

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
    cfg.n_words = 25
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

    # Prepare side-by-side visualization canvas
    H, W, _ = Irgb1_bgr.shape
    canvas = np.hstack([Irgb1_bgr.copy(), Irgb2_bgr.copy()])

    # Distinct colors for drawing connection arrows
    np.random.seed(100)
    palette_colors = [tuple(int(c) for c in color) for color in np.random.randint(60, 255, (num_labels2 + 10, 3))]

    # 6. Query each piece component from pieces02 against the learned model
    query_results = []
    print("\n[Query Results] Matching individual pieces02 objects against pieces01 model:")
    print("-" * 65)
    print(f"  {'Query Piece ID':<16} {'Size (px)':<12} {'Matched Piece':<16} {'Chi2 Distance':<15}")
    print("-" * 65)

    for comp_id in range(1, num_labels2):
        mask = (labels2 == comp_id)
        pixel_count = int(np.sum(mask))

        # Filter out trivial noise components (< 10 pixels)
        if pixel_count < 10:
            continue

        query_rgb = Irgb2[mask].T  # (3, N) RGB matrix
        top_match = matcher.query(query_rgb, top_k=1)[0]
        matched_label = top_match['label']
        dist = top_match['distance']

        query_results.append((comp_id, pixel_count, matched_label, dist))
        print(f"  Piece_{comp_id:02d}          {pixel_count:<12d} Piece_{matched_label:<10s}    {dist:.6f}")

        # Compute centroid of query piece in Dataset 2
        ys2, xs2 = np.where(mask)
        cx2, cy2 = int(np.mean(xs2)), int(np.mean(ys2))
        pt2 = (cx2 + W, cy2)  # Shift x by W for right panel

        # Draw connecting arrow on side-by-side canvas
        if matched_label in centroids1:
            pt1 = centroids1[matched_label]
            color = palette_colors[comp_id % len(palette_colors)]

            # Draw arrow from left (database piece) to right (query piece)
            cv2.arrowedLine(canvas, pt1, pt2, color, thickness=1, tipLength=0.01)
            cv2.circle(canvas, pt1, 4, color, -1)
            cv2.circle(canvas, pt2, 4, color, -1)

    print("-" * 65)
    print(f"[Summary] Successfully queried {len(query_results)} piece objects.")

    # Draw header text on canvas
    cv2.putText(canvas, "Dataset 1: Database Pieces (Model)", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(canvas, "Dataset 2: Query Pieces", (W + 20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # 7. Generate quantized images using vocabulary centroids
    quant1_rgb = matcher.quantizeImage(Irgb1, Iseg1_bin)
    quant2_rgb = matcher.quantizeImage(Irgb2, Iseg2_bin)

    quant1_bgr = cv2.cvtColor(quant1_rgb, cv2.COLOR_RGB2BGR)
    quant2_bgr = cv2.cvtColor(quant2_rgb, cv2.COLOR_RGB2BGR)

    quant_canvas = np.hstack([quant1_bgr, quant2_bgr])
    cv2.putText(quant_canvas, "Dataset 1: Quantized (Centroid Colors)", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
    cv2.putText(quant_canvas, "Dataset 2: Quantized (Centroid Colors)", (W + 20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

    # 8. Save visualization artifacts
    vis_path = os.path.join(cpath, 'pieces_match_visualization.png')
    cv2.imwrite(vis_path, canvas)

    cv2.imwrite(os.path.join(cpath, 'pieces01_quantized.png'), quant1_bgr)
    cv2.imwrite(os.path.join(cpath, 'pieces02_quantized.png'), quant2_bgr)
    cv2.imwrite(os.path.join(cpath, 'pieces_quantized_comparison.png'), quant_canvas)

    vocab_swatch = matcher.vocabulary_as_image(swatch_size=40)
    cv2.imwrite(os.path.join(cpath, 'pieces_vocab_swatches.png'), vocab_swatch)

    hist_vis = matcher.histogram_image(group_idx=0)
    cv2.imwrite(os.path.join(cpath, 'pieces01_histogram.png'), hist_vis)

    print(f"\n[Output] Saved side-by-side matching visualization to '{os.path.basename(vis_path)}'")
    print("[Output] Saved quantized images to 'pieces01_quantized.png' and 'pieces02_quantized.png'")
    print("[Output] Saved side-by-side quantized comparison to 'pieces_quantized_comparison.png'")
    print("[Output] Saved vocabulary swatches to 'pieces_vocab_swatches.png'")
    print("[Output] Saved sample histogram to 'pieces01_histogram.png'")
    print("\nTest bow05_real_pieces Passed Successfully!\n")

    if doDisp:
      display.bgr(canvas, window_name="Matches")
      display.bgr(quant_canvas, window_name="Quantized Images")
      display.wait()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Run BoW fitting and matching on test data.")
    argparser.add_argument("--display", action='store_true', help="Display outcome in user interactive move.")
    opts = argparser.parse_args()

    test_real_pieces(opts.display)
