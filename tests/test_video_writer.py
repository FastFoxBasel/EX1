from pathlib import Path
import tempfile
import unittest

import numpy as np

import cv2

from src.video_writer import _display_window, _to_grayscale, make_error_frame, write_mp4


class VideoWriterTests(unittest.TestCase):
    def test_all_zero_volume_stays_black(self):
        volume = np.zeros((2, 2, 2), dtype=np.uint8)
        low, high = _display_window(volume)

        result = _to_grayscale(volume[:, :, 0], low, high)

        np.testing.assert_array_equal(result, np.zeros((2, 2), dtype=np.uint8))

    def test_constant_nonzero_volume_maps_to_visible_midgray(self):
        volume = np.full((2, 2, 2), 5, dtype=np.uint8)
        low, high = _display_window(volume)

        result = _to_grayscale(volume[:, :, 0], low, high)

        np.testing.assert_array_equal(result, np.full((2, 2), 128, dtype=np.uint8))

    def test_writes_one_frame_per_projection_on_common_canvas(self):
        volume = np.arange(1, 101, dtype=np.uint8).reshape((10, 10, 1))
        frames = [np.full((3, 4), 50, dtype=np.uint8), np.full((2, 2), 100, dtype=np.uint8)]

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "projection.mp4"
            write_mp4(frames, output, volume)

            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 0)
            capture = cv2.VideoCapture(str(output))
            try:
                self.assertEqual(int(capture.get(cv2.CAP_PROP_FRAME_COUNT)), 2)
                self.assertEqual(int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), 4)
                self.assertEqual(int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)), 4)
                self.assertGreaterEqual(capture.get(cv2.CAP_PROP_FPS), 30.0)
            finally:
                capture.release()

    def test_rejects_output_rate_below_30_fps(self):
        volume = np.ones((2, 2, 2), dtype=np.uint8)
        frame = np.ones((2, 2), dtype=np.uint8)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "too_slow.mp4"
            with self.assertRaisesRegex(ValueError, "at least 30 FPS"):
                write_mp4([frame], output, volume, fps=29)

    def test_error_frame_is_visible(self):
        volume = np.full((2, 2, 2), 5, dtype=np.uint8)
        frame = make_error_frame("invalid plane", volume)

        self.assertEqual(frame.shape, (96, 480))
        gray = _to_grayscale(frame, *_display_window(volume))
        self.assertGreater(int(gray.max()), 180)
        self.assertEqual(int(gray.min()), 0)


if __name__ == "__main__":
    unittest.main()
