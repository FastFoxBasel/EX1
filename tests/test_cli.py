import io
from contextlib import redirect_stdout
import unittest
from unittest.mock import call, patch

import numpy as np

import Ex0


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.volume = np.ones((3, 3, 3), dtype=np.uint8)
        self.frame = np.ones((1, 1), dtype=np.uint8)
        self.a = (0.0, 0.0, 0.0)
        self.b = (2.0, 0.0, 0.0)
        self.c = (0.0, 2.0, 0.0)

    def _run(self, planes, options=()):
        with (
            patch("Ex0.load_nrrd", return_value=(self.volume, {})),
            patch("Ex0.load_coordinates", return_value=planes),
            patch("Ex0.project", return_value=self.frame) as project_mock,
            patch("Ex0.write_mp4") as write_mock,
            redirect_stdout(io.StringIO()) as stdout,
        ):
            status = Ex0.main(
                ["volume.nrrd", "planes.csv", "output.mp4", *options]
            )
        return status, project_mock, write_mock, stdout.getvalue()

    def test_default_cli_completes_triangles_for_display(self):
        status, project_mock, write_mock, output = self._run(
            [(self.a, self.b, self.c)]
        )

        self.assertEqual(status, 0)
        expected_rect = Ex0.complete_triangle(self.a, self.b, self.c)
        project_mock.assert_called_once_with(
            self.volume, *expected_rect
        )
        write_mock.assert_called_once()
        self.assertIn("Completed 1 triangle(s)", output)

    def test_exact_triangles_keeps_three_point_projection_exact(self):
        status, project_mock, write_mock, output = self._run(
            [(self.a, self.b, self.c)],
            options=("--exact-triangles",),
        )

        self.assertEqual(status, 0)
        project_mock.assert_called_once_with(
            self.volume, self.a, self.b, self.c
        )
        write_mock.assert_called_once()
        self.assertNotIn("Completed", output)

    def test_complete_triangles_flag_completes_triangles(self):
        rectangle = (
            (0.0, 0.0, 0.0),
            (0.0, 2.0, 0.0),
            (2.0, 0.0, 0.0),
            (2.0, 2.0, 0.0),
        )
        status, project_mock, write_mock, output = self._run(
            [(self.a, self.b, self.c), rectangle],
            options=("--complete-triangles",),
        )

        self.assertEqual(status, 0)
        expected_rect = Ex0.complete_triangle(self.a, self.b, self.c)
        self.assertEqual(
            project_mock.call_args_list,
            [
                call(self.volume, *expected_rect),
                call(self.volume, *rectangle),
            ],
        )
        write_mock.assert_called_once()
        self.assertIn("Completed 1 triangle(s)", output)

    def test_bad_plane_gets_error_frame_and_later_plane_runs(self):
        valid = (self.a, self.b, self.c)
        invalid = (self.a, self.b, (1.0, 2.0, 0.0))
        error_frame = np.zeros((96, 480), dtype=np.uint8)
        with (
            patch("Ex0.load_nrrd", return_value=(self.volume, {})),
            patch("Ex0.load_coordinates", return_value=[valid, invalid, valid]),
            patch(
                "Ex0.project",
                side_effect=[self.frame, ValueError("bad geometry"), self.frame],
            ),
            patch("Ex0.make_error_frame", return_value=error_frame),
            patch("Ex0.write_mp4") as write_mock,
            redirect_stdout(io.StringIO()) as stdout,
        ):
            status = Ex0.main(["volume.nrrd", "planes.csv", "output.mp4"])

        self.assertEqual(status, 0)
        frames = write_mock.call_args.args[0]
        self.assertEqual(len(frames), 3)
        self.assertIs(frames[1], error_frame)
        self.assertIn("later planes were still processed", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
