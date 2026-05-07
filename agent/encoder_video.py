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


def _convolve2d_same(frame: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """2D convolution with same-size output (reflect padding). Pure numpy."""
    h, w = frame.shape
    ks = kernel.shape[0]
    hk = ks // 2
    padded = np.pad(frame, hk, mode="reflect")
    out = np.zeros((h, w), dtype=np.float32)
    for ky in range(ks):
        for kx in range(ks):
            out += padded[ky : ky + h, kx : kx + w] * kernel[ky, kx]
    return out


def encode_frame(
    frame_grayscale: np.ndarray,
    patch_grid: tuple[int, int] = (16, 16),
    filter_bank: np.ndarray | None = None,
    amplitude_threshold: float = 0.05,
) -> list[tuple[int, int, int, float, bool]]:
    """For each patch in the grid, compute response to each oriented filter.

    Convolves the full frame with each filter (reflect-padded, same size),
    then takes the peak absolute response within each patch. Returns
    (patch_x, patch_y, orientation_id, magnitude, sign) tuples for responses
    with magnitude ≥ amplitude_threshold. Sign is the sign of the peak
    response pixel.
    """
    if filter_bank is None:
        filter_bank = build_oriented_filter_bank()
    n_orientations = filter_bank.shape[0]
    h, w = frame_grayscale.shape
    pg_y, pg_x = patch_grid
    patch_h = h // pg_y
    patch_w = w // pg_x
    out: list[tuple[int, int, int, float, bool]] = []
    for o in range(n_orientations):
        resp_map = _convolve2d_same(frame_grayscale, filter_bank[o])
        for py in range(pg_y):
            for px in range(pg_x):
                patch_resp = resp_map[
                    py * patch_h : (py + 1) * patch_h,
                    px * patch_w : (px + 1) * patch_w,
                ]
                # peak absolute response within patch
                abs_resp = np.abs(patch_resp)
                peak_idx = int(np.argmax(abs_resp))
                peak_abs = float(abs_resp.flat[peak_idx])
                if peak_abs < amplitude_threshold:
                    continue
                peak_signed = float(patch_resp.flat[peak_idx])
                sign = peak_signed >= 0.0
                out.append((int(px), int(py), int(o), min(peak_abs, 1.0), bool(sign)))
    return out
