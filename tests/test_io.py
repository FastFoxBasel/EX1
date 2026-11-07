import csv
from pathlib import Path
import tempfile
import unittest

import numpy as np

from src.csv_loader import InvalidPlaneRow, load_coordinates
from src.nrrd_loader import load_nrrd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class InputTests(unittest.TestCase):
    def test_csv_reads_three_and_four_point_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "planes.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow((0, 0, 0, 2, 0, 0, 0, 2, 0))
                writer.writerow((0, 0, 0, 0, 2, 0, 2, 0, 0, 2, 2, 0))

            planes = load_coordinates(path)

        self.assertEqual(len(planes), 2)
        self.assertEqual(len(planes[0]), 3)
        self.assertEqual(len(planes[1]), 4)
        self.assertEqual(planes[0][1], (2.0, 0.0, 0.0))

    def test_csv_rejects_non_finite_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            path.write_text("0,0,0,2,0,0,0,nan,0\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "non-finite"):
                load_coordinates(path)

    def test_csv_reads_counted_header_rows_and_comments(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "extended.csv"
            path.write_text(
                "# generated plane list\n"
                "Number of Points (3 or 4),x1,y1,z1,x2,y2,z2,x3,y3,z3,x4,y4,z4\n"
                "3,0,0,0,2,0,0,0,2,0,,,\n"
                "4,0,0,0,0,2,0,2,0,0,2,2,0\n",
                encoding="utf-8",
            )

            planes = load_coordinates(path)

        self.assertEqual(len(planes), 2)
        self.assertEqual(len(planes[0]), 3)
        self.assertEqual(len(planes[1]), 4)
        self.assertEqual(planes[0][2], (0.0, 2.0, 0.0))

    def test_uploaded_head_csv_loads_all_plane_rows(self):
        planes = load_coordinates(PROJECT_ROOT / "data" / "csv" / "head.csv")

        self.assertEqual(len(planes), 280)
        self.assertEqual(sum(len(points) == 3 for points in planes), 60)
        self.assertEqual(sum(len(points) == 4 for points in planes), 220)

    def test_supplied_nrrd_loads_in_index_order(self):
        volume, header = load_nrrd(
            PROJECT_ROOT / "data" / "nrrd" / "MRHead_1.nrrd"
        )

        self.assertEqual(volume.shape, (256, 256, 130))
        self.assertTrue(np.issubdtype(volume.dtype, np.integer))
        self.assertEqual(header["dimension"], 3)

    def test_scan_mode_keeps_malformed_csv_rows_in_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mixed.csv"
            path.write_text(
                "0,0,0,2,0,0,0,2,0\nnot,a,plane\n"
                "0,0,0,0,2,0,2,0,0,2,2,0\n",
                encoding="utf-8",
            )
            rows = load_coordinates(path, continue_on_error=True)

        self.assertEqual(len(rows), 3)
        self.assertEqual(len(rows[0]), 3)
        self.assertIsInstance(rows[1], InvalidPlaneRow)
        self.assertEqual(rows[1].line_number, 2)
        self.assertEqual(len(rows[2]), 4)


if __name__ == "__main__":
    unittest.main()
