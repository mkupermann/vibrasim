"""Import observations + species into the DB from on-disk snapshot files."""
from __future__ import annotations
from pathlib import Path
import numpy as np

from app.db import (
    insert_observation, insert_species_observations, delete_observations,
)
from app.viewer import list_snapshots, load_snapshot


def import_run_from_snapshots(run_id: str, snapshot_dir: str | Path,
                               replace: bool = True) -> dict:
    """Walk every snapshot in `snapshot_dir`, derive counts, write to DB.

    Returns a dict with counts of what was imported.
    """
    snaps = list_snapshots(snapshot_dir)
    if not snaps:
        return {"snapshots": 0, "species_first_seen": 0,
                "error": f"no snapshot_t*.npz files in {snapshot_dir}"}

    if replace:
        delete_observations(run_id)

    species_seen: set[str] = set()
    n_species_first = 0

    for path in snaps:
        snap = load_snapshot(path)
        # Aggregate counts per level
        n_atoms = 0
        n_l5 = n_l6 = n_l7 = n_l8 = n_higher = 0
        n_pairs = n_triads = 0
        for lvl in snap.k_level.tolist():
            if lvl == 2:
                n_pairs += 1
            elif lvl == 3:
                n_triads += 1
            elif lvl == 4:
                n_atoms += 1
            elif lvl == 5:
                n_l5 += 1
            elif lvl == 6:
                n_l6 += 1
            elif lvl == 7:
                n_l7 += 1
            elif lvl == 8:
                n_l8 += 1
            elif lvl > 8:
                n_higher += 1

        # Electron count is the count of level-1 nodes
        n_electrons = int((snap.k_level == 1).sum())

        insert_observation(
            run_id, snap.t,
            n_vibrations_alive=len(snap.v_pos),
            n_electrons=n_electrons,
            n_pairs=n_pairs,
            n_triads=n_triads,
            n_atoms=n_atoms,
            n_molecule_l5=n_l5,
            n_molecule_l6=n_l6,
            n_molecule_l7=n_l7,
            n_molecule_l8=n_l8,
            n_molecule_higher=n_higher,
            total_vibrations=len(snap.v_pos),
        )

        # Species fingerprints
        species_counts: dict[str, int] = {}
        for fp in snap.species_fp:
            if not fp:
                continue
            species_counts[fp] = species_counts.get(fp, 0) + 1
        first_seen = {fp for fp in species_counts if fp not in species_seen}
        species_seen.update(first_seen)
        n_species_first += len(first_seen)
        if species_counts:
            insert_species_observations(run_id, snap.t, species_counts, first_seen=first_seen)

    return {
        "snapshots": len(snaps),
        "species_first_seen": n_species_first,
        "species_total": len(species_seen),
    }
