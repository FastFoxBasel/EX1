# Software Requirements Specification

## 1. Introduction

### 1.1 Purpose

The purpose of this software is to generate a two-dimensional projection of a specified plane through a three-dimensional volumetric data matrix.

The system should provide a correct, stable, and runtime-efficient implementation of the projection algorithm.

### 1.2 Scope

The system will:

1. Read 3D volumetric data from an NRRD file.
2. Accept a plane represented by three or four 3D points.
3. Validate that the supplied points satisfy the plane definition specified by the assignment.
4. Generate a 2D projection of the specified plane.
5. Treat points outside the input volume as having value zero.
6. Support repeated projection operations for multiple plane coordinates.
7. Produce the required output for the demonstration.
8. Support performance testing and evaluation.

---

## 2. Definitions

### 2.1 3D Matrix

`M` is the input volumetric data matrix.

It has dimensions:

`sx × sy × sz`

and contains unsigned integer values.

### 2.2 Plane

The plane is represented by either three or four 3D points.

For three points `(a,b,c)`, the assignment requires:

`|dist(a,b) - dist(a,c)| < EPS`

where:

`EPS = 0.001`

### 2.3 Projection

The projection is the process of sampling values from the 3D matrix along the specified plane and placing those values into a 2D matrix.

### 2.4 Output Matrix

`E` is the 2D matrix produced by the projection algorithm.

---

## 3. Functional Requirements

### FR-1: Read Input Data

The system shall accept a 3D volumetric dataset in NRRD format.

### FR-2: Represent the Plane

The system shall accept a plane represented using either three or four 3D coordinates.

### FR-3: Validate Three-Point Planes

For three points `(a,b,c)`, the system shall verify:

`|dist(a,b) - dist(a,c)| < EPS`

with:

`EPS = 0.001`.

### FR-4: Validate Four-Point Planes

For four points `(a1,a2,b,c)`, the system shall verify the conditions specified by the assignment:

1. `|dist(a1,b) - dist(a2,c)| < EPS`
2. `dist(a1,a2) <= dist(b,c)`
3. `a1→b` and `a2→c` lie on the same plane.

### FR-5: Generate Projection

The system shall generate a 2D matrix representing the specified plane.

### FR-6: Sample the Input Matrix

For every sampled point `p`, the system shall obtain its value from `M`.

### FR-7: Handle Points Outside the Volume

If a sampled point is not inside `M`, its value shall be treated as zero.

### FR-8: Produce Demo Output

The system shall support the required demonstration interface and produce an MP4 output containing a frame for each corresponding plane coordinate in the CSV input.

---

## 4. Non-Functional Requirements

### NFR-1: Correctness

The implementation shall produce correct projections according to the defined projection algorithm.

### NFR-2: Stability

The implementation shall handle valid input data reliably without unexpected failures.

### NFR-3: Runtime Efficiency

The implementation shall be designed for efficient processing of large volumetric datasets.

The assignment specifies a performance expectation of at least 100 FPS for a `500^3` byte matrix, with an additional 30 FPS requirement.

### NFR-4: Code Quality

The implementation should prioritize clear organization, maintainability, and robust design.

### NFR-5: Reproducibility

The project shall contain enough information and test data definitions for the projection results and performance measurements to be reproduced.

---

## 5. Input Requirements

### 5.1 NRRD Input

The system shall accept a valid NRRD file representing a 3D volumetric dataset.

### 5.2 CSV Input

The demonstration CSV file shall contain a list of either three or four point coordinates.

### 5.3 Plane Coordinates

Each coordinate shall represent a point in the three-dimensional volume.

---

## 6. Output Requirements

The projection algorithm shall produce a 2D matrix.

The demonstration shall additionally produce an MP4 video.

Each frame shall correspond to a plane coordinate supplied in the CSV file, in the order provided.

---

## 7. Constraints

The project must use one of the languages permitted by the assignment:

- Java
- Python
- C
- C++

The input matrix dimensions satisfy:

`1 <= sx, sy, sz < 2^10`

The matrix values may be unsigned 8-bit, 16-bit, or 32-bit integers.

---

## 8. Performance Requirements

The system shall be designed with performance as a major consideration.

The assignment specifies testing with a matrix of size `500^3` bytes and expects at least 100 FPS, with an additional 30 FPS requirement.

Performance measurements shall therefore be included in the final experiment.

---

## 9. Testing Requirements

Testing shall cover:

- Valid input matrices.
- Different plane orientations.
- Points inside the volume.
- Points outside the volume.
- Three-point plane definitions.
- Four-point plane definitions.
- Boundary coordinates.
- Invalid plane definitions.
- Runtime performance.
- Correctness of generated projections.

---

## 10. Demonstration Requirements

The demonstration shall support:

```text
python Ex0.py file.nrrd file.csv file.mp4
```

The arguments represent:

1. NRRD input file.
2. CSV file containing plane coordinates.
3. MP4 output file.

The generated MP4 shall contain a frame corresponding to each plane coordinate in the CSV file.
