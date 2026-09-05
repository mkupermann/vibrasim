from dataclasses import replace

import numpy as np
import pytest

from vibrasim2.p2.artifacts import (
    P2ArtifactError,
    P2CellJournal,
    iter_energy_records,
    iter_events,
    iter_snapshots,
    scientific_digest,
    write_run_manifest,
)
from vibrasim2.p2.dynamics import initial_state
from vibrasim2.p2.trajectory import P2EnergyRecord, P2Snapshot, TimedBondEvent
from vibrasim2.p2.types import Bond, P2Arm, P2Cell, P2Config, P2Purpose


def cell():
    return P2Cell(P2Arm.FULL, P2Purpose.PRIMARY, (4, 16), 0.025, 4)


def test_manifest_is_create_only_and_contains_frozen_identity(tmp_path):
    config = P2Config.registered()

    manifest = write_run_manifest(tmp_path, "v2-p2-test", config, (cell(),))

    assert manifest["run_id"] == "v2-p2-test"
    assert manifest["experiment"] == "P2"
    assert manifest["registration_sha256"]
    assert manifest["cell_order"] == [cell().slug]
    with pytest.raises(P2ArtifactError, match="already exists"):
        write_run_manifest(tmp_path, "v2-p2-other", config, (cell(),))


def test_cell_journal_round_trips_records_events_and_snapshots(tmp_path):
    config = P2Config.registered()
    journal = P2CellJournal(tmp_path / cell().slug, cell(), config)
    record = P2EnergyRecord(0, 0.0, 1.0, 0.0, 0.0, 0.0, 0, 0.0, True)
    event = TimedBondEvent(1, 0.025, "formed", 0, 1)
    state = replace(
        initial_state(config, (4, 16)),
        reservoirs=np.arange(6, dtype=float) / 100,
        bonds=(Bond(0, 1, 0.25, 0.1, -0.2),),
        formation_sink=0.02,
        bond_time=0.5,
    )
    snapshot = P2Snapshot(1, 0.025, state)

    journal.append_energy(record)
    journal.append_event(event)
    journal.append_snapshot(snapshot)

    assert tuple(iter_energy_records(journal.path)) == (record,)
    assert tuple(iter_events(journal.path)) == (event,)
    restored = tuple(iter_snapshots(journal.path))
    assert len(restored) == 1
    assert restored[0].tick == 1
    np.testing.assert_array_equal(restored[0].state.reservoirs, state.reservoirs)
    assert restored[0].state.bonds == state.bonds


def test_journal_rejects_nonmonotonic_append(tmp_path):
    config = P2Config.registered()
    journal = P2CellJournal(tmp_path / cell().slug, cell(), config)
    record = P2EnergyRecord(1, 0.025, 1.0, 0.0, 0.0, 0.0, 0, 0.0, True)
    journal.append_energy(record)

    with pytest.raises(P2ArtifactError, match="strictly increasing"):
        journal.append_energy(record)


def test_digest_changes_with_scientific_payload_but_ignores_view_events(tmp_path):
    config = P2Config.registered()
    write_run_manifest(tmp_path, "v2-p2-test", config, (cell(),))
    journal = P2CellJournal(tmp_path / cell().slug, cell(), config)
    before = scientific_digest(tmp_path)
    (tmp_path / "view-events.jsonl").write_text("observer-only\n", encoding="utf-8")
    assert scientific_digest(tmp_path) == before
    journal.append_energy(P2EnergyRecord(0, 0.0, 1.0, 0.0, 0.0, 0.0, 0, 0.0, True))
    assert scientific_digest(tmp_path) != before

