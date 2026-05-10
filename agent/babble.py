"""Predictive-babble runner.

Iteration 4b of the predictive-babble pipeline (see
``docs/superpowers/specs/2026-05-10-predictive-babble-design.md``, §3 row
``agent/babble.py``).

A ``BabbleRunner`` takes a substrate that has already been trained
through the curriculum and produces a wav of "babble": run the substrate
forward in time with external audio input gated off, observe which atoms
inside the audio_output port fire, and decode those firings into a
waveform via :mod:`agent.decoder_audio`.

Design notes:

* Input gating is enforced by replacing the loop config's ``audio_io``
  with ``None`` *on a copy* of the config — the caller's config object
  is not mutated. This matches the spec's "gated off" requirement and
  keeps multi-substrate runs safe.

* We do **not** call :meth:`AutonomousLoop.run` because that loop is
  daemon-style with no time-bounded mode — it would block until the
  caller flips ``stop_event``. Instead we run a small synchronous
  mini-loop that advances simulated time via :func:`world.physics.tick`
  until ``world.t - start_t >= duration_seconds``. This is also what
  the tests need (deterministic, no threads).

* Firings are filtered to the audio_output port box only. The spec
  defines an atom as "in the output port" iff its position is inside
  ``[port_origin, port_origin + port_size]`` on every axis. Atom
  membership is computed once at run start (the substrate may grow new
  atoms during the babble window, but the spec scopes babble to the
  substrate's settled state, so we lock the membership snapshot).
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from world.state import World


@dataclass
class BabbleRunner:
    """Run a trained substrate with input gated and capture a babble wav.

    Parameters
    ----------
    world
        The (already-trained) substrate. The runner advances ``world.t``
        forward by ``duration_seconds`` of simulated time.
    autonomous_loop_cfg
        The loop config used for training. The runner copies this via
        :func:`dataclasses.replace` and forces ``audio_io=None`` on the
        copy. The caller's config object is left intact.
    duration_seconds
        Simulated seconds of babble. Spec default 30.0; production runs
        use 5 minutes (§6 acceptance criterion).
    output_path
        If set, the wav is written to this path (parent directories are
        created on demand). If ``None``, the wav is returned in memory
        only.
    sample_rate
        Audio sample rate for the decoded waveform. Defaults to 16 kHz
        to match the encoder.
    """

    world: World
    autonomous_loop_cfg: "object"  # AutonomousLoopConfig — typed loosely to avoid import cycles
    duration_seconds: float = 30.0
    output_path: Optional[Path] = None
    sample_rate: int = 16000
    enable_dream_replay: bool = False
    """When True, the babble window runs in dream-replay mode and the
    audio_output port atoms get a temporary high-eligibility + sentinel
    pattern_id so dream's seed selection picks them. After the window
    closes both are restored. Default False preserves existing behaviour
    for tests and the --mini contract; the predictive-babble pipeline
    (run_full) sets this True so the substrate produces output during
    babble from internal state alone."""
    # Internal — captured for diagnostics.
    _gated_cfg: Optional[object] = field(default=None, init=False, repr=False)

    # ------------------------------------------------------------------

    def run(self) -> tuple[np.ndarray, Optional[Path]]:
        """Execute the babble run and return ``(samples, written_path)``.

        ``samples`` is a float32 array of length
        ``int(round(duration_seconds * sample_rate))`` (give or take the
        ISTFT's small padding tolerance, then truncated/padded by
        :func:`agent.decoder_audio.decode_block`).

        ``written_path`` is ``output_path`` if set (and the file was
        written) or ``None``.
        """
        if self.duration_seconds <= 0.0:
            raise ValueError("duration_seconds must be positive")

        # Lazy import: keeps this module importable in CI without
        # numba/JIT eagerness during collection.
        from agent.decoder_audio import (
            decode_block,
            port_position_to_freq,
            write_wav,
        )

        # 1. Copy the loop config and force input gating.
        self._gated_cfg = dataclasses.replace(
            self.autonomous_loop_cfg, audio_io=None,
        )

        cfg = self.world.config
        port_origin = tuple(cfg.audio_output_port_origin)
        port_size = tuple(cfg.audio_output_port_size)

        # 2. Snapshot the audio_output atom membership.
        output_atom_set = self._collect_output_port_atoms(port_origin, port_size)

        # 3. Run the substrate forward by duration_seconds of sim time.
        start_t = float(self.world.t)
        firing_events_baseline_len = len(self.world.firing_events)
        self._run_simulated_seconds(self.duration_seconds)

        # 4. Walk new firings, filter by output-port membership, decode.
        firings: list[tuple[float, float, bool]] = []
        for evt in self.world.firing_events[firing_events_baseline_len:]:
            t, idx = evt
            t = float(t)
            idx = int(idx)
            if idx not in output_atom_set:
                continue
            if t < start_t:
                # Defensive: the loop only appends with current world.t,
                # but if a tick reorders we still want the babble window only.
                continue
            pos = self.world.k_pos[idx]
            freq = port_position_to_freq(
                (float(pos[0]), float(pos[1]), float(pos[2])),
                port_origin=port_origin,
                port_size=port_size,
                freq_min=float(cfg.audio_freq_min),
                freq_max=float(cfg.audio_freq_max),
            )
            polarity = bool(self.world.k_pol[idx])
            firings.append((t - start_t, freq, polarity))

        # 5. Decode and (optionally) persist.
        samples = decode_block(
            firings,
            duration_seconds=self.duration_seconds,
            sample_rate=self.sample_rate,
        )

        written: Optional[Path] = None
        if self.output_path is not None:
            out = Path(self.output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            write_wav(samples, out, sample_rate=self.sample_rate)
            written = out

        return samples, written

    # --- helpers ------------------------------------------------------

    def _collect_output_port_atoms(
        self,
        port_origin: tuple[float, float, float],
        port_size: tuple[float, float, float],
    ) -> set[int]:
        """Indices of alive atoms whose position is inside the output box.

        An atom is "inside" the box iff each coordinate satisfies
        ``origin[a] <= pos[a] <= origin[a] + size[a]``. The check is
        inclusive on both ends to match the encoder's clipping behaviour
        (it places frequencies at the upper edge for ``f >= freq_max``).
        """
        K = int(self.world.k_count)
        if K == 0:
            return set()
        ox, oy, oz = port_origin
        sx, sy, sz = port_size
        pos = self.world.k_pos[:K]
        alive = self.world.k_alive[:K]
        in_x = (pos[:, 0] >= ox) & (pos[:, 0] <= ox + sx)
        in_y = (pos[:, 1] >= oy) & (pos[:, 1] <= oy + sy)
        in_z = (pos[:, 2] >= oz) & (pos[:, 2] <= oz + sz)
        mask = alive & in_x & in_y & in_z
        return {int(i) for i in np.where(mask)[0]}

    def _run_simulated_seconds(self, target_seconds: float) -> None:
        """Advance world.t by ``target_seconds`` of simulated time.

        When ``enable_dream_replay`` is False (default), this is a plain
        tick loop — preserves existing behaviour for tests and --mini.

        When True, the run is wrapped in dream mode and audio_output
        port atoms get a temporary pattern_id=42 + eligibility=4.0 so
        dream replay actually fires them. Without these the audio
        output port has no source of firings during babble (input is
        gated, atoms have eligibility 0). Both are restored after.
        """
        from world.physics import tick

        dt = float(self.world.config.dt)
        if dt <= 0.0:
            raise ValueError("world.config.dt must be positive for babble")
        n_ticks = int(round(target_seconds / dt))
        n_ticks = max(1, n_ticks)

        if not self.enable_dream_replay:
            for _ in range(n_ticks):
                tick(self.world, dt)
            return

        from world.dream import begin_dream_state, end_dream_state
        cfg = self.world.config
        ao_origin = np.asarray(cfg.audio_output_port_origin, dtype=np.float64)
        ao_size = np.asarray(cfg.audio_output_port_size, dtype=np.float64)
        K = int(self.world.k_count)
        output_mask = None
        saved_pid = saved_elig = None
        if K > 0:
            pos = self.world.k_pos[:K]
            in_x = (pos[:, 0] >= ao_origin[0]) & (pos[:, 0] <= ao_origin[0] + ao_size[0])
            in_y = (pos[:, 1] >= ao_origin[1]) & (pos[:, 1] <= ao_origin[1] + ao_size[1])
            in_z = (pos[:, 2] >= ao_origin[2]) & (pos[:, 2] <= ao_origin[2] + ao_size[2])
            output_mask = self.world.k_alive[:K] & in_x & in_y & in_z
            if output_mask.any():
                saved_pid = self.world.k_pattern_id[:K][output_mask].copy()
                saved_elig = self.world.k_eligibility[:K][output_mask].copy()
                BABBLE_PID = 42
                self.world.k_pattern_id[:K][output_mask] = BABBLE_PID
                self.world.k_eligibility[:K][output_mask] = 4.0

        begin_dream_state(self.world)
        try:
            for _ in range(n_ticks):
                tick(self.world, dt)
        finally:
            end_dream_state(self.world)
            if output_mask is not None and output_mask.any():
                self.world.k_pattern_id[:K][output_mask] = saved_pid
                self.world.k_eligibility[:K][output_mask] = saved_elig
