# Sub-project C — Audio I/O (mic + speaker, buffered)

**Date:** 2026-05-06
**Status:** draft (awaiting user approval; ready to convert to a writing-plans plan once approved)
**Parent design doc:** `docs/superpowers/specs/2026-05-06-baby-brain-foundation-design.md` §4.1
**Prerequisite:** none — independent of Plans A and B at the substrate level. Audio I/O calls into the substrate via the public `inject_burst`-style API; substrate dynamics layer (with or without Plan A/B amendments) handles whatever it receives.

---

## 1. What this sub-project adds

The substrate so far is silent. It can take vibrations from a Python test harness via `inject_burst()`, fire atoms when they cluster, and emit vibrations from firing atoms — but it has no connection to the outside world. Plan C closes that gap on the audio side: the substrate listens to a live microphone and speaks through a live speaker. Same encoder, run in reverse for output.

The user's stated north star (the M4 acceptance test from the foundation spec) is the glass-of-water demo: webcam at a glass + spoken "water", repeat 50 times, then show the glass alone and have the substrate produce something that sounds like "water". Plan C provides the audio half of that loop. Plan D provides the visual half. Plan E wires them together with the reward channel into a closed-loop orchestrator.

Plan C, on its own, gives us: a substrate that converts live audio into vibrations injected at the audio input port, and converts firing activity in the audio output port into audible sound played through the speaker. With Plan A's growth amendments, repeating audio patterns will leave persistent structure at frequency-mapped positions in the input port (a tonotopic map). With Plan B's STDP, bridges between co-active frequency regions get directional and the substrate begins to *predict* — but Plan C alone is just the I/O pipe.

## 2. Architecture overview

Three modules, all under a new top-level `agent/` package (introduced by this plan):

1. `agent/encoder_audio.py` — pure-functional audio encoding/decoding. Frequency-to-position mapping, STFT and ISTFT helpers. No threads, no state, no I/O. Easily testable.

2. `agent/audio_io.py` — the live mic and speaker subsystem. Owns two background threads (capture, playback) and two circular buffers. Imports `encoder_audio` for the frequency-to-position math. Exposes one public class `AudioIO` with `start()`, `stop()`, `inject_into_substrate(world, dt)`, and `read_from_substrate(world, dt)` methods.

3. `agent/__init__.py` — re-exports for convenience.

Plus tests in `tests/`.

## 3. Module: `agent/encoder_audio.py`

### 3.1 Frequency-to-position mapping

The substrate's audio input port is a 3D region (set by spec §4 to roughly 25% of one face of the box). Inside the port, vibrations injected by the encoder are placed at positions determined by their frequency bin.

**Recommended choice: logarithmic mapping along one axis of the port.** Real cochlea is logarithmic (octaves are equally spaced), and STFT bins naturally cover 0–8 kHz at 16 kHz sample rate — a wide range where log is the right metric.

```python
def freq_to_port_position(freq: float,
                          freq_min: float = 50.0,
                          freq_max: float = 8000.0,
                          port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
                          port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
                          ) -> tuple[float, float, float]:
    """Map an audio frequency (Hz) to a 3D position inside the port volume.

    Frequency is mapped to the X-axis of the port logarithmically. The Y and
    Z coordinates are random within the port box (so different frequencies
    don't always land on the same y/z and bind into the same electron).
    """
    # Clamp + log-normalise the frequency to [0, 1]
    f_clamped = max(freq_min, min(freq_max, freq))
    log_norm = (np.log(f_clamped) - np.log(freq_min)) / (np.log(freq_max) - np.log(freq_min))
    x = port_origin[0] + log_norm * port_size[0]
    # Y and Z are random within the port box (caller supplies an RNG)
    return x  # (caller picks y, z; see below)
```

(In practice the encoder will compute `x` deterministically from frequency and pick `y`, `z` from the world's RNG so that each emission is reproducible given a seed.)

**Why logarithmic, not linear or Mel:** Logarithmic is the canonical choice in audio neuroscience and the simplest one-knob option that respects the octave structure of natural sound. Mel is a perceptual fine-tune that adds complexity without buying us anything for the proof-of-concept stage. We can switch to Mel in a later sub-project if needed.

### 3.2 Audio block encoding (`encode_block`)

Given a 1D numpy array of audio samples and a sample rate, produce a list of (frequency, amplitude, polarity) triples. The encoder runs an STFT on the block, picks bins with amplitude above a threshold (so silent bins don't inject noise), and emits one (frequency, amplitude, polarity) per significant bin.

```python
def encode_block(samples: np.ndarray,
                 sample_rate: int = 16000,
                 fft_size: int = 512,
                 amplitude_threshold: float = 0.01,
                 freq_min: float = 50.0,
                 freq_max: float = 8000.0
                 ) -> list[tuple[float, float, bool]]:
    """STFT a block, return (freq, amplitude, polarity) per significant bin.

    Polarity is encoded as the sign of the bin's real part: positive → True,
    negative → False. Amplitude is the magnitude clipped to [0, 1].
    """
    spectrum = np.fft.rfft(samples, n=fft_size)
    freqs = np.fft.rfftfreq(fft_size, d=1.0 / sample_rate)
    out = []
    for i, c in enumerate(spectrum):
        f = float(freqs[i])
        if f < freq_min or f > freq_max:
            continue
        a = float(np.abs(c)) / fft_size  # normalise
        if a < amplitude_threshold:
            continue
        polarity = bool(c.real >= 0)
        out.append((f, min(a, 1.0), polarity))
    return out
```

### 3.3 Audio block decoding (`decode_to_audio`)

Inverse of `encode_block`: given a list of (frequency, intensity, polarity) triples (extracted from firing activity in the output port), produce a block of audio samples.

```python
def decode_to_audio(emissions: list[tuple[float, float, bool]],
                    block_size: int = 256,
                    sample_rate: int = 16000,
                    fft_size: int = 512,
                    freq_min: float = 50.0,
                    freq_max: float = 8000.0
                    ) -> np.ndarray:
    """Inverse-STFT a list of (freq, intensity, polarity) triples to audio samples."""
    spectrum = np.zeros(fft_size // 2 + 1, dtype=complex)
    bin_width = sample_rate / fft_size
    for f, a, polarity in emissions:
        if f < freq_min or f > freq_max:
            continue
        bin_idx = int(round(f / bin_width))
        if bin_idx < 0 or bin_idx >= len(spectrum):
            continue
        sign = 1.0 if polarity else -1.0
        spectrum[bin_idx] += a * fft_size * sign  # un-normalise
    samples = np.fft.irfft(spectrum, n=fft_size)
    # Take the first block_size samples; ignore the windowing tail for v1
    return samples[:block_size].astype(np.float32)
```

The v1 decoder skips proper overlap-add windowing — windowing comes in a future iteration if the audio sounds clipped or has artifacts. Acceptance test I2 just needs spectral correlation, not phase-perfect reconstruction.

## 4. Module: `agent/audio_io.py`

### 4.1 The `AudioIO` class

```python
class AudioIO:
    """Live mic + speaker bridge to the substrate's audio input/output ports.

    Two background threads (capture, playback) and two circular buffers
    (input audio, output audio). The main substrate thread drains the input
    buffer and fills the output buffer at its own consumption rate; the
    capture thread fills the input buffer at the live mic rate; the playback
    thread drains the output buffer at the speaker rate.
    """

    def __init__(self,
                 sample_rate: int = 16000,
                 block_size: int = 256,
                 buffer_seconds: float = 30.0,
                 input_port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
                 input_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
                 output_port_origin: tuple[float, float, float] = (45.0, 0.0, 0.0),
                 output_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
                 freq_min: float = 50.0,
                 freq_max: float = 8000.0,
                 mic_device: int | None = None,
                 speaker_device: int | None = None):
        ...

    def start(self) -> None:
        """Open mic and speaker streams; start capture + playback threads."""

    def stop(self) -> None:
        """Stop threads cleanly; close streams."""

    def inject_into_substrate(self, world, dt: float) -> int:
        """Drain input buffer up to dt seconds of audio; encode each block;
        inject vibrations into world at frequency-mapped positions inside
        the input port. Returns count of injected vibrations."""

    def read_from_substrate(self, world, dt: float) -> int:
        """Sample firing activity inside the output port; map firings back
        to frequency bins; decode to audio samples; write to output buffer.
        Returns count of audio samples written."""
```

### 4.2 The two threads

**Capture thread.** Spawned by `start()`. Uses `sounddevice.InputStream` with a callback that writes incoming blocks to the input circular buffer. The buffer has a maximum of `buffer_seconds * sample_rate` samples; on overflow, the oldest data is dropped. The callback is non-blocking and short.

**Playback thread.** Spawned by `start()`. Uses `sounddevice.OutputStream` with a callback that reads from the output circular buffer. If the buffer underruns (substrate isn't producing fast enough), the callback fills with silence rather than blocking.

The substrate thread does NOT run inside `AudioIO`. The application's main loop calls `inject_into_substrate()` and `read_from_substrate()` once per simulation tick.

### 4.3 Circular-buffer implementation

Pure NumPy implementation. Two buffers, each a NumPy array of size `buffer_seconds * sample_rate * 2` (factor 2 to avoid wraparound copies for typical block sizes). Each buffer has its own lock (threading.Lock). Reads and writes lock briefly, copy a block, release.

For v1, simple. We don't need lock-free or atomics — the substrate ticks at ~0.3× realtime, audio threads tick at ~62.5 fps (16000/256), so contention is rare.

## 5. Configuration parameters (added to `WorldConfig`)

All defaults are inert when audio I/O isn't started.

```python
# Plan C — audio I/O
audio_io_enabled: bool = False
audio_sample_rate: int = 16000
audio_block_size: int = 256
audio_fft_size: int = 512
audio_buffer_seconds: float = 30.0
audio_amplitude_threshold: float = 0.01
audio_freq_min: float = 50.0
audio_freq_max: float = 8000.0

# Audio port placement (relative to box_size)
audio_input_port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
audio_input_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
audio_output_port_origin: tuple[float, float, float] = (45.0, 0.0, 0.0)
audio_output_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
```

The `audio_io_enabled` flag is mostly a hint — the actual switch is whether `AudioIO.start()` is called. The flag is useful for tests and for the dashboard UI to know if audio is wired in.

## 6. Acceptance tests

### 6.1 Necessary (unit + integration)

| ID | Test | Pass criterion |
|---|---|---|
| AC1 | `freq_to_port_position` is logarithmic | `freq_to_port_position(50)` is at port left edge; `freq_to_port_position(8000)` is at port right edge; `freq_to_port_position(632)` (one octave above 316, geometric mean of 50 and 8000) is at port centre (within 5% of port width) |
| AC2 | `encode_block` round-trips a pure tone | Generate a 5-cycle 1000 Hz sine wave at 16 kHz; encode_block produces an emission near 1000 Hz with amplitude > threshold; out-of-band silent bins are excluded |
| AC3 | `encode_block` filters silence | All-zero input produces empty list (or list of bins below threshold which are filtered out) |
| AC4 | `decode_to_audio` reconstructs a single tone | Pass `[(1000.0, 0.5, True)]` to decoder; result has spectral peak at 1000 Hz ±2% |
| AC5 | Encode→decode preserves dominant frequency | Encode a 1 kHz tone, decode the resulting emissions, the spectral peak of the decoded signal is at 1 kHz ±5% |
| AC6 | `AudioIO.inject_into_substrate` injects vibrations into the input port | Build a synthetic audio buffer with a 1 kHz tone; call inject_into_substrate; verify world.s_alive has new vibrations within the input port volume; verify their frequencies are near 1 kHz |
| AC7 | `AudioIO.read_from_substrate` produces audio from firings | Manually fire atoms inside the output port at frequency-mapped positions for 1 kHz; call read_from_substrate; verify the output buffer has samples whose dominant frequency is 1 kHz |
| AC8 | Mic→speaker round-trip on synthetic file | Replace `sd.InputStream` with a deterministic synthetic source (10-second 1 kHz tone). Run AudioIO + a substrate that simply re-emits whatever it receives. Verify the speaker output (captured to file) has a spectral peak at 1 kHz with amplitude within 50% of the input. |

### 6.2 Headline integration tests (foundation spec §6.1)

| ID | Test | Pass criterion |
|---|---|---|
| **I1** | **Tonotopic correctness** | Inject a 440 Hz tone for 5 simulated seconds via `AudioIO.inject_into_substrate`. Verify firings (or vibration positions) localised within ±5% of the 440 Hz-mapped position along the port's tonotopic axis. |
| **I2** | **Speaker fidelity** | Manually fire atoms at the 440 Hz-mapped position in the output port for 5 simulated seconds. Verify `read_from_substrate` produces audio with a spectral peak at 440 Hz ±2%. |
| **I3** | **Closed-loop stability** | Run `inject_into_substrate` and `read_from_substrate` together for 5 simulated minutes with the substrate's emit rate equal to its receive rate (i.e. a passthrough). The substrate's vibration count must not grow unbounded; the buffer fill levels must stay within 80% of capacity. No runaway oscillation. |

### 6.3 Stretch

| ID | Test | Pass criterion |
|---|---|---|
| AC9 | Multi-tone preserved | Encode a chord (440 + 880 + 1320 Hz simultaneously); inject; verify all three frequency-mapped positions receive vibrations within 100 ms of each other. |
| AC10 | Buffer overflow handling | Run capture thread at full speed against a substrate consuming at 0.1× realtime for 60 seconds. Confirm buffer drops oldest samples (no crash, no memory growth). |

## 7. Out of scope (future sub-projects)

- **Live webcam (Plan D)** — independent of audio.
- **Reward channel + agent loop (Plan E)** — depends on audio + video being in place.
- **Real-time substrate performance** — the substrate stays at ~0.3× realtime; the substrate's voice plays back slowed-down. Real-time is its own future sub-project.
- **Overlap-add windowing in the decoder** — v1 takes the first `block_size` samples of each ISTFT'd block. Phase artifacts are tolerated as long as I2's spectral correlation passes.
- **Multi-channel audio** — mono only for v1.
- **Adaptive amplitude thresholds** — fixed for v1.

## 8. New module / test layout

```
agent/
  __init__.py             # re-exports AudioIO, encoder helpers
  encoder_audio.py        # freq_to_port_position, encode_block, decode_to_audio
  audio_io.py             # AudioIO class with capture/playback threads

tests/
  test_encoder_audio_freq_mapping.py     # AC1
  test_encoder_audio_encode_block.py     # AC2, AC3
  test_encoder_audio_decode_to_audio.py  # AC4, AC5
  test_audio_io_injection.py             # AC6
  test_audio_io_read.py                  # AC7
  test_audio_io_round_trip.py            # AC8 (uses synthetic source, no real device)
  test_audio_io_tonotopic.py             # I1
  test_audio_io_speaker_fidelity.py      # I2
  test_audio_io_closed_loop.py           # I3 (slow)
  test_audio_io_multi_tone.py            # AC9 (stretch)
  test_audio_io_buffer_overflow.py       # AC10 (stretch)
```

## 9. Decision log

- **Why logarithmic frequency-to-position (not linear)** — biological cochlea is log; octaves are perceptually equal; STFT bins span a wide frequency range where log gives uniform information density. Linear would crowd low frequencies into a tiny region and waste port volume on high frequencies.
- **Why STFT (not wavelet, MFCC, Mel)** — STFT is the simplest, most invertible, most widely understood transform. Bin-to-position mapping is direct. Wavelets give multi-resolution at the cost of decoder complexity. Mel is perceptual and not strictly invertible. STFT is right for the proof-of-concept; we can layer alternatives later.
- **Why polarity = sign of real part** — uses the substrate's polarity field for something audio-meaningful. Phase information per bin is one bit of polarity. Better than always-True.
- **Why two background threads (not one async loop)** — `sounddevice` callbacks run in C threads anyway; treating them as Python threads with a producer/consumer buffer is the cleanest separation. Async would add dependency (asyncio in the substrate).
- **Why circular buffer with drop-oldest on overflow** — the substrate's slowness is a known constraint; we want the agent to perceive the most-recent audio, not the oldest. Drop-oldest preserves recency.
- **Why `audio_io_enabled` flag in WorldConfig** — the dashboard needs to know whether the agent is wired up to live audio. Substrate ticks don't change behaviour based on the flag, but the orchestrator does.
- **Why no decoder windowing in v1** — the acceptance test (I2) is spectral correlation, not perceptual quality. Windowing solves clipping at block boundaries; the demo will sound rough but the test passes. Windowing is a quality improvement, not a correctness fix.

## 10. Risks and what to watch for

- **Audio device discovery on Linux (ALSA) vs macOS (CoreAudio) vs Windows (WASAPI).** `sounddevice` handles cross-platform but the default device is sometimes wrong (Bluetooth headsets that aren't actually connected). Default to `mic_device=None` and `speaker_device=None` (system default), provide config override.
- **Sample format mismatch** — sounddevice defaults to float32. Make sure encode/decode operate in float32 throughout. Tests use float32 explicitly.
- **Latency loop on closed-loop test.** When mic and speaker share a device (loopback), the speaker output is captured by the mic. With substrate ≈ 0.3× realtime, this creates a 3× echo per round-trip. Possible feedback howl. Mitigation: cap the input amplitude threshold so quiet feedback gets filtered out.
- **Buffer sizing.** 30s buffers at 16kHz = 480k samples = ~2 MB per buffer. Two buffers = 4 MB. Fine for desktop, ok for embedded.
- **Permissions.** macOS / iOS require explicit microphone permission. The first run of an agent that uses the mic will trigger an OS prompt. Document this in the README.

---

## Approval gate

Before this becomes a writing-plans plan, the user should confirm:

1. **Logarithmic frequency-to-position mapping** along one axis of the port. Y and Z are random within the port box for variety. Acceptable, or do you want Mel scale or linear instead?

2. **STFT-based encoder** with `fft_size=512`, `amplitude_threshold=0.01`, `freq_min=50, freq_max=8000` Hz. These are sensible for speech and music but tunable. Acceptable defaults?

3. **Polarity = sign of bin real part.** Encodes one bit of phase per bin. Alternative: ignore phase, set polarity at random. Going with sign-of-real adds information without complicating the test. Acceptable?

4. **Two-thread architecture** (capture + playback) plus `inject_into_substrate` / `read_from_substrate` called from the main substrate thread. Alternative: a third thread inside `AudioIO` that calls into the substrate every tick automatically. Acceptable to keep substrate-loop control in the orchestrator, not in `AudioIO`?

5. **`sounddevice` library** dependency. Adds ~3 MB. Cross-platform. Alternative: `pyaudio` (also fine, slightly older). Acceptable to add `sounddevice` to `pyproject.toml`?

6. **Acceptance test I3 (closed-loop stability)** runs for 5 simulated minutes (~15 wall minutes at 0.3× realtime). Mark as `@pytest.mark.slow` and skip in normal CI? Or run as part of standard suite?

If approved, this design becomes the basis for `docs/superpowers/plans/2026-05-06-baby-brain-foundation-plan-C-audio-io.md` with bite-sized TDD tasks following the same pattern as Plans A and B.
