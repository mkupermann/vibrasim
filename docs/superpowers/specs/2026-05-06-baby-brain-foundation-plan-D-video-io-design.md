# Sub-project D — Video I/O (webcam, Gabor patch features)

**Date:** 2026-05-06
**Status:** draft (awaiting user approval; ready to convert to a writing-plans plan once approved)
**Parent design doc:** `docs/superpowers/specs/2026-05-06-baby-brain-foundation-design.md` §4.2
**Prerequisite:** none — independent of Plans A, B, C at the substrate level. Video I/O calls into the substrate via the same `inject_burst`-style API used by Plan C.

---

## 1. What this sub-project adds

Plan C lets the substrate hear. Plan D lets it see. The webcam stream is converted into vibration injections at the *video input port* — a 3D region of the substrate's box positioned on a face adjacent to the audio input port (so cross-modal bridges can form between them). The retinotopic encoding mirrors what biological V1 does: each frame is divided into a grid of patches, and oriented filters extract edge orientation + intensity per patch. Each oriented feature becomes a vibration burst at a substrate position derived from `(patch_x, patch_y, orientation_id)`.

Plan D, on its own, gives us: a substrate that ingests live video as a flow of frequency-encoded vibrations laid out retinotopically. Combined with Plan A's growth amendments, repeated visual patterns will build persistent structure in the video port. Combined with Plan B's STDP, audio events that co-occur with visual events will form cross-modal bridges between the audio and video ports. The glass-of-water demo (foundation spec M4) becomes possible once Plans A through E are all in place.

This plan does **not** add video output. The substrate doesn't dream pictures yet — that's a future sub-project. Plan D is video-input-only.

## 2. Architecture overview

Two modules, paralleling Plan C's structure, plus shared use of the `agent/` package introduced by Plan C:

1. `agent/encoder_video.py` — pure-functional video encoding. Frame-to-features pipeline (downsample → patch grid → oriented filter bank → feature list). Retinotopic position mapping. No threads, no state, no I/O. Easily testable.

2. `agent/video_io.py` — the live webcam subsystem. Owns one background thread (capture) and one circular frame buffer. Imports `encoder_video` for the patch-feature math. Exposes one public class `VideoIO` with `start()`, `stop()`, `inject_into_substrate(world, dt)` methods.

(There's no `read_from_substrate` because Plan D is input-only.)

## 3. Module: `agent/encoder_video.py`

### 3.1 Frame downsampling

Webcam frames at 640×480 are too large to encode efficiently. Downsample to a fixed working size (default 128×128 grayscale) before patch extraction. Use bilinear interpolation. Preserve aspect ratio by cropping the centre.

```python
def downsample_frame(frame: np.ndarray,
                     output_size: tuple[int, int] = (128, 128)) -> np.ndarray:
    """Crop to centre square + resize to output_size + convert to grayscale.
    Returns a float32 array in [0, 1]."""
    if frame.ndim == 3:
        # Convert RGB → grayscale (luma weights)
        frame = (0.299 * frame[..., 0] + 0.587 * frame[..., 1] + 0.114 * frame[..., 2])
    h, w = frame.shape
    side = min(h, w)
    top = (h - side) // 2
    left = (w - side) // 2
    cropped = frame[top:top + side, left:left + side]
    # Resize via PIL or cv2 — both work; use whichever the project already has
    from PIL import Image
    img = Image.fromarray(cropped.astype(np.uint8))
    img = img.resize(output_size, resample=Image.BILINEAR)
    return np.asarray(img, dtype=np.float32) / 255.0
```

### 3.2 Patch grid + oriented filter bank

Default: 16×16 patches over a 128×128 frame → each patch is 8×8 pixels. For each patch, run a small oriented-filter bank with 8 orientations (every 22.5°). Each filter is a 5×5 Sobel-like kernel rotated to its orientation; convolution gives the response per patch.

```python
ORIENTATIONS_DEG = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5]

def build_oriented_filter_bank(kernel_size: int = 5,
                                orientations_deg: list[float] = ORIENTATIONS_DEG
                                ) -> np.ndarray:
    """Return a (n_orientations, kernel_size, kernel_size) bank of edge filters."""
    bank = np.zeros((len(orientations_deg), kernel_size, kernel_size), dtype=np.float32)
    half = kernel_size // 2
    for i, deg in enumerate(orientations_deg):
        rad = np.radians(deg)
        cos_t = np.cos(rad)
        sin_t = np.sin(rad)
        # Project each pixel offset onto the filter direction; positive on
        # one side of the line, negative on the other → edge detector.
        for y in range(kernel_size):
            for x in range(kernel_size):
                dy = y - half
                dx = x - half
                proj = dx * cos_t + dy * sin_t
                bank[i, y, x] = proj
        # Normalise so each filter is zero-mean
        bank[i] -= bank[i].mean()
        norm = float(np.linalg.norm(bank[i]))
        if norm > 1e-9:
            bank[i] /= norm
    return bank


def encode_frame(frame_grayscale: np.ndarray,
                 patch_grid: tuple[int, int] = (16, 16),
                 filter_bank: np.ndarray | None = None,
                 amplitude_threshold: float = 0.05
                 ) -> list[tuple[int, int, int, float, bool]]:
    """For each patch, compute response to each oriented filter. Return a list
    of (patch_x, patch_y, orientation_id, magnitude, sign) tuples for responses
    above amplitude_threshold.

    `sign` is the sign of the patch response — light-on-dark vs dark-on-light.
    """
    if filter_bank is None:
        filter_bank = build_oriented_filter_bank()
    n_orientations = filter_bank.shape[0]
    h, w = frame_grayscale.shape
    pg_y, pg_x = patch_grid
    patch_h = h // pg_y
    patch_w = w // pg_x
    out = []
    for py in range(pg_y):
        for px in range(pg_x):
            patch = frame_grayscale[py*patch_h:(py+1)*patch_h,
                                     px*patch_w:(px+1)*patch_w]
            for o in range(n_orientations):
                # Tile the filter to patch size if smaller; use mean of valid rows
                ksize = filter_bank.shape[1]
                if patch.shape[0] >= ksize and patch.shape[1] >= ksize:
                    centre_y, centre_x = patch.shape[0] // 2, patch.shape[1] // 2
                    half = ksize // 2
                    region = patch[centre_y - half: centre_y - half + ksize,
                                    centre_x - half: centre_x - half + ksize]
                    response = float(np.sum(region * filter_bank[o]))
                else:
                    response = 0.0
                magnitude = abs(response)
                if magnitude < amplitude_threshold:
                    continue
                sign = response >= 0.0
                out.append((px, py, o, min(magnitude, 1.0), sign))
    return out
```

### 3.3 Retinotopic position mapping

Each (patch_x, patch_y, orientation_id) tuple maps to a 3D position inside the video input port. The mapping preserves spatial layout: patches in the upper-left of the frame map to positions in the upper-left of the port. Orientation is encoded along the third axis (so different orientations of the same patch land at different depths).

```python
def patch_to_port_position(patch_x: int,
                           patch_y: int,
                           orientation_id: int,
                           patch_grid: tuple[int, int] = (16, 16),
                           n_orientations: int = 8,
                           port_origin: tuple[float, float, float] = (0.0, 0.0, 45.0),
                           port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
                           ) -> tuple[float, float, float]:
    """Map a (patch_x, patch_y, orientation_id) to a 3D position in the video port."""
    pg_x, pg_y = patch_grid
    x = port_origin[0] + (patch_x + 0.5) / pg_x * port_size[0]
    y = port_origin[1] + (patch_y + 0.5) / pg_y * port_size[1]
    z = port_origin[2] + (orientation_id + 0.5) / n_orientations * port_size[2]
    return (x, y, z)
```

The vibration's frequency is determined by the feature's magnitude: stronger edges produce higher-frequency vibrations (so they bind faster — the substrate "notices" them more eagerly).

```python
def feature_magnitude_to_frequency(magnitude: float,
                                    freq_min: float = 1000.0,
                                    freq_max: float = 12000.0) -> float:
    """Map magnitude in [0, 1] to a frequency in [freq_min, freq_max]."""
    return freq_min + magnitude * (freq_max - freq_min)
```

## 4. Module: `agent/video_io.py`

### 4.1 The `VideoIO` class

```python
class VideoIO:
    """Live webcam capture into the substrate's video input port.

    One background thread (capture) and one circular frame buffer. The main
    substrate thread drains the buffer at its own consumption rate; the
    capture thread fills the buffer at the webcam's native frame rate.
    """

    def __init__(self,
                 fps: int = 30,
                 buffer_seconds: float = 5.0,
                 patch_grid: tuple[int, int] = (16, 16),
                 n_orientations: int = 8,
                 amplitude_threshold: float = 0.05,
                 video_port_origin: tuple[float, float, float] = (0.0, 0.0, 45.0),
                 video_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
                 freq_min: float = 1000.0,
                 freq_max: float = 12000.0,
                 webcam_index: int = 0):
        ...

    def start(self) -> None:
        """Open webcam; start capture thread."""

    def stop(self) -> None:
        """Stop capture thread cleanly; release webcam."""

    def inject_into_substrate(self, world, dt: float) -> int:
        """Drain the most-recent frame from the buffer; encode features;
        inject vibrations at retinotopic positions inside the video port.
        Returns count of injected vibrations."""
```

### 4.2 The capture thread

Spawned by `start()`. Uses `cv2.VideoCapture(webcam_index)` (OpenCV) with a tight loop that reads frames at the webcam's native rate and writes them to the circular frame buffer. The buffer holds up to `fps * buffer_seconds` frames; on overflow the oldest frame is dropped.

`inject_into_substrate` reads the *most recent* frame from the buffer (not the oldest), encodes it, and injects. We do not encode every captured frame — at 30 fps that's 30 × 256 features × n_orientations = ~60,000 vibrations per second of webcam, which the substrate cannot consume. We encode only the frame that's "current" at substrate-tick time.

This means the substrate sees a strobed video signal: one frame per substrate-tick interval (~16.7 ms at the substrate's `dt = 1/60`, ~50 ms at 0.3× realtime → roughly 20 fps perceived). That's fine for the proof-of-concept.

### 4.3 OpenCV vs other capture libraries

`cv2.VideoCapture` is the de facto standard. Alternatives: `picamera` (Pi-only), `imageio` (slower for webcam), `v4l2` directly (Linux-only). OpenCV is cross-platform, well-maintained, and gives float32 RGB arrays. The cost is the dependency size (~50 MB for opencv-python-headless) — acceptable for desktop, may need to be optional for embedded.

## 5. Configuration parameters (added to `WorldConfig`)

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

Note: `video_input_port_origin` defaults to `(0, 0, 45)` — same X/Y face as the audio input port, but offset along Z. This puts the audio and video ports on the *same face* of the box at non-overlapping Z bands, so cross-modal bridges form across the boundary at Z=30 (the spec's "adjacent faces" intent simplified to "non-overlapping regions on the same face").

## 6. Acceptance tests

### 6.1 Necessary (unit + integration)

| ID | Test | Pass criterion |
|---|---|---|
| VC1 | `downsample_frame` produces 128×128 grayscale float32 in [0,1] | Test with a 640×480 RGB image; output has shape (128, 128) and dtype float32 and values in [0, 1] |
| VC2 | `build_oriented_filter_bank` produces 8 zero-mean unit-norm filters | Each filter has mean ≈ 0 and Frobenius norm = 1 |
| VC3 | `encode_frame` of a uniform grey frame produces empty output | Edge-free frame → no features above threshold |
| VC4 | `encode_frame` of a vertical-edge image produces a vertical-orientation feature | A frame split half-black, half-white along a vertical line → encode produces a feature with `orientation_id` corresponding to 0° (horizontal gradient) — i.e. *vertical edges* manifest as horizontal-direction filters firing strongest |
| VC5 | `encode_frame` of a horizontal-edge image produces a horizontal-orientation feature | Symmetric to VC4 |
| VC6 | `patch_to_port_position` is retinotopic | patch at (0,0) maps to port lower-left at depth 0; patch at (15,15) maps to upper-right at max depth; orientation_id=4 maps to mid-depth |
| VC7 | `VideoIO.inject_into_substrate` injects vibrations into the video port | Build a synthetic 640×480 frame with a single bright vertical bar; call inject_into_substrate; verify world.s_alive has new vibrations within the video port volume; verify their positions cluster on the bar's column |
| VC8 | Two distinct shapes produce distinct port patterns | Show a vertical line, capture the port firing pattern. Show a horizontal line, capture again. Pairwise cosine similarity between the patterns < 0.5. |

### 6.2 Headline integration test (foundation spec §6.1)

| ID | Test | Pass criterion |
|---|---|---|
| **I4** | **Video encoding distinctness** | Synthesise three 256×256 frames: (a) a single horizontal line, (b) a single vertical line, (c) a circle. For each frame, run `encode_frame` + `patch_to_port_position` and capture the set of port positions that received features. Pairwise cosine similarity between any two of the three patterns must be < 0.5 (i.e. the three shapes produce structurally distinct vibration patterns in the port). |

### 6.3 Stretch

| ID | Test | Pass criterion |
|---|---|---|
| VC9 | Webcam round-trip on synthetic frames | Replace `cv2.VideoCapture` with a deterministic stub that returns a sequence of pre-built frames (vertical line, horizontal line, circle, blank). Verify the buffer accumulates all four; encode_frame produces the expected set of port firings for each. |
| VC10 | Buffer overflow handling | Run capture stub at full speed against a substrate that only consumes one frame per second for 30 seconds. Confirm the buffer drops oldest frames (no crash, no memory growth). |

## 7. Out of scope (future sub-projects)

- **Video output.** The substrate doesn't generate pictures yet. A future "dream" sub-project could.
- **Color encoding.** v1 is grayscale only. Color → vibration polarity could come later.
- **Motion features (optical flow).** v1 encodes static frames independently. Motion-as-feature is a future addition.
- **Multi-camera support.** v1 supports one webcam.
- **Real-time webcam display in dashboard.** That's the dashboard's problem, not Plan D's.

## 8. New module / test layout

```
agent/
  __init__.py             # already created in Plan C; re-exports VideoIO
  encoder_video.py        # downsample_frame, build_oriented_filter_bank, encode_frame, patch_to_port_position
  video_io.py             # VideoIO class with capture thread

tests/
  test_encoder_video_downsample.py        # VC1
  test_encoder_video_filter_bank.py       # VC2
  test_encoder_video_encode_frame.py      # VC3, VC4, VC5
  test_encoder_video_position_mapping.py  # VC6
  test_video_io_injection.py              # VC7
  test_video_io_distinct_patterns.py      # VC8
  test_video_io_distinctness.py           # I4 (headline integration)
  test_video_io_synthetic_round_trip.py   # VC9 (stretch)
  test_video_io_buffer_overflow.py        # VC10 (stretch)
```

## 9. Decision log

- **Why 16×16 patch grid (not finer/coarser)** — 256 patches × 8 orientations = 2048 features per frame, which is on the edge of what the substrate can absorb at substrate tick rates. Coarser (8×8 grid → 64 patches) loses spatial detail. Finer (32×32 → 1024 patches × 8 = 8192 features) overwhelms the input buffer.
- **Why 8 orientations (not 4 or 16)** — 8 covers half-quadrants (every 22.5°), enough to distinguish typical edge orientations without over-saturating the orientation axis of the port. Biological V1 has many more orientations per location, but they're tuned to a continuous space — we approximate with 8.
- **Why grayscale (not color)** — color is a separable concern. Adding RGB triples the encoder cost and the input rate, and color-based learning is a different research question. v1 is grayscale.
- **Why oriented Sobel-like filters (not Gabor wavelets)** — Sobel is faster, simpler, and the difference is small for edge detection at typical patch sizes. Gabor is more biologically faithful but adds frequency tuning per orientation, which doesn't buy us anything for the demo. Could swap to Gabor in a perf-tuning pass.
- **Why retinotopic mapping (not random)** — preserves spatial locality. Two pixels that are spatially close in the visual field land at spatially close positions in the port. This is what biological V1 does, and it's what makes spatial co-occurrence translate into spatial co-firing → bridge formation between adjacent areas.
- **Why orientation along Z-axis (not folded into XY)** — keeps the XY plane purely retinotopic (matching the visual field) and uses the third dimension for the feature axis. Different orientations of the same patch land at different depths, so they form bridges to *different* substrate regions, allowing the system to learn which orientation matters.
- **Why one capture thread, not many** — webcams are single-channel devices; one thread is enough.
- **Why most-recent-frame consumption (not encoding every frame)** — substrate cannot keep up with 30 fps × 2048 features. We accept frame-skipping as the natural rate-matching mechanism.

## 10. Risks and what to watch for

- **Webcam permissions on macOS.** First-run prompt to allow camera access. Document in the README. Tests use synthetic frames, not real webcam, to remain CI-friendly.
- **Webcam discovery.** `webcam_index=0` is the default but Macs with multiple cameras (built-in, external, virtual cams from Zoom/Teams) may surface unexpected devices. Provide a config override.
- **OpenCV dependency size.** ~50 MB. Acceptable for desktop.
- **Performance.** 256 patches × 8 orientations × 5×5 convolution = ~50,000 ops per frame. At 30 fps, ~1.5M ops/sec. Pure NumPy: trivial. Pre-compiling the filter bank as a single tensor and using `np.einsum` makes this even faster.

---

## Approval gate

Before this becomes a writing-plans plan, the user should confirm:

1. **Grayscale-only encoding for v1.** Color comes in a future sub-project. Acceptable, or do you want color from day one?

2. **Oriented Sobel-like filters with 8 orientations** vs Gabor wavelets. Sobel is simpler, faster, and gives the same edge-detection behaviour for our purposes. Acceptable, or do you specifically want Gabor's biological fidelity?

3. **16×16 patch grid** (4× downsampled from a 128×128 frame, so each patch is 8×8 pixels). Tunable. Acceptable as default?

4. **Most-recent-frame consumption** (not encoding every captured frame). Means the substrate sees roughly one frame per substrate-tick — a strobed video signal. Acceptable, or do you want the substrate to encode every frame at the cost of overwhelming the buffer?

5. **Retinotopic XY + orientation Z** layout in the video port. Patches preserve spatial layout in XY; orientation_id maps to Z. Acceptable, or do you want a different axis layout (e.g. orientation interleaved with X)?

6. **OpenCV (`cv2`)** dependency. Cross-platform but ~50 MB. Alternative: `imageio` (smaller, slower). Acceptable to add `opencv-python-headless` to `pyproject.toml`?

If approved, this design becomes the basis for `docs/superpowers/plans/2026-05-06-baby-brain-foundation-plan-D-video-io.md` with bite-sized TDD tasks following the same pattern as Plans A, B, C.
