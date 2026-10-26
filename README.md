# 3D Plane Projection

## 1. Project Overview

This project implements an algorithm for projecting a plane through a 3D volumetric data matrix into a 2D image matrix.

The input consists of:

- A 3D matrix `M` containing unsigned integer voxel values.
- A plane represented by either 3 or 4 three-dimensional points.

The output is a 2D matrix representing the values sampled from the specified plane.

The project focuses not only on obtaining a correct result, but also on designing a robust and runtime-efficient solution.

## 2. Problem Definition

Given a 3D matrix `M` of size:

`sx × sy × sz`

where:

- `1 <= sx, sy, sz < 2^10`
- `0 <= x < sx`
- `0 <= y < sy`
- `0 <= z < sz`

and each matrix value is an unsigned integer of 8, 16, or 32 bits, the goal is to project a specified plane through the volume into a 2D matrix.

A plane can be represented using three or four points.

For three points `(a,b,c)`, the assignment specifies that:

`|dist(a,b) - dist(a,c)| < EPS`

where `EPS = 0.001`.

The assignment also defines conditions for a four-point representation.

## 3. Projection

For the three-point case, the plane is represented by points `a`, `b`, and `c`, where:

`dist(a,b) = dist(a,c)`

The projection algorithm creates a 2D output matrix and samples points along the plane.

The algorithm moves from `a` toward `b` and from `a` toward `c`. For each resulting row, it traverses between the two corresponding points and samples the 3D matrix.

If a sampled point is outside the input matrix, its value is considered to be zero.

## 4. Input

The project uses NRRD files containing 3D volumetric data.

The assignment encourages the use of NRRD data from the open-source 3D Slicer project, including an MRI dataset.

The demo will also accept a CSV file containing a list of 3 or 4 plane-coordinate points.

## 5. Output

The projection algorithm produces a 2D matrix representing the requested plane.

The final demo is expected to produce an MP4 video containing a frame for each plane coordinate supplied in the CSV file.

## 6. Scope

The project includes:

- Definition of the projection problem.
- Software requirements specification.
- Design of the projection algorithm.
- Definition of the NRRD dataset used for testing.
- Testing strategy.
- Implementation of the projection algorithm.
- A command-line demo.
- Performance evaluation.
- An experiment and results description.

The implementation will be written in one of the languages permitted by the assignment:

- Java
- Python
- C
- C++

## 7. Performance Goal

The implementation should be correct and stable while also being runtime efficient.

For a matrix of size `500^3` bytes, the assignment expects at least 100 FPS, with an additional 30 FPS requirement. The assignment notes that a proper Java implementation can achieve substantially higher performance on an M2 Mac. 

## 8. Project Structure

The planned project structure is:

```text
Ex1/
├── README.md
├── SRS.md
├── src/
├── tests/
├── data/
└── demo/
```

## 9. Demo Interface

The required demo format is:

```text
python Ex0.py file.nrrd file.csv file.mp4
```

Where:

- `file.nrrd` is the 3D volumetric NRRD input.
- `file.csv` contains 3 or 4 point coordinates.
- `file.mp4` is the generated video output.

## 10. Project Goal

The main goal is to design and implement a robust and efficient method for projecting arbitrary supported planes through 3D volumetric data while maintaining good code quality and runtime performance.
