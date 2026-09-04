import json

import numpy as np
import pytest

from vibrasim2.p0.artifacts import (
    ADDENDUM_GIT_BLOB,
    ADDENDUM_SHA256,
    PREREGISTRATION_GIT_BLOB,
    PREREGISTRATION_SHA256,
    ArtifactError,
    CellJournal,
    atomic_write_json,
    iter_energy_records,
    iter_snapshots,
    read_json,
    scientific_digest,
    write_run_manifest,
)
from vibrasim2.p0.energy import EnergyRecord, Trajectory
from vibrasim2.p0.types import (
    ChannelMode,
    P0Config,
    P0State,
    P0StateSnapshot,
    RunCell,
    RunPurpose,
    Topology,
)


def tiny_config() -> P0Config:
    return P0Config((2, 2), 1.0, 0.5, 1.0, 0.05, 2.0, 20, 10, ((0, 0),))


def make_cell() -> RunCell:
    return RunCell(
        Topology.CYCLE,
        ChannelMode.FULL,
        RunPurpose.PRIMARY,
        (0, 0),
        0.05,
        20,
    )


def make_snapshot(tick: int) -> P0StateSnapshot:
    state = P0State(
        np.arange(4, dtype=np.float64).reshape(2, 2),
        np.zeros((2, 2), dtype=np.float64),
        np.array((0.25,), dtype=np.float64),
        np.zeros(1, dtype=np.float64),
    )
    return P0StateSnapshot(tick=tick, simulation_time=tick * 0.05, state=state)


def make_record(tick: int, *, finite: bool = True) -> EnergyRecord:
    value = float(tick + 1) if finite else None
    return EnergyRecord(
        tick,
        tick * 0.05,
        value,
        0.0 if finite else None,
        0.0 if finite else None,
        value,
        0.0 if finite else None,
        0.0 if finite else None,
        0.0 if finite else None,
        0.0 if finite else None,
        finite,
    )


def make_journal(path) -> CellJournal:
    return CellJournal(
        path,
        stage="A",
        cell=make_cell(),
        config=tiny_config(),
        coupling_sites=np.array(((0, 0),), dtype=np.int64),
        supplied_edges=np.empty((0, 2), dtype=np.int64),
    )


def build_minimal_scientific_tree(root, *, core_digest: str = "1" * 64) -> None:
    cell = make_cell()
    write_run_manifest(
        root,
        run_id="digest-fixture",
        config=tiny_config(),
        cells=(cell,),
        scientific_core_sha256=core_digest,
    )
    journal = make_journal(root / cell.slug)
    journal.append_energy(make_record(0))
    journal.append_snapshot(make_snapshot(tick=0))


def test_run_manifest_records_frozen_identity_and_leased_core(tmp_path):
    cell = make_cell()
    write_run_manifest(
        tmp_path,
        run_id="run-001",
        config=tiny_config(),
        cells=(cell,),
        scientific_core_sha256="a" * 64,
    )
    manifest = read_json(tmp_path / "run.json")
    assert manifest == {
        "addendum_git_blob": ADDENDUM_GIT_BLOB,
        "addendum_sha256": ADDENDUM_SHA256,
        "cell_order": [cell.slug],
        "config": {
            "c": 1.0,
            "dt": 0.05,
            "frame_stride": 10,
            "g": 1.0,
            "grid_shape": [2, 2],
            "k_b": 0.5,
            "sigma": 2.0,
            "source_centres": [[0, 0]],
            "steps": 20,
        },
        "display_scale": 4.0,
        "observation_schema_version": 1,
        "preregistration_git_blob": PREREGISTRATION_GIT_BLOB,
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "run_id": "run-001",
        "schema_version": 1,
        "scientific_core_sha256": "a" * 64,
    }


def test_energy_and_snapshot_round_trip(tmp_path):
    journal = make_journal(tmp_path / "cell")
    journal.append_energy(make_record(0))
    journal.append_energy(make_record(1, finite=False))
    snapshot = make_snapshot(tick=10)
    journal.append_snapshot(snapshot)

    assert tuple(iter_energy_records(tmp_path / "cell")) == (
        make_record(0),
        make_record(1, finite=False),
    )
    loaded = tuple(iter_snapshots(tmp_path / "cell"))
    assert len(loaded) == 1
    assert loaded[0].tick == 10
    np.testing.assert_array_equal(loaded[0].state.u, snapshot.state.u)


def test_trajectory_helper_requires_matching_cell(tmp_path):
    journal = make_journal(tmp_path / "cell")
    trajectory = Trajectory(make_cell(), (make_record(0),), (make_snapshot(0),))
    journal.append_trajectory(trajectory)
    assert len(tuple(iter_energy_records(tmp_path / "cell"))) == 1
    assert len(tuple(iter_snapshots(tmp_path / "cell"))) == 1

    other = RunCell(
        Topology.BRANCH,
        ChannelMode.FULL,
        RunPurpose.PRIMARY,
        (0, 0),
        0.05,
        20,
    )
    with pytest.raises(ArtifactError, match="cell"):
        journal.append_trajectory(Trajectory(other, (), ()))


def test_snapshot_file_precedes_manifest_entry(tmp_path):
    journal = make_journal(tmp_path / "cell")
    snapshot = make_snapshot(tick=10)
    journal.append_snapshot(snapshot)
    entry = json.loads(
        (tmp_path / "cell/snapshots/manifest.jsonl").read_text().splitlines()[0]
    )
    assert set(entry) == {"schema_version", "tick", "simulation_time", "file"}
    assert (tmp_path / "cell/snapshots" / entry["file"]).is_file()


def test_journals_are_append_only_and_ticks_are_ordered(tmp_path):
    cell_dir = tmp_path / "cell"
    journal = make_journal(cell_dir)
    with pytest.raises(ArtifactError, match="already exists"):
        make_journal(cell_dir)

    with pytest.raises(ArtifactError, match="contiguous"):
        journal.append_energy(make_record(1))
    journal.append_energy(make_record(0))
    with pytest.raises(ArtifactError, match="contiguous"):
        journal.append_energy(make_record(0))

    journal.append_snapshot(make_snapshot(tick=10))
    with pytest.raises(ArtifactError, match="strictly increasing"):
        journal.append_snapshot(make_snapshot(tick=10))


def test_snapshot_reader_rejects_manifest_file_mismatch(tmp_path):
    journal = make_journal(tmp_path / "cell")
    journal.append_snapshot(make_snapshot(0))
    np.savez(
        tmp_path / "cell/snapshots/snapshot-0000000001.npz",
        u=np.zeros((2, 2), dtype=np.float64),
        p=np.zeros((2, 2), dtype=np.float64),
        q=np.zeros(1, dtype=np.float64),
        r=np.zeros(1, dtype=np.float64),
    )
    with pytest.raises(ArtifactError, match="manifest/file mismatch"):
        tuple(iter_snapshots(tmp_path / "cell"))


def test_snapshot_reader_rejects_wrong_dtype_shape_or_keys(tmp_path):
    for defect in ("dtype", "shape", "keys"):
        cell_dir = tmp_path / defect
        journal = make_journal(cell_dir)
        journal.append_snapshot(make_snapshot(0))
        target = cell_dir / "snapshots/snapshot-0000000000.npz"
        arrays = {
            "u": np.zeros((2, 2), dtype=np.float64),
            "p": np.zeros((2, 2), dtype=np.float64),
            "q": np.zeros(1, dtype=np.float64),
            "r": np.zeros(1, dtype=np.float64),
        }
        if defect == "dtype":
            arrays["u"] = arrays["u"].astype(np.float32)
        elif defect == "shape":
            arrays["q"] = np.zeros(2, dtype=np.float64)
        else:
            del arrays["r"]
        with target.open("wb") as stream:
            np.savez(stream, **arrays)
        with pytest.raises(ArtifactError, match=defect):
            tuple(iter_snapshots(cell_dir))


def test_nonfinite_snapshot_arrays_are_preserved(tmp_path):
    journal = make_journal(tmp_path / "cell")
    state = make_snapshot(0).state
    u = np.array(state.u, copy=True)
    u[0, 0] = np.nan
    journal.append_snapshot(
        P0StateSnapshot(0, 0.0, P0State(u, state.p, state.q, state.r))
    )
    loaded = next(iter_snapshots(tmp_path / "cell"))
    assert np.isnan(loaded.state.u[0, 0])


def test_atomic_result_must_survive_readback(tmp_path, monkeypatch):
    target = tmp_path / "result.json"
    atomic_write_json(target, {"verdict": "NULL"})
    assert read_json(target) == {"verdict": "NULL"}
    monkeypatch.setattr("vibrasim2.p0.artifacts.os.replace", lambda left, right: None)
    with pytest.raises(ArtifactError, match="readback"):
        atomic_write_json(target, {"verdict": "PASS"})


def test_failed_first_atomic_write_leaves_no_target(tmp_path, monkeypatch):
    target = tmp_path / "result.json"
    monkeypatch.setattr("vibrasim2.p0.artifacts.os.replace", lambda left, right: None)
    with pytest.raises(ArtifactError, match="readback"):
        atomic_write_json(target, {"verdict": "PASS"})
    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


def test_digest_ignores_view_events_result_run_id_and_observation_metadata(tmp_path):
    build_minimal_scientific_tree(tmp_path)
    first = scientific_digest(tmp_path)
    manifest = read_json(tmp_path / "run.json")
    manifest.update(
        run_id="another-run",
        observation_schema_version=99,
        display_scale=999.0,
        wallclock=22,
        process_id=42,
    )
    atomic_write_json(tmp_path / "run.json", manifest)
    atomic_write_json(tmp_path / "result.json", {"scientific_digest": "ignored"})
    (tmp_path / "view-events.jsonl").write_text(
        '{"dropped":9,"wallclock":22}\n', encoding="utf-8"
    )
    assert scientific_digest(tmp_path) == first


def test_digest_includes_leased_core_digest(tmp_path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    build_minimal_scientific_tree(left, core_digest="1" * 64)
    build_minimal_scientific_tree(right, core_digest="2" * 64)
    assert scientific_digest(left) != scientific_digest(right)


def test_digest_uses_decoded_json_not_serialization_whitespace(tmp_path):
    build_minimal_scientific_tree(tmp_path)
    first = scientific_digest(tmp_path)
    manifest_path = tmp_path / "run.json"
    manifest_path.write_text(
        json.dumps(read_json(manifest_path), indent=4, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    energy_path = tmp_path / make_cell().slug / "energy.jsonl"
    energy_path.write_text(
        json.dumps(json.loads(energy_path.read_text()), indent=None) + "\n",
        encoding="utf-8",
    )
    assert scientific_digest(tmp_path) == first
