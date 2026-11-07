# Data Files

Data files are grouped by type:

- `csv/` contains the plane coordinate CSV files, including the small demo input `planes.csv`.
- `nrrd/` contains the 3D NRRD volumes used with the CSV inputs.
- `images/` contains the five dataset screenshots and `overview.png`, used to compare expected views with generated MP4 output. These images are for manual checking and are not read by the program.

## Included NRRD Volumes

| Volume | Shape | Type | Matching CSV |
| --- | --- | --- | --- |
| `nrrd/MRHead_1.nrrd` | `256 x 256 x 130` | signed 16-bit | `csv/head.csv` |
| `nrrd/biscuit_cake.nrrd` | `256 x 256 x 130` | unsigned 16-bit | `csv/biscuit_cake.csv` |
| `nrrd/onion.nrrd` | `256 x 256 x 130` | unsigned 8-bit | `csv/onion.csv` |
| `nrrd/swiss_roll.nrrd` | `256 x 256 x 130` | unsigned 32-bit | `csv/swiss_roll.csv` |

The Croissant reference image and coordinate file are included, but the matching `croissant.nrrd` volume is not, so its CSV cannot be projected against its intended data. The `edge_cases.csv` comments refer to a synthetic `dice.nrrd` volume that is not included.

CSV coordinates are interpreted as voxel indices `(x,y,z)` in NRRD array order; physical-space spacing is not applied. The loader accepts the original 9/12-coordinate format and the extended point-count format with an optional header. Blank lines and comment rows are ignored.
