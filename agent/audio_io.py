"""Plan C — live mic + speaker bridge to the substrate's audio ports."""
import threading
from typing import Optional
import numpy as np

from agent.encoder_audio import encode_block, decode_to_audio, freq_to_port_position


class AudioIO:
    """Live mic + speaker bridge.

    Two background threads (capture, playback) and two circular numpy
    buffers. The substrate thread calls inject_into_substrate() and
    read_from_substrate() once per tick; AudioIO does not run the
    substrate.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        block_size: int = 256,
        buffer_seconds: float = 30.0,
        input_port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
        input_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
        output_port_origin: tuple[float, float, float] = (45.0, 0.0, 0.0),
        output_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
        freq_min: float = 50.0,
        freq_max: float = 8000.0,
        fft_size: int = 512,
        amplitude_threshold: float = 0.01,
        mic_device: Optional[int] = None,
        speaker_device: Optional[int] = None,
        rng: Optional[np.random.Generator] = None,
    ):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.buffer_seconds = buffer_seconds
        self.input_port_origin = input_port_origin
        self.input_port_size = input_port_size
        self.output_port_origin = output_port_origin
        self.output_port_size = output_port_size
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.fft_size = fft_size
        self.amplitude_threshold = amplitude_threshold
        self.mic_device = mic_device
        self.speaker_device = speaker_device
        self.rng = rng if rng is not None else np.random.default_rng()

        # Circular buffers — float32 mono
        n_buffer_samples = int(buffer_seconds * sample_rate * 2)
        self._input_buffer = np.zeros(n_buffer_samples, dtype=np.float32)
        self._input_write_pos = 0
        self._input_read_pos = 0
        self._input_lock = threading.Lock()

        self._output_buffer = np.zeros(n_buffer_samples, dtype=np.float32)
        self._output_write_pos = 0
        self._output_read_pos = 0
        self._output_lock = threading.Lock()

        self._capture_stream = None
        self._playback_stream = None
        self._running = False

    def _write_input_buffer(self, audio: np.ndarray) -> None:
        """Direct write — used by tests and by the capture thread."""
        with self._input_lock:
            n = len(audio)
            buf_len = len(self._input_buffer)
            for i in range(n):
                self._input_buffer[(self._input_write_pos + i) % buf_len] = audio[i]
            self._input_write_pos = (self._input_write_pos + n) % buf_len

    def _read_input_buffer(self, n_samples: int) -> np.ndarray:
        """Read up to n_samples; returns float32 array of however many available."""
        with self._input_lock:
            buf_len = len(self._input_buffer)
            available = (self._input_write_pos - self._input_read_pos) % buf_len
            n = min(n_samples, available)
            if n == 0:
                return np.zeros(0, dtype=np.float32)
            out = np.empty(n, dtype=np.float32)
            for i in range(n):
                out[i] = self._input_buffer[(self._input_read_pos + i) % buf_len]
            self._input_read_pos = (self._input_read_pos + n) % buf_len
            return out

    def _write_output_buffer(self, audio: np.ndarray) -> None:
        with self._output_lock:
            n = len(audio)
            buf_len = len(self._output_buffer)
            for i in range(n):
                self._output_buffer[(self._output_write_pos + i) % buf_len] = audio[i]
            self._output_write_pos = (self._output_write_pos + n) % buf_len

    def _read_output_buffer(self, n_samples: int) -> np.ndarray:
        with self._output_lock:
            buf_len = len(self._output_buffer)
            available = (self._output_write_pos - self._output_read_pos) % buf_len
            n = min(n_samples, available)
            if n == 0:
                return np.zeros(0, dtype=np.float32)
            out = np.empty(n, dtype=np.float32)
            for i in range(n):
                out[i] = self._output_buffer[(self._output_read_pos + i) % buf_len]
            self._output_read_pos = (self._output_read_pos + n) % buf_len
            return out

    def inject_into_substrate(self, world, dt: float) -> int:
        """Drain dt seconds of audio from the input buffer; encode each
        block; inject vibrations at frequency-mapped positions inside
        the input port."""
        n_samples_to_drain = int(dt * self.sample_rate)
        audio = self._read_input_buffer(n_samples_to_drain)
        if len(audio) == 0:
            return 0
        n_blocks = len(audio) // self.block_size
        n_injected = 0
        for b in range(n_blocks):
            block = audio[b * self.block_size : (b + 1) * self.block_size]
            # Pad to fft_size if needed
            if len(block) < self.fft_size:
                block = np.pad(block, (0, self.fft_size - len(block)))
            emissions = encode_block(
                block,
                sample_rate=self.sample_rate,
                fft_size=self.fft_size,
                amplitude_threshold=self.amplitude_threshold,
                freq_min=self.freq_min,
                freq_max=self.freq_max,
            )
            for f, a, polarity in emissions:
                pos = freq_to_port_position(
                    f, freq_min=self.freq_min, freq_max=self.freq_max,
                    port_origin=self.input_port_origin,
                    port_size=self.input_port_size,
                    rng=self.rng,
                )
                # Inject one vibration per emission
                free_idx = np.where(~world.s_alive)[0]
                if len(free_idx) == 0:
                    break
                i = int(free_idx[0])
                world.s_pos[i] = pos
                world.s_vel[i] = 0.0
                world.s_freq[i] = float(f)
                world.s_pol[i] = polarity
                world.s_alive[i] = True
                world.n_alive = max(world.n_alive, i + 1)
                n_injected += 1
        return n_injected

    def read_from_substrate(self, world, dt: float) -> int:
        """Sample firing activity inside the output port; map firings back
        to frequency bins; decode to audio; write to output buffer.

        Returns count of audio samples written.
        """
        # Find firings inside the output port within (t-dt, t]
        ox, oy, oz = self.output_port_origin
        sx, sy, sz = self.output_port_size
        n_blocks = int(dt * self.sample_rate / self.block_size)
        if n_blocks == 0:
            return 0
        block_duration = self.block_size / self.sample_rate

        # Group firings by block
        per_block_emissions: list[list[tuple[float, float, bool]]] = [[] for _ in range(n_blocks)]
        K = world.k_count
        t_window_start = world.t - dt
        for t_fire, atom_idx in world.firing_events:
            if t_fire <= t_window_start or t_fire > world.t:
                continue
            if atom_idx >= K:
                continue
            pos = world.k_pos[atom_idx]
            # Inside output port?
            if not (ox <= pos[0] <= ox + sx and oy <= pos[1] <= oy + sy and oz <= pos[2] <= oz + sz):
                continue
            # Inverse log-mapping: x → freq
            log_norm = (pos[0] - ox) / sx
            log_freq = log_norm * (np.log(self.freq_max) - np.log(self.freq_min)) + np.log(self.freq_min)
            f = float(np.exp(log_freq))
            block_idx = int((t_fire - t_window_start) / block_duration)
            if 0 <= block_idx < n_blocks:
                per_block_emissions[block_idx].append((f, 0.5, True))

        n_written = 0
        for block_idx in range(n_blocks):
            block_audio = decode_to_audio(
                per_block_emissions[block_idx],
                block_size=self.block_size,
                sample_rate=self.sample_rate,
                fft_size=self.fft_size,
                freq_min=self.freq_min,
                freq_max=self.freq_max,
            )
            self._write_output_buffer(block_audio)
            n_written += len(block_audio)
        return n_written

    def start(self) -> None:
        """Open mic and speaker streams; start capture and playback threads.

        sounddevice is imported lazily so substrate-only users don't pay
        for the portaudio system dep.
        """
        if self._running:
            return
        import sounddevice as sd

        def _capture_callback(indata, frames, time_info, status):
            self._write_input_buffer(indata[:, 0].astype(np.float32))

        def _playback_callback(outdata, frames, time_info, status):
            block = self._read_output_buffer(frames)
            if len(block) < frames:
                # Underrun: pad with silence
                outdata[:] = 0.0
                outdata[:len(block), 0] = block
            else:
                outdata[:, 0] = block

        self._capture_stream = sd.InputStream(
            samplerate=self.sample_rate, blocksize=self.block_size,
            channels=1, dtype="float32", device=self.mic_device,
            callback=_capture_callback,
        )
        self._playback_stream = sd.OutputStream(
            samplerate=self.sample_rate, blocksize=self.block_size,
            channels=1, dtype="float32", device=self.speaker_device,
            callback=_playback_callback,
        )
        self._capture_stream.start()
        self._playback_stream.start()
        self._running = True

    def stop(self) -> None:
        if not self._running:
            return
        if self._capture_stream is not None:
            self._capture_stream.stop()
            self._capture_stream.close()
            self._capture_stream = None
        if self._playback_stream is not None:
            self._playback_stream.stop()
            self._playback_stream.close()
            self._playback_stream = None
        self._running = False
