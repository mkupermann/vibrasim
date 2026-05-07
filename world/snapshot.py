from __future__ import annotations
import dataclasses
import numpy as np
from pathlib import Path
from world.config import WorldConfig
from world.state import World


def snapshot_filename(t: float) -> str:
    return f"snapshot_t{t:09.2f}.npz"


def save_snapshot(world: World, path: Path | str) -> None:
    cfg_dict = dataclasses.asdict(world.config)
    np.savez(
        path,
        s_pos=world.s_pos, s_vel=world.s_vel, s_freq=world.s_freq,
        s_pol=world.s_pol, s_alive=world.s_alive,
        k_pos=world.k_pos, k_vel=world.k_vel, k_freq=world.k_freq,
        k_pol=world.k_pol, k_level=world.k_level, k_birth=world.k_birth,
        k_alive=world.k_alive,
        k_comp_offset=world.k_comp_offset, k_comp_end=world.k_comp_end,
        k_comp_indices=world.k_comp_indices,
        k_comp_kind=world.k_comp_kind,
        k_charge=world.k_charge,
        k_refractory_until=world.k_refractory_until,
        k_strength=world.k_strength,
        k_orientation=world.k_orientation,
        k_ref_count=world.k_ref_count,
        t=np.array([world.t]),
        n_alive=np.array([world.n_alive]),
        k_count=np.array([world.k_count]),
        k_comp_used=np.array([world.k_comp_used]),
        firing_events=np.array(world.firing_events, dtype=object) if world.firing_events
                      else np.array([], dtype=object),
        config_json=np.array([str(cfg_dict)], dtype=object),
    )


def load_snapshot(path: Path | str) -> World:
    data = np.load(path, allow_pickle=True)
    cfg_dict = eval(str(data["config_json"][0]))
    if "box_size" in cfg_dict and isinstance(cfg_dict["box_size"], list):
        cfg_dict["box_size"] = tuple(cfg_dict["box_size"])
    # Drop fields the current WorldConfig doesn't know about (forward-compat
    # for snapshots saved before new config fields were added).
    valid_fields = {f.name for f in dataclasses.fields(WorldConfig)}
    cfg_dict = {k: v for k, v in cfg_dict.items() if k in valid_fields}
    cfg = WorldConfig(**cfg_dict)
    w = World(cfg)
    w.s_pos[:] = data["s_pos"]
    w.s_vel[:] = data["s_vel"]
    w.s_freq[:] = data["s_freq"]
    w.s_pol[:] = data["s_pol"]
    w.s_alive[:] = data["s_alive"]
    w.k_pos[:] = data["k_pos"]
    w.k_vel[:] = data["k_vel"]
    w.k_freq[:] = data["k_freq"]
    w.k_pol[:] = data["k_pol"]
    w.k_level[:] = data["k_level"]
    w.k_birth[:] = data["k_birth"]
    w.k_alive[:] = data["k_alive"]
    w.k_comp_offset[:] = data["k_comp_offset"]
    if "k_comp_end" in data.files:
        w.k_comp_end[:] = data["k_comp_end"]
    else:
        # Backward compat: pre-Plan-A.5 snapshots stored end-pointers in
        # k_comp_offset[i+1] (the bug we just fixed). Reconstruct k_comp_end
        # from the loaded k_comp_offset so old snapshots load with intact
        # composition spans.
        w.k_comp_end[:] = data["k_comp_offset"][1:len(w.k_comp_end) + 1]
    w.k_comp_indices[:] = data["k_comp_indices"]
    w.k_comp_kind[:] = data["k_comp_kind"]
    if "k_charge" in data.files:
        w.k_charge[:] = data["k_charge"]
    if "k_refractory_until" in data.files:
        w.k_refractory_until[:] = data["k_refractory_until"]
    if "k_strength" in data.files:
        w.k_strength[:] = data["k_strength"]
    if "k_orientation" in data.files:
        w.k_orientation[:] = data["k_orientation"]
    if "k_ref_count" in data.files:
        w.k_ref_count[:] = data["k_ref_count"]
    if "firing_events" in data.files and len(data["firing_events"]):
        w.firing_events = [(float(t), int(i)) for t, i in data["firing_events"]]
    w.t = float(data["t"][0])
    w.n_alive = int(data["n_alive"][0])
    w.k_count = int(data["k_count"][0])
    w.k_comp_used = int(data["k_comp_used"][0])
    return w
