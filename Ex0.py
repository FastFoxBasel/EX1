"""Command-line demo: project every CSV plane into an MP4 frame."""

import argparse
from time import perf_counter

from src.csv_loader import InvalidPlaneRow, load_coordinates
from src.nrrd_loader import load_nrrd
from src.projection import project
from src.video_writer import DEFAULT_FPS, make_error_frame, write_mp4


def complete_triangle(a, b, c):
    """Complete an isosceles triangle (a,b,c) into an orthogonal bounding rectangle on the plane.

    The altitude vector v_alt = (b + c)/2 - a and base vector v_base = c - b
    are exactly orthogonal in 3D because |dist(a,b) - dist(a,c)| < EPS.
    Spanning the base width and altitude height forms a rectangular planar region
    that encloses the triangle without shear distortion or aspect ratio warping.
    """
    half_base = tuple((ci - bi) / 2.0 for bi, ci in zip(b, c))
    p1 = tuple(ai - h for ai, h in zip(a, half_base))
    p2 = tuple(ai + h for ai, h in zip(a, half_base))
    p3 = tuple(b)
    p4 = tuple(c)
    return (p1, p2, p3, p4)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Project 3D NRRD data along the planes listed in a CSV file."
    )
    parser.add_argument("file_nrrd", help="input 3D NRRD volume")
    parser.add_argument("file_csv", help="CSV file with one plane per row")
    parser.add_argument("file_mp4", help="output MP4 video")
    parser.add_argument(
        "--complete-triangles",
        action="store_true",
        default=True,
        help=(
            "for video display, infer an orthogonal bounding rectangle on the "
            "plane to complete each triangle without shear (default: enabled)"
        ),
    )
    parser.add_argument(
        "--exact-triangles",
        action="store_true",
        help="preserve raw triangular masks without completing for video display",
    )
    args = parser.parse_args(argv)

    should_complete = args.complete_triangles and not args.exact_triangles

    try:
        volume, _header = load_nrrd(args.file_nrrd)
        planes = load_coordinates(args.file_csv, continue_on_error=True)
        print(
            f"Loaded volume: {volume.shape} ({volume.dtype}); "
            f"{len(planes)} plane(s)."
        )

        start = perf_counter()
        frames = []
        error_frames = 0
        completed_triangles = 0
        progress_interval = max(1, len(planes) // 10)
        for index, points in enumerate(planes, start=1):
            if isinstance(points, InvalidPlaneRow):
                frames.append(make_error_frame(points.message, volume))
                error_frames += 1
                continue
            projection_points = points
            if should_complete and len(points) == 3:
                projection_points = complete_triangle(*points)
                completed_triangles += 1

            try:
                frame = project(volume, *projection_points)
            except (ValueError, OverflowError, MemoryError) as exc:
                frames.append(make_error_frame(str(exc), volume))
                error_frames += 1
                print(f"Plane {index}/{len(planes)}: {exc}; added error frame.")
                continue
            frames.append(frame)
            if index == 1 or index == len(planes) or index % progress_interval == 0:
                print(
                    f"Projected plane {index}/{len(planes)}: {frame.shape} pixels."
                )
        projection_seconds = perf_counter() - start

        write_mp4(frames, args.file_mp4, volume, fps=DEFAULT_FPS)
        rate = len(frames) / projection_seconds if projection_seconds else float("inf")
        print(
            f"Wrote {args.file_mp4} with {len(frames)} frame(s) at {DEFAULT_FPS:g} FPS."
        )
        if completed_triangles:
            print(
                f"Completed {completed_triangles} triangle(s) as orthogonal "
                "rectangles for display."
            )
        if error_frames:
            print(f"Added {error_frames} error frame(s); later planes were still processed.")
        print(
            f"Projection compute time: {projection_seconds:.4f} s "
            f"({rate:.1f} projected frame(s)/s; video encoding excluded)."
        )
        return 0
    except Exception as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
