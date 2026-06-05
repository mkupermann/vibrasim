"""audio_features — turn a real SOUND into a feature vector the engine can 'hear' (per Michael: hear 'A').

Reads a WAV file (the stdlib `wave` module -- no extra install) and extracts a fixed-length log-FFT feature, the same
representation the cross-modal grounding (JEP-288) uses. So Michael can RECORD himself saying 'A' (Windows Voice
Recorder -> .wav), and the teaching tool grounds that sound to the written 'A' via the (modality='sound', symbol) store.

Live microphone streaming needs `sounddevice` (pip install sounddevice); this file works from WAV files with only the
stdlib, so the hear-path runs everywhere. No transformer, no pretrained audio model -- just FFT.
"""
import wave
import numpy as np

N_BINS = 32


def wav_to_samples(path):
    """Load a WAV -> mono float samples in [-1,1] + sample rate."""
    with wave.open(str(path), "rb") as w:
        n, sw, ch, sr = w.getnframes(), w.getsampwidth(), w.getnchannels(), w.getframerate()
        raw = w.readframes(n)
    dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw, np.int16)
    a = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    peak = float(2 ** (8 * sw - 1))
    return a / (peak + 1e-9), sr


def samples_to_feature(samples, sr=None):
    """Fixed-length log-FFT feature (N_BINS contiguous frequency bands), normalized -- the 'heard' vector."""
    a = np.asarray(samples, dtype=np.float64)
    if len(a) < 8:
        return np.zeros(N_BINS)
    a = a / (np.max(np.abs(a)) + 1e-9)
    mag = np.abs(np.fft.rfft(a * np.hanning(len(a))))
    B = max(1, len(mag) // N_BINS)
    binned = np.array([mag[i * B:(i + 1) * B].mean() for i in range(N_BINS)])
    feat = np.log1p(binned)
    return feat / (np.linalg.norm(feat) + 1e-9)


def wav_to_feature(path):
    s, sr = wav_to_samples(path)
    return samples_to_feature(s, sr)


def synth_tone(freqs, dur=0.4, sr=16000, noise=0.0, rng=None):
    """Synthesize a tone (sum of sines) -- a stand-in for a spoken sound, for testing the pipeline without a mic."""
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    wave_ = sum(np.sin(2 * np.pi * f * t) for f in freqs)
    if noise and rng is not None:
        wave_ = wave_ + rng.normal(0, noise, wave_.shape)
    return wave_, sr


def write_wav(path, samples, sr=16000):
    """Write float samples [-1,1] to a 16-bit mono WAV."""
    a = np.clip(np.asarray(samples, dtype=np.float64), -1, 1)
    pcm = (a * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(pcm.tobytes())
