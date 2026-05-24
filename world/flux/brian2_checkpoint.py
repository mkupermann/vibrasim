"""Brian2 substrate checkpoint/resume — Phase B long-training infrastructure.

Enables multi-day continuous training by periodically pickling substrate
state to disk and rebuilding network from saved state on resume.

State captured:
  - Per-neuron: v (membrane potential), v_thresh (if homeostatic),
                ge, gi (synaptic conductances)
  - Per-synapse plastic group: w (weight), Apre, Apost (eligibility traces)
  - Connection indices (i, j) — needed to recreate sparse synapses exactly
  - Spike monitor counts

Limitation: between-chunk Python-side state (e.g., homeostasis counters)
must be saved separately by caller.
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict


def collect_neuron_state(ng) -> Dict[str, Any]:
    """Extract neuron state from a Brian2 NeuronGroup."""
    state = {
        "N": int(len(ng)),
        "v": _arr(ng.v),
        "ge": _arr(ng.ge),
        "gi": _arr(ng.gi),
    }
    # v_thresh may not exist for non-homeostatic models
    try:
        state["v_thresh"] = _arr(ng.v_thresh)
    except (AttributeError, KeyError):
        pass
    return state


def collect_synapse_state(syn, plastic: bool) -> Dict[str, Any]:
    """Extract synapse state from a Brian2 Synapses object."""
    state = {
        "i": _arr(syn.i),
        "j": _arr(syn.j),
        "w": _arr(syn.w),
        "N": int(len(syn)),
        "plastic": plastic,
    }
    if plastic:
        try:
            state["Apre"] = _arr(syn.Apre)
            state["Apost"] = _arr(syn.Apost)
        except (AttributeError, KeyError):
            pass
    return state


def _arr(brian_var):
    """Convert Brian2 quantity/VariableView to plain numpy array of SI values."""
    import numpy as np
    raw = brian_var[:]
    # np.asarray on a Brian2 Quantity returns base-SI float values.
    return np.asarray(raw).astype(float)


def restore_neuron_state(ng, state: Dict[str, Any]):
    """Restore neuron state into a Brian2 NeuronGroup."""
    from brian2 import volt
    ng.v = state["v"] * volt
    ng.ge = state["ge"]
    ng.gi = state["gi"]
    if "v_thresh" in state:
        ng.v_thresh = state["v_thresh"] * volt


def restore_synapse_state(syn, state: Dict[str, Any]):
    """Restore synapse state into a Brian2 Synapses object.

    NOTE: caller must have created the Synapses object with .connect(i=..., j=...)
    using the SAME indices as in state, BEFORE calling this function.
    Otherwise the weight arrays won't match.
    """
    syn.w = state["w"]
    if state.get("plastic"):
        if "Apre" in state:
            syn.Apre = state["Apre"]
        if "Apost" in state:
            syn.Apost = state["Apost"]


def save_checkpoint(state: Dict[str, Any], path: Path):
    """Pickle the full state to path. Atomic via temp-file + rename."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as f:
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
    tmp.replace(path)


def load_checkpoint(path: Path) -> Dict[str, Any]:
    """Load pickled state from path."""
    with open(Path(path), "rb") as f:
        return pickle.load(f)
