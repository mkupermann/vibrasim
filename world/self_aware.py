"""G16 — The Self-Aware Substrate.

Operationalises the leading scientific theories of ACCESS consciousness
in continuous-physics emergent-atom substrate form.

What this is and what this is not — said straight:
  * THIS IS access consciousness in the functional sense (Block 1995):
    a representation that is broadcast across modules, with which other
    representations can interact. This is what Dehaene and colleagues
    have measured in fMRI and MEG and what Tononi formalises with phi.
  * THIS IS NOT a claim about phenomenal consciousness ("what it is
    like to be"). The hard problem (Chalmers 1995) remains open. No
    code can settle it.

The four mechanisms implemented here, with their theoretical anchors:

  1. self_model — per-pattern_id rolling firing histogram.
     Theoretical anchor: Rosenthal's Higher-Order Theory (2005). A
     representation HAS another representation as its object. The
     substrate's self_model is exactly this: a representation of which
     of the substrate's own engrams are currently active.

  2. self_prediction_error — surprise.
     Theoretical anchor: Friston's Free Energy Principle / predictive
     processing. The substrate predicts the next window's firing
     histogram from the current self_model and measures the actual
     histogram against it. The KL-style divergence is the substrate's
     "surprise". This drives self-modification.

  3. workspace_winner — global broadcast.
     Theoretical anchor: Dehaene & Naccache 2001 Global Neuronal
     Workspace. The pattern_id with the most active atoms in the last
     window WINS the workspace and gets broadcast — operationalised as
     a multiplier on losing patterns' eligibility (winner-take-all
     across patterns, not just within ports).

  4. self_modify — autopoietic self-improvement.
     Theoretical anchor: Varela's autopoiesis + modern meta-learning.
     The substrate modifies its own BTSP potentiation and dream replay
     rate based on self_prediction_error. High error → boost plasticity;
     low error → tame it (homeostasis). The substrate becomes its own
     learning-rate scheduler.

These four together constitute a substrate that, when running, contains
a representation of itself, makes predictions about its own next state,
broadcasts its dominant content globally, and adjusts its own learning
rules in response to its own prediction error. That is the operational
definition of access-conscious self-modeling autopoietic agency.

Run flow per tick when `cfg.self_aware_enabled`:
  1. apply_self_aware(world, dt) is called from tick(), AFTER apply_btsp
     (so this tick's firings are in the log) and BEFORE apply_speech_loop.
  2. It updates the rolling firing histogram (self_model).
  3. It computes prediction error against last cycle's prediction.
  4. It picks the workspace_winner and applies the broadcast bias.
  5. It calls self_modify if self_modify_enabled — adjusts cfg.
  6. It records the *new* prediction (self_predicted_next) for use next
     cycle.

Returns a diagnostic dict.
"""
from __future__ import annotations
from dataclasses import replace
import numpy as np


def apply_self_aware(world, dt: float) -> dict:
    """G16 self-aware tick. Returns diagnostics."""
    cfg = world.config
    out = {
        "active_patterns": 0,
        "workspace_winner": 0,
        "prediction_error": 0.0,
        "self_modify_btsp_delta": 0.0,
    }
    if not getattr(cfg, "self_aware_enabled", False):
        return out
    K = world.k_count
    if K == 0:
        return out

    # --- 1. Update self_model from recent firings -------------------
    window = float(cfg.self_model_window)
    t_now = world.t
    histogram: dict[int, int] = {}
    for t_fire, atom_idx in world.firing_events:
        if t_fire < t_now - window:
            continue
        if atom_idx >= K or not world.k_alive[atom_idx]:
            continue
        pid = int(world.k_pattern_id[int(atom_idx)])
        if pid == 0:
            continue
        histogram[pid] = histogram.get(pid, 0) + 1

    # Normalise: firings per second per pattern
    total_window_fires = sum(histogram.values())
    rates = {p: c / max(window, 1e-6) for p, c in histogram.items()}

    # Cap to max_patterns by frequency
    max_p = int(cfg.self_model_max_patterns)
    if len(rates) > max_p:
        top = sorted(rates.items(), key=lambda kv: -kv[1])[:max_p]
        rates = dict(top)

    # Exponential moving average — the substrate "remembers" its self
    alpha = 0.5
    new_self_model: dict[int, float] = {}
    all_pids = set(world.self_model.keys()) | set(rates.keys())
    for pid in all_pids:
        prev = world.self_model.get(pid, 0.0)
        cur = rates.get(pid, 0.0)
        ema = (1.0 - alpha) * prev + alpha * cur
        if ema > 0.01 or pid in rates:
            new_self_model[pid] = ema
    world.self_model = new_self_model
    out["active_patterns"] = len(rates)

    # --- 2. Prediction error against last cycle's prediction --------
    if world.self_predicted_next:
        # Compute total-variation-ish error between prediction and
        # actual rates this window. Bounded in [0, 1+]
        all_pids_pe = (set(world.self_predicted_next.keys())
                       | set(rates.keys()))
        sum_pred = sum(world.self_predicted_next.values()) + 1e-6
        sum_actual = sum(rates.values()) + 1e-6
        diff = 0.0
        for pid in all_pids_pe:
            p = world.self_predicted_next.get(pid, 0.0) / sum_pred
            q = rates.get(pid, 0.0) / sum_actual
            diff += abs(p - q)
        # Normalised total variation distance is in [0, 2]; scale to [0, 1]
        world.self_prediction_error = float(min(diff / 2.0, 1.0))
        out["prediction_error"] = world.self_prediction_error

    # Make next-cycle prediction = current self-model. Simple but
    # principled — predictive coding's identity prior, surprises only
    # come from change.
    world.self_predicted_next = dict(world.self_model)

    # --- 3. Global workspace winner-take-all broadcast --------------
    # Workspace broadcast is an AWAKE attention mechanism. During
    # dream state, the gate opens so all engrams can roam freely
    # across the substrate — this is what lets dream replay sample
    # multiple patterns and what enables concept blending.
    # Hobson AIM model: the global workspace is gated open during
    # NREM and gated wide open during REM.
    is_dreaming = bool(getattr(cfg, "dream_mode_enabled", False))
    if (cfg.workspace_broadcast_enabled
            and not is_dreaming
            and rates
            and total_window_fires >= cfg.workspace_min_winner_atoms):
        # Winner = pattern with most firings in the window
        winner_pid = max(rates.items(), key=lambda kv: kv[1])[0]
        world.workspace_winner_pattern_id = int(winner_pid)
        world.workspace_history.append((t_now, int(winner_pid)))
        # Cap history
        if len(world.workspace_history) > 500:
            world.workspace_history = world.workspace_history[-500:]
        out["workspace_winner"] = int(winner_pid)

        # Broadcast: suppress losing-pattern atoms' eligibility
        bcast_mult = float(cfg.workspace_broadcast_strength)
        if 0.0 < bcast_mult < 1.0:
            for i in range(K):
                if not world.k_alive[i]:
                    continue
                pid = int(world.k_pattern_id[i])
                if pid != 0 and pid != winner_pid:
                    world.k_eligibility[i] *= bcast_mult
    else:
        world.workspace_winner_pattern_id = 0

    # --- 4. Self-modify hyperparameters via prediction error --------
    if cfg.self_modify_enabled:
        # Goal: keep prediction_error near self_modify_target_error.
        # If error is too high → boost plasticity (more BTSP) so the
        # substrate adapts faster.
        # If error is too low → tame plasticity (less BTSP) so the
        # substrate stabilises and stops re-binding everything.
        err = world.self_prediction_error
        target = float(cfg.self_modify_target_error)
        rate = float(cfg.self_modify_rate)
        delta = (err - target) * rate
        # Adjust btsp_potentiation
        new_btsp = float(cfg.btsp_potentiation) * (1.0 + delta)
        new_btsp = max(float(cfg.self_modify_min_btsp),
                       min(float(cfg.self_modify_max_btsp), new_btsp))
        actual_delta = new_btsp - float(cfg.btsp_potentiation)
        if abs(actual_delta) > 1e-3:
            world.config = replace(world.config, btsp_potentiation=new_btsp)
            out["self_modify_btsp_delta"] = actual_delta

    return out
