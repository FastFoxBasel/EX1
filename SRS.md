# Software Requirements Specification

## 1. Introduction

### 1.1 Purpose

The software projects specified planar regions through a three-dimensional NRRD volume and writes the resulting images to an MP4 video.

### 1.2 Scope

The command-line program reads an NRRD volume and a CSV list of plane coordinates. It validates each plane, samples its voxels, and writes one grayscale video frame per CSV row. The project includes the algorithm design, source data description, tests, demo, and a repeatable performance experiment.

## 2. Definitions

- **Volume:** A non-empty 3D integer matrix `M[x,y,z]`.
- **Three-point plane:** An isosceles triangle `(a,b,c)` with `abs(dist(a,b) - dist(a,c)) < 0.001`.
- **Four-point plane:** A trapezoid represented by four points whose paired sides are equal in length and coplanar. Either base may be listed first; the software reorients the pair so the shorter base is first.
- **Projection:** The 2D matrix of nearest-neighbour voxel values sampled over the supplied region. Points outside the volume contribute zero.

## 3. Functional Requirements

- **FR-1 — Read volume:** Read a 3D NRRD volume, including the supplied gzip-compressed dataset, while preserving NRRD index order.
- **FR-2 — Read planes:** Read one plane per data row, supporting both 9/12-coordinate rows and the extended point-count plus 12-coordinate-column format. Accept the optional `Number of Points...` header, blank unused fourth-point fields for triangles, blank lines, and comment lines.
- **FR-3 — Validate three points:** Enforce the equal-side tolerance `EPS = 0.001` and reject degenerate or collinear triangles.
- **FR-4 — Validate four points:** Enforce the equal-side tolerance, normalize reversed base order while preserving the paired sides, and enforce coplanarity; reject degenerate regions.
- **FR-5 — Project:** Return a two-dimensional integer matrix that includes both endpoints and preserves the source dtype.
- **FR-6 — Sample voxels:** Use nearest-neighbour voxel sampling with half-up rounding.
- **FR-7 — Handle boundaries:** Return zero when a continuous sample coordinate is outside the volume bounds.
- **FR-8 — Create demo video:** Implement `python Ex0.py file.nrrd file.csv file.mp4` and write one frame per valid plane row in order, skipping blank lines, comments, and the recognized header.
- **FR-9 — Report errors:** Reject malformed CSV, invalid planes, invalid NRRD dimensions, and unsupported output paths with a useful error message.

## 4. Non-Functional Requirements

- **NFR-1 — Correctness:** Follow the documented algorithm and boundary rules in [Algorithm.md](Algorithm.md).
- **NFR-2 — Stability:** Validate user input before indexing the volume or creating the output video.
- **NFR-3 — Runtime:** Design the implementation for efficient plane sampling. The course brief states a target of 100 frames per second for a `500^3` byte volume and calls for an additional 30 FPS. Measure the achieved projection rate on the available machine; video encoding is measured separately.
- **NFR-4 — Maintainability:** Separate volume loading, CSV parsing, projection, video encoding, and documentation.
- **NFR-5 — Reproducibility:** Include the test data, unit tests, benchmark script, test command, benchmark command, and experiment results.

## 5. Constraints

- The implementation language is Python, which is permitted by the assignment.
- The assignment's volume dimensions are positive and smaller than `2^10` per axis.
- The assignment describes unsigned 8-, 16-, and 32-bit values; the included MRI file uses NRRD type `short` and is therefore read as a signed 16-bit array.
- Plane coordinates are interpreted as NRRD voxel indices, not physical-space coordinates.
- Python dependencies are listed in `requirements.txt`.

## 6. Output Requirements

The projection API returns an integer NumPy matrix. The demo writes an MP4 at 30 FPS or higher. If projections have different dimensions, the video centers them on an even-sized common canvas without resizing the voxel data. Intensities use one 1st-to-99th percentile window from non-zero volume values.

## 7. Verification Requirements

Tests cover three- and four-point geometry, invalid definitions, nearest-neighbour values, boundary zeros, CSV parsing, NRRD loading, and MP4 frame creation. A separate benchmark measures projection computation on a synthetic `500 x 500 x 500` `uint8` volume. The results are documented in [Experiment.md](Experiment.md).
