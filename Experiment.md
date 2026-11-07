# Experiment and Results

## Projection Benchmark

Command: `python benchmarks/benchmark.py --repetitions 30`

The deterministic `500 x 500 x 500` byte-volume benchmark measured a median projection time of **3.435 ms**, mean **3.453 ms**, and median throughput of **291.1 projections/s** (72.77 Mpixels/s). This exceeds the course's 130 FPS target. The measurement excludes volume allocation, JIT warm-up, and video encoding.

Environment: Windows 11, AMD Ryzen 7 5800H, Python 3.14.10, NumPy 2.5.4, Numba 0.68.1, pynrrd 1.1.3, OpenCV 5.0.0.

## Newly Supplied CSV Runs

The supplied CSV files were organized under `data/csv/`, their corresponding available volumes are under `data/nrrd/`, and outputs are in `demo/csv_import_runs/`.

| CSV | Volume used | Decoded frames | Result |
| --- | --- | ---: | --- |
| `biscuit_cake.csv` | `biscuit_cake.nrrd` | 120 | Completed at 30 FPS |
| `head.csv` | `MRHead_1.nrrd` | 280 | Completed at 30 FPS; dimensions changed and were padded to a common canvas |
| `lecturer_example.csv` | `MRHead_1.nrrd` | 4 | Completed at 30 FPS; one invalid plane produced an error frame |
| `onion.csv` | `onion.nrrd` | 120 | Completed at 30 FPS |
| `swiss_roll.csv` | `swiss_roll.nrrd` | 120 | Completed at 30 FPS |

`croissant.csv` parses as 100 rows, but its matching NRRD volume was not supplied, so its intended video could not be generated. `edge_cases.csv` refers to an absent synthetic `dice.nrrd` volume and contains a very large plane; it was not rendered as a full video.

## Automated Tests

Command: `python -m unittest discover -s tests -v`

Result: **26 tests passed**. Coverage includes plane geometry, sampling, boundaries, CSV and NRRD input, error frames, and video output.
