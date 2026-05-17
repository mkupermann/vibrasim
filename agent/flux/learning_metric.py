"""F3 frequency-localisation metric — pure function over substrate state.

Reads only `bridges.alive`, `bridges.src`, `bridges.dst`, and
`nodes.freq` (log-Hz). No audio, no injection history, no flux counts.

A bridge counts as "in band" iff BOTH endpoint nodes have log-frequency
within `band_log_hz` of `log(f_train_hz)`. The metric is the in-band
fraction of all alive bridges; returns 0.0 if there are no alive bridges.

See `docs/superpowers/plans/2026-05-16-flux-substrate-F3.md` §"File
structure" for the locked definition.
"""
from __future__ import annotations

import numpy as np

from world.flux.bridges import Bridges
from world.flux.structures import Nodes


def frequency_localisation_index(
    bridges: Bridges,
    nodes: Nodes,
    f_train_hz: float,
    band_log_hz: float,
) -> float:
    """Fraction of alive bridges whose BOTH endpoints lie within
    ±`band_log_hz` of `log(f_train_hz)` in `nodes.freq`.

    Args:
        bridges: live Bridges container (SoA).
        nodes: live Nodes container (SoA); `nodes.freq` is in log-Hz.
        f_train_hz: training centre frequency in Hz.
        band_log_hz: half-window in log-Hz around `log(f_train_hz)`.

    Returns:
        f_loc ∈ [0, 1]. 0.0 if no alive bridges.
    """
    alive_mask = bridges.alive
    n_alive = int(alive_mask.sum())
    if n_alive == 0:
        return 0.0
    band_centre = float(np.log(f_train_hz))
    alive_idx = np.where(alive_mask)[0]
    src = bridges.src[alive_idx]
    dst = bridges.dst[alive_idx]
    freq_src = nodes.freq[src]
    freq_dst = nodes.freq[dst]
    in_band = (
        (np.abs(freq_src - band_centre) <= band_log_hz)
        & (np.abs(freq_dst - band_centre) <= band_log_hz)
    )
    return float(in_band.sum()) / float(n_alive)
