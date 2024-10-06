# ================================ puzzle.utils.sideExtractor ================================
#
# @brief    To extract the 4 sides from a regular puzzle piece template.
#           Credit from https://github.com/ralbertazzi/jigsaw-puzzle-solver
#           See details in https://towardsdatascience.com/solving-jigsaw-puzzles-with-python-and-opencv-d775ba730660?gi=7f5f85686413
#
# ================================ puzzle.utils.sideExtractor ================================
#
# @file     sideExtractor.py
#
# @author   Riccardo Albertazzi
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2018/09/29 [created]
# @date     2021/08/17 [created]
#
#
# ================================ puzzle.utils.sideExtractor ================================

# ===== Environment / Dependencies
#

import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
from sklearn.cluster import KMeans
from camera.utils import display

from puzzle.utils.imageProcessing import rotate_im

# ===== Helper Elements
#
# LEFT, RIGHT, TOP, BOTTOM
_corner_indexes = [(0, 2), (1, 3), (0, 1), (3, 2)]


# ===== Utils Functions
#
def get_line_through_points(p0, p1):
    """
    Given two points p0 (x0, y0) and p1 (x1, y1),
    compute the coefficients (a, b, c) of the line
    that passes through both points.
    """
    x0, y0 = p0
    x1, y1 = p1

    return y1 - y0, x0 - x1, x1 * y0 - x0 * y1


def distance_point_line_squared(line_param, pts):
    """
    Computes the squared distance of a 2D point (x0, y0) from a line ax + by + c = 0
    """

    a, b, c = line_param
    x0, y0 = pts

    return (a * x0 + b * y0 + c) ** 2 / (a ** 2 + b ** 2)


def distance_point_line_signed(line_param, pts):
    """
    Computes the signed distance of a 2D point (x0, y0) from a line ax + by + c = 0
    """

    a, b, c = line_param
    x0, y0 = pts

    return (a * x0 + b * y0 + c) / np.sqrt(a ** 2 + b ** 2)


def rotate(image, degrees):
    """
    Rotate an image by the amount specified in degrees
    """

    if len(image.shape) == 3:
        rows, cols, _ = image.shape
    else:
        rows, cols = image.shape

    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), degrees, 1)

    return cv2.warpAffine(image, M, (cols, rows)), M


# ===== Main Functions
#
def compute_barycentre(thresh, value=0):
    """
    Given the segmented puzzle piece, compute its barycentre.
    """
    idx_shape = np.where(thresh == value)
    return [int(np.round(coords.mean())) for coords in idx_shape]


def compute_minmax_xy(thresh):
    """
    Given the thresholded image, compute the minimum and maximum x and y
    coordinates of the segmented puzzle piece.
    """
    idx_shape = np.where(thresh == 0)
    return [np.array([coords.min(), coords.max()]) for coords in idx_shape]


# def segment_piece(image, bin_threshold=128):
#     """
#     Apply segmentation of the image by simple binarization
#     """
#     return cv2.threshold(image, bin_threshold, 255, cv2.THRESH_BINARY)[1]


# def extract_piece(thresh):
#
#   # Here we build a square image centered on the blob (piece of the puzzle).
#   # The image is constructed large enough to allow for piece rotations.
#
#   minmax_y, minmax_x = compute_minmax_xy(thresh)
#
#   ly, lx = minmax_y[1] - minmax_y[0], minmax_x[1] - minmax_x[0]
#   size = int(max(ly, lx) * np.sqrt(2))
#
#   x_extract = thresh[minmax_y[0]:minmax_y[1] + 1, minmax_x[0]:minmax_x[1] + 1]
#   ly, lx = x_extract.shape
#
#   xeh, xew = x_extract.shape
#   x_copy = np.full((size, size), 255, dtype='uint8')
#   sy, sx = size // 2 - ly // 2, size // 2 - lx // 2
#
#   x_copy[sy: sy + ly, sx: sx + lx] = x_extract
#   thresh = x_copy
#   thresh = 255 - thresh
#   return thresh

def prune_lines_by_voting(lines, angle_threshold=5):
    accumulator = np.zeros(45)
    angles = lines[:, 1] * 180 / np.pi
    angles[angles >= 135] = 180 - angles[angles >= 135]
    angles[angles >= 90] -= 90
    angles[angles >= 45] = 90 - angles[angles >= 45]

    for angle, weight in zip(angles, np.linspace(1, 0.5, len(lines))):

        angle = int(np.round(angle))

        def add(a, w):
            if a >= 0 and a < len(accumulator):
                accumulator[a] += w

        add(angle - 3, weight * 0.1)
        add(angle - 2, weight * 0.5)
        add(angle - 1, weight * 0.8)
        add(angle, weight)
        add(angle + 1, weight * 0.8)
        add(angle + 2, weight * 0.5)
        add(angle + 3, weight * 0.1)

    # print accumulator
    best_angle = np.argmax(accumulator)
    print('best angle', best_angle)
    return lines[np.abs(angles - best_angle) <= angle_threshold]


def compute_mean_line(lines, debug=False):
    if len(lines) == 1:
        return lines[0]

    neg_idx = np.where(lines[:, 0] < 0)
    lines = lines.copy()
    lines[neg_idx, 0] = np.abs(lines[neg_idx, 0])
    lines[neg_idx, 1] = lines[neg_idx, 1] - np.pi

    weights = np.linspace(1.0, 0.5, len(lines))

    rhos = np.abs(lines[:, 0])
    mean_rho, std_rho = np.mean(rhos), np.std(rhos)

    gaussian_weigthts = np.array([scipy.stats.norm(mean_rho, std_rho).pdf(r) for r in rhos])
    weights *= gaussian_weigthts

    sum_weights = np.sum(weights)

    # Compute weighted sum
    m_rho = np.sum(rhos * weights) / sum_weights

    sines, cosines = np.sin(lines[:, 1]), np.cos(lines[:, 1])

    m_sine = np.sum(sines * weights) / sum_weights
    m_cosine = np.sum(cosines * weights) / sum_weights
    m_theta = np.arctan2(m_sine, m_cosine)

    if debug:
        # print(correction_factor)
        print(weights)
        # print

    return np.array([m_rho, m_theta])


def line_intersection(line1, line2):
    # Solve the linear system that computes the intersection between
    # two lines, each one defined as a tuple (rho, theta) (the result comes from Hough lines)
    # If the lines have the same theta (parallel lines), a None result is returned

    rho1, theta1 = line1
    rho2, theta2 = line2

    if theta1 == theta2:
        return None, None

    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])
    b = np.array([[rho1], [rho2]])

    x0, y0 = np.linalg.solve(A, b)
    x0, y0 = int(np.round(x0)), int(np.round(y0))

    return x0, y0


def compute_intersections(mean_lines, size):
    h, w = size
    intersections = []

    for i, line_i in enumerate(mean_lines):
        for j, line_j in enumerate(mean_lines[i + 1:], start=i + 1):

            x0, y0 = line_intersection(line_i, line_j)

            if x0 >= 0 and y0 >= 0 and x0 < w and y0 < h:
                intersections.append([x0, y0])

    return np.array(intersections)


def corner_detection(edges, intersections, pts, rect_size=50, show=False):
    xb, yb = pts
    # Find corners by taking the highest distant point from a 45 degrees inclined line
    # inside a squared ROI centerd on the previously found intersection point.
    # Inclination of the line depends on which corner we are looking for, and is
    # computed based on the position of the barycenter of the piece.

    corners = []

    for idx, intersection in enumerate(intersections):

        xi, yi = intersection

        m = -1 if (yb - yi) * (xb - xi) > 0 else 1
        y0 = 0 if yb < yi else 2 * rect_size
        x0 = 0 if xb < xi else 2 * rect_size

        a, b, c = m, -1, -m * x0 + y0

        rect = edges[yi - rect_size: yi + rect_size, xi - rect_size: xi + rect_size].copy()

        edge_idx = np.nonzero(rect)
        if len(edge_idx[0]) > 0:
            distances = [(a * edge_x + b * edge_y + c) ** 2 for edge_y, edge_x in zip(*edge_idx)]
            corner_idx = np.argmax(distances)

            rect_corner = np.array((edge_idx[1][corner_idx], edge_idx[0][corner_idx]))
            offset_corner = rect_corner - rect_size
            real_corner = intersection + offset_corner

            corners.append(real_corner)
        else:
            # If the window is completely black I can make no assumption: I keep the same corner
            corners.append(intersection)

        if show:
            plt.subplot(220 + idx + 1)
            cv2.circle(rect, tuple(rect_corner), 5, 128)

            plt.title("{0} | {1}".format(intersection, (x0, y0)))
            plt.imshow(rect)

    if show:
        plt.show()

    return corners


def order_corners(corners):
    corners.sort(key=lambda k: k[0] + k[1])
    antidiag_corners = sorted(corners[1:3], key=lambda k: k[1])
    corners[1:3] = antidiag_corners
    return corners


def compute_line_params(corners):
    return [get_line_through_points(corners[i1], corners[i2]) for i1, i2 in _corner_indexes]


def shape_classification(edges, line_params, d_threshold=500, n_hs=10):
    # First part: we take all edge points and classify them only if their distance to one of the 4 piece
    # lines is smaller than a certain threshold. If that happens, we can be certain that the point belongs
    # to that side of the piece. If each one of the four distances is higher than the threshold, the point
    # will be classified during the second phase.

    y_nonzero, x_nonzero = np.nonzero(edges)
    distances = []

    class_image = np.zeros(edges.shape, dtype='uint8')
    non_classified_points = []

    for x_edge, y_edge in zip(x_nonzero, y_nonzero):
        d = [distance_point_line_squared(line_param, (x_edge, y_edge)) for line_param in line_params]
        if np.min(d) < d_threshold:
            # Edge 1-4
            class_image[y_edge, x_edge] = np.argmin(d) + 1
        else:
            non_classified_points.append((x_edge, y_edge))

    non_classified_points = np.array(non_classified_points)

    # Second part: hysteresis classification
    # Edge points that have not been classified because they are too far from all lines
    # will be classified based on their neighborhood: if the neighborhood of a point contains
    # an already classified point, it will be classified with the same class.
    # It's very unlikely that the neighborhood of a non classified point will contain two different
    # classes, so we just take the first non-zero value that we find inside the neighborhood
    # The process is repeated and at each iteration the newly classified points are removed from the ones
    # that still need to be classified. The process is interrupted when no new point has been classified
    # or when a maximum number of iterations has been reached (in case of a noisy points that has no neighbours).

    map_iteration = 0
    max_map_iterations = 50

    while map_iteration < max_map_iterations:

        map_iteration += 1
        classified_points_at_current_iteration = []

        for idx, (x_edge, y_edge) in enumerate(non_classified_points):

            neighborhood = class_image[y_edge - n_hs: y_edge + n_hs + 1, x_edge - n_hs: x_edge + n_hs + 1]
            n_mapped = np.nonzero(neighborhood)
            if len(n_mapped[0]) > 0:
                ny, nx = n_mapped[0][0] - n_hs, n_mapped[1][0] - n_hs
                class_image[y_edge, x_edge] = class_image[y_edge + ny, x_edge + nx]
                classified_points_at_current_iteration.append(idx)

        if len(non_classified_points) > 0:
            non_classified_points = np.delete(non_classified_points, classified_points_at_current_iteration, axis=0)
        else:
            break

    return class_image


def compute_inout(class_image, line_params, pts, d_threshold=10):
    """
    Given the full class image, the line parameters and the coordinates of the barycenter,
    compute for each side if the curve of the piece goes inside (in) or outside (out).
    This is done by computing the mean coordinates for each class and see if the signed distance
    from the corners' line has the same sign of the signed distance of the barycenter. If that
    true, the two points lie on the same side and we have a in; otherwise we have a out.
    To let the points of the curve to contribute more to the mean point calculation, only the
    signed distances that are greater than a threshold are used.
    """

    xb, yb = pts

    inout = []

    for line_param, cl in zip(line_params, (1, 2, 3, 4)):

        coords = np.array([zip(*np.where(class_image == cl))])[0]

        distances = np.array([distance_point_line_signed(line_param, (x0, y0)) for y0, x0 in coords])
        distances = distances[np.abs(distances) > d_threshold]

        if len(distances) > 30:
            m_dist = np.mean(distances)

            b_dist = distance_point_line_signed(line_param, (xb, yb))

            if b_dist * m_dist > 0:
                # inout.append('in')
                inout.append(1)
            else:
                # inout.append('out')
                inout.append(2)
        else:
            # inout.append('flat')
            inout.append(3)

    return inout


def create_side_images_simple(class_image, inout, corners):
    side_images = []

    for cl in (1, 2, 3, 4):
        side_image = np.zeros(class_image.shape, dtype='uint8')
        side_image[class_image == cl] = cl
        side_images.append(side_image)

    return side_images


def create_side_images(class_image, inout, corners):
    how_to_rotate = [(90, -90), (180, 0), (-90, 90), (0, 180)]
    side_images = []

    for cl in (1, 2, 3, 4):

        side_image = np.zeros(class_image.shape, dtype='uint8')
        side_image[class_image == cl] = cl

        io = inout[cl - 1]
        htw = how_to_rotate[cl - 1]
        side_corners_idx = _corner_indexes[cl - 1]

        htw = htw[0] if io == 'in' else htw[1]
        side_image_rot, M = rotate(side_image, htw)

        side_corners = np.array(np.round([M.dot((corners[corner_idx][0], corners[corner_idx][1], 1))
                                          for corner_idx in side_corners_idx])).astype(int)

        # Order the corners from higher (smaller y coordinate)
        if side_corners[0, 1] > side_corners[1, 1]:
            side_corners = side_corners[::-1]

        # Correct the angle on each side separately
        if side_corners[0, 0] != side_corners[1, 0]:
            m = float(side_corners[1, 1] - side_corners[0, 1]) / (side_corners[1, 0] - side_corners[0, 0])
            corners_angle = np.arctan(m) * 180 / np.pi
            correction_angle = - (corners_angle / abs(corners_angle) * 90 - corners_angle)

            side_image_rot, M = rotate(side_image_rot, correction_angle)

        side_image_rot[side_image_rot <= 0.5] = 0
        side_image_rot[side_image_rot > 0.5] = 1

        nz = np.nonzero(side_image_rot)
        min_y, max_y, min_x, max_x = np.min(nz[0]), np.max(nz[0]), np.min(nz[1]), np.max(nz[1])
        side_image_rot = side_image_rot[min_y:max_y + 1, min_x:max_x + 1]

        side_images.append(side_image_rot)

    return side_images


def plot_side_images(side_images, inout):
    for cl, (side_image, io) in enumerate(zip(side_images, inout), start=1):
        plt.subplot(220 + cl)
        plt.title("{0} {1}".format(cl, io))
        plt.imshow(cv2.dilate(side_image, (3, 3)))


def draw_lines(image, lines, color):
    for rho, theta in lines:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))

        cv2.line(image, (x1, y1), (x2, y2), color, 2)

    return image


def cluster_lines(lines):
    # split based on angle
    sines = np.sin(lines[:, 1])
    ordinates = np.abs(lines[:, 0])

    kmeans_angle = KMeans(n_clusters=2).fit(sines.reshape(-1, 1))
    ord0 = ordinates[kmeans_angle.labels_ == 0]
    ord1 = ordinates[kmeans_angle.labels_ == 1]

    print(sines[kmeans_angle.labels_ == 0])
    print(sines[kmeans_angle.labels_ == 1])

    # split based on ordinate
    kmeans_lines0 = KMeans(n_clusters=2).fit(ord0.reshape(-1, 1))
    kmeans_lines1 = KMeans(n_clusters=2).fit(ord1.reshape(-1, 1))

    count_lines0 = 0
    count_lines1 = 0

    final_labels = []
    for idx in range(len(lines)):
        angle_label = kmeans_angle.labels_[idx]
        if angle_label == 0:
            coord_label = kmeans_lines0.labels_[count_lines0]
            count_lines0 += 1

            if coord_label == 0:
                final_labels.append(0)
            else:
                final_labels.append(1)
        else:
            coord_label = kmeans_lines1.labels_[count_lines1]
            count_lines1 += 1

            if coord_label == 0:
                final_labels.append(2)
            else:
                final_labels.append(3)

    return np.array(final_labels)


#================================= get_corners =================================
#
def get_corners(dst, neighborhood_size=5, score_factor=0.2, minmax_factor=0.2):
    """
    @brief  Given the input Harris image (where in each pixel the Harris function is
            computed), extract discrete corners satisfying detection constraints.

    @param[in]  dst
    @param[in]  neighborhood_size
    @param[in]  score_threshold
    @param[in]  minmax_threshold

    @param[out] xy ??
    """

    # @note Not documented, so unsure if processing is optimal / uses libraries well.
    #       May need to more rigorously review later. PAV 2023/11/13.

    data = dst.copy()       # Will be modified and manipulated, hence copy.

    #DEBUG
    #print('get_corners')
    #print(f'max and lower bar: {[dst.max(), score_factor * dst.max()]}')

    data[data < score_factor * dst.max()] = 0.

    #DEBUG
    #print(np.sum(data>0))
    #print(f'unique = {np.unique(dst.flatten())}')

    data_max = filters.maximum_filter(data, neighborhood_size, mode='constant', cval = 0)
    maxima   = (data == data_max)
    data_min = filters.minimum_filter(data, neighborhood_size, mode='constant', cval = 0)
    diff     = ((data_max - data_min))

    #DEBUG
    #print(f'data_max unique = {np.unique(data_max.flatten())}')
    #print(np.sum(data_max>0))
    #diff     = ((data_max - data_min) > minmax_threshold)
    #print(np.max(diff))
    #print(f'diff unique = {np.unique(diff.flatten())}')

    diff  = diff >= minmax_factor*np.max(diff) # minmax_threshold 
    maxima[diff == 0] = 0

    # WHY NOT JUST GET TOP FOUR??? WOULDN'T THAT BE MORE ROBUST?? OTHERWISE
    # THE THRESHOLD CAN GIVE MORE OR LESS THAN FOUR ELEMENTS.
    #
    # @todo AT LEAST OVERRIDE THE minmax_threshold to be a ratio. PAV 2023/11/13.

    labeled, num_objects = ndimage.label(maxima)
    #DEBUG VISUAL
    #plt.imshow(data)
    #plt.figure()
    #plt.imshow(data_max)
    #plt.figure()
    #plt.imshow(labeled)
    #plt.show()
    #print(np.shape(labeled))
    #print(num_objects)
    # slices = ndimage.find_objects(labeled)
    yx = np.array(ndimage.center_of_mass(data, labeled, range(1, num_objects + 1)))
    xy = yx[:, ::-1]

    #DEBUG
    #print(np.sum(maxima))
    #print(yx)

    return xy


def get_best_fitting_rect_coords(xy, d_threshold=30, perp_angle_thresh=20, verbose=0):
    """
    Since we expect the 4 puzzle corners to be the corners of a rectangle, here we take
    all detected Harris corners and we find the best corresponding rectangle.
    We perform a recursive search with max depth = 2:
    - At depth 0 we take one of the input point as the first corner of the rectangle
    - At depth 1 we select another input point (with distance from the first point greater
    than d_threshold) as the second point
    - At depth 2 and 3 we take the other points. However, the lines 01-12 and 12-23 should be
    as perpendicular as possible. If the angle formed by these lines is too much far from the
    right angle, we discard the choice.
    - At depth 3, if a valid candidate (4 points that form an almost perpendicular rectangle) is found,
    we add it to the list of candidates.

    Given a list of candidate rectangles, we then select the best one by taking the candidate that maximizes
    the function: area * Gaussian(rectangularness)
    - area: it is the area of the candidate shape. We expect that the puzzle corners will form the maximum area
    - rectangularness: it is the mse of the candidate shape's angles compared to a 90 degree angles. The smaller
            this value, the most the shape is similar toa rectangle.
    """
    N = len(xy)

    distances = scipy.spatial.distance.cdist(xy, xy)
    distances[distances < d_threshold] = 0

    def compute_angles(xy):

        angles = np.zeros((N, N))

        for i in range(N):
            for j in range(i + 1, N):

                point_i, point_j = xy[i], xy[j]
                if point_i[0] == point_j[0]:
                    angle = 90
                else:
                    angle = np.arctan2(point_j[1] - point_i[1], point_j[0] - point_i[0]) * 180 / np.pi

                angles[i, j] = angle
                angles[j, i] = angle

        return angles

    angles = compute_angles(xy)
    possible_rectangles = []

    def search_for_possible_rectangle(idx, prev_points=[]):

        curr_point = xy[idx]
        depth = len(prev_points)

        if depth == 0:
            right_points_idx = np.nonzero(np.logical_and(xy[:, 0] > curr_point[0], distances[idx] > 0))[0]

            if verbose >= 2:
                print('point', idx, curr_point)

            for right_point_idx in right_points_idx:
                search_for_possible_rectangle(right_point_idx, [idx])

            if verbose >= 2:
                print('')

            return

        last_angle = angles[idx, prev_points[-1]]
        perp_angle = last_angle - 90
        if perp_angle < 0:
            perp_angle += 180

        if depth in (1, 2):

            if verbose >= 2:
                print('\t' * depth, 'point', idx, '- last angle', last_angle, '- perp angle', perp_angle)

            diff0 = np.abs(angles[idx] - perp_angle) <= perp_angle_thresh
            diff180_0 = np.abs(angles[idx] - (perp_angle + 180)) <= perp_angle_thresh
            diff180_1 = np.abs(angles[idx] - (perp_angle - 180)) <= perp_angle_thresh
            all_diffs = np.logical_or(diff0, np.logical_or(diff180_0, diff180_1))

            diff_to_explore = np.nonzero(np.logical_and(all_diffs, distances[idx] > 0))[0]

            if verbose >= 2:
                print('\t' * depth, 'diff0:', np.nonzero(diff0)[0], 'diff180:', np.nonzero(diff180_0)[0],
                      'diff_to_explore:', diff_to_explore)

            for dte_idx in diff_to_explore:
                if dte_idx not in prev_points:  # unlikely to happen but just to be certain
                    next_points = prev_points[::]
                    next_points.append(idx)

                    search_for_possible_rectangle(dte_idx, next_points)

        if depth == 3:
            angle41 = angles[idx, prev_points[0]]

            diff0 = np.abs(angle41 - perp_angle) <= perp_angle_thresh
            diff180_0 = np.abs(angle41 - (perp_angle + 180)) <= perp_angle_thresh
            diff180_1 = np.abs(angle41 - (perp_angle - 180)) <= perp_angle_thresh
            dist = distances[idx, prev_points[0]] > 0

            if dist and (diff0 or diff180_0 or diff180_1):
                rect_points = prev_points[::]
                rect_points.append(idx)

                if verbose == 2:
                    print('We have a rectangle:', rect_points)

                already_present = False
                for possible_rectangle in possible_rectangles:
                    if set(possible_rectangle) == set(rect_points):
                        already_present = True
                        break

                if not already_present:
                    possible_rectangles.append(rect_points)

    if verbose >= 2:
        print('Coords', xy)
        print('Distances', distances)
        print('Angles', angles)

    # # Debug only
    # import time
    # start = time.time()

    for i in range(N):
        search_for_possible_rectangle(i)

    # # Debug only
    # end = time.time()-start
    # print(end)
    # if end >5:
    #     debug_mask = np.zeros((400,400))
    #     for i in xy:
    #         cv2.circle(debug_mask,i,5,255,-1)
    #     cv2.imshow('debug',debug_mask)
    #     cv2.waitKey()

    if len(possible_rectangles) == 0:
        return None

    def PolyArea(x, y):
        return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    areas = []
    rectangularness = []
    diff_angles = []

    for r in possible_rectangles:
        points = xy[r]
        areas.append(PolyArea(points[:, 0], points[:, 1]))

        mse = 0
        da = []
        for i1, i2, i3 in [(0, 1, 2), (1, 2, 3), (2, 3, 0), (3, 0, 1)]:
            diff_angle = abs(angles[r[i1], r[i2]] - angles[r[i2], r[i3]])
            da.append(abs(diff_angle - 90))
            mse += (diff_angle - 90) ** 2

        diff_angles.append(da)
        rectangularness.append(mse)

    areas = np.array(areas)
    rectangularness = np.array(rectangularness)

    scores = areas * scipy.stats.norm(0, 150).pdf(rectangularness)
    best_fitting_idxs = possible_rectangles[np.argmax(scores)]

    return xy[best_fitting_idxs]


#============================== get_default_params =============================
#
def get_default_params():
    side_extractor_default_values = {
        # 'before_segmentation_func': partial(cv2.medianBlur, ksize=5),
        # 'bin_threshold': 130,
        # 'after_segmentation_func': None,
        'scale_factor': 1,
        'harris_blocksize': 5,
        'harris_ksize': 5,
        'harris_kfactor' : 0.04,
        'corner_nsize': 5,
        'corner_cull_factor' : 0.2,
        'corner_score_factor': 0.30,
        'corner_minmax_factor': 0.30, 
        'corner_refine_rect_size': 5,
        'edge_erode_size': 3,
        'shape_classification_distance_threshold': 100,
        'shape_classification_nhs': 5,
        'inout_distance_threshold': 5,
        'perp_angle_thresh': 30,
        'd_thresh': 30,
        'enable_rotate': True
    }

    return side_extractor_default_values.copy()


def get_binarymask_params():
    side_extractor_default_values = {
        # 'before_segmentation_func': partial(cv2.medianBlur, ksize=5),
        # 'bin_threshold': 130,
        # 'after_segmentation_func': None,
        'scale_factor': 1,
        'harris_blocksize': 5,
        'harris_ksize': 5,
        'harris_kfactor' : 0.04,
        'corner_nsize': 5,
        'corner_cull_factor' : 0.2,
        'corner_score_factor': 0.30,
        'corner_minmax_factor': 0.30, 
        'corner_refine_rect_size': 5,
        'edge_erode_size': 3,
        'shape_classification_distance_threshold': 100,
        'shape_classification_nhs': 5,
        'inout_distance_threshold': 5,
        'perp_angle_thresh': 30,
        'd_thresh': 30,
        'enable_rotate': True
    }

    return side_extractor_default_values.copy()

# @todo These should really be a part of Regular piece.  That is when they are
#       triggered. Also create a single entry point for the parameters.
#       Placing deep within this is not good.  Should be possible to
#       just invoke this within the Regular piece configuration script.
#       That way it exists externally and can be modified there to work
#       for binary masks.
#       Should work on next.  10/06/2024 - PAV.
#

#================================ sideExtractor ================================
#
def sideExtractor(puzzleTemplate, **kwargs):
    """!
    @brief  Unsure what does.  No documentation. PAV - 2023/11/13.

    @param[in]  puzzleTemplate  Puzzle piece template instance.
    @param[in]  OTHERS. WHO KNOWS.
    """

    params = get_default_params()
    for key in kwargs:
        params[key] = kwargs[key]

    out_dict = {}

    mask    = puzzleTemplate.mask.copy()
    contour = puzzleTemplate.contour.copy()
    image   = puzzleTemplate.image.copy()

    # cv2.imshow('mask',mask)
    # cv2.imshow('contour',contour)
    # cv2.imshow('image',image)
    # cv2.waitKey()

    # To enable cornerHarris to function properly, create an enlarged image

    # @note Should only need to process the mask!! Why others? - PAV 10/06/2024. 
    mask    = np.pad(puzzleTemplate.mask, 10, mode='constant', constant_values=(0,))
    contour = np.pad(puzzleTemplate.contour, 10, mode='constant', constant_values=(0,))
    image   = np.pad(puzzleTemplate.image, ((10,),(10,),(0,)) , mode='constant', constant_values=(0,))

    # REMOVE CODE SINCE REPLACE WITH NP.PAD ABOVE.  NOT SURE WHY DID NOT USE ORIGINALLY.
    # WHAT IS UP WITH STUDENT'S PYTHON CODING SKILLS??
    #
    #mask_enlarged    = np.zeros((mask.shape[0] + 20, mask.shape[1] + 20), dtype='uint8')
    #contour_enlarged = mask_enlarged.copy()
    #image_enlarged = np.zeros((image.shape[0] + 20, image.shape[1] + 20, 3), dtype='uint8')

    #mask_enlarged[10:mask.shape[0] + 10, 10:mask.shape[1] + 10] = mask
    #contour_enlarged[10:contour.shape[0] + 10, 10:contour.shape[1] + 10] = contour
    #image_enlarged[10:image.shape[0] + 10, 10:image.shape[1] + 10, :] = image

    #DEBUG 
    #print("In sideExtractor function.")
    #print(params)
    #print(type(mask))
    #print(type(mask[0,0]))
    #print(np.max(mask))

    #DEBUG VISUAL
    #display.binary_cv(mask, window_name='Mask')
    #display.rgb_cv(image,window_name='Piece')
    #display.binary_cv(contour*255,window_name='Contour')
    #print("OpenCV wait for key")

    harris = cv2.cornerHarris(np.float32(mask), params['harris_blocksize'], 
                                          params['harris_ksize'], params['harris_kfactor'])

    #DEBUG
    #print(f"Harris max is {harris.max()}")

    # Perform a simple thresholding
    i, j = 0, 1
    tauHarris = params['corner_cull_factor'] * harris.max()
    harris_pts = np.argwhere(harris > tauHarris)
    harris_pts.T[[i, j]] = harris_pts.T[[j, i]]

    out_dict['simple_harris_pts'] = harris_pts - 10

    harris = harris * mask

    #DEBUG VISUAL
    #dst = cv2.dilate(harris, None)
    #image[dst > tauHarris] = [0,0,255]
    #display.rgb_cv(image,window_name='Corners')

    # Get set of candidate harris corner position using non-maximum suppression plus
    # additional thresholding on possible candidate set.
    #
    #DEBUG
    #print('--- get corners -->')
    xy = get_corners(harris, params['corner_nsize'], params['corner_score_factor'],
                     params['corner_minmax_factor'])
    #DEBUG
    #print('--- get corners --|')
    xy = np.round(xy / params['scale_factor']).astype(int)
    out_dict['filtered_harris_pts'] = xy - 10

    #DEBUG
    #print(f'xy shape is {np.shape(xy)}')
    #print(f'xy = {xy}')
    #print('--- xy corner check. --|')

    #DEBUG VISUAL : Pick one of two below.
    #display.wait_cv(250)
    #display.wait_cv()

    try:
      if len(xy) < 4:
          raise RuntimeError('Not enough corners')
    except:
        print("UH - OH. Going to crap out now!!! View output then press a key to accept.")
        dst = cv2.dilate(harris, None)
        image[dst > tauHarris] = [0,0,255]
        display.rgb_cv(image,window_name='Corners')
        display.wait_cv()

    # Since there can be more than 4 candidate corner pieces, the next step is to get
    # the four that provide the best rectangle from a puzzle piece perspective.
    #
    intersections = get_best_fitting_rect_coords(xy, d_threshold=params['d_thresh'],
                                                 perp_angle_thresh=params['perp_angle_thresh'])

    #DEBUG
    #print(intersections)

    out_dict['rectangle_pts'] = intersections - 10
    if intersections is None:
        raise RuntimeError('No rectangle found')

    if params['enable_rotate']:
        # Rotate to get a horizontal puzzle piece
        if intersections[1, 0] == intersections[0, 0]:
            rotation_angle = 90
        else:
            rotation_angle = np.arctan2(intersections[1, 1] - intersections[0, 1],
                                        intersections[1, 0] - intersections[0, 0]) * 180 / np.pi
        out_dict['rotation_angle'] = rotation_angle
        edges = contour

        # Without relative translation return
        # edges, mask_temp, M, x_pad, y_pad = rotate_im(edges, rotation_angle)
        # theImage, _, _, _, _ = rotate_im(image_enlarged, rotation_angle, mask=mask_temp)
        # theMask, _, _, _, _ = rotate_im(mask_enlarged, rotation_angle, mask=mask_temp)

        # With relative translation return
        edges, mask_temp, M, x_pad, y_pad, _ = rotate_im(edges, rotation_angle)
        theImage, _, _, _, _, _ = rotate_im(image, rotation_angle, mask=mask_temp)
        theMask, _, _, _, _, _ = rotate_im(mask, rotation_angle, mask=mask_temp)

        # # Debug only
        # masked = cv2.bitwise_and(theImage, theImage, mask=edges)
        # cv2.imshow('demo', edges)
        # cv2.imshow('demo2', theImage)
        # cv2.imshow('demo3', masked)
        # cv2.imshow('demo4', theMask)
        # cv2.waitKey()

        # With Rotation
        # @todo I do not think we need to recover the original image. Not necessary to do that.
        out_dict['edges'] = edges

        # @todo Rotate
        # Rotate intersection points

        intersections = np.array(
            np.round([M.dot((point[0] + x_pad[0], point[1] + y_pad[0], 1)) for point in intersections])).astype(int)

        # With Rotation
        intersections = intersections + np.array([x_pad[1] + x_pad[2], y_pad[1] + y_pad[2]])
        yb, xb = compute_barycentre(theMask)

        # # Debug only
        # for point in intersections:
        #     cv2.circle(theMask,point,3,0,10)
        # cv2.imshow('demo4', theMask)
        # cv2.waitKey()

        # # Refine the corner detections
        corners = corner_detection(edges, intersections, (xb, yb), params['corner_refine_rect_size'], show=False)
        corners = order_corners(corners)

        # corners = intersections
        line_params = compute_line_params(corners)
        class_image = shape_classification(edges, line_params, params['shape_classification_distance_threshold'],
                                           params['shape_classification_nhs'])
        out_dict['class_image'] = class_image

    else:       # without rotation
        out_dict['rotation_angle'] = 0

        edges = contour_enlarged
        out_dict['edges'] = edges[10:mask.shape[0] + 10, 10:mask.shape[1] + 10]

        yb, xb = compute_barycentre(mask_enlarged)

        # # Refine the corner detections
        corners = corner_detection(edges, intersections, (xb, yb), params['corner_refine_rect_size'], show=False)
        corners = order_corners(corners)

        # corners = intersections
        line_params = compute_line_params(corners)
        class_image = shape_classification(edges, line_params, params['shape_classification_distance_threshold'],
                                           params['shape_classification_nhs'])
        out_dict['class_image'] = class_image[10:mask.shape[0] + 10, 10:mask.shape[1] + 10]


    inout = compute_inout(class_image, line_params, (xb, yb), params['inout_distance_threshold'])
    out_dict['inout'] = inout

    side_images = create_side_images_simple(out_dict['class_image'], inout, corners)
    out_dict['side_images'] = side_images

    return out_dict
