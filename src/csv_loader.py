"""Read one plane definition per CSV row."""

import csv
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class InvalidPlaneRow:
    """A nonblank CSV data row that cannot be parsed as a plane."""

    line_number: int
    message: str


def load_coordinates(filename, *, continue_on_error=False):
    """Return CSV rows as lists of three or four 3D points.

    Supported rows are the original 9/12-coordinate form and the extended
    ``point_count,x1,y1,z1,...,x4,y4,z4`` form. Extended files may include a
    header and leave the fourth point blank for three-point planes. Blank and
    comment rows are ignored.
    """
    planes = []

    with open(filename, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        for line_number, row in enumerate(reader, start=1):
            if not row or all(not value.strip() for value in row):
                continue
            if row[0].strip().startswith("#"):
                continue
            if " ".join(row[0].strip().casefold().split()).startswith("number of points"):
                continue

            try:
                coordinate_fields = row
                if len(row) in (10, 13):
                    try:
                        point_count = int(row[0].strip())
                    except ValueError:
                        point_count = None

                    if point_count in (3, 4):
                        required_fields = point_count * 3
                        if len(row) < required_fields + 1:
                            raise ValueError(
                                f"CSV line {line_number} declares {point_count} points "
                                f"but contains fewer than {required_fields} coordinates."
                            )
                        coordinate_fields = row[1:required_fields + 1]
                        extra_fields = row[required_fields + 1:]
                        if any(value.strip() for value in extra_fields):
                            raise ValueError(
                                f"CSV line {line_number} has coordinates beyond its "
                                "declared point count."
                            )
                    elif row[0].strip().isdigit():
                        raise ValueError(
                            f"CSV line {line_number} point count must be 3 or 4."
                        )

                try:
                    values = [float(value.strip()) for value in coordinate_fields]
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid number on CSV line {line_number}."
                    ) from exc

                if len(values) not in (9, 12):
                    raise ValueError(
                        f"CSV line {line_number} must contain 9 numbers (3 points) "
                        "or 12 numbers (4 points), with an optional leading point count."
                    )
                if not all(math.isfinite(value) for value in values):
                    raise ValueError(
                        f"CSV line {line_number} contains a non-finite coordinate."
                    )

                points = [tuple(values[index:index + 3])
                          for index in range(0, len(values), 3)]
                planes.append(points)
            except ValueError as exc:
                if not continue_on_error:
                    raise
                planes.append(InvalidPlaneRow(line_number, str(exc)))

    if not planes:
        raise ValueError("The CSV file contains no plane coordinates.")

    return planes
