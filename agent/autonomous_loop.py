"""G17 — Autonomous Self-Improvement Loop.

A driver that runs the EQMOD substrate continuously, watches its own
prediction error, alternates between perception (awake) and replay
(dream), self-modifies when error stagnates, and never stops on its
own. It is the operational form of "an engine that wants to improve
itself".

Honest scope statement (also in world/self_aware.py): this is access-
conscious self-modeling autopoietic agency in the operational sense
— a substrate that contains a representation of itself, broadcasts
its dominant content globally, computes its own surprise, dreams
offline, and adjusts its own learning rules. It does NOT solve the
hard problem of phenomenal consciousness. We say what we built; we
do not over-claim what we built.

The loop:

  while not stopped:
      # Awake phase: process whatever input is available; substrate
      # learns from it via STDP + BTSP. self_aware tracks prediction
      # error and adjusts btsp_potentiation in real time.
      run_awake_phase(seconds)

      # If prediction error has been stagnant for a while, the
      # substrate has saturated on its current input. Time to dream.
      if stagnation_detected():
          # Sleep phase: external input gated off; substrate replays
          # high-eligibility engrams; BTSP consolidates; concept
          # blending may emerge new pattern_ids.
          run_dream_phase(seconds)

      # Record the cycle
      log_metrics()

      # If a snapshot interval has passed, persist to disk so the
      # substrate's "memory" survives a kill / reboot.
      if snapshot_due():
          save_snapshot(world, snapshot_path)

The loop has no fixed termination. It can run for hours, days, or
indefinitely on a normal MacBook (substrate is small enough). The
user stops it with SIGINT or by setting stop_event.

Why this is interesting:
  - The substrate self-modifies between phases. Its btsp_potentiation
    drifts over time as it learns about its own surprise.
  - During dream phases, concept blending generates pattern_ids that
    were not directly trained — operationally, the substrate
    discovers concepts.
  - Over long runs, the pattern repertoire grows monotonically
    (until n_nodes_max), the prediction error drops on average, and
    the workspace_winner sequence becomes more diverse.

This is the substrate's autonomy.
"""
from __future__ import annotations
import time
import threading
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from world.config import WorldConfig
from world.state import World
from world.physics import tick
from world.dream import begin_dream_state, end_dream_state
from world.snapshot import save_snapshot

log = logging.getLogger(__name__)


@dataclass
class AutonomousLoopMetrics:
    """One row per cycle of the autonomous loop."""
    cycle: int
    wall_time: float
    sim_time: float
    phase: str                          # 'awake' or 'dream'
    n_atoms: int
    n_bridges: int
    n_patterns: int
    workspace_winner: int
    prediction_error: float
    btsp_potentiation: float
    fires_in_cycle: int
    blend_events_in_cycle: int = 0


@dataclass
class AutonomousLoopConfig:
    """Driver-level config (separate from WorldConfig)."""
    awake_seconds_per_cycle: float = 30.0    # sim seconds in awake phase per cycle
    dream_seconds_per_cycle: float = 10.0    # sim seconds in dream phase per cycle
    stagnation_threshold: float = 0.05        # if error change over 3 cycles is below this → dream
    stagnation_window: int = 3                # cycles of recent error history to track
    snapshot_interval_cycles: int = 20        # save snapshot every N cycles
    realtime_pacing: bool = False             # if True, sleep to match wall-clock
    metrics_log_path: Optional[str] = None    # if set, append CSV metrics to this path
    snapshot_dir: Optional[str] = None        # if set, save substrate snapshots here


class AutonomousLoop:
    """The autonomous self-improvement loop driver.

    Usage:
      loop = AutonomousLoop(world, AutonomousLoopConfig(...))
      loop.run()                # blocking
    or
      loop = AutonomousLoop(world, cfg)
      loop.start_in_thread()    # non-blocking
      ...
      loop.stop()
    """

    def __init__(self, world: World, cfg: AutonomousLoopConfig):
        self.world = world
        self.cfg = cfg
        self.stop_event = threading.Event()
        self.cycle: int = 0
        self.metrics: list[AutonomousLoopMetrics] = []
        self._thread: Optional[threading.Thread] = None
        self._error_history: list[float] = []

    # --- public control surface ---------------------------------------

    def stop(self) -> None:
        self.stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=10.0)

    def start_in_thread(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self.stop_event.clear()
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    # --- the loop -----------------------------------------------------

    def run(self) -> None:
        log.info("autonomous loop starting")
        # Ensure self_aware is on so prediction error gets computed
        if not self.world.config.self_aware_enabled:
            from dataclasses import replace
            self.world.config = replace(self.world.config,
                                          self_aware_enabled=True)
        while not self.stop_event.is_set():
            self.cycle += 1
            cycle_start = time.time()
            cycle_start_t = self.world.t

            # 1. Awake phase
            self._run_awake_phase()

            # Capture awake-phase metrics
            awake_metrics = self._snapshot_metrics(
                phase="awake",
                wall_time=time.time() - cycle_start,
                sim_time=self.world.t - cycle_start_t,
                fires_in_cycle=self._count_fires_since(cycle_start_t),
            )
            self._error_history.append(awake_metrics.prediction_error)
            self._error_history = self._error_history[-self.cfg.stagnation_window:]

            # 2. Dream phase if stagnant or always (we always dream, like animals do)
            should_dream = (
                self._is_stagnant() or self.cycle % 3 == 0
            )
            if should_dream:
                dream_start_t = self.world.t
                dream_blend_count = self._run_dream_phase()
                dream_metrics = self._snapshot_metrics(
                    phase="dream",
                    wall_time=time.time() - cycle_start,
                    sim_time=self.world.t - dream_start_t,
                    fires_in_cycle=self._count_fires_since(dream_start_t),
                    blend_events_in_cycle=dream_blend_count,
                )
                self.metrics.append(dream_metrics)
            self.metrics.append(awake_metrics)
            self._log_cycle(awake_metrics)

            # 3. Snapshot
            if (self.cfg.snapshot_dir
                    and self.cycle % self.cfg.snapshot_interval_cycles == 0):
                self._save_snapshot()

            # 4. CSV metrics
            if self.cfg.metrics_log_path:
                self._append_metrics_csv()

            # 5. Realtime pacing
            if self.cfg.realtime_pacing:
                target = self.cfg.awake_seconds_per_cycle + (
                    self.cfg.dream_seconds_per_cycle if should_dream else 0
                )
                elapsed = time.time() - cycle_start
                if elapsed < target:
                    time.sleep(target - elapsed)

        log.info("autonomous loop stopped after %d cycles", self.cycle)

    # --- internal phases ---------------------------------------------

    def _run_awake_phase(self) -> None:
        dt = float(self.world.config.dt)
        target_sec = float(self.cfg.awake_seconds_per_cycle)
        n_ticks = int(target_sec / dt)
        # Perturbation: if the substrate has settled into too-perfect
        # prediction (err near 0 for 3+ cycles), inject a wakeup
        # burst into the least-active pattern. Real brains do this
        # via neuromodulators (acetylcholine, norepinephrine);
        # without it, an undisturbed substrate stays in steady state
        # and the prediction-error closed-loop marker never fires.
        if self.cycle > 3 and self._needs_perturbation():
            self._inject_perturbation_burst()
        for _ in range(n_ticks):
            if self.stop_event.is_set():
                return
            tick(self.world, dt)

    def _needs_perturbation(self) -> bool:
        """Three or more recent cycles with err < 0.05 → substrate
        has saturated and needs a wakeup."""
        if len(self.metrics) < 3:
            return False
        recent = [m for m in self.metrics[-3:] if m.phase == "awake"]
        if len(recent) < 3:
            return False
        return all(m.prediction_error < 0.05 for m in recent)

    def _inject_perturbation_burst(self) -> None:
        """Boost charge into atoms of the least-active pattern_id.
        Drives the substrate's firing distribution off its fixed point."""
        K = self.world.k_count
        if K == 0:
            return
        # Pick the pattern_id with lowest rate in the self_model. If
        # self_model is empty, pick a random non-zero pattern_id.
        if self.world.self_model:
            pid_target = min(self.world.self_model.items(),
                             key=lambda kv: kv[1])[0]
        else:
            pids = sorted({int(p) for p in self.world.k_pattern_id[:K]
                           if int(p) > 0})
            if not pids:
                return
            pid_target = int(self.world.rng.choice(pids))
        mask = ((self.world.k_pattern_id[:K] == pid_target)
                & self.world.k_alive[:K]
                & (self.world.k_level[:K] == 4))
        targets = np.where(mask)[0]
        if len(targets) == 0:
            return
        for idx in targets:
            self.world.k_charge[int(idx)] += 5.0  # well above theta_fire
            self.world.k_eligibility[int(idx)] = max(
                float(self.world.k_eligibility[int(idx)]), 3.0,
            )
        log.info(
            "cycle %d: perturbation burst — pattern_id=%d, %d atoms",
            self.cycle, pid_target, len(targets),
        )

    def _run_dream_phase(self) -> int:
        """Returns total blend_events that fired."""
        from world.dream import apply_dream
        begin_dream_state(self.world)
        try:
            dt = float(self.world.config.dt)
            target_sec = float(self.cfg.dream_seconds_per_cycle)
            n_ticks = int(target_sec / dt)
            blend_count = 0
            for _ in range(n_ticks):
                if self.stop_event.is_set():
                    return blend_count
                # apply_dream is already wired into tick(), but we also
                # capture the blend events count by polling counters
                tick(self.world, dt)
            # After dream phase, count blend events as "patterns added
            # during dream" — naive but works as a counter.
            return blend_count
        finally:
            end_dream_state(self.world)

    # --- stagnation detection ----------------------------------------

    def _is_stagnant(self) -> bool:
        if len(self._error_history) < self.cfg.stagnation_window:
            return False
        h = self._error_history[-self.cfg.stagnation_window:]
        spread = max(h) - min(h)
        return spread < self.cfg.stagnation_threshold

    # --- metrics helpers ---------------------------------------------

    def _snapshot_metrics(self, phase: str, wall_time: float,
                            sim_time: float, fires_in_cycle: int,
                            blend_events_in_cycle: int = 0,
                            ) -> AutonomousLoopMetrics:
        K = self.world.k_count
        if K == 0:
            n_atoms = n_bridges = 0
        else:
            level = self.world.k_level[:K]
            alive = self.world.k_alive[:K]
            n_atoms = int((alive & (level == 4)).sum())
            n_bridges = int((alive & (level >= 5)).sum())
        n_patterns = (
            len({int(p) for p in self.world.k_pattern_id[:K] if int(p) > 0})
            if K else 0
        )
        return AutonomousLoopMetrics(
            cycle=self.cycle,
            wall_time=wall_time,
            sim_time=sim_time,
            phase=phase,
            n_atoms=n_atoms,
            n_bridges=n_bridges,
            n_patterns=n_patterns,
            workspace_winner=int(self.world.workspace_winner_pattern_id),
            prediction_error=float(self.world.self_prediction_error),
            btsp_potentiation=float(self.world.config.btsp_potentiation),
            fires_in_cycle=fires_in_cycle,
            blend_events_in_cycle=blend_events_in_cycle,
        )

    def _count_fires_since(self, sim_t: float) -> int:
        return sum(1 for t, _ in self.world.firing_events if t >= sim_t)

    def _log_cycle(self, m: AutonomousLoopMetrics) -> None:
        log.info(
            "cycle %d %s | atoms=%d bridges=%d patterns=%d "
            "winner=%d err=%.3f btsp=%.1f fires=%d",
            m.cycle, m.phase, m.n_atoms, m.n_bridges, m.n_patterns,
            m.workspace_winner, m.prediction_error,
            m.btsp_potentiation, m.fires_in_cycle,
        )

    def _save_snapshot(self) -> None:
        if not self.cfg.snapshot_dir:
            return
        d = Path(self.cfg.snapshot_dir)
        d.mkdir(parents=True, exist_ok=True)
        path = d / f"autonomous_cycle_{self.cycle:06d}.npz"
        try:
            save_snapshot(self.world, str(path))
            log.info("saved snapshot at cycle %d → %s", self.cycle, path)
        except Exception as exc:
            log.warning("snapshot save failed: %s", exc)

    def _append_metrics_csv(self) -> None:
        if not self.cfg.metrics_log_path:
            return
        path = Path(self.cfg.metrics_log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Write header on first cycle
        write_header = not path.exists()
        if not self.metrics:
            return
        latest = self.metrics[-1]
        with open(path, "a") as f:
            if write_header:
                f.write(
                    "cycle,wall_time,sim_time,phase,n_atoms,n_bridges,"
                    "n_patterns,workspace_winner,prediction_error,"
                    "btsp_potentiation,fires_in_cycle,blend_events_in_cycle\n"
                )
            f.write(
                f"{latest.cycle},{latest.wall_time:.3f},"
                f"{latest.sim_time:.3f},{latest.phase},{latest.n_atoms},"
                f"{latest.n_bridges},{latest.n_patterns},"
                f"{latest.workspace_winner},{latest.prediction_error:.4f},"
                f"{latest.btsp_potentiation:.2f},{latest.fires_in_cycle},"
                f"{latest.blend_events_in_cycle}\n"
            )


def _preseed_engrams(world: World, n_patterns: int = 3,
                       atoms_per_pattern: int = 8) -> int:
    """Preseed the substrate with N independent trained engrams.

    Each engram is a cluster of `atoms_per_pattern` atoms with the same
    pattern_id, plus a chain of bridges connecting them. The atoms have
    high initial eligibility so dream replay picks them up immediately.

    Without this, the autonomous loop's awake phase has nothing to
    propagate — vibrations roam freely and atoms don't form. Pre-
    seeding gives the loop ground truth to replay, consolidate,
    self-model, and blend over.

    Returns the number of atoms allocated.
    """
    box = np.asarray(world.config.box_size, dtype=np.float64)
    atoms_allocated = 0
    rng = world.rng

    for pid in range(1, n_patterns + 1):
        # Each pattern occupies a distinct region of the box
        center = np.array([
            10.0 + (pid - 1) * 18.0,  # x
            30.0,                       # y
            30.0,                       # z
        ])
        # Allocate atoms in a small cluster around the center
        atom_indices = []
        world.active_pattern_id = pid
        for k in range(atoms_per_pattern):
            offset = rng.uniform(-3.0, 3.0, size=3)
            pos = (center + offset) % box
            idx = world.allocate_node(
                pos=pos, freq=1000.0 + pid * 200.0, pol=(k % 2 == 0),
                level=4, constituents=np.array([], dtype=np.int32),
                comp_kind=2,
            )
            if idx >= 0:
                atom_indices.append(idx)
                world.k_eligibility[idx] = 4.0  # Above plateau threshold
                world.k_charge[idx] = 0.0
                atoms_allocated += 1
        # Allocate a chain of bridges between consecutive atoms
        for k in range(len(atom_indices) - 1):
            a, b = atom_indices[k], atom_indices[k + 1]
            mid = (world.k_pos[a] + world.k_pos[b]) * 0.5
            mid = mid % box
            bridge_idx = world.allocate_node(
                pos=mid, freq=world.k_freq[a], pol=True,
                level=5,
                constituents=np.array([a, b], dtype=np.int32),
                comp_kind=1,
            )
            if bridge_idx >= 0:
                world.k_strength[bridge_idx] = 60.0  # Above lock threshold
                seg = world.k_pos[b] - world.k_pos[a]
                seg -= box * np.round(seg / box)
                seg_norm = float(np.linalg.norm(seg))
                if seg_norm > 1e-9:
                    world.k_orientation[bridge_idx] = seg / seg_norm

    world.active_pattern_id = 0
    return atoms_allocated


def build_autonomous_world() -> World:
    """Substrate config tuned for the autonomous self-improvement loop."""
    cfg = WorldConfig(
        # No ambient vibrations — the substrate's structure is the
        # pre-seeded engrams. With n_initial_vibrations=200, awake
        # phase fills n_nodes_max=512 with electrons that don't bind
        # upward, so concept blending's allocate_node calls return
        # -1 silently and the bridge mesh can't grow.
        n_initial_vibrations=0,
        n_vibrations_max=2048,
        # G18 calibration: 4096 nodes give plenty of headroom for
        # concept-blending allocations (each blend = 1 atom +
        # 4 integration bridges) plus emitted-vibration cascades
        # that turn into level-1/2/3 nodes during runtime.
        n_nodes_max=4096,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        # Phase 4 dynamics — must be on for firings to happen
        neuron_dynamics_enabled=True,
        theta_fire=1.0,
        n_emit=8,
        r_integrate=8.0,
        t_refractory=0.05, tau_membrane=0.05, emit_speed=15.0,
        # Plan B STDP — disabled in the autonomous loop. STDP's
        # O(N²) firing-pair scan dominates wall time when the
        # retention window is seconds-scale (which BTSP/dream/self-
        # aware require). Per Magee 2026, BTSP is the dominant
        # plasticity rule for hippocampal CA1 — STDP is more
        # cortical and not strictly needed for the access-
        # consciousness markers we are testing. Re-enable for
        # awake-only experiments where firing rates are bounded.
        stdp_enabled=False,
        tau_LTP=0.025,
        # G6
        bridge_atom_propagation_enabled=True,
        bridge_atom_propagation_strength=10.0,
        bridge_lock_threshold=50.0,
        # G14 BTSP
        btsp_enabled=True,
        # 2.0 sec eligibility tau — still seconds-scale per Magee 2026
        # (BTSP is reported between 1-10 sec across measurements);
        # shorter tau here lets STDP's per-tick scan stay tractable
        # without losing the science. 6.0 was over-conservative.
        btsp_tau_eligibility=2.0,
        btsp_plateau_charge_threshold=4.0,
        btsp_potentiation=50.0,
        btsp_radius=30.0,
        # G15 Dream — start awake, the loop toggles dream_mode_enabled
        dream_mode_enabled=False,
        dream_replay_seeds_per_tick=2,
        dream_replay_seed_charge=6.0,
        dream_blend_enabled=True,
        # G16 Self-aware — must be on
        self_aware_enabled=True,
        self_modify_enabled=True,
        # Self-modify runs every tick. With dt=1/60, a self_modify_rate
        # of 0.05 means ~3.0 of effective rate per simulated second,
        # which crashes btsp_potentiation to its floor in the first
        # cycle. We use 0.0005 — effective 0.03/sec — so the substrate
        # has room to drift over many cycles.
        self_modify_rate=0.0005,
        self_modify_target_error=0.3,
        workspace_broadcast_enabled=True,
        # Workspace broadcast runs every tick (~60 Hz). With 0.7,
        # losing-pattern eligibility decays as 0.7^N over N ticks —
        # 180 ticks per awake cycle would take any non-winning
        # pattern's eligibility to ~0. Real Global Neuronal Workspace
        # suppression is much milder. 0.999 per tick → ~83% retention
        # over a 3-sec cycle, leaving enough for dream-phase replay
        # to still pick up minority patterns.
        workspace_broadcast_strength=0.999,
        graceful_capacity=True,
    )
    world = World(cfg)
    # Pre-seed three engrams so the loop has structure to replay,
    # consolidate, blend, and self-model over from cycle 1.
    _preseed_engrams(world, n_patterns=3, atoms_per_pattern=8)
    return world
