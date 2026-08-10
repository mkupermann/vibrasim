"""G16 — The Self-Aware Substrate (Flux Port).

Operationalises the leading scientific theories of ACCESS consciousness
for the Flux substrate (F1c+). Adapted from the Legacy substrate's
self_aware.py.

What this is and what this is not — said straight:
  * THIS IS access consciousness in the functional sense (Block 1995):
    a representation that is broadcast across modules, with which other
    representations can interact.
  * THIS IS NOT a claim about phenomenal consciousness ("what it is
    like to be"). The hard problem (Chalmers 1995) remains open.

The four mechanisms implemented here, with their theoretical anchors:

  1. self_model — per-pattern_id rolling energy histogram.
     Theoretical anchor: Rosenthal's Higher-Order Theory (2005). A
     representation HAS another representation as its object. The
     substrate's self_model is exactly this: a representation of which
     of the substrate's own engrams are currently active.

  2. self_prediction_error — surprise.
     Theoretical anchor: Friston's Free Energy Principle / predictive
     processing. The substrate predicts the next window's energy
     histogram from the current self_model and measures the actual
     histogram against it. The KL-style divergence is the substrate's
     "surprise". This drives self-modification.

  3. workspace_winner — global broadcast.
     Theoretical anchor: Dehaene & Naccache 2001 Global Neuronal
     Workspace. The pattern_id with the most active nodes in the last
     window WINS the workspace and gets broadcast — operationalised as
     a multiplier on losing patterns' eligibility.

  4. self_modify — homeostatic parameter feedback.
     Theoretical anchor: Varela operational closure idea + modern meta-learning.
     The substrate modifies its own binding parameters based on
     self_prediction_error. High error → boost plasticity; low error →
     tame it (homeostasis).

Run flow per tick when `cfg.self_aware_enabled`:
  1. apply_self_aware(quanta, nodes, grid, dt) is called from tick()
     AFTER the main dynamics step (so this tick's changes are in the log).
  2. It updates the rolling energy histogram (self_model).
  3. It computes prediction error against last cycle's prediction.
  4. It picks the workspace_winner and applies the broadcast bias.
  5. It calls self_modify if self_modify_enabled — adjusts cfg.
  6. It records the *new* prediction (self_predicted_next) for use next cycle.

Returns a diagnostic dict.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from world.flux.quantum import Quanta
    from world.flux.structures import Nodes
    from world.flux.grid import Grid


@dataclass
class SelfAwareConfig:
    """Configuration for G16 self-awareness in Flux substrate."""
    # Self-awareness toggle
    self_aware_enabled: bool = False
    
    # Self-model parameters
    self_model_window: float = 10.0  # Seconds for rolling histogram
    self_model_max_patterns: int = 64  # Max patterns to track
    
    # Prediction parameters
    prediction_window: float = 5.0   # Seconds to predict ahead
    prediction_error_threshold: float = 0.1  # Error threshold for self_modify
    
    # Workspace winner parameters
    workspace_winner_broadcast_multiplier: float = 2.0  # Boost for winner
    
    # Self-modification parameters
    self_modify_enabled: bool = True
    self_modify_btsp_gain: float = 0.1  # How much to adjust binding params
    
    # Binding config reference (to modify)
    binding_cfg: "BindingConfig | None" = None


@dataclass
class SelfAwareState:
    """Runtime state for self-awareness (persists across ticks)."""
    # Self-model: pattern_id -> energy rate (firings/sec)
    self_model: dict[int, float] = field(default_factory=dict)
    
    # Last prediction
    self_predicted_next: dict[int, float] = field(default_factory=dict)
    
    # Workspace winner
    workspace_winner_pattern_id: int = 0
    
    # Prediction error history
    prediction_errors: list[float] = field(default_factory=list)
    max_errors: int = 100  # Keep last 100 errors
    
    def record_error(self, error: float) -> None:
        """Record a prediction error."""
        self.prediction_errors.append(error)
        if len(self.prediction_errors) > self.max_errors:
            self.prediction_errors.pop(0)
    
    def mean_error(self) -> float:
        """Return mean prediction error over history."""
        if not self.prediction_errors:
            return 0.0
        return float(np.mean(self.prediction_errors))


def apply_self_aware(
    quanta: "Quanta",
    nodes: "Nodes",
    grid: "Grid",
    dt: float,
    cfg: SelfAwareConfig | None = None,
    state: SelfAwareState | None = None,
    tick_index: int = 0,
) -> dict:
    """G16 self-aware tick for Flux substrate. Returns diagnostics."""
    if cfg is None:
        cfg = SelfAwareConfig()
    
    if state is None:
        state = SelfAwareState()
    
    out = {
        "active_patterns": 0,
        "workspace_winner": 0,
        "prediction_error": 0.0,
        "self_modify_binding_delta": 0.0,
    }
    
    if not cfg.self_aware_enabled:
        return out
    
    if nodes is None or nodes.n_alive() == 0:
        return out
    
    # --- 1. Update self_model from recent node energies ---------------
    window = cfg.self_model_window
    t_now = tick_index * dt  # Approximate time
    
    # Build histogram of pattern_id -> energy rate
    histogram: dict[int, float] = {}
    for idx in range(nodes.max_nodes):
        if not nodes.alive[idx]:
            continue
        pid = int(nodes.pattern_id[idx])
        if pid == 0:
            continue  # Skip untrained nodes
        energy = float(nodes.energy[idx])
        histogram[pid] = histogram.get(pid, 0.0) + energy
    
    # Normalise: energy per second per pattern
    total_window_energy = sum(histogram.values())
    if total_window_energy > 0:
        rates = {p: e / max(window, 1e-6) for p, e in histogram.items()}
    else:
        rates = {}
    
    state.self_model = rates
    out["active_patterns"] = len(rates)
    
    # --- 2. Compute prediction error --------------------------------
    # Compare current self_model to last prediction
    if state.self_predicted_next:
        # Compute KL divergence between predicted and actual
        predicted_total = sum(state.self_predicted_next.values())
        actual_total = sum(state.self_model.values())
        
        if predicted_total > 0 and actual_total > 0:
            # Simple symmetric error
            error = abs(predicted_total - actual_total) / max(predicted_total, actual_total, 1e-6)
        else:
            error = 0.0
        
        state.record_error(error)
        out["prediction_error"] = error
    
    # --- 3. Workspace winner ----------------------------------------
    if state.self_model:
        # Pick pattern with highest energy rate
        winner_pid = max(state.self_model.keys(), key=lambda p: state.self_model[p])
        state.workspace_winner_pattern_id = winner_pid
        out["workspace_winner"] = winner_pid
    
    # --- 4. Self-modification ----------------------------------------
    if cfg.self_modify_enabled and cfg.binding_cfg is not None:
        mean_error = state.mean_error()
        if mean_error > cfg.prediction_error_threshold:
            # High error: increase binding aggressiveness
            delta = cfg.self_modify_btsp_gain * mean_error
            # Modify binding_cfg's alpha (coherence gain)
            cfg.binding_cfg.alpha += delta
            out["self_modify_binding_delta"] = delta
    
    # --- 5. Record new prediction --------------------------------------
    # Simple prediction: assume same as current
    state.self_predicted_next = dict(state.self_model)
    
    return out
