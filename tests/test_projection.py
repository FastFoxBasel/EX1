import unittest
from unittest.mock import patch

import numpy as np

from src.projection import project


class ProjectionTests(unittest.TestCase):
    def test_three_point_triangle_includes_endpoints(self):
        volume = np.arange(4 * 4 * 2, dtype=np.int16).reshape((4, 4, 2), order="F")

        result = project(
            volume,
            (0, 0, 1),
            (2, 0, 1),
            (0, 2, 1),
        )

        self.assertEqual(result.shape, (3, 4))
        self.assertEqual(result[0, 2], volume[0, 0, 1])
        self.assertEqual(result[-1, 0], volume[2, 0, 1])
        self.assertEqual(result[-1, -1], volume[0, 2, 1])
        self.assertEqual(result.dtype, volume.dtype)

    def test_equal_side_tolerance_still_reaches_both_endpoints(self):
        volume = np.arange(4 * 4 * 2, dtype=np.int16).reshape((4, 4, 2), order="F")

        result = project(
            volume,
            (0, 0, 1),
            (2, 0, 1),
            (0, 2.0005, 1),
        )

        self.assertEqual(result.shape, (4, 4))
        self.assertEqual(result[-1, 0], volume[2, 0, 1])
        self.assertEqual(result[-1, -1], volume[0, 2, 1])

    def test_four_point_trapezoid_samples_each_rectangle_voxel(self):
        volume = np.arange(4 * 4 * 2, dtype=np.uint8).reshape((4, 4, 2), order="F")
        points = (
            (0, 0, 0),
            (0, 2, 0),
            (2, 0, 0),
            (2, 2, 0),
        )

        result = project(volume, *points)

        expected = np.array(
            [[volume[x, y, 0] for y in range(3)] for x in range(3)],
            dtype=volume.dtype,
        )
        np.testing.assert_array_equal(result, expected)

    def test_four_point_trapezoid_accepts_longer_base_first(self):
        volume = np.arange(4 * 4 * 2, dtype=np.uint8).reshape((4, 4, 2), order="F")
        points = (
            (0, 0, 0),
            (0, 3, 0),
            (2, 0.5, 0),
            (2, 2.5, 0),
        )

        result = project(volume, *points)

        self.assertEqual(result.shape, (4, 4))
        self.assertEqual(result[0, 1], volume[2, 1, 0])

    def test_outside_coordinates_are_zero(self):
        volume = np.full((4, 4, 3), 9, dtype=np.uint8)

        result = project(
            volume,
            (-1, 0, 1),
            (1, 0, 1),
            (-1, 2, 1),
        )

        self.assertEqual(result[0, 2], 0)
        self.assertEqual(result[-1, 0], 9)
        self.assertEqual(result[-1, -1], 0)

    def test_invalid_three_point_side_lengths_are_rejected(self):
        volume = np.zeros((4, 4, 4), dtype=np.uint8)

        with self.assertRaisesRegex(ValueError, "equal-side"):
            project(volume, (0, 0, 0), (2, 0, 0), (0, 3, 0))

    def test_collinear_three_points_are_rejected(self):
        volume = np.zeros((4, 4, 4), dtype=np.uint8)

        with self.assertRaisesRegex(ValueError, "collinear"):
            project(volume, (0, 0, 0), (2, 0, 0), (-2, 0, 0))

    def test_non_coplanar_four_points_are_rejected(self):
        volume = np.zeros((4, 4, 4), dtype=np.uint8)
        points = (
            (0, 0, 0),
            (0, 2, 0),
            (2, 0, 0),
            (2, 2, 0.05),
        )

        with self.assertRaisesRegex(ValueError, "same plane"):
            project(volume, *points)

    def test_non_three_dimensional_volume_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "3D matrix"):
            project(np.zeros((4, 4), dtype=np.uint8), (0, 0, 0), (2, 0, 0), (0, 2, 0))

    def test_numpy_fallback_matches_compiled_kernel(self):
        volume = np.arange(4 * 4 * 2, dtype=np.int16).reshape((4, 4, 2), order="F")
        points = (
            (0.25, 0.25, 1),
            (2.75, 0.25, 1),
            (0.25, 2.75, 1),
        )
        compiled = project(volume, *points)

        with patch("src.projection._compiled_project", None):
            fallback = project(volume, *points)

        np.testing.assert_array_equal(fallback, compiled)

    def test_unsigned_sixteen_and_thirty_two_bit_volumes(self):
        for dtype in (np.uint16, np.uint32):
            with self.subTest(dtype=dtype):
                volume = np.arange(4 * 4 * 4, dtype=dtype).reshape((4, 4, 4))
                result = project(
                    volume,
                    (0, 0, 1),
                    (2, 0, 1),
                    (0, 2, 1),
                )
                self.assertEqual(result.dtype, dtype)


if __name__ == "__main__":
    unittest.main()
