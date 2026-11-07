"""Load a 3D NRRD volume while preserving NRRD axis order."""

try:
    import nrrd
except ImportError as exc:  # pragma: no cover - depends on local installation
    raise ImportError(
        "NRRD support is not installed. Run 'python -m pip install -r requirements.txt'."
    ) from exc


def load_nrrd(filename):
    """Return the 3D volume and header, with array axes matching NRRD indices."""
    volume, header = nrrd.read(filename, index_order="F")
    if volume.ndim != 3:
        raise ValueError(
            f"Expected a 3D NRRD volume, got {volume.ndim} dimensions."
        )
    return volume, header
