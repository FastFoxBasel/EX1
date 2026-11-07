# Testing Strategy and Results

## 1. Purpose

Verify geometry validation, projection values, boundary handling, input parsing, NRRD loading, MP4 creation, and the performance requirement.

## 2. Automated Coverage

Run from the project root:

```bash
python -m unittest discover -s tests -v
```

The unit tests cover:

- Three-point triangles, endpoint inclusion, and nearest-neighbour values.
- Four-point trapezoids and exact sampling of a small rectangle.
- Invalid side lengths, collinear points, non-coplanar points, and reversed-base normalization.
- Zero values for out-of-volume coordinates.
- Rejection of non-3D matrices.
- Legacy and counted/header CSV rows, comments, non-finite CSV values, and the supplied NRRD dataset.
- MP4 creation with one frame per projection and a common canvas for different image sizes.
- Stable display-window behavior for all-zero and constant nonzero volumes.
- CLI default behavior completing triangles into orthogonal planar rectangles for clear display, alongside `--exact-triangles` for raw triangular masks.
- Invalid CSV and invalid plane rows produce marked error frames and allow later planes to continue.

## 3. Demo Check

The short end-to-end demonstration uses:

```bash
python Ex0.py data/nrrd/MRHead_1.nrrd data/csv/planes.csv demo/projection_demo.mp4
```

The input has two plane rows (one triangle and one trapezoid). The MP4 is reopened through OpenCV to confirm that it decodes to two frames and that both frames have the same even dimensions.

The uploaded extended CSV was also run with:

```bash
python Ex0.py data/nrrd/MRHead_1.nrrd data/csv/head.csv demo/head_demo.mp4
```

The new CSV batch produced decoded videos for biscuit cake (120 frames), head (280), lecturer example (4), onion (120), and swiss roll (120), all at 30 FPS. The lecturer example emitted an error frame for its invalid fourth plane and continued. Croissant lacks a matching NRRD volume; `edge_cases.csv` references a synthetic volume that is absent and includes a very large plane, so it was not rendered as a full video.

## 4. Performance Check

The benchmark creates a deterministic `500 x 500 x 500` `uint8` volume and projects a `500 x 500` plane. It warms up the compiled Numba kernel before recording repeated timings. The benchmark excludes one-time volume allocation, JIT compilation, and video encoding. Run it with:

```bash
python benchmarks/benchmark.py --repetitions 30
```

## 5. Results

On the recorded Windows 11 / AMD Ryzen 7 5800H machine:

- Automated unit suite: **26 tests passed**.
- Demo: **2 input planes, 2 decoded MP4 frames**; projections were `61 x 86` and `61 x 61` before common-canvas padding.
- CSV batch: **644 data rows** rendered across the five available matching/usable volumes, including one error frame in lecturer example.
- Benchmark: **291.1 projections per second median** for a `500 x 500` result (3.435 ms median), above the 130 FPS target.

See [Experiment.md](Experiment.md) for timings, versions, and interpretation.
