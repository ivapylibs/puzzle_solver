## @file color_bow.py
#  @brief Bag-of-Words style color matching system using OpenCV K-Means.
#
#  @details
#  Pipeline:
#  -# Pool all RGB samples from every group.
#  -# Run K-Means++ (OpenCV) to auto-discover a color vocabulary of `n_words` centroids.
#  -# Encode each group as a normalized frequency histogram over the vocabulary.
#  -# Match query groups to a database using configurable distance metrics.
#
#  Input contract: each group is a (3, N) numpy ndarray with dtype uint8 or
#  float32 in [0, 255], where row 0 = R channel, row 1 = G channel,
#  row 2 = B channel, and N is the number of pixels/samples (may vary per group).

from __future__ import annotations

import numpy as np
import cv2
from typing import Literal

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

## @typedef RGBMatrix
#  @brief A (3, N) numpy ndarray of dtype uint8 or float32 holding RGB pixel data.
RGBMatrix = np.ndarray

## @typedef Histogram
#  @brief A (n_words,) float32 numpy ndarray representing an L1-normalized BoW histogram.
Histogram = np.ndarray


# ---------------------------------------------------------------------------
# 1.  Vocabulary discovery
# ---------------------------------------------------------------------------

def build_vocabulary(
    groups: list[RGBMatrix],
    n_words: int = 20,
    *,
    max_iter: int = 100,
    epsilon: float = 1.0,
    attempts: int = 5,
    random_seed: int = 42,
) -> np.ndarray:
    """
    @brief Discover a color vocabulary by running K-Means on pooled RGB samples.

    @details
    All samples from every group are concatenated into a single point cloud and
    passed to cv2.kmeans with K-Means++ initialization.  The resulting cluster
    centroids form the "color words" of the vocabulary.  Running multiple
    independent attempts and keeping the best result (lowest compactness) guards
    against degenerate local minima.

    @param groups      List of (3, N) RGB matrices whose pixels will be pooled.
    @param n_words     Number of cluster centroids (vocabulary size). Default 20.
    @param max_iter    Maximum number of K-Means iterations per attempt. Default 100.
    @param epsilon     Convergence threshold in pixel-space Euclidean distance. Default 1.0.
    @param attempts    Number of independent K-Means runs; the best is retained. Default 5.
    @param random_seed NumPy random seed for reproducibility. Default 42.

    @return (n_words, 3) float32 ndarray of centroid RGB values -- the color vocabulary.
    """
    # Stack all samples into a single (M, 3) float32 matrix
    all_samples = np.hstack(groups).T.astype(np.float32)  # (M, 3)

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        max_iter,
        epsilon,
    )
    flags = cv2.KMEANS_PP_CENTERS  # k-means++ initialisation (better coverage)

    np.random.seed(random_seed)
    _, _, centroids = cv2.kmeans(
        all_samples,
        n_words,
        None,
        criteria,
        attempts,
        flags,
    )
    return centroids  # (n_words, 3), float32


# ---------------------------------------------------------------------------
# 2.  Histogram encoding
# ---------------------------------------------------------------------------

def encode_histogram(
    group: RGBMatrix,
    centroids: np.ndarray,
    *,
    normalize: bool = True,
) -> Histogram:
    """
    @brief Encode a single group as a Bag-of-Words histogram over the color vocabulary.

    @details
    Each pixel in the group is hard-assigned to its nearest centroid in RGB space
    using squared Euclidean distance computed via broadcasting.  The resulting
    assignment indices are tallied with numpy.bincount to produce a raw frequency
    vector, which is optionally L1-normalized so that groups of different sizes
    are directly comparable.

    @param group      (3, N) RGB matrix for a single group.
    @param centroids  (n_words, 3) float32 vocabulary returned by build_vocabulary().
    @param normalize  If True (default), L1-normalize the histogram so it sums to 1.

    @return (n_words,) float32 histogram over the color vocabulary.
    """
    samples = group.T.astype(np.float32)          # (N, 3)
    n_words = centroids.shape[0]

    # Compute squared Euclidean distances: (N, n_words)
    # Using broadcasting: each row of `samples` minus each centroid.
    diff = samples[:, np.newaxis, :] - centroids[np.newaxis, :, :]  # (N, K, 3)
    sq_dists = (diff ** 2).sum(axis=2)                               # (N, K)

    assignments = sq_dists.argmin(axis=1)          # (N,) -- nearest centroid index

    hist = np.bincount(assignments, minlength=n_words).astype(np.float32)

    if normalize and hist.sum() > 0:
        hist /= hist.sum()

    return hist


def encode_all(
    groups: list[RGBMatrix],
    centroids: np.ndarray,
    *,
    normalize: bool = True,
) -> list[Histogram]:
    """
    @brief Encode every group in the list into a BoW histogram.

    @details
    Convenience wrapper that calls encode_histogram() on each element of
    @p groups using the shared @p centroids vocabulary.

    @param groups     List of (3, N) RGB matrices.
    @param centroids  (n_words, 3) float32 vocabulary from build_vocabulary().
    @param normalize  If True (default), L1-normalize each histogram.

    @return List of (n_words,) float32 histograms, one per group.
    """
    return [encode_histogram(g, centroids, normalize=normalize) for g in groups]


# ---------------------------------------------------------------------------
# 3.  Distance / similarity metrics
# ---------------------------------------------------------------------------

## @typedef DistanceMetric
#  @brief Literal type enumerating supported histogram distance metrics.
#  Valid values: "chi2", "intersection", "hellinger", "l2", "cosine".
DistanceMetric = Literal["chi2", "intersection", "hellinger", "l2", "cosine"]


def histogram_distance(
    h1: Histogram,
    h2: Histogram,
    metric: DistanceMetric = "chi2",
) -> float:
    """
    @brief Compute a scalar distance between two normalized BoW histograms.

    @details
    All returned values are distances (lower = more similar).  Supported metrics:
    - **chi2**         : Chi-Squared distance; sensitive to differences in rare color words.
                         Formula: sum((h1-h2)^2 / (h1+h2+eps))
    - **intersection** : 1 - Histogram Intersection similarity (via cv2.compareHist).
    - **hellinger**    : Bhattacharyya / Hellinger distance (via cv2.compareHist);
                         robust to outliers and scale differences.
    - **l2**           : Standard Euclidean distance.
    - **cosine**       : 1 - Cosine similarity; ignores magnitude, focuses on direction.

    @param h1      First (n_words,) float32 histogram.
    @param h2      Second (n_words,) float32 histogram.
    @param metric  Distance metric to use. Default "chi2".

    @return Scalar float distance value (lower = more similar).

    @throws ValueError if @p metric is not one of the supported strings.
    """
    h1 = h1.astype(np.float64)
    h2 = h2.astype(np.float64)

    if metric == "chi2":
        # Chi-Squared: sum((h1-h2)^2 / (h1+h2+eps))
        eps = 1e-10
        return float(np.sum((h1 - h2) ** 2 / (h1 + h2 + eps)))

    elif metric == "intersection":
        # OpenCV HISTCMP_INTERSECT returns similarity; convert to distance.
        similarity = cv2.compareHist(
            h1.astype(np.float32),
            h2.astype(np.float32),
            cv2.HISTCMP_INTERSECT,
        )
        return float(1.0 - similarity)

    elif metric == "hellinger":
        return float(cv2.compareHist(
            h1.astype(np.float32),
            h2.astype(np.float32),
            cv2.HISTCMP_BHATTACHARYYA,
        ))

    elif metric == "l2":
        return float(np.linalg.norm(h1 - h2))

    elif metric == "cosine":
        denom = (np.linalg.norm(h1) * np.linalg.norm(h2))
        if denom < 1e-10:
            return 1.0
        return float(1.0 - np.dot(h1, h2) / denom)

    else:
        raise ValueError(f"Unknown metric: {metric!r}")


# ---------------------------------------------------------------------------
# 4.  Matcher
# ---------------------------------------------------------------------------

class ColorBoWMatcher:
    """
    @brief End-to-end Bag-of-Words color matcher.

    @details
    Encapsulates the full BoW pipeline: vocabulary discovery via K-Means++,
    histogram encoding for a database of groups, and ranked retrieval of the
    closest matches to a query group.

    Typical usage:
    @code
    matcher = ColorBoWMatcher(n_words=20)
    matcher.fit(groups)               # build vocabulary + encode database
    results = matcher.query(q_group)  # rank database groups by similarity
    @endcode
    """

    def __init__(
        self,
        n_words: int = 20,
        metric: DistanceMetric = "chi2",
        **kmeans_kwargs,
    ):
        """
        @brief Initialise the matcher with vocabulary size and distance metric.

        @param n_words        Number of K-Means cluster centroids (vocabulary size). Default 20.
        @param metric         Distance metric for histogram comparison. Default "chi2".
        @param kmeans_kwargs  Additional keyword arguments forwarded to build_vocabulary()
                              (e.g., max_iter, epsilon, attempts, random_seed).
        """
        self.n_words = n_words
        self.metric = metric
        self._kmeans_kwargs = kmeans_kwargs

        ## @var centroids_
        #  @brief (n_words, 3) float32 array of discovered color centroids. None before fit().
        self.centroids_: np.ndarray | None = None

        ## @var histograms_
        #  @brief List of encoded BoW histograms, one per database group.
        self.histograms_: list[Histogram] = []

        ## @var group_labels_
        #  @brief Human-readable labels for each database group.
        self.group_labels_: list[str] = []

    # ------------------------------------------------------------------
    # Fitting (vocabulary discovery + database encoding)
    # ------------------------------------------------------------------

    #======================= fitFromImageSegmented =======================

    def fitFromImageSegmented(self, Irgb: np.ndarray, Iseg: np.ndarray, hasLabs: bool = False) -> "ColorBoWMatcher":
        """!
        @brief  Given an image and a segmentation, generate BoW fit.

        @details
        Permits fitting based on two images, one with all objects of interest
        in it as a color image.  The next as a segmentation isolating the objects.
        If should be considered binary in nature, then no labels assumed.  If it
        has labels (each unique value is the label), then snag from Iseg as labels.

        @param[in]  Irgb    Source color image.
        @param[in]  Iseg    Binary segmentation of image, or label segmentation.
        @param[in]  hasLabs Iseg has labels (True) or is interpreted as binary (False). Default: False.

        @return Self, to allow method chaining.
        """
        groups: list[RGBMatrix] = []

        Iseg_2d = np.squeeze(Iseg) if (Iseg.ndim == 3 and Iseg.shape[2] == 1) else Iseg

        if hasLabs:
            labels: list[str] = []
            unique_labs = np.unique(Iseg_2d[Iseg_2d != 0])
            for lab in unique_labs:
                mask = (Iseg_2d == lab)
                if Irgb.ndim == 3 and Irgb.shape[2] == 3:
                    pixels = Irgb[mask].T
                elif Irgb.ndim == 3 and Irgb.shape[0] == 3:
                    pixels = Irgb[:, mask]
                else:
                    pixels = Irgb[mask].T

                if pixels.shape[1] > 0:
                    groups.append(pixels)
                    labels.append(str(lab))

            if not groups:
                raise ValueError("No non-zero segmentation pixels found in Iseg.")

            return self.fit(groups, labels=labels)
        else:
            mask = (Iseg_2d != 0)
            if Irgb.ndim == 3 and Irgb.shape[2] == 3:
                pixels = Irgb[mask].T
            elif Irgb.ndim == 3 and Irgb.shape[0] == 3:
                pixels = Irgb[:, mask]
            else:
                pixels = Irgb[mask].T

            if pixels.shape[1] > 0:
                groups.append(pixels)

            if not groups:
                raise ValueError("No non-zero segmentation pixels found in Iseg.")

            return self.fit(groups)

    def fit(
        self,
        groups: list[RGBMatrix],
        labels: list[str] | None = None,
    ) -> "ColorBoWMatcher":
        """
        @brief Build the color vocabulary and encode all groups as BoW histograms.

        @details
        Calls build_vocabulary() on the pooled pixel data from all groups to
        discover centroids, then calls encode_all() to convert each group into a
        normalized frequency histogram.  Must be called before query().

        @param groups  List of (3, N) RGB matrices forming the database.
        @param labels  Optional list of human-readable names, one per group.
                       Auto-generated as "group_0", "group_1", ... if None.

        @return Self, to allow method chaining (e.g., matcher.fit(groups).query(q)).

        @throws ValueError if len(labels) != len(groups).
        """
        if labels is None:
            labels = [f"group_{i}" for i in range(len(groups))]
        if len(labels) != len(groups):
            raise ValueError("`labels` length must match `groups` length.")

        self.group_labels_ = list(labels)
        self.centroids_ = build_vocabulary(
            groups, n_words=self.n_words, **self._kmeans_kwargs
        )
        self.histograms_ = encode_all(groups, self.centroids_)
        return self

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def query(
        self,
        query_group: RGBMatrix,
        top_k: int | None = None,
    ) -> list[dict]:
        """
        @brief Rank all database groups by color similarity to a query group.

        @details
        Encodes @p query_group into a BoW histogram using the fitted vocabulary,
        then computes the configured distance metric against every database
        histogram.  Results are returned sorted by ascending distance
        (rank 1 = most similar).

        @param query_group  (3, N) RGB matrix of the query sample.
        @param top_k        If set, return only the top-k closest matches.
                            Returns all database groups if None (default).

        @return List of dicts sorted by ascending distance, e.g.:
                [{"rank": 1, "label": "group_2", "distance": 0.031}, ...]

        @throws RuntimeError if fit() has not been called.
        """
        if self.centroids_ is None:
            raise RuntimeError("Call .fit() before .query().")

        q_hist = encode_histogram(query_group, self.centroids_)

        distances = [
            histogram_distance(q_hist, db_hist, metric=self.metric)
            for db_hist in self.histograms_
        ]

        ranked = sorted(
            [
                {"rank": 0, "label": lbl, "distance": dist}
                for lbl, dist in zip(self.group_labels_, distances)
            ],
            key=lambda x: x["distance"],
        )
        for i, entry in enumerate(ranked):
            entry["rank"] = i + 1

        return ranked[:top_k] if top_k is not None else ranked

    def query_histogram(self, query_hist: Histogram, top_k: int | None = None) -> list[dict]:
        """
        @brief Rank database groups by similarity to a pre-computed query histogram.

        @details
        Identical to query() but accepts an already-encoded histogram directly,
        avoiding redundant encoding when the caller has pre-computed it.

        @param query_hist  (n_words,) float32 histogram to match against the database.
        @param top_k       If set, return only the top-k closest matches.
                           Returns all database groups if None (default).

        @return List of dicts sorted by ascending distance:
                [{"rank": 1, "label": "group_2", "distance": 0.031}, ...]

        @throws RuntimeError if fit() has not been called.
        """
        if self.centroids_ is None:
            raise RuntimeError("Call .fit() before .query_histogram().")

        distances = [
            histogram_distance(query_hist, db_hist, metric=self.metric)
            for db_hist in self.histograms_
        ]

        ranked = sorted(
            [
                {"rank": 0, "label": lbl, "distance": dist}
                for lbl, dist in zip(self.group_labels_, distances)
            ],
            key=lambda x: x["distance"],
        )
        for i, entry in enumerate(ranked):
            entry["rank"] = i + 1

        return ranked[:top_k] if top_k is not None else ranked

    # ------------------------------------------------------------------
    # Inspection helpers
    # ------------------------------------------------------------------

    def vocabulary_as_image(self, swatch_size: int = 60) -> np.ndarray:
        """
        @brief Render the discovered color vocabulary as a row of solid-color swatches.

        @details
        Produces a BGR image of shape (swatch_size, n_words * swatch_size, 3) where
        each square block is filled with the RGB color of one centroid.  Useful for
        visually inspecting the quality and spread of the discovered vocabulary.

        @param swatch_size  Pixel width and height of each color swatch. Default 60.

        @return (swatch_size, n_words * swatch_size, 3) uint8 BGR image.

        @throws RuntimeError if fit() has not been called.
        """
        if self.centroids_ is None:
            raise RuntimeError("Call .fit() first.")

        swatches = []
        for rgb in self.centroids_.astype(np.uint8):
            swatch = np.full((swatch_size, swatch_size, 3), rgb[::-1], dtype=np.uint8)  # RGB->BGR
            swatches.append(swatch)
        return np.hstack(swatches)

    def histogram_image(
        self,
        group_idx: int,
        width: int = 600,
        height: int = 200,
    ) -> np.ndarray:
        """
        @brief Render a color-coded bar chart of a group's BoW histogram.

        @details
        Each bar corresponds to one vocabulary word (centroid) and its height is
        proportional to the word's frequency in the group.  The fill color of each
        bar matches the RGB value of its corresponding centroid, making it easy to
        see which colors dominate a group.  The image is returned in BGR format
        for direct use with OpenCV.

        @param group_idx  Zero-based index of the database group to visualize.
        @param width      Width of the output image in pixels. Default 600.
        @param height     Height of the output image in pixels. Default 200.

        @return (height, width, 3) uint8 BGR bar-chart image.

        @throws RuntimeError if fit() has not been called.
        """
        if not self.histograms_:
            raise RuntimeError("Call .fit() first.")

        hist = self.histograms_[group_idx]
        img = np.ones((height, width, 3), dtype=np.uint8) * 240  # light grey bg

        bar_w = width // len(hist)
        max_val = hist.max() if hist.max() > 0 else 1.0

        for i, (val, centroid) in enumerate(zip(hist, self.centroids_)):
            bar_h = int((val / max_val) * (height - 20))
            x0, x1 = i * bar_w, (i + 1) * bar_w
            y0, y1 = height - bar_h - 10, height - 10
            color = tuple(int(c) for c in centroid[::-1])  # RGB -> BGR
            cv2.rectangle(img, (x0, y0), (x1, y1), color, -1)
            cv2.rectangle(img, (x0, y0), (x1, y1), (50, 50, 50), 1)

        return img


# ---------------------------------------------------------------------------
# 5.  Demo / smoke-test
# ---------------------------------------------------------------------------

def _make_demo_groups(
    n_groups: int = 5,
    n_pixels_per_group: int = 500,
    n_true_colors: int = 20,
    rng: np.random.Generator | None = None,
) -> tuple[list[RGBMatrix], list[str]]:
    """
    @brief Synthesise synthetic RGB group data for testing and demonstration.

    @details
    Generates @p n_groups groups of (3, N) RGB matrices.  A shared ground-truth
    palette of @p n_true_colors random colors is created; each group is drawn from
    a random subset of 8-15 of those palette colors with small per-pixel Gaussian
    noise added to simulate real-world color variation.

    @param n_groups            Number of groups to generate. Default 5.
    @param n_pixels_per_group  Number of pixels (samples) per group. Default 500.
    @param n_true_colors       Size of the shared underlying color palette. Default 20.
    @param rng                 Optional numpy random Generator for reproducibility.
                               A default_rng(0) is created if None.

    @return Tuple (groups, labels) where groups is a list of (3, N) uint8 RGBMatrix
            arrays and labels is a list of corresponding string identifiers.
    """
    if rng is None:
        rng = np.random.default_rng(0)

    # Random ground-truth palette
    palette = rng.integers(20, 235, size=(n_true_colors, 3), dtype=np.uint8)

    groups: list[RGBMatrix] = []
    labels: list[str] = []
    for g in range(n_groups):
        # Each group samples from a random subset of 8-15 palette colors
        n_active = rng.integers(8, min(15, n_true_colors) + 1)
        active_colors = palette[rng.choice(n_true_colors, n_active, replace=False)]

        pixels = []
        for _ in range(n_pixels_per_group):
            base = active_colors[rng.integers(n_active)]
            noise = rng.integers(-15, 16, size=3)
            pixel = np.clip(base.astype(int) + noise, 0, 255).astype(np.uint8)
            pixels.append(pixel)

        rgb_matrix = np.stack(pixels, axis=1)  # (3, N)
        groups.append(rgb_matrix)
        labels.append(f"group_{g}")

    return groups, labels


if __name__ == "__main__":
    import pprint

    print("=" * 60)
    print("  Color Bag-of-Words Demo")
    print("=" * 60)

    # --- Generate synthetic data -----------------------------------------
    rng = np.random.default_rng(42)
    groups, labels = _make_demo_groups(
        n_groups=5,
        n_pixels_per_group=600,
        n_true_colors=20,
        rng=rng,
    )
    print(f"\n[Data]  {len(groups)} groups, each (3, {groups[0].shape[1]}) RGB matrix")

    # --- Build matcher with auto-discovered vocabulary --------------------
    matcher = ColorBoWMatcher(n_words=20, metric="chi2")
    matcher.fit(groups, labels=labels)

    print(f"\n[Vocabulary]  {matcher.n_words} centroids discovered via K-Means++")
    print("  Centroid RGB values (first 5):")
    for i, c in enumerate(matcher.centroids_[:5]):
        print(f"    word_{i:02d}:  R={c[0]:.0f}  G={c[1]:.0f}  B={c[2]:.0f}")

    # --- Display encoded histograms ---------------------------------------
    print("\n[Histograms]  (normalized, non-zero bins shown)")
    for lbl, hist in zip(labels, matcher.histograms_):
        nonzero = {f"w{i}": f"{v:.3f}" for i, v in enumerate(hist) if v > 0}
        print(f"  {lbl}: {nonzero}")

    # --- Query: use group_0 as the query ---------------------------------
    query_group = groups[0]
    print(f"\n[Query]  Using '{labels[0]}' as query  (metric=chi2)")
    results = matcher.query(query_group)
    pprint.pprint(results)

    # --- Try all metrics -------------------------------------------------
    print("\n[Metric Comparison]  top-1 match for each metric:")
    for m in ("chi2", "intersection", "hellinger", "l2", "cosine"):
        matcher.metric = m
        top = matcher.query(query_group, top_k=2)
        # top[0] is the query itself (distance~0), top[1] is the closest other
        best = top[1] if top[0]["distance"] < 1e-6 else top[0]
        print(f"  {m:15s} ->  {best['label']}  (dist={best['distance']:.4f})")

    # --- Optional: save vocabulary swatch image --------------------------
    vocab_img = matcher.vocabulary_as_image(swatch_size=50)
    cv2.imwrite("color_vocabulary.png", vocab_img)
    print("\n[Output]  Vocabulary swatch saved to  color_vocabulary.png")

    hist_img = matcher.histogram_image(group_idx=0)
    cv2.imwrite("histogram_group0.png", hist_img)
    print("[Output]  Histogram image saved to   histogram_group0.png")

    print("\nDone.")
