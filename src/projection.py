"""Validated, nearest-neighbour projection of 3D volumes onto planar regions."""

from itertools import combinations
import math
from typing import Sequence

import numpy as np

try:
    from numba import njit
except ImportError:  # A NumPy implementation remains available without Numba.
    njit = None


EPS = 0.001


def _point(value: Sequence[float], name: str) -> np.ndarray:
    try:
        point = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain three finite coordinates.") from exc

    if point.shape != (3,) or not np.all(np.isfinite(point)):
        raise ValueError(f"{name} must contain three finite coordinates.")
    return point


def _plane_geometry(points: Sequence[Sequence[float]]) -> tuple[
    np.ndarray, np.ndarray, np.ndarray, float, float, float, np.ndarray
]:
    """Validate a supported plane and return its two swept edges and extents.

    Three points are interpreted as ``(a, b, c)``. Four points are interpreted
    as ``(a1, a2, b, c)``: ``a1 -> b`` and ``a2 -> c`` are the equal-length
    sides, and ``a1 -> a2`` is the shorter base.
    """
    if len(points) == 3:
        a, b, c = (_point(point, f"Point {index}")
                   for index, point in enumerate(points, start=1))
        dab = float(np.linalg.norm(b - a))
        dac = float(np.linalg.norm(c - a))
        base = float(np.linalg.norm(c - b))

        if not all(math.isfinite(value) for value in (dab, dac, base)):
            raise ValueError("Three-point coordinates produce an unbounded distance.")
        if abs(dab - dac) >= EPS:
            raise ValueError(
                "Three-point equal-side condition failed: "
                "require |dist(a,b) - dist(a,c)| < 0.001."
            )
        if dab <= EPS or base <= EPS:
            raise ValueError("The three points must define a non-degenerate plane.")
        doubled_area = float(np.linalg.norm(np.cross(b - a, c - a)))
        if not math.isfinite(doubled_area) or doubled_area <= EPS * max(dab, dac, base, 1.0):
            raise ValueError("The three points must not be collinear.")

        return a, a, (b - a) / dab, dab, dac, base, (c - a) / dac

    if len(points) == 4:
        a1, a2, b, c = (_point(point, f"Point {index}")
                        for index, point in enumerate(points, start=1))
        first_leg = float(np.linalg.norm(b - a1))
        second_leg = float(np.linalg.norm(c - a2))
        short_base = float(np.linalg.norm(a2 - a1))
        long_base = float(np.linalg.norm(c - b))

        if not all(math.isfinite(value) for value in
                   (first_leg, second_leg, short_base, long_base)):
            raise ValueError("Four-point coordinates produce an unbounded distance.")
        if abs(first_leg - second_leg) >= EPS:
            raise ValueError(
                "Four-point planes require |dist(a1,b) - dist(a2,c)| < 0.001."
            )
        if first_leg <= EPS:
            raise ValueError("The equal-length sides must have positive length.")
        if short_base > long_base + EPS:
            # CSV sources do not always start at the shorter base. Swap the
            # two bases while preserving the side pairings (1->3 and 2->4).
            a1, a2, b, c = b, c, a1, a2
            short_base, long_base = long_base, short_base

        all_points = (a1, a2, b, c)
        normal = None
        normal_length = 0.0
        for first, second, third in combinations(all_points, 3):
            candidate = np.cross(second - first, third - first)
            candidate_length = float(np.linalg.norm(candidate))
            if candidate_length > normal_length:
                normal = candidate
                normal_length = candidate_length

        scale = max(first_leg, short_base, long_base, 1.0)
        if (normal is None or not math.isfinite(normal_length)
                or normal_length <= EPS * scale):
            raise ValueError("The four points must define a non-degenerate plane.")
        plane_point = a1
        for point in all_points:
            distance_from_plane = abs(float(np.dot(point - plane_point, normal))) / normal_length
            if not math.isfinite(distance_from_plane) or distance_from_plane >= EPS:
                raise ValueError("The four points must lie in the same plane.")

        return (
            a1,
            a2,
            (b - a1) / first_leg,
            first_leg,
            second_leg,
            long_base,
            (c - a2) / second_leg,
        )

    raise ValueError("A plane must contain either three or four 3D points.")


def _project_kernel(data, start_a, start_b, direction_a, direction_b,
                    leg_length_a, leg_length_b, height, width):
    """Scalar sampling kernel compiled by Numba when it is installed."""
    result = np.zeros((height, width), dtype=data.dtype)
    center_column = (width - 1) / 2.0
    max_x = data.shape[0] - 1
    max_y = data.shape[1] - 1
    max_z = data.shape[2] - 1

    for row in range(height):
        row_distance_a = min(float(row), leg_length_a)
        row_distance_b = min(float(row), leg_length_b)
        ax = start_a[0] + row_distance_a * direction_a[0]
        ay = start_a[1] + row_distance_a * direction_a[1]
        az = start_a[2] + row_distance_a * direction_a[2]
        bx = start_b[0] + row_distance_b * direction_b[0]
        by = start_b[1] + row_distance_b * direction_b[1]
        bz = start_b[2] + row_distance_b * direction_b[2]

        dx = bx - ax
        dy = by - ay
        dz = bz - az
        row_length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if row_length > EPS:
            ux = dx / row_length
            uy = dy / row_length
            uz = dz / row_length
        else:
            ux = uy = uz = 0.0

        for step in range(math.ceil(row_length) + 1):
            along = min(float(step), row_length)
            column_position = center_column - row_length / 2.0 + step
            column = math.floor(column_position + 0.5)
            if column < 0 or column >= width:
                continue

            x = ax + along * ux
            y = ay + along * uy
            z = az + along * uz
            if 0.0 <= x <= max_x and 0.0 <= y <= max_y and 0.0 <= z <= max_z:
                ix = math.floor(x + 0.5)
                iy = math.floor(y + 0.5)
                iz = math.floor(z + 0.5)
                result[row, column] = data[ix, iy, iz]

    return result


_compiled_project = njit(cache=True)(_project_kernel) if njit is not None else None


def project(volume: np.ndarray, *points: Sequence[float]) -> np.ndarray:
    """Project a triangular or trapezoidal plane into a 2D NumPy array.

    Coordinates use the input array's axis order: ``volume[x, y, z]``. The
    output has shape ``(rows, columns)`` and preserves the volume's dtype.
    Distances are measured in voxel coordinates. Sampling uses nearest-neighbour
    voxel values, with coordinates rounded half up; points beyond the volume's
    continuous bounds contribute zero.

    Both ends of every edge are included. Along each dimension, samples are at
    most one voxel apart, and the output has ``ceil(extent) + 1`` pixels so the
    last endpoint fits in the result.
    """
    data = np.asarray(volume)
    if data.ndim != 3 or any(size == 0 for size in data.shape):
        raise ValueError("The input volume must be a non-empty 3D matrix.")
    if not np.issubdtype(data.dtype, np.integer):
        raise ValueError("The input volume must contain integer voxel values.")

    (
        start_a,
        start_b,
        direction_a,
        leg_length_a,
        leg_length_b,
        base_length,
        direction_b,
    ) = _plane_geometry(points)
    height = int(math.ceil(max(leg_length_a, leg_length_b) - 1e-4)) + 1
    width = int(math.ceil(base_length - 1e-4)) + 1

    if _compiled_project is not None:
        return _compiled_project(
            data,
            start_a,
            start_b,
            direction_a,
            direction_b,
            leg_length_a,
            leg_length_b,
            height,
            width,
        )

    row_indices = np.arange(height, dtype=np.float64)
    row_distances_a = np.minimum(row_indices, leg_length_a)
    row_distances_b = np.minimum(row_indices, leg_length_b)
    row_starts = start_a + row_distances_a[:, None] * direction_a
    row_ends = start_b + row_distances_b[:, None] * direction_b
    row_vectors = row_ends - row_starts
    row_lengths = np.linalg.norm(row_vectors, axis=1)
    row_directions = np.zeros_like(row_vectors)
    nonzero_rows = row_lengths > EPS
    row_directions[nonzero_rows] = (
        row_vectors[nonzero_rows] / row_lengths[nonzero_rows, None]
    )

    # A centered row is sampled in steps of at most one voxel. Its final sample
    # is clamped to the endpoint when its length is not an integer.
    x_steps = np.arange(width, dtype=np.float64)[None, :]
    along = np.minimum(x_steps, row_lengths[:, None])
    row_sample_limit = np.ceil(row_lengths)[:, None]
    sample_exists = x_steps <= row_sample_limit
    coords = row_starts[:, None, :] + along[:, :, None] * row_directions[:, None, :]

    center_column = (width - 1) / 2.0
    column_positions = center_column - row_lengths[:, None] / 2.0 + x_steps
    columns = np.floor(column_positions + 0.5).astype(np.intp)

    upper_bounds = np.asarray(data.shape, dtype=np.float64) - 1.0
    inside = np.all((coords >= 0.0) & (coords <= upper_bounds), axis=2)
    inside &= sample_exists & (columns >= 0) & (columns < width)
    safe_coords = np.where(inside[:, :, None], coords, 0.0)
    voxel_indices = np.floor(safe_coords + 0.5).astype(np.intp)

    result = np.zeros((height, width), dtype=data.dtype)
    row_indices, sample_indices = np.nonzero(inside)
    result[row_indices, columns[row_indices, sample_indices]] = data[
        voxel_indices[row_indices, sample_indices, 0],
        voxel_indices[row_indices, sample_indices, 1],
        voxel_indices[row_indices, sample_indices, 2],
    ]
    return result
