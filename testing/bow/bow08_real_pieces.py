#!/usr/bin/python3
#============================ bow08_real_pieces ============================
##@file
# @brief    Load a previously saved BoW color model and query it against the
#           pieces02 image data to produce per-piece color matches.
#
# @details  Reads the YAML configuration file (bow_pieces01.yaml) and the HDF5
#           model file (bow_pieces01.h5) written by bow07_real_pieces.py, then:
#             - Instantiates ColorBoWMatcher from HDF5 (centroids + histograms
#               fully restored; no re-fitting required).
#             - Extracts connected component pieces from pieces02_seg.png.
#             - Queries each component's RGB pixels against the restored model.
#             - Renders a side-by-side match visualization with arrows and a
#               side-by-side quantized comparison image, both saved to disk.
#
#           Run bow07_real_pieces.py first to generate the required files.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Antigravity + Patricio A. Vela, pvela@gatech.edu
# @date     2026/07/30
#
# @quit
#============================ bow08_real_pieces ============================

import os
import cv2
import numpy as np
import argparse

from puzzle.pieces.BoW import ColorBoWMatcher
import ivapy.display_cv as display

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# Paths written by bow07_real_pieces.py
YAML_PATH = os.path.join(cpath, 'bow_pieces01.yaml')
HDF5_PATH = os.path.join(cpath, 'bow_pieces01.h5')


def test_load_and_query(doDisp=False):
    print("=" * 65)
    print("  BoW Test 08: Load Saved Model and Query Against pieces02")
    print("=" * 65)

    # 1. Verify serialized files exist (must run bow07 first)
    assert os.path.exists(YAML_PATH), \
        f"YAML config not found: {YAML_PATH}\n  -> Run bow07_real_pieces.py first."
    assert os.path.exists(HDF5_PATH), \
        f"HDF5 model not found: {HDF5_PATH}\n  -> Run bow07_real_pieces.py first."

    # 2. Restore matcher from HDF5 (centroids + histograms are fully recovered)
    print(f"[Load] Restoring model from '{os.path.basename(HDF5_PATH)}'...")
    matcher = ColorBoWMatcher.load(HDF5_PATH)

    print(f"[Load] Config from     '{os.path.basename(YAML_PATH)}'  (verification):")
    print(f"         n_words = {matcher.n_words}  |  metric = {matcher.metric}")
    print(f"[Model] {len(matcher.group_labels_)} database piece histograms, "
          f"{matcher.n_words} vocabulary words.")

    # 3. Load pieces01 RGB for the left panel of the visualization
    img1_rgb_path = os.path.join(cpath, 'pieces01_rgb.png')
    img1_seg_path = os.path.join(cpath, 'pieces01_seg.png')
    assert os.path.exists(img1_rgb_path), f"Missing image: {img1_rgb_path}"
    assert os.path.exists(img1_seg_path), f"Missing image: {img1_seg_path}"

    Irgb1_bgr = cv2.imread(img1_rgb_path, cv2.IMREAD_COLOR)
    Irgb1     = cv2.cvtColor(Irgb1_bgr, cv2.COLOR_BGR2RGB)
    Iseg1_bin = cv2.imread(img1_seg_path, cv2.IMREAD_GRAYSCALE)

    # Rebuild centroids dict for Database 1 pieces (used for arrow anchors)
    num_labels1, labels1 = cv2.connectedComponents((Iseg1_bin > 0).astype(np.uint8))
    centroids1 = {}
    for pid in range(1, num_labels1):
        ys, xs = np.where(labels1 == pid)
        if len(xs) > 0:
            centroids1[str(pid)] = (int(np.mean(xs)), int(np.mean(ys)))

    # 4. Load pieces02 images (query source)
    img2_rgb_path = os.path.join(cpath, 'pieces02_rgb.png')
    img2_seg_path = os.path.join(cpath, 'pieces02_seg.png')
    assert os.path.exists(img2_rgb_path), f"Missing image: {img2_rgb_path}"
    assert os.path.exists(img2_seg_path), f"Missing image: {img2_seg_path}"

    Irgb2_bgr = cv2.imread(img2_rgb_path, cv2.IMREAD_COLOR)
    Irgb2     = cv2.cvtColor(Irgb2_bgr, cv2.COLOR_BGR2RGB)
    Iseg2_bin = cv2.imread(img2_seg_path, cv2.IMREAD_GRAYSCALE)

    # 5. Extract connected components from pieces02 segmentation
    num_labels2, labels2 = cv2.connectedComponents((Iseg2_bin > 0).astype(np.uint8))
    print(f"\n[Dataset 2] Found {num_labels2 - 1} connected components in pieces02.")

    # 6. Prepare side-by-side visualization canvas
    H, W, _ = Irgb1_bgr.shape
    canvas   = np.hstack([Irgb1_bgr.copy(), Irgb2_bgr.copy()])

    np.random.seed(100)
    palette = [tuple(int(c) for c in col)
               for col in np.random.randint(60, 255, (num_labels2 + 10, 3))]

    # 7. Query each pieces02 component against the loaded model
    query_results = []
    print("\n[Query Results] Matching individual pieces02 objects against restored model:")
    print("-" * 65)
    print(f"  {'Query Piece ID':<16} {'Size (px)':<12} {'Matched Piece':<16} {'Chi2 Distance':<15}")
    print("-" * 65)

    for comp_id in range(1, num_labels2):
        mask        = (labels2 == comp_id)
        pixel_count = int(np.sum(mask))

        # Skip noise components
        if pixel_count < 10:
            continue

        query_rgb   = Irgb2[mask].T          # shape (3, N)
        top_match   = matcher.query(query_rgb, top_k=1)[0]
        matched_lbl = top_match['label']
        dist        = top_match['distance']

        query_results.append((comp_id, pixel_count, matched_lbl, dist))
        print(f"  Piece_{comp_id:02d}          {pixel_count:<12d} Piece_{matched_lbl:<10s}    {dist:.6f}")

        # Centroid of this query piece (right panel)
        ys2, xs2 = np.where(mask)
        cx2, cy2 = int(np.mean(xs2)), int(np.mean(ys2))
        pt2 = (cx2 + W, cy2)

        if matched_lbl in centroids1:
            pt1   = centroids1[matched_lbl]
            color = palette[comp_id % len(palette)]
            cv2.arrowedLine(canvas, pt1, pt2, color, thickness=1, tipLength=0.01)
            cv2.circle(canvas, pt1, 4, color, -1)
            cv2.circle(canvas, pt2, 4, color, -1)

    print("-" * 65)
    print(f"[Summary] Queried {len(query_results)} piece objects.")

    # Header text on match canvas
    cv2.putText(canvas, "Dataset 1: Database Model (loaded from HDF5)",
                (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
    cv2.putText(canvas, "Dataset 2: Query Pieces (pieces02)",
                (W + 20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

    # 8. Quantized renderings
    quant1_rgb = matcher.quantizeImage(Irgb1, Iseg1_bin)
    quant2_rgb = matcher.quantizeImage(Irgb2, Iseg2_bin)

    quant1_bgr = cv2.cvtColor(quant1_rgb, cv2.COLOR_RGB2BGR)
    quant2_bgr = cv2.cvtColor(quant2_rgb, cv2.COLOR_RGB2BGR)

    quant_canvas = np.hstack([quant1_bgr, quant2_bgr])
    cv2.putText(quant_canvas, "Dataset 1: Quantized (loaded vocabulary)",
                (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
    cv2.putText(quant_canvas, "Dataset 2: Quantized (loaded vocabulary)",
                (W + 20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

    # 9. Save output images
    vis_path   = os.path.join(cpath, 'bow08_match_visualization.png')
    quant_path = os.path.join(cpath, 'bow08_quantized_comparison.png')
    cv2.imwrite(vis_path,   canvas)
    cv2.imwrite(quant_path, quant_canvas)

    print(f"\n[Output] Saved match visualization  -> '{os.path.basename(vis_path)}'")
    print(f"[Output] Saved quantized comparison -> '{os.path.basename(quant_path)}'")
    print("\nTest bow08_real_pieces Passed Successfully!\n")

    if doDisp:
        display.bgr(canvas,       window_name="Matches (loaded model)")
        display.bgr(quant_canvas, window_name="Quantized (loaded vocabulary)")
        display.wait()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="Load saved BoW model and query pieces02 against it.")
    argparser.add_argument("--display", action='store_true',
                           help="Display output images interactively.")
    opts = argparser.parse_args()

    test_load_and_query(opts.display)
