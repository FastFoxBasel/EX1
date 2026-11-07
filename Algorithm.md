# Projection Algorithm Design

## 1. Objective and Coordinate Convention

Given a three-dimensional integer volume `M` and a supported planar region, return a two-dimensional matrix containing nearest-neighbour samples from that region. Coordinates are in voxel-index units and follow the NRRD array order: `M[x, y, z]`. The returned image is organized as `E[row, column]`.

The assignment specifies a triangle through three points or an isosceles trapezoid through four points. Its pseudocode leaves the integer dimensions, fractional distances, voxel rounding, and image-axis layout open. This design defines those details explicitly.

## 2. Input Validation

The volume must be a non-empty 3D integer NumPy array. Each point must have three finite coordinates.

### Three-point triangle `(a, b, c)`

1. Compute `Dab = dist(a,b)`, `Dac = dist(a,c)`, and `Dbc = dist(b,c)`.
2. Require `abs(Dab - Dac) < EPS`, where `EPS = 0.001`.
3. Reject a zero-length edge or a collinear point set, since it cannot define a plane.
4. Use the normalized vectors from `a` to `b` and from `a` to `c` as the two swept edges.

### Four-point trapezoid `(a1, a2, b, c)`

1. Treat `a1 -> b` and `a2 -> c` as the equal-length swept sides. If the first listed base is strictly longer than the second base by more than `EPS = 0.001`, reverse the base order while preserving those side pairings, so the shorter base is the row start. When the two bases are equal within `EPS` (such as a square or rectangle), the orientation is preserved without floating-point swapping glitches.
2. Require `abs(dist(a1,b) - dist(a2,c)) < EPS`.
3. Require `dist(a1,a2) <= dist(b,c) + EPS`.
4. Require all four points to be coplanar within `EPS` voxel units. The implementation finds a non-degenerate plane through three of the points and measures the remaining point's perpendicular distance to it.
5. Reject a zero-length swept side or a degenerate, collinear point set.

The four-point checks follow the course Q&A. The equal-side and coplanarity tolerances use the specified `EPS` value; the base-length condition is the specified non-strict inequality.

## 3. Discrete Output Size

Let `La` and `Lb` be the lengths of the two swept sides, and `B` the larger base length. The side lengths may differ by less than `EPS`; each dimension includes both endpoints:

```text
height = ceil(max(La, Lb) - 1e-4) + 1
width  = ceil(B - 1e-4) + 1
```

A small epsilon (`1e-4`) absorbs floating-point roundoff near integer dimensions (e.g., `255.00000000000003` stays `256`), preventing pixel-dimension jitter between consecutive video frames. This conversion means an edge of integer length `n` has `n + 1` endpoint-inclusive samples. A fractional final step is shorter than one voxel. For a three-point plane, `B = dist(b,c)`. For a four-point plane, `B = dist(b,c)` under the validated shorter-base rule.

## 4. Row Construction

For a triangle, both swept edges start at `a`; their directions point toward `b` and `c`. For a trapezoid, they start at `a1` and `a2`; their directions point toward `b` and `c`.

For each row index `r`:

1. Set the distances along the two swept edges to `min(r, La)` and `min(r, Lb)`. This gives row zero at the first base and includes both far endpoints in the last row, even when the valid side lengths differ slightly within `EPS`.
2. Advance both start points by that distance along their respective unit vectors.
3. The segment between the advanced points defines the current row. Let its length be `Drow` and its direction be the normalized segment vector. If `Drow` is zero, the row contains one point.

## 5. Sampling a Row

The row is centered in the output image. For each integer step `k` from zero through `ceil(Drow)`:

1. Use distance `min(k, Drow)` along the row. The final fractional step therefore lands on the endpoint rather than beyond it.
2. Map the sample to output column:

   ```text
   center = (width - 1) / 2
   column = round_half_up(center - Drow / 2 + k)
   ```

3. If the continuous sample coordinate lies outside any volume axis, store zero. Otherwise round each coordinate half up to the nearest voxel and read `M[x,y,z]`.
4. Store the value at `E[row, column]`.

The implementation uses a Numba-compiled sampling kernel to walk rows and sample voxels without Python overhead. If Numba is unavailable, a NumPy-vectorized fallback performs the same calculations. Both paths retain the input integer dtype in `E`.

## 6. Boundary and Numeric Rules

- A continuous coordinate is inside only when `0 <= coordinate <= size - 1` on all axes. For example, `x = -0.2` is outside even though it could round to voxel zero.
- Out-of-volume points return zero and never index the matrix.
- Voxel and output-column rounding use `floor(value + 0.5)`, which rounds half values upward.
- Input coordinates and intermediate geometry must be finite.
- Plane dimensions are in voxel units; NRRD physical-space spacing is not applied to the assignment's index-coordinate points.

## 7. Complexity

For an output of `H x W` pixels, projection requires `O(HW)` coordinate calculations and voxel reads. Its temporary arrays are also `O(HW)`. The implementation does not scan the input volume; it accesses only points on the requested plane.
