"""Plan D — pure-functional video encoding.

Frame-to-features pipeline (downsample → patch grid → oriented filter bank →
feature list) and retinotopic position mapping. No threads, no state, no I/O.
Easily testable.
"""
import numpy as np
from PIL import Image


def downsample_frame(
    frame: np.ndarray,
    output_size: tuple[int, int] = (128, 128),
) -> np.ndarray:
    """Crop to centre square + resize to output_size + convert to grayscale.

    Returns a float32 array in [0, 1].
    """
    if frame.ndim == 3:
        # RGB → grayscale via luma weights
        frame = (
            0.299 * frame[..., 0]
            + 0.587 * frame[..., 1]
            + 0.114 * frame[..., 2]
        )
    h, w = frame.shape
    side = min(h, w)
    top = (h - side) // 2
    left = (w - side) // 2
    cropped = frame[top : top + side, left : left + side]
    img = Image.fromarray(cropped.astype(np.uint8))
    img = img.resize(output_size, resample=Image.BILINEAR)
    return np.asarray(img, dtype=np.float32) / 255.0


ORIENTATIONS_DEG = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5]


def build_oriented_filter_bank(
    kernel_size: int = 5,
    orientations_deg: list[float] | None = None,
) -> np.ndarray:
    """Build a (n_orientations, kernel_size, kernel_size) bank of edge filters.

    Each filter is a directional projection: pixels offset in the filter's
    direction are positive, opposite direction negative. Normalised to
    zero-mean unit-norm.
    """
    if orientations_deg is None:
        orientations_deg = ORIENTATIONS_DEG
    n = len(orientations_deg)
    bank = np.zeros((n, kernel_size, kernel_size), dtype=np.float32)
    half = kernel_size // 2
    for i, deg in enumerate(orientations_deg):
        rad = np.radians(deg)
        cos_t = float(np.cos(rad))
        sin_t = float(np.sin(rad))
        for y in range(kernel_size):
            for x in range(kernel_size):
                dy = y - half
                dx = x - half
                bank[i, y, x] = dx * cos_t + dy * sin_t
        bank[i] -= bank[i].mean()
        norm = float(np.linalg.norm(bank[i]))
        if norm > 1e-9:
            bank[i] /= norm
    return bank
