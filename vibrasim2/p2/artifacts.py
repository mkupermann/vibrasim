"""Durable, validated scientific artifacts for V2-P2."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Iterator

import numpy as np

from .registration import P2_REGISTRATION_SHA256
from .trajectory import P2EnergyRecord, P2Snapshot, TimedBondEvent
from .types import Bond, P2Arm, P2Cell, P2Config, P2Purpose, P2State


class P2ArtifactError(RuntimeError):
    pass


def _json_bytes(value: object) -> bytes:
    try:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    except (TypeError, ValueError) as exc:
        raise P2ArtifactError(f"invalid finite JSON payload: {exc}") from exc


def _atomic_create_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(_json_bytes(value))
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            raise P2ArtifactError(f"artifact already exists: {path}")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _cell_json(cell: P2Cell) -> dict[str, object]:
    return {
        "arm": cell.arm.value,
        "purpose": cell.purpose.value,
        "source_centre": list(cell.source_centre),
        "dt": cell.dt,
        "steps": cell.steps,
        "slug": cell.slug,
    }


def _config_json(config: P2Config) -> dict[str, object]:
    value = asdict(config)
    value["grid_shape"] = list(config.grid_shape)
    value["source_centres"] = [list(source) for source in config.source_centres]
    return value


def write_run_manifest(
    output_dir: Path,
    run_id: str,
    config: P2Config,
    cells: tuple[P2Cell, ...],
) -> dict[str, object]:
    if not run_id.startswith("v2-p2-"):
        raise P2ArtifactError("P2 run_id must start with v2-p2-")
    if not cells or len({cell.slug for cell in cells}) != len(cells):
        raise P2ArtifactError("run cells must be non-empty and unique")
    manifest: dict[str, object] = {
        "schema_version": 1,
        "observation_schema_version": 1,
        "display_scale": 4.0,
        "experiment": "P2",
        "run_id": run_id,
        "registration_sha256": P2_REGISTRATION_SHA256,
        "config": _config_json(config),
        "cell_order": [cell.slug for cell in cells],
    }
    _atomic_create_json(Path(output_dir) / "run.json", manifest)
    return manifest


class P2CellJournal:
    def __init__(self, path: Path, cell: P2Cell, config: P2Config) -> None:
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        cell_path = self.path / "cell.json"
        if not cell_path.exists():
            _atomic_create_json(
                cell_path,
                {**_cell_json(cell), "config": _config_json(config)},
            )
        self._last_energy_tick = _last_jsonl_tick(self.path / "energy.jsonl")
        self._last_event_tick = _last_jsonl_tick(self.path / "events.jsonl")
        existing = sorted((self.path / "snapshots").glob("*.npz")) if (self.path / "snapshots").exists() else []
        self._last_snapshot_tick = int(existing[-1].stem) if existing else -1

    @staticmethod
    def _append(path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("ab") as stream:
            stream.write(_json_bytes(value))
            stream.flush()
            os.fsync(stream.fileno())

    def append_energy(self, record: P2EnergyRecord) -> None:
        if record.tick <= self._last_energy_tick:
            raise P2ArtifactError("energy ticks must be strictly increasing")
        self._append(self.path / "energy.jsonl", asdict(record))
        self._last_energy_tick = record.tick

    def append_event(self, event: TimedBondEvent) -> None:
        if event.tick < self._last_event_tick:
            raise P2ArtifactError("event ticks must be non-decreasing")
        self._append(self.path / "events.jsonl", asdict(event))
        self._last_event_tick = event.tick

    def append_snapshot(self, snapshot: P2Snapshot) -> None:
        if snapshot.tick <= self._last_snapshot_tick:
            raise P2ArtifactError("snapshot ticks must be strictly increasing")
        directory = self.path / "snapshots"
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / f"{snapshot.tick:08d}.npz"
        temporary = directory / f".{target.name}.{uuid.uuid4().hex}.tmp"
        bonds = np.asarray(
            [
                (bond.left, bond.right, bond.age, bond.matter_rest, bond.field_rest)
                for bond in snapshot.state.bonds
            ],
            dtype=np.float64,
        ).reshape((-1, 5))
        try:
            with temporary.open("xb") as stream:
                np.savez_compressed(
                    stream,
                    tick=np.int64(snapshot.tick),
                    simulation_time=np.float64(snapshot.simulation_time),
                    u=snapshot.state.u,
                    p=snapshot.state.p,
                    q=snapshot.state.q,
                    r=snapshot.state.r,
                    reservoirs=snapshot.state.reservoirs,
                    bonds=bonds,
                    formation_sink=np.float64(snapshot.state.formation_sink),
                    bond_time=np.float64(snapshot.state.bond_time),
                )
                stream.flush()
                os.fsync(stream.fileno())
            if target.exists():
                raise P2ArtifactError(f"snapshot already exists: {target}")
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        self._last_snapshot_tick = snapshot.tick


def _last_jsonl_tick(path: Path) -> int:
    if not path.exists():
        return -1
    values = list(_iter_jsonl(path))
    return int(values[-1]["tick"]) if values else -1


def _iter_jsonl(path: Path) -> Iterator[dict[str, object]]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                value = json.loads(line, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
            except (json.JSONDecodeError, ValueError) as exc:
                raise P2ArtifactError(f"invalid JSON at {path}:{line_number}") from exc
            if not isinstance(value, dict):
                raise P2ArtifactError(f"record must be an object at {path}:{line_number}")
            yield value


def iter_energy_records(cell_dir: Path) -> Iterator[P2EnergyRecord]:
    previous = -1
    for value in _iter_jsonl(Path(cell_dir) / "energy.jsonl"):
        record = P2EnergyRecord(**value)
        if record.tick <= previous:
            raise P2ArtifactError("persisted energy ticks are not strictly increasing")
        previous = record.tick
        yield record


def iter_events(cell_dir: Path) -> Iterator[TimedBondEvent]:
    previous = -1
    for value in _iter_jsonl(Path(cell_dir) / "events.jsonl"):
        event = TimedBondEvent(**value)
        if event.tick < previous:
            raise P2ArtifactError("persisted event ticks are decreasing")
        previous = event.tick
        yield event


def iter_snapshots(cell_dir: Path) -> Iterator[P2Snapshot]:
    previous = -1
    for path in sorted((Path(cell_dir) / "snapshots").glob("*.npz")):
        try:
            with np.load(path, allow_pickle=False) as data:
                tick = int(data["tick"])
                simulation_time = float(data["simulation_time"])
                raw_bonds = np.asarray(data["bonds"], dtype=np.float64)
                bonds = tuple(
                    Bond(int(row[0]), int(row[1]), float(row[2]), float(row[3]), float(row[4]))
                    for row in raw_bonds
                )
                state = P2State(
                    data["u"], data["p"], data["q"], data["r"], data["reservoirs"],
                    bonds, float(data["formation_sink"]), float(data["bond_time"]),
                )
        except (OSError, KeyError, ValueError) as exc:
            raise P2ArtifactError(f"invalid snapshot: {path}") from exc
        if tick <= previous or path.stem != f"{tick:08d}":
            raise P2ArtifactError("persisted snapshot ticks are not strictly increasing")
        previous = tick
        yield P2Snapshot(tick, simulation_time, state)


def scientific_digest(output_dir: Path) -> str:
    """Hash only scientific inputs and cell evidence, excluding UI diagnostics."""
    root = Path(output_dir)
    selected: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.name in {"view-events.jsonl", "result.json"}:
            continue
        if relative.name in {"run.json", "cell.json", "energy.jsonl", "events.jsonl"} or "snapshots" in relative.parts:
            selected.append(path)
    hasher = hashlib.sha256()
    for path in sorted(selected, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode()
        payload = path.read_bytes()
        hasher.update(len(relative).to_bytes(8, "big"))
        hasher.update(relative)
        hasher.update(len(payload).to_bytes(8, "big"))
        hasher.update(payload)
    return hasher.hexdigest()

