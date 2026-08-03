#!/usr/bin/python3
#============================ bow07_real_pieces ============================
##@file
# @brief    Fit a BoW color model on pieces01 image data, then persist the
#           configuration to a YAML file and the fitted model to an HDF5 file.
#
# @details  Connected components are extracted from pieces01_seg.png to provide
#           per-piece labeled pixel groups.  A ColorBoWMatcher vocabulary is
#           discovered from those groups, and the resulting model is serialized:
#             - Configuration (hyper-parameters) -> bow_pieces01.yaml
#             - Fitted state (centroids + histograms) -> bow_pieces01.h5
#           A quantized rendering of pieces01_rgb.png is also saved to disk to
#           visually confirm that the vocabulary has been learned correctly.
#           bow08_real_pieces.py loads both files and runs inference on pieces02.
#
# @ingroup  TestPuzzle_Tracking
#
# @author   Antigravity + Patricio A. Vela, pvela@gatech.edu
# @date     2026/07/30
#
# @quit
#============================ bow07_real_pieces ============================

import os
import cv2
import numpy as np
import argparse

from puzzle.pieces.BoW import ColorBoWMatcher, CfgBoW
import ivapy.display_cv as display

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# Paths for serialized outputs (read by bow08)
YAML_PATH = os.path.join(cpath, 'bow_pieces01.yaml')
HDF5_PATH = os.path.join(cpath, 'bow_pieces01.h5')


def test_fit_and_save(doDisp=False):
    print("=" * 60)
    print("  BoW Test 07: Fit on pieces01 and Save Model to Disk")
    print("=" * 60)

    # 1. Load pieces01 images
    img1_rgb_path = os.path.join(cpath, 'pieces01_rgb.png')
    img1_seg_path = os.path.join(cpath, 'pieces01_seg.png')

    assert os.path.exists(img1_rgb_path), f"Missing image: {img1_rgb_path}"
    assert os.path.exists(img1_seg_path), f"Missing image: {img1_seg_path}"

    Irgb1_bgr = cv2.imread(img1_rgb_path, cv2.IMREAD_COLOR)
    Irgb1     = cv2.cvtColor(Irgb1_bgr, cv2.COLOR_BGR2RGB)
    Iseg1_bin = cv2.imread(img1_seg_path, cv2.IMREAD_GRAYSCALE)

    # 2. Extract connected components (one per puzzle piece)
    num_labels1, labels1 = cv2.connectedComponents((Iseg1_bin > 0).astype(np.uint8))
    print(f"[Dataset 1] Found {num_labels1 - 1} piece connected components in pieces01.")

    # 3. Configure and fit ColorBoWMatcher
    cfg          = CfgBoW()
    cfg.n_words  = 25
    cfg.metric   = "chi2"
    cfg.tau      = 0.5
    matcher      = ColorBoWMatcher(cfg)

    print("Fitting BoW color vocabulary on pieces01 piece components...")
    matcher.fitFromImageSegmented(Irgb1, labels1, hasLabs=True)

    print(f"[Vocabulary] Discovered {matcher.n_words} color words.")
    print(f"[Database]   Model populated with {len(matcher.group_labels_)} piece histograms.")

    # 4. Save configuration to YAML
    matcher.saveToYAML(YAML_PATH)
    print(f"\n[Saved] Configuration  -> '{os.path.basename(YAML_PATH)}'")

    # 5. Save fitted model (centroids + histograms) to HDF5
    matcher.save(HDF5_PATH)
    print(f"[Saved] Fitted model   -> '{os.path.basename(HDF5_PATH)}'")

    # 6. Quantized rendering of pieces01 to confirm vocabulary quality
    quant1_rgb = matcher.quantizeImage(Irgb1, Iseg1_bin)
    quant1_bgr = cv2.cvtColor(quant1_rgb, cv2.COLOR_RGB2BGR)
    quant1_path = os.path.join(cpath, 'bow07_pieces01_quantized.png')
    cv2.imwrite(quant1_path, quant1_bgr)
    print(f"[Saved] Quantized image -> '{os.path.basename(quant1_path)}'")

    # 7. Vocabulary swatch strip
    vocab_swatch = matcher.vocabulary_as_image(swatch_size=40)
    vocab_path   = os.path.join(cpath, 'bow07_vocab_swatches.png')
    cv2.imwrite(vocab_path, vocab_swatch)
    print(f"[Saved] Vocab swatches  -> '{os.path.basename(vocab_path)}'")

    print("\nTest bow07_real_pieces Passed Successfully!\n")

    if doDisp:
        display.bgr(quant1_bgr, window_name="pieces01 Quantized")
        display.bgr(vocab_swatch, window_name="Vocabulary Swatches")
        display.wait()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="Fit BoW model on pieces01 and save to YAML + HDF5.")
    argparser.add_argument("--display", action='store_true',
                           help="Display output images interactively.")
    opts = argparser.parse_args()

    test_fit_and_save(opts.display)
