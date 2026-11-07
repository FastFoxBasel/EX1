"""Benchmark projection compute time for a 500-cubed byte volume."""

import argparse
from pathlib import Path
import statistics
import sys
from time import perf_counter

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.projection import project  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repetitions", type=int, default=30,
        help="number of measured projections after warm-up (default: 30)",
    )
    args = parser.parse_args(argv)
    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")

    rng = np.random.default_rng(20261028)
    volume = rng.integers(0, 256, size=(500, 500, 500), dtype=np.uint8)
    # A 499-voxel square on z=250 yields a 500 x 500 output plane.
    points = (
        (0, 0, 250),
        (0, 499, 250),
        (499, 0, 250),
        (499, 499, 250),
    )

    for _ in range(min(5, args.repetitions)):
        project(volume, *points)

    timings = []
    for _ in range(args.repetitions):
        start = perf_counter()
        result = project(volume, *points)
        timings.append(perf_counter() - start)

    median_seconds = statistics.median(timings)
    mean_seconds = statistics.mean(timings)
    pixels = int(result.size)
    print(f"Volume: {volume.shape}, {volume.nbytes:,} bytes, {volume.dtype}")
    print(f"Projection: {result.shape}, {pixels:,} output pixels")
    print(f"Repetitions: {args.repetitions} (plus {min(5, args.repetitions)} warm-up)")
    print(f"Median compute time: {median_seconds * 1000:.3f} ms")
    print(f"Mean compute time: {mean_seconds * 1000:.3f} ms")
    print(f"Median throughput: {1.0 / median_seconds:.1f} projections/s")
    print(f"Median sampled-pixel rate: {pixels / median_seconds / 1_000_000:.2f} Mpixels/s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
