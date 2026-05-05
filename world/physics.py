from __future__ import annotations
import numpy as np
from numba import njit


@njit(cache=True)
def move_vibrations(
    s_pos: np.ndarray,
    s_vel: np.ndarray,
    s_alive: np.ndarray,
    box: np.ndarray,
    dt: float,
) -> None:
    """In-place: advance alive vibrations by dt with periodic-wrap into the box."""
    n = s_pos.shape[0]
    for i in range(n):
        if not s_alive[i]:
            continue
        s_pos[i, 0] = (s_pos[i, 0] + s_vel[i, 0] * dt) % box[0]
        s_pos[i, 1] = (s_pos[i, 1] + s_vel[i, 1] * dt) % box[1]
