# 3D Plane Projection

This project samples a triangular or trapezoidal plane from a 3D NRRD volume and writes one 2D projection per CSV row to an MP4 video. The design and implementation focus on clear geometry rules, validation, stable boundary handling, and efficient voxel sampling.

## Problem and Scope

The input volume is a three-dimensional integer matrix `M[x, y, z]`. The assignment bounds each matrix dimension below `2^10` and describes 8-, 16-, or 32-bit voxel values. The program accepts either three points defining an isosceles triangle or four points defining an isosceles trapezoid, projects each requested plane, and creates an MP4 video with the projections in CSV order.

The implementation supports gzip-compressed NRRD volumes, preserves the NRRD index order, and returns a 2D NumPy matrix with rows along the equal-length sides and columns across each row. Points beyond the volume contribute zero. The assignment's complete problem statement and projection pseudocode are in the supplied course brief; this repository documents the implementation choices needed to make that pseudocode discrete and executable.

## Requirements

- Python 3.10 or later
- Packages in `requirements.txt` (`numpy`, `numba`, `pynrrd`, and headless OpenCV)

Install the packages from the project root:

```bash
python -m pip install -r requirements.txt
```

## Run the Demo

```bash
python Ex0.py data/nrrd/MRHead_1.nrrd data/csv/planes.csv demo/projection_demo.mp4
```

The command accepts:

1. A 3D NRRD volume.
2. A CSV file with one plane per data row.
3. An `.mp4` output path.

Every valid plane row produces exactly one video frame in CSV order; blank lines, comments, and the recognized header are skipped. Videos are encoded at 30 FPS or higher. Frames use one intensity window derived from the non-zero volume values; differently sized projections are centered on a common black canvas without resizing their voxels.

For clear and continuous video display, three-point inputs are completed into an orthogonal bounding rectangle on the same plane by default (spanning the perpendicular altitude and base vectors without shear distortion). To keep the raw uncompleted triangular mask instead, pass `--exact-triangles`. The core projection API (`project()`) always evaluates the exact geometric triangle or trapezoid as specified in the assignment algorithm.

## CSV Format

The loader accepts the original format (9 coordinate values for three points or 12 for four) and the uploaded extended format, which starts with a point count and has 12 coordinate columns:

```csv
Number of Points (3 or 4),x1,y1,z1,x2,y2,z2,x3,y3,z3,x4,y4,z4
3,80,80,60,140,80,60,80,140,60,,,
4,80,80,60,80,140,60,140,80,60,140,140,60
```

Extended files may use the shown `Number of Points...` header. Three-point rows can leave the fourth point's three columns blank. Blank lines and lines beginning with `#` are ignored. Coordinates are listed as `x,y,z` triples in NRRD index order.

For four points, the paired sides are `point1 -> point3` and `point2 -> point4`. If a CSV lists the longer base first (by more than `EPS`), the projection normalizes the base order automatically while keeping those side pairings. Rectangular/square slices where both bases are equal within tolerance retain their given orientation without jitter.

The included `data/csv/planes.csv` contains one triangle and one trapezoid; `data/csv/head.csv` has 280 plane rows and can be run with:

```bash
python Ex0.py data/nrrd/MRHead_1.nrrd data/csv/head.csv demo/head_demo.mp4
```

To output the raw triangular masks without orthogonal rectangle completion:

```bash
python Ex0.py data/nrrd/MRHead_1.nrrd data/csv/head.csv demo/head_projections.mp4 --exact-triangles
```

## Geometry and Sampling Choices

- Three-point input must satisfy `abs(dist(a,b) - dist(a,c)) < 0.001` and the points must not be collinear.
- Four-point input pairs sides as `point1 -> point3` and `point2 -> point4`. It must satisfy the equal-side tolerance and coplanarity within `0.001` voxel units. If a trapezoid lists the longer base first (by more than `EPS = 0.001`), the shorter base is used as the row start without disturbing equal-base slices.
- Output dimensions are `ceil(extent - 1e-4) + 1` so that both endpoints fit cleanly without floating-point precision jitter near integer dimensions.
- Each line is sampled at intervals no greater than one voxel. Fractional final intervals end exactly at the supplied point.
- Coordinates use nearest-neighbour sampling with half-up rounding. A continuous coordinate outside `[0, size - 1]` on any axis returns zero.
- Values in the output retain the NRRD array's integer dtype. Video frames are mapped to 8-bit grayscale using a single non-zero-volume percentile window.

See [Algorithm.md](Algorithm.md) for the full design and validation details.

## Data

The loader accepts any three-dimensional integer NRRD volume, including the uploaded `uint8`, `uint16`, `uint32`, and signed `short` datasets. CSV files are in `data/csv/`, NRRD volumes are in `data/nrrd/`, and visual reference images are in `data/images/`. See [data/README.md](data/README.md) for their contents.

## Tests and Performance Experiment

Run the unit tests from the project root:

```bash
python -m unittest discover -s tests -v
```

Run the reproducible 500-cubed byte-volume benchmark:

```bash
python benchmarks/benchmark.py --repetitions 30
```

The benchmark measures projection computation only; it excludes video encoding and the one-time volume allocation. Results, the test run, and the generated demonstration video are recorded in [Experiment.md](Experiment.md).

## Project Files

- `Ex0.py` — command-line demo; sample outputs include `demo/projection_demo.mp4`, `demo/head_demo.mp4`, and the newly generated videos in `demo/csv_import_runs/`.
- `src/projection.py` — plane validation and compiled projection kernel, with a NumPy fallback.
- `src/csv_loader.py`, `src/nrrd_loader.py` — input readers.
- `src/video_writer.py` — grayscale normalization and MP4 encoding.
- `tests/` — geometry, boundary, input, and video tests.
- `benchmarks/benchmark.py` — reproducible performance measurement.
- `Algorithm.md`, `SRS.md`, `Testing.md`, `Experiment.md` — design and project documentation.
