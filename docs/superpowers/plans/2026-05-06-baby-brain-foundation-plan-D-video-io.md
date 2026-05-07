# Plan D — Video I/O (webcam, retinotopic patch features) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect the substrate to a live webcam. Each frame is downsampled to 128×128 grayscale, divided into a 16×16 patch grid, run through an oriented Sobel-like filter bank (8 orientations), and the resulting (patch_x, patch_y, orientation_id, magnitude, sign) features are injected as vibrations at retinotopic positions inside a video input port.

**Architecture:** Two-module addition to the `agent/` package created by Plan C. (1) `agent/encoder_video.py` — pure functions: `downsample_frame`, `build_oriented_filter_bank`, `encode_frame`, `patch_to_port_position`, `feature_magnitude_to_frequency`. (2) `agent/video_io.py` — `VideoIO` class with one background capture thread (OpenCV `cv2.VideoCapture`) and a circular frame buffer; `inject_into_substrate(world, dt)` reads the most-recent buffered frame, encodes it, injects features. **Input only** — no `read_from_substrate`; substrate doesn't dream pictures yet.

**Tech Stack:** Python 3.13, NumPy, `opencv-python-headless` (~50 MB), Pillow (already a transitive dep — used for downsample), pytest. New runtime dep: `opencv-python-headless>=4.9,<5.0` added to the existing `agent` extra in pyproject.toml.

**Spec reference:** `docs/superpowers/specs/2026-05-06-baby-brain-foundation-plan-D-video-io-design.md` — approved 2026-05-07. All six approval-gate questions accepted with the spec's recommended defaults.

**Prerequisite:** Plan C merged to main (provides `agent/__init__.py` + the `agent` extra in pyproject.toml). Plan D extends both.

---

## File map

| Path | Action | Responsibility |
|---|---|---|
| `pyproject.toml` | Modify | Add `opencv-python-headless>=4.9,<5.0` to existing `agent` extra |
| `world/config.py` | Modify | Add 11 video fields with safe defaults |
| `agent/__init__.py` | Modify | Re-export VideoIO + video encoder helpers |
| `agent/encoder_video.py` | Create | `downsample_frame`, `build_oriented_filter_bank`, `encode_frame`, `patch_to_port_position`, `feature_magnitude_to_frequency` |
| `agent/video_io.py` | Create | `VideoIO` class — capture thread + circular frame buffer + `inject_into_substrate` |
| `tests/test_encoder_video_downsample.py` | Create | VC1 |
| `tests/test_encoder_video_filter_bank.py` | Create | VC2 |
| `tests/test_encoder_video_encode_frame.py` | Create | VC3, VC4, VC5 |
| `tests/test_encoder_video_position_mapping.py` | Create | VC6 |
| `tests/test_video_io_injection.py` | Create | VC7 |
| `tests/test_video_io_distinct_patterns.py` | Create | VC8 |
| `tests/test_video_io_distinctness.py` | Create | I4 (headline integration) |
| `db/migrations/0008_planD_video_io_amendment.sql` | Create | VIDEO-IO-R1 amendment + Makefile target |

VC9 and VC10 (synthetic round-trip + buffer overflow stretch tests) deferred to follow-up plan if needed. Webcam-real tests are not in scope — all tests use synthetic frames.

---

## Task 1: Plan D config fields + opencv dep

**Files:**
- Modify: `world/config.py`
- Modify: `pyproject.toml`
- Test: `tests/test_config.py` (append)

- [ ] **Step 1.1: Append the failing test**

```python
def test_plan_D_video_fields_have_safe_defaults():
    """Plan D video fields default off so legacy configs are unaffected."""
    cfg = WorldConfig()
    assert cfg.video_io_enabled is False
    assert cfg.video_fps == 30
    assert cfg.video_buffer_seconds == 5.0
    assert cfg.video_patch_grid == (16, 16)
    assert cfg.video_n_orientations == 8
    assert cfg.video_amplitude_threshold == 0.05
    assert cfg.video_freq_min == 1000.0
    assert cfg.video_freq_max == 12000.0
    assert cfg.video_input_port_origin == (0.0, 0.0, 45.0)
    assert cfg.video_input_port_size == (15.0, 15.0, 15.0)
    assert cfg.video_webcam_index == 0
```

- [ ] **Step 1.2: Run test, expect failure**

```bash
uv run pytest tests/test_config.py::test_plan_D_video_fields_have_safe_defaults -v
```

- [ ] **Step 1.3: Add fields to WorldConfig**

In `world/config.py`, add after the Plan C audio block, before Plan A.5:

```python
    # Plan D — video I/O
    video_io_enabled: bool = False
    video_fps: int = 30
    video_buffer_seconds: float = 5.0
    video_patch_grid: tuple[int, int] = (16, 16)
    video_n_orientations: int = 8
    video_amplitude_threshold: float = 0.05
    video_freq_min: float = 1000.0
    video_freq_max: float = 12000.0
    video_input_port_origin: tuple[float, float, float] = (0.0, 0.0, 45.0)
    video_input_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
    video_webcam_index: int = 0
```

- [ ] **Step 1.4: Add opencv to pyproject.toml's `agent` extra**

The `agent` extra was created in Plan C with `sounddevice`. Append `opencv-python-headless>=4.9,<5.0`:

```toml
agent = [
    "sounddevice>=0.4,<1.0",
    "opencv-python-headless>=4.9,<5.0",
]
```

- [ ] **Step 1.5: Run test + suite**

```bash
uv run pytest -q -m "not slow"
```

Expected: 230 passed (Plan C baseline 229 + 1 new), 14 deselected.

- [ ] **Step 1.6: Commit**

```
feat(config): add Plan D video I/O fields + opencv-python-headless extra

11 video fields default to inert values; VideoIO start() is the actual
switch. opencv-python-headless added to the existing 'agent' extra
alongside sounddevice. Substrate-only users skip the dep.
```

---

## Task 2: `downsample_frame` (VC1)

**Files:**
- Create: `agent/encoder_video.py`
- Create: `tests/test_encoder_video_downsample.py`

- [ ] **Step 2.1: Create test**

```python
"""Tests for frame downsampling (VC1)."""
import numpy as np
from agent.encoder_video import downsample_frame


def test_VC1_downsample_640_480_rgb_to_128_128_grayscale():
    """640×480 RGB uint8 → 128×128 grayscale float32 in [0, 1]."""
    rng = np.random.default_rng(0)
    frame = rng.integers(0, 256, size=(480, 640, 3), dtype=np.uint8)
    out = downsample_frame(frame, output_size=(128, 128))
    assert out.shape == (128, 128)
    assert out.dtype == np.float32
    assert (out >= 0.0).all() and (out <= 1.0).all()


def test_VC1b_uniform_grey_input_produces_uniform_output():
    frame = np.full((480, 640, 3), 128, dtype=np.uint8)
    out = downsample_frame(frame, output_size=(128, 128))
    # All pixels should be very close to 128/255 ≈ 0.502
    assert abs(float(out.mean()) - 128.0 / 255.0) < 0.01
    assert float(out.std()) < 0.05


def test_VC1c_already_grayscale_input_works():
    """A 2D grayscale input should not crash on the RGB-to-luma branch."""
    frame = np.full((480, 640), 200, dtype=np.uint8)
    out = downsample_frame(frame, output_size=(128, 128))
    assert out.shape == (128, 128)
    assert abs(float(out.mean()) - 200.0 / 255.0) < 0.01
```

- [ ] **Step 2.2: Run, expect ImportError**

- [ ] **Step 2.3: Implement `agent/encoder_video.py`**

```python
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
```

- [ ] **Step 2.4: Run, expect pass**

Expected: 233 passed (230 + 3).

- [ ] **Step 2.5: Commit**

```
feat(agent): downsample_frame — webcam to 128×128 grayscale (VC1)

Plan D Task 2: centre-crop + bilinear resize via Pillow + RGB-to-luma
conversion. Returns float32 in [0, 1].
```

---

## Task 3: `build_oriented_filter_bank` (VC2)

**Files:**
- Modify: `agent/encoder_video.py`
- Create: `tests/test_encoder_video_filter_bank.py`

- [ ] **Step 3.1: Create test**

```python
"""Tests for oriented filter bank construction (VC2)."""
import numpy as np
from agent.encoder_video import build_oriented_filter_bank


def test_VC2_filter_bank_shape_and_count():
    bank = build_oriented_filter_bank()
    # 8 orientations by default, 5×5 kernel
    assert bank.shape == (8, 5, 5)
    assert bank.dtype == np.float32


def test_VC2b_each_filter_zero_mean_unit_norm():
    bank = build_oriented_filter_bank()
    for i in range(bank.shape[0]):
        f = bank[i]
        assert abs(float(f.mean())) < 1e-5, f"filter {i} mean={f.mean()}"
        assert abs(float(np.linalg.norm(f)) - 1.0) < 1e-5, (
            f"filter {i} norm={np.linalg.norm(f)}"
        )


def test_VC2c_orientations_are_distinct():
    """No two orientation filters should be identical."""
    bank = build_oriented_filter_bank()
    n = bank.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            cosine = float(
                np.sum(bank[i] * bank[j]) /
                (np.linalg.norm(bank[i]) * np.linalg.norm(bank[j]))
            )
            assert abs(cosine) < 0.99, (
                f"filters {i} and {j} too similar (cos={cosine})"
            )
```

- [ ] **Step 3.2: Run, expect ImportError**

- [ ] **Step 3.3: Implement**

Append to `agent/encoder_video.py`:

```python
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
```

- [ ] **Step 3.4: Run, expect pass**

Expected: 236 passed (233 + 3).

- [ ] **Step 3.5: Commit**

```
feat(agent): build_oriented_filter_bank — 8 directional Sobel-like edge filters (VC2)

Plan D Task 3: each filter is a directional projection over the kernel
window; normalised zero-mean unit-norm. Default 8 orientations every
22.5°.
```

---

## Task 4: `encode_frame` (VC3, VC4, VC5)

**Files:**
- Modify: `agent/encoder_video.py`
- Create: `tests/test_encoder_video_encode_frame.py`

- [ ] **Step 4.1: Tests**

```python
"""Tests for frame encoding (VC3, VC4, VC5)."""
import numpy as np
from agent.encoder_video import encode_frame, build_oriented_filter_bank


def test_VC3_uniform_grey_produces_no_features():
    """Edge-free frame → no features above threshold."""
    frame = np.full((128, 128), 0.5, dtype=np.float32)
    features = encode_frame(frame, patch_grid=(16, 16), amplitude_threshold=0.05)
    assert features == []


def test_VC4_vertical_edge_image_produces_horizontal_filter_response():
    """A vertical line (left half black, right half white) produces a strong
    response from the filter oriented at 0° — the horizontal-gradient detector."""
    frame = np.zeros((128, 128), dtype=np.float32)
    frame[:, 64:] = 1.0  # right half white
    features = encode_frame(frame, patch_grid=(16, 16), amplitude_threshold=0.05)
    assert len(features) > 0
    # Filter index 0 = 0° orientation (horizontal direction → detects vertical edges)
    horizontal_responses = [f for f in features if f[2] == 0]
    assert len(horizontal_responses) > 0, (
        f"VC4: expected feature with orientation_id=0, got {[f[2] for f in features]}"
    )


def test_VC5_horizontal_edge_image_produces_vertical_filter_response():
    """A horizontal line (top half black, bottom half white) produces a strong
    response from the filter oriented at 90° — the vertical-gradient detector."""
    frame = np.zeros((128, 128), dtype=np.float32)
    frame[64:, :] = 1.0  # bottom half white
    features = encode_frame(frame, patch_grid=(16, 16), amplitude_threshold=0.05)
    assert len(features) > 0
    # Filter index 4 = 90° orientation (vertical direction → detects horizontal edges)
    vertical_responses = [f for f in features if f[2] == 4]
    assert len(vertical_responses) > 0, (
        f"VC5: expected feature with orientation_id=4, got {[f[2] for f in features]}"
    )


def test_VC3b_below_threshold_filtered():
    rng = np.random.default_rng(0)
    # Tiny noise — magnitude well below 0.05 threshold
    frame = (0.5 + 0.001 * rng.standard_normal((128, 128))).astype(np.float32)
    features = encode_frame(frame, patch_grid=(16, 16), amplitude_threshold=0.05)
    assert features == []


def test_VC4b_returns_5tuples():
    """encode_frame returns (patch_x, patch_y, orientation_id, magnitude, sign)."""
    frame = np.zeros((128, 128), dtype=np.float32)
    frame[:, 64:] = 1.0
    features = encode_frame(frame, patch_grid=(16, 16))
    assert len(features) > 0
    f = features[0]
    assert len(f) == 5
    assert isinstance(f[0], int) or isinstance(f[0], np.integer)
    assert isinstance(f[1], int) or isinstance(f[1], np.integer)
    assert isinstance(f[2], int) or isinstance(f[2], np.integer)
    assert isinstance(f[3], float)
    assert isinstance(f[4], (bool, np.bool_))
```

- [ ] **Step 4.2: Run, expect ImportError on encode_frame**

- [ ] **Step 4.3: Implement**

Append to `agent/encoder_video.py`:

```python
def encode_frame(
    frame_grayscale: np.ndarray,
    patch_grid: tuple[int, int] = (16, 16),
    filter_bank: np.ndarray | None = None,
    amplitude_threshold: float = 0.05,
) -> list[tuple[int, int, int, float, bool]]:
    """For each patch in the grid, compute response to each oriented filter.

    Returns (patch_x, patch_y, orientation_id, magnitude, sign) tuples for
    responses with magnitude ≥ amplitude_threshold. Sign is the sign of the
    raw filter response.
    """
    if filter_bank is None:
        filter_bank = build_oriented_filter_bank()
    n_orientations = filter_bank.shape[0]
    h, w = frame_grayscale.shape
    pg_y, pg_x = patch_grid
    patch_h = h // pg_y
    patch_w = w // pg_x
    ksize = filter_bank.shape[1]
    half_k = ksize // 2
    out: list[tuple[int, int, int, float, bool]] = []
    for py in range(pg_y):
        for px in range(pg_x):
            patch = frame_grayscale[
                py * patch_h : (py + 1) * patch_h,
                px * patch_w : (px + 1) * patch_w,
            ]
            if patch.shape[0] < ksize or patch.shape[1] < ksize:
                continue
            cy, cx = patch.shape[0] // 2, patch.shape[1] // 2
            region = patch[cy - half_k : cy - half_k + ksize, cx - half_k : cx - half_k + ksize]
            for o in range(n_orientations):
                response = float(np.sum(region * filter_bank[o]))
                magnitude = abs(response)
                if magnitude < amplitude_threshold:
                    continue
                sign = response >= 0.0
                out.append((int(px), int(py), int(o), min(magnitude, 1.0), bool(sign)))
    return out
```

- [ ] **Step 4.4: Run, expect pass**

Expected: 241 passed (236 + 5).

- [ ] **Step 4.5: Commit**

```
feat(agent): encode_frame — patch grid × orientation features (VC3-VC5)

Plan D Task 4: per-patch convolution against the oriented filter bank;
returns (patch_x, patch_y, orientation_id, magnitude, sign) for
responses above amplitude_threshold. Edge-free frames → empty list.
Vertical edges fire the 0° (horizontal-gradient) filter; horizontal
edges fire the 90° filter.
```

---

## Task 5: `patch_to_port_position` + `feature_magnitude_to_frequency` (VC6)

**Files:**
- Modify: `agent/encoder_video.py`
- Create: `tests/test_encoder_video_position_mapping.py`

- [ ] **Step 5.1: Tests**

```python
"""Tests for retinotopic position mapping (VC6)."""
import numpy as np
import pytest
from agent.encoder_video import patch_to_port_position, feature_magnitude_to_frequency


def test_VC6_lower_left_patch_maps_to_lower_left_of_port():
    pos = patch_to_port_position(
        patch_x=0, patch_y=0, orientation_id=0,
        patch_grid=(16, 16), n_orientations=8,
        port_origin=(0.0, 0.0, 45.0), port_size=(15.0, 15.0, 15.0),
    )
    # patch (0,0) → centre of first patch at (0+0.5)/16 × 15 = 0.46875
    assert pos[0] == pytest.approx(0.46875, abs=1e-3)
    assert pos[1] == pytest.approx(0.46875, abs=1e-3)
    # orientation_id=0 → centre of first depth bin: 45 + (0+0.5)/8 × 15 = 45.9375
    assert pos[2] == pytest.approx(45.9375, abs=1e-3)


def test_VC6b_upper_right_patch_maps_to_upper_right_of_port():
    pos = patch_to_port_position(
        patch_x=15, patch_y=15, orientation_id=7,
        patch_grid=(16, 16), n_orientations=8,
        port_origin=(0.0, 0.0, 45.0), port_size=(15.0, 15.0, 15.0),
    )
    # patch (15,15) → (15+0.5)/16 × 15 = 14.53125
    assert pos[0] == pytest.approx(14.53125, abs=1e-3)
    assert pos[1] == pytest.approx(14.53125, abs=1e-3)
    # orientation_id=7 → 45 + (7+0.5)/8 × 15 = 59.0625
    assert pos[2] == pytest.approx(59.0625, abs=1e-3)


def test_VC6c_orientation_4_at_mid_depth():
    pos = patch_to_port_position(
        patch_x=8, patch_y=8, orientation_id=4,
        patch_grid=(16, 16), n_orientations=8,
        port_origin=(0.0, 0.0, 45.0), port_size=(15.0, 15.0, 15.0),
    )
    # orientation_id=4 → 45 + (4+0.5)/8 × 15 = 53.4375
    assert pos[2] == pytest.approx(53.4375, abs=1e-3)


def test_VC6d_feature_magnitude_to_frequency_endpoints():
    assert feature_magnitude_to_frequency(0.0, freq_min=1000.0, freq_max=12000.0) == 1000.0
    assert feature_magnitude_to_frequency(1.0, freq_min=1000.0, freq_max=12000.0) == 12000.0
    assert feature_magnitude_to_frequency(0.5, freq_min=1000.0, freq_max=12000.0) == 6500.0
```

- [ ] **Step 5.2: Run, expect ImportError**

- [ ] **Step 5.3: Implement**

Append to `agent/encoder_video.py`:

```python
def patch_to_port_position(
    patch_x: int,
    patch_y: int,
    orientation_id: int,
    patch_grid: tuple[int, int] = (16, 16),
    n_orientations: int = 8,
    port_origin: tuple[float, float, float] = (0.0, 0.0, 45.0),
    port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
) -> tuple[float, float, float]:
    """Map a (patch_x, patch_y, orientation_id) to a 3D position in the video port.

    XY is retinotopic — patch centre maps to the matching XY-fraction of the
    port. Z is the orientation axis — orientation_id 0..n_orientations-1 maps
    to evenly-spaced depth bins.
    """
    pg_x, pg_y = patch_grid
    x = port_origin[0] + (patch_x + 0.5) / pg_x * port_size[0]
    y = port_origin[1] + (patch_y + 0.5) / pg_y * port_size[1]
    z = port_origin[2] + (orientation_id + 0.5) / n_orientations * port_size[2]
    return (float(x), float(y), float(z))


def feature_magnitude_to_frequency(
    magnitude: float,
    freq_min: float = 1000.0,
    freq_max: float = 12000.0,
) -> float:
    """Map magnitude in [0, 1] linearly to a frequency in [freq_min, freq_max]."""
    return float(freq_min + magnitude * (freq_max - freq_min))
```

- [ ] **Step 5.4: Run, expect pass**

Expected: 245 passed (241 + 4).

- [ ] **Step 5.5: Commit**

```
feat(agent): patch_to_port_position + feature_magnitude_to_frequency (VC6)

Plan D Task 5: retinotopic XY mapping inside the video port; orientation
goes along the Z axis. Stronger edges → higher-frequency vibrations
(closer to upper end of the substrate's audible band).
```

---

## Task 6: `VideoIO` skeleton + `inject_into_substrate` (VC7)

**Files:**
- Create: `agent/video_io.py`
- Modify: `agent/__init__.py` (re-export VideoIO + video helpers)
- Create: `tests/test_video_io_injection.py`

- [ ] **Step 6.1: Tests**

```python
"""Tests for VideoIO.inject_into_substrate (VC7)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.video_io import VideoIO


def _world_for_video():
    return World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=2048,
        box_size=(60.0, 60.0, 60.0),
        video_io_enabled=True,
        video_input_port_origin=(0.0, 0.0, 45.0),
        video_input_port_size=(15.0, 15.0, 15.0),
    ))


def test_VC7_inject_creates_vibrations_in_video_port():
    """Synthetic frame with a vertical bright bar → injected vibrations
    cluster on that column inside the video port."""
    w = _world_for_video()
    io = VideoIO(
        fps=30, buffer_seconds=1.0,
        patch_grid=(16, 16), n_orientations=8,
        amplitude_threshold=0.05,
        video_port_origin=(0.0, 0.0, 45.0),
        video_port_size=(15.0, 15.0, 15.0),
    )
    # Synthetic 640×480 frame: vertical bright bar in the right half
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, 320:, :] = 255
    io._write_frame_buffer(frame)

    n_alive_before = int(w.s_alive.sum())
    n_injected = io.inject_into_substrate(w, dt=1.0 / 30)
    n_alive_after = int(w.s_alive.sum())

    assert n_injected > 0, "VC7: no vibrations injected from a bright-bar frame"
    assert n_alive_after > n_alive_before
    # All injected vibrations within the video port box
    new_indices = np.where(w.s_alive)[0]
    pos = w.s_pos[new_indices]
    assert ((pos[:, 0] >= 0.0) & (pos[:, 0] <= 15.0)).all()
    assert ((pos[:, 1] >= 0.0) & (pos[:, 1] <= 15.0)).all()
    assert ((pos[:, 2] >= 45.0) & (pos[:, 2] <= 60.0)).all()
```

- [ ] **Step 6.2: Run, expect ImportError**

- [ ] **Step 6.3: Implement `agent/video_io.py`**

```python
"""Plan D — live webcam capture into the substrate's video input port."""
import threading
from collections import deque
from typing import Optional
import numpy as np

from agent.encoder_video import (
    downsample_frame,
    build_oriented_filter_bank,
    encode_frame,
    patch_to_port_position,
    feature_magnitude_to_frequency,
)


class VideoIO:
    """Live webcam → vibration injections into the video input port.

    One background thread (capture) and one circular frame buffer. The
    main substrate thread calls inject_into_substrate() once per tick;
    VideoIO does not run the substrate.
    """

    def __init__(
        self,
        fps: int = 30,
        buffer_seconds: float = 5.0,
        patch_grid: tuple[int, int] = (16, 16),
        n_orientations: int = 8,
        amplitude_threshold: float = 0.05,
        video_port_origin: tuple[float, float, float] = (0.0, 0.0, 45.0),
        video_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
        freq_min: float = 1000.0,
        freq_max: float = 12000.0,
        webcam_index: int = 0,
        rng: Optional[np.random.Generator] = None,
    ):
        self.fps = fps
        self.buffer_seconds = buffer_seconds
        self.patch_grid = patch_grid
        self.n_orientations = n_orientations
        self.amplitude_threshold = amplitude_threshold
        self.video_port_origin = video_port_origin
        self.video_port_size = video_port_size
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.webcam_index = webcam_index
        self.rng = rng if rng is not None else np.random.default_rng()

        self._filter_bank = build_oriented_filter_bank(
            kernel_size=5, orientations_deg=None,
        )

        max_frames = int(fps * buffer_seconds)
        self._frame_buffer: deque[np.ndarray] = deque(maxlen=max_frames)
        self._frame_lock = threading.Lock()

        self._capture_thread: Optional[threading.Thread] = None
        self._capture_running = False

    def _write_frame_buffer(self, frame: np.ndarray) -> None:
        """Direct write — used by tests and by the capture thread."""
        with self._frame_lock:
            self._frame_buffer.append(frame)

    def _read_latest_frame(self) -> Optional[np.ndarray]:
        """Read the most-recent frame; returns None if buffer is empty."""
        with self._frame_lock:
            if len(self._frame_buffer) == 0:
                return None
            return self._frame_buffer[-1]

    def inject_into_substrate(self, world, dt: float) -> int:
        """Read the most-recent buffered frame; encode features; inject one
        vibration per feature at its retinotopic port position."""
        frame = self._read_latest_frame()
        if frame is None:
            return 0
        downsampled = downsample_frame(frame, output_size=(128, 128))
        features = encode_frame(
            downsampled,
            patch_grid=self.patch_grid,
            filter_bank=self._filter_bank,
            amplitude_threshold=self.amplitude_threshold,
        )
        n_injected = 0
        for px, py, o, magnitude, sign in features:
            pos = patch_to_port_position(
                px, py, o,
                patch_grid=self.patch_grid,
                n_orientations=self.n_orientations,
                port_origin=self.video_port_origin,
                port_size=self.video_port_size,
            )
            f = feature_magnitude_to_frequency(
                magnitude, freq_min=self.freq_min, freq_max=self.freq_max,
            )
            free_idx = np.where(~world.s_alive)[0]
            if len(free_idx) == 0:
                break
            i = int(free_idx[0])
            world.s_pos[i] = pos
            world.s_vel[i] = 0.0
            world.s_freq[i] = float(f)
            world.s_pol[i] = bool(sign)
            world.s_alive[i] = True
            world.n_alive = max(world.n_alive, i + 1)
            n_injected += 1
        return n_injected

    def start(self) -> None:
        """Open webcam; start capture thread.

        Lazy-imports cv2 so substrate-only users don't need OpenCV.
        """
        if self._capture_running:
            return
        import cv2

        cap = cv2.VideoCapture(self.webcam_index)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open webcam at index {self.webcam_index}")

        self._capture_running = True

        def _loop():
            while self._capture_running:
                ok, frame = cap.read()
                if not ok:
                    break
                # cv2 returns BGR; convert to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self._write_frame_buffer(frame_rgb)

        self._capture_thread = threading.Thread(target=_loop, daemon=True)
        self._capture_thread.start()
        self._cap = cap

    def stop(self) -> None:
        if not self._capture_running:
            return
        self._capture_running = False
        if self._capture_thread is not None:
            self._capture_thread.join(timeout=2.0)
            self._capture_thread = None
        if hasattr(self, "_cap"):
            self._cap.release()
            del self._cap
```

Update `agent/__init__.py` to re-export VideoIO:

```python
"""Agent package: I/O bridges between the substrate and the outside world."""
from agent.encoder_audio import freq_to_port_position, encode_block, decode_to_audio
from agent.audio_io import AudioIO
from agent.encoder_video import (
    downsample_frame,
    build_oriented_filter_bank,
    encode_frame,
    patch_to_port_position,
    feature_magnitude_to_frequency,
)
from agent.video_io import VideoIO

__all__ = [
    "AudioIO",
    "VideoIO",
    "freq_to_port_position",
    "encode_block",
    "decode_to_audio",
    "downsample_frame",
    "build_oriented_filter_bank",
    "encode_frame",
    "patch_to_port_position",
    "feature_magnitude_to_frequency",
]
```

- [ ] **Step 6.4: Run, expect pass**

Expected: 246 passed (245 + 1).

- [ ] **Step 6.5: Commit**

```
feat(agent): VideoIO skeleton + inject_into_substrate (VC7)

Plan D Task 6: VideoIO with one threading.Lock-protected deque frame
buffer. inject_into_substrate reads the most-recent frame, encodes
features via the encoder pipeline, injects one vibration per feature
at its retinotopic port position. start() lazy-imports cv2 and runs
a capture thread; tests use _write_frame_buffer directly so no real
webcam is required for CI.
```

---

## Task 7: VC8 distinct-shape patterns

**Files:**
- Create: `tests/test_video_io_distinct_patterns.py`

- [ ] **Step 7.1: Test**

```python
"""Tests that distinct shapes produce distinct port firing patterns (VC8)."""
import numpy as np
from agent.encoder_video import (
    downsample_frame, encode_frame, patch_to_port_position,
)


def _features_to_position_set(features, patch_grid=(16, 16), n_orientations=8):
    return {(f[0], f[1], f[2]) for f in features}


def test_VC8_distinct_shapes_produce_distinct_patterns():
    """Vertical line, horizontal line, and uniform-grey produce port firing
    patterns whose pairwise Jaccard similarity is < 0.5."""
    # Vertical line
    f_vert = np.zeros((480, 640, 3), dtype=np.uint8)
    f_vert[:, 320, :] = 255  # one-pixel vertical line

    # Horizontal line
    f_horiz = np.zeros((480, 640, 3), dtype=np.uint8)
    f_horiz[240, :, :] = 255  # one-pixel horizontal line

    # Half-and-half (different from both)
    f_half = np.zeros((480, 640, 3), dtype=np.uint8)
    f_half[:, 320:, :] = 255  # right half white

    features_v = encode_frame(downsample_frame(f_vert), amplitude_threshold=0.05)
    features_h = encode_frame(downsample_frame(f_horiz), amplitude_threshold=0.05)
    features_b = encode_frame(downsample_frame(f_half), amplitude_threshold=0.05)

    set_v = _features_to_position_set(features_v)
    set_h = _features_to_position_set(features_h)
    set_b = _features_to_position_set(features_b)

    def jaccard(a, b):
        if not a and not b:
            return 1.0
        return len(a & b) / max(len(a | b), 1)

    j_vh = jaccard(set_v, set_h)
    j_vb = jaccard(set_v, set_b)
    j_hb = jaccard(set_h, set_b)
    print(f"VC8 jaccards: V↔H={j_vh:.2f}, V↔B={j_vb:.2f}, H↔B={j_hb:.2f}")
    assert j_vh < 0.5, f"VC8: vertical vs horizontal too similar ({j_vh})"
    assert j_vb < 0.5, f"VC8: vertical vs half too similar ({j_vb})"
    assert j_hb < 0.5, f"VC8: horizontal vs half too similar ({j_hb})"
```

- [ ] **Step 7.2: Run, expect pass**

Expected: 247 passed.

- [ ] **Step 7.3: Commit**

```
test(agent): VC8 — distinct shapes produce distinct port patterns

Plan D Task 7: vertical line, horizontal line, half-and-half — pairwise
Jaccard similarity of feature position sets < 0.5. Validates the
encoder discriminates structural shape differences.
```

---

## Task 8: I4 video encoding distinctness (headline)

**Files:**
- Create: `tests/test_video_io_distinctness.py`

- [ ] **Step 8.1: Test**

```python
"""Headline integration test I4 — video encoding distinctness."""
import numpy as np
from agent.encoder_video import (
    downsample_frame, encode_frame, patch_to_port_position,
)


def _feature_set(features):
    """Convert features to a set of (px, py, o) tuples for similarity."""
    return {(f[0], f[1], f[2]) for f in features}


def test_I4_video_encoding_distinctness():
    """Three 256×256 frames — horizontal line, vertical line, circle —
    produce port firing patterns with pairwise cosine similarity < 0.5.
    """
    # Horizontal line
    f_h = np.zeros((256, 256), dtype=np.uint8)
    f_h[128, :] = 255

    # Vertical line
    f_v = np.zeros((256, 256), dtype=np.uint8)
    f_v[:, 128] = 255

    # Circle
    f_c = np.zeros((256, 256), dtype=np.uint8)
    yy, xx = np.ogrid[:256, :256]
    cx, cy, r = 128, 128, 60
    mask = (xx - cx) ** 2 + (yy - cy) ** 2
    f_c[(mask >= (r - 2) ** 2) & (mask <= (r + 2) ** 2)] = 255

    features = [
        encode_frame(downsample_frame(f), amplitude_threshold=0.05)
        for f in (f_h, f_v, f_c)
    ]
    sets = [_feature_set(fs) for fs in features]
    sizes = [len(s) for s in sets]
    print(f"I4 set sizes: {sizes}")

    def cosine(a, b):
        # Treat sets as binary vectors over their union.
        u = a | b
        if not u:
            return 1.0
        va = np.array([1 if e in a else 0 for e in u])
        vb = np.array([1 if e in b else 0 for e in u])
        norm_a = float(np.linalg.norm(va))
        norm_b = float(np.linalg.norm(vb))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(va @ vb / (norm_a * norm_b))

    cos_hv = cosine(sets[0], sets[1])
    cos_hc = cosine(sets[0], sets[2])
    cos_vc = cosine(sets[1], sets[2])
    print(f"I4 cosines: H↔V={cos_hv:.2f}, H↔C={cos_hc:.2f}, V↔C={cos_vc:.2f}")
    assert cos_hv < 0.5
    assert cos_hc < 0.5
    assert cos_vc < 0.5
```

- [ ] **Step 8.2: Run, expect pass**

Expected: 248 passed.

- [ ] **Step 8.3: Commit**

```
test(agent): I4 — video encoding distinctness (headline)

Plan D Task 8: horizontal line, vertical line, circle — pairwise cosine
similarity of feature sets < 0.5. Headline integration test for the
input pipeline.
```

---

## Task 9: VIDEO-IO-R1 dashboard amendment migration

**Files:**
- Create: `db/migrations/0008_planD_video_io_amendment.sql`
- Modify: `Makefile`

- [ ] **Step 9.1: Migration**

Pattern matches `0007_planC_audio_io_amendment.sql`. INSERT VIDEO-IO-R1 row + parameterised UPDATE binding `:'merge_sha'`.

- [ ] **Step 9.2: Makefile target**

`db-migrate-planD-mark-implemented MERGE_SHA=<sha>` matching prior migrations.

- [ ] **Step 9.3: Suite check**

```bash
uv run pytest -q -m "not slow"
```

Expected: 248 passed, 14 deselected.

- [ ] **Step 9.4: Commit**

```
feat(infra): Plan D Task 9 — VIDEO-IO-R1 amendment migration

Checked-in migration + Makefile target, same pattern as Plan A.5,
Plan B, Plan C. Run after merge:
    make db-migrate-planD-mark-implemented MERGE_SHA=<sha>

Plan D implementation complete. Final code review next, then merge
to main.
```

---

## Plan D complete

Verify final state:

```bash
uv run pytest -q -m "not slow"  # 248 expected
uv run pytest tests/test_encoder_video_*.py tests/test_video_io_*.py -v  # all pass
git log --oneline feat/baby-brain-plan-D  # ~10 commits including the plan
```

**Next plans:**
- **Plan E** — Reward channel + closed-loop orchestrator. Depends on A + C + D. **Spec needs to be brainstormed** (no spec exists yet) before writing the plan.
- **Plan F** — Brain checkpoint / resume. Extends snapshot persistence to handle long-running brain state including audio/video buffers.
- **Plan G** — End-to-end M4 demo (glass-of-water).
