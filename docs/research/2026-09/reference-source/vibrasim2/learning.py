"""MM1: explicitly engineered local spring association, not V2-P0 physics.

Input ports are externally clamped during exposure. Local co-exposure changes
spring conductance. During retrieval only audio is clamped; all other ports
relax to the minimum of sum(b_ij*(q_i-q_j)^2)/2 + leak*sum(q_j^2)/2.
No labels or candidate images enter this system.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np


@dataclass(frozen=True)
class LearningConfig:
    audio_ports: int = 8
    visual_side: int = 8
    text_ports: int = 16
    learning_rate: float = 0.8
    decay: float = 0.002
    max_strength: float = 1.0
    leak: float = 0.2
    fps: int = 10
    sample_rate: int = 16000

    def as_dict(self) -> dict:
        return asdict(self)


class SensoryPorts:
    def __init__(self, config: LearningConfig = LearningConfig()):
        self.config = config

    def encode(self, image: np.ndarray, audio: np.ndarray, text: str = "") -> tuple[np.ndarray, np.ndarray]:
        c = self.config
        image = np.asarray(image, dtype=float)
        if image.ndim == 3:
            image = image[..., :3].mean(axis=2)
        if image.shape != (32, 32):
            raise ValueError("sensory images must be 32×32")
        if not np.isfinite(image).all():
            raise ValueError("nonfinite image")
        visual = np.clip(image, 0, 1).reshape(c.visual_side, 4, c.visual_side, 4).mean(axis=(1, 3)).ravel()
        audio = np.asarray(audio, dtype=float)
        if audio.ndim != 1 or not np.isfinite(audio).all():
            raise ValueError("audio must be finite mono samples")
        spectrum = np.abs(np.fft.rfft(audio * np.hanning(len(audio)))) ** 2 if len(audio) else np.zeros(1)
        freq = np.fft.rfftfreq(max(1, len(audio)), 1 / c.sample_rate)
        edges = np.geomspace(80, 7800, c.audio_ports + 1)
        bands = np.array([spectrum[(freq >= lo) & (freq < hi)].sum() for lo, hi in zip(edges[:-1], edges[1:])])
        if bands.max() > 1e-12:
            bands = np.sqrt(bands / bands.max())
        # Fixed byte-bit occupancy. This deliberately makes no language claim.
        bits = np.zeros(c.text_ports)
        for i, byte in enumerate(text.encode("utf-8")):
            for bit in range(8):
                bits[(i % 2) * 8 + bit] = max(bits[(i % 2) * 8 + bit], (byte >> bit) & 1)
        return bands, np.concatenate((visual, bits))


class SpringMemory:
    def __init__(self, config: LearningConfig = LearningConfig()):
        self.config = config
        self.strength = np.zeros((config.audio_ports, config.visual_side ** 2 + config.text_ports))
        self.response = np.zeros(self.strength.shape[1])
        self.audio = np.zeros(config.audio_ports)
        self.adaptation_work = 0.0
        self.elapsed = 0.0

    def expose(self, audio: np.ndarray, other: np.ndarray, dt: float, plastic: bool = True) -> None:
        audio, other = self._inputs(audio, other)
        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be positive and finite")
        old = self.strength.copy()
        self.strength *= np.exp(-self.config.decay * dt)
        if plastic:
            local = np.outer(audio, other)
            self.strength += (self.config.max_strength - self.strength) * (1 - np.exp(-self.config.learning_rate * dt * local))
        # Work to change spring stiffness at externally clamped displacements.
        self.adaptation_work += float(0.5 * np.sum((self.strength - old) * (audio[:, None] - other[None, :]) ** 2))
        self.audio = audio.copy()
        self.response = other.copy()
        self.elapsed += dt

    def cue(self, audio: np.ndarray) -> np.ndarray:
        audio, _ = self._inputs(audio, np.zeros(self.strength.shape[1]))
        self.audio = audio.copy()
        # Exact overdamped equilibrium, not a learned output mapping.
        self.response = (audio @ self.strength) / (self.config.leak + self.strength.sum(axis=0))
        return self.response.copy()

    def idle(self, seconds: float) -> None:
        if not np.isfinite(seconds) or seconds < 0:
            raise ValueError("idle duration must be nonnegative")
        self.strength *= np.exp(-self.config.decay * seconds)
        self.elapsed += seconds
        self.reset_activity()

    def reset_activity(self) -> None:
        self.audio.fill(0)
        self.response.fill(0)

    def _inputs(self, audio, other):
        a, b = np.asarray(audio, float), np.asarray(other, float)
        if a.shape != (self.strength.shape[0],) or b.shape != (self.strength.shape[1],):
            raise ValueError("port dimensions do not match")
        if not np.isfinite(a).all() or not np.isfinite(b).all() or np.any(a < 0) or np.any(a > 1) or np.any(b < 0) or np.any(b > 1):
            raise ValueError("port values must be finite and in [0,1]")
        return a, b

    def snapshot(self) -> dict:
        energy = 0.5 * np.sum(self.strength * (self.audio[:, None] - self.response[None, :]) ** 2)
        energy += 0.5 * self.config.leak * np.sum(self.response ** 2)
        return {"strength": self.strength.tolist(), "audio": self.audio.tolist(),
                "response": self.response.tolist(), "elapsed": self.elapsed,
                "elastic_energy": float(energy), "adaptation_work": self.adaptation_work}

    def restore(self, state: dict) -> None:
        strength = np.asarray(state["strength"], float)
        audio, response = self._inputs(state["audio"], state["response"])
        if strength.shape != self.strength.shape or not np.isfinite(strength).all() or np.any(strength < 0) or np.any(strength > self.config.max_strength):
            raise ValueError("invalid spring snapshot")
        self.strength = strength.copy()
        self.audio, self.response = audio.copy(), response.copy()
        self.elapsed = float(state["elapsed"])
        self.adaptation_work = float(state["adaptation_work"])


def retrieval_score(response: np.ndarray, candidates: list[np.ndarray], expected: int) -> tuple[float, list[float]]:
    """External fixed forced-choice measurement. Ties receive fractional credit."""
    response = np.asarray(response, float)
    scores = [float(np.dot(response, x) / max(1e-12, np.linalg.norm(response) * np.linalg.norm(x))) for x in candidates]
    winners = np.flatnonzero(np.isclose(scores, max(scores), atol=1e-9, rtol=0))
    return (1 / len(winners) if expected in winners else 0.0), scores


def verdict(accuracies: dict[str, float], valid: bool) -> str:
    names = {"trained", "retained", "frozen", "shuffled", "erased"}
    if not valid or set(accuracies) != names or not all(np.isfinite(v) and 0 <= v <= 1 for v in accuracies.values()):
        return "INCONCLUSIVE"
    control = max(accuracies[k] for k in ("frozen", "shuffled", "erased"))
    return "PASS" if min(accuracies['trained'], accuracies['retained']) >= .75 and control <= .50 and accuracies['trained'] - control >= .25 else "NULL"
