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
