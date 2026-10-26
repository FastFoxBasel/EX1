# Detailed Projection Algorithm Design

## 1. Objective

Given:

- A 3D matrix `M`.
- A plane represented by three points `a`, `b`, and `c`.

Generate a 2D matrix `E` containing the values sampled from the plane.

The three-point representation assumes:

`dist(a,b) = dist(a,c)`

within the allowed tolerance.

---

## 2. Inputs

### Input Matrix

`M` is a 3D matrix with dimensions:

`sx × sy × sz`

Each element contains an unsigned integer value.

### Plane Points

The three points are:

- `a`
- `b`
- `c`

The required geometric condition is:

`|dist(a,b) - dist(a,c)| < EPS`

where:

`EPS = 0.001`.

---

## 3. Geometric Quantities

First calculate:

`Dab = dist(a,b)`

and:

`Dbc = dist(b,c)`

Because the plane is defined using an isosceles triangle:

`dist(a,b) ≈ dist(a,c)`.

Next calculate the normalized direction vectors:

`v(ab) = vector(a,b) / Dab`

and:

`v(ac) = vector(a,c) / Dab`

These vectors describe the directions from `a` toward `b` and `a` toward `c`.

---

## 4. Output Matrix

Create a 2D matrix:

`E`

with dimensions:

`Dab × Dbc`

as specified by the assignment.

The exact implementation representation of these dimensions will need to account for the programming language's indexing and integer representation.

---

## 5. Row Traversal

Create two temporary points:

`a1 = a`

`a2 = a`

For each row:

`y = 0 ... Dab`

advance both points:

`a1 = a1 + v(ab)`

`a2 = a2 + v(ac)`

Therefore:

- `a1` moves from `a` toward `b`.
- `a2` moves from `a` toward `c`.

The segment between `a1` and `a2` represents the current row of the plane.

---

## 6. Traversing One Row

For each row, initialize:

`p = a1`

Calculate:

`d12 = dist(a1,a2)`

Then calculate the normalized direction:

`dp = vector(a1,a2) / d12`

This vector determines the direction in which the algorithm moves across the current row.

---

## 7. Sampling

For:

`x1 = 0 ... d12`

perform the following operations.

### Step 1

Read the value at the current 3D point:

`v = M[p]`

If `p` is not inside the matrix, use:

`v = 0`

### Step 2

Calculate the output x-coordinate:

`x = (Dbc / 2) - (d12 / 2) + x1`

### Step 3

Store the sampled value:

`E[x][y] = v`

### Step 4

Advance to the next point:

`p = p + dp`

---

## 8. Return Value

After all rows and samples have been processed:

`return E`

The result is the 2D projection of the plane through the volume.

---

## 9. Boundary Handling

Before accessing `M[p]`, the point must be checked against the matrix boundaries.

The point is inside the matrix only if its coordinates satisfy the valid ranges for:

`x`

`y`

`z`

If the point lies outside these ranges, the algorithm uses zero rather than attempting an invalid matrix access.

---

## 10. Four-Point Plane

The assignment also permits a plane represented by four points:

`(a1, a2, b, c)`

The specified conditions are:

1. `|dist(a1,b) - dist(a2,c)| < EPS`
2. `dist(a1,a2) <= dist(b,c)`
3. `a1→b` and `a2→c` are on the same plane.

The four-point representation is therefore treated as a planar shape with two vectors having the same length, as described in the assignment.

---

## 11. Algorithm Flow

```text
Input NRRD volume M
        |
        v
Read plane coordinates
        |
        v
Validate plane
        |
        v
Calculate distances
        |
        v
Calculate normalized direction vectors
        |
        v
Create output matrix E
        |
        v
Initialize a1 and a2
        |
        v
For every output row:
        |
        +--> Move a1 toward b
        |
        +--> Move a2 toward c
        |
        +--> Calculate distance between a1 and a2
        |
        +--> Calculate normalized row direction
        |
        +--> Traverse from a1 to a2
                  |
                  +--> Check whether p is inside M
                  |
                  +--> Read M[p], or use 0
                  |
                  +--> Calculate output coordinate
                  |
                  +--> Store value in E
                  |
                  +--> Move to next p
        |
        v
Return E
```

---

## 12. Design Priorities

The implementation should prioritize:

1. Correctness.
2. Stable handling of boundary conditions.
3. Clear separation of geometry and matrix access.
4. Runtime efficiency.
5. Maintainable code.

The assignment explicitly emphasizes design and code quality in addition to the algorithm itself.
