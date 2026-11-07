"""Normalize projected slices and encode them as an MP4 video."""

from pathlib import Path

import numpy as np


MIN_FPS = 30.0
DEFAULT_FPS = 30.0


def _display_window(volume):
    """Choose a stable window; constant nonzero data maps to visible mid-gray."""
    values = np.asarray(volume)
    nonzero = values[values != 0]
    if not nonzero.size:
        return 0.0, 1.0

    low, high = np.percentile(nonzero, (1.0, 99.0))
    if high <= low:
        low = float(np.min(nonzero))
        high = float(np.max(nonzero))
    if high <= low:
        padding = max(abs(low) * 1e-6, 0.5)
        low -= padding
        high += padding
    return float(low), float(high)


def _to_grayscale(frame, low, high):
    pixels = np.asarray(frame)
    if pixels.ndim != 2:
        raise ValueError("Each projection must be a 2D matrix.")
    scaled = np.clip((pixels.astype(np.float64) - low) * (255.0 / (high - low)),
                     0.0, 255.0)
    return np.floor(scaled + 0.5).astype(np.uint8)


def make_error_frame(message, volume):
    """Make a visible error card in the display range used for this volume."""
    import cv2

    low, high = _display_window(volume)
    card = np.zeros((96, 480), dtype=np.uint8)
    cv2.putText(card, "INVALID PLANE", (12, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, 255, 2, cv2.LINE_AA)
    cv2.putText(card, str(message)[:66], (12, 58), cv2.FONT_HERSHEY_SIMPLEX,
                0.42, 255, 1, cv2.LINE_AA)
    cv2.putText(card, "Scan continues", (12, 82), cv2.FONT_HERSHEY_SIMPLEX,
                0.42, 190, 1, cv2.LINE_AA)
    return low + card.astype(np.float64) * ((high - low) / 255.0)


def write_mp4(frames, output_path, volume, fps=DEFAULT_FPS):
    """Write one frame per projection, preserving aspect and pixel size.

    Frames with different dimensions are centered on the same black canvas.
    A single display window derived from ``volume`` keeps their brightness
    comparable. The output dimensions are padded to even values for MP4 codecs.
    """
    try:
        import cv2
    except ImportError as exc:  # pragma: no cover - depends on local installation
        raise RuntimeError(
            "MP4 support is not installed. Run 'python -m pip install -r requirements.txt'."
        ) from exc

    frames = list(frames)
    if not frames:
        raise ValueError("At least one projection is required to create a video.")
    if not np.isfinite(fps) or fps < MIN_FPS:
        raise ValueError(f"The video frame rate must be at least {MIN_FPS:g} FPS.")

    gray_frames = []
    low, high = _display_window(volume)
    for frame in frames:
        gray_frames.append(_to_grayscale(frame, low, high))

    canvas_height = max(frame.shape[0] for frame in gray_frames)
    canvas_width = max(frame.shape[1] for frame in gray_frames)
    canvas_height += canvas_height % 2
    canvas_width += canvas_width % 2

    destination = Path(output_path)
    if destination.suffix.lower() != ".mp4":
        raise ValueError("The output video filename must end in .mp4.")
    destination.parent.mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(
        str(destination),
        cv2.VideoWriter_fourcc(*"mp4v"),
        float(fps),
        (canvas_width, canvas_height),
        isColor=True,
    )
    if not writer.isOpened():
        writer.release()
        raise RuntimeError(
            f"Could not open an MP4 encoder for '{destination}'. "
            "Install a build of OpenCV with MP4 video support."
        )

    try:
        for frame in gray_frames:
            canvas = np.zeros((canvas_height, canvas_width), dtype=np.uint8)
            top = (canvas_height - frame.shape[0]) // 2
            left = (canvas_width - frame.shape[1]) // 2
            canvas[top:top + frame.shape[0], left:left + frame.shape[1]] = frame
            writer.write(cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR))
    finally:
        writer.release()

    if not destination.is_file() or destination.stat().st_size == 0:
        raise RuntimeError(f"The MP4 file was not written: '{destination}'.")

    return destination
