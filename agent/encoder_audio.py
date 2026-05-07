"""Plan C — pure-functional audio encoding/decoding.

Frequency-to-position mapping, STFT and ISTFT helpers. No threads, no state,
no I/O. Easily testable.
"""
import numpy as np


def freq_to_port_position(
    freq: float,
    freq_min: float = 50.0,
    freq_max: float = 8000.0,
    port_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
    rng: np.random.Generator | None = None,
) -> tuple[float, float, float]:
    """Map an audio frequency (Hz) to a 3D position inside the port volume.

    X is deterministic — log-normalised mapping along the port's X axis.
    Y and Z are random within the port box (so different frequencies don't
    always land on the same y/z and bind into the same electron).
    """
    if rng is None:
        rng = np.random.default_rng()
    f_clamped = max(freq_min, min(freq_max, freq))
    log_norm = (np.log(f_clamped) - np.log(freq_min)) / (np.log(freq_max) - np.log(freq_min))
    x = port_origin[0] + log_norm * port_size[0]
    y = port_origin[1] + float(rng.random()) * port_size[1]
    z = port_origin[2] + float(rng.random()) * port_size[2]
    return (float(x), y, z)
