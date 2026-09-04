"""Durable append-only artifacts and canonical scientific identity for P0."""

from __future__ import annotations

import json
import math
import os
import re
import tempfile
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np

from .energy import EnergyRecord, Trajectory
from .types import P0Config, P0State, P0StateSnapshot, RunCell

SCHEMA_VERSION = 1
OBSERVATION_SCHEMA_VERSION = 1
DISPLAY_SCALE = 4.0
PREREGISTRATION_SHA256 = (
    "28992a8b131100ed4eb2cd9147ddea7b3251921777211a63bb4b64e5524ca9e1"
)
PREREGISTRATION_GIT_BLOB = "e5460f0b9ce837ec551bd0c3fb26d269c180f61b"
ADDENDUM_SHA256 = "f0c20858ffaf3750320bd05cc1b120222264e7bd3e84109406f7b4a3cb7d9cb0"
ADDENDUM_GIT_BLOB = "ff77a39fb5f9ac9f895d23a96ea9ff3f3b423b37"

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_SNAPSHOT_KEYS = frozenset(("u", "p", "q", "r"))
_SNAPSHOT_MANIFEST_KEYS = frozenset(
    ("schema_version", "tick", "simulation_time", "file")
)
_ENERGY_KEYS = frozenset(("schema_version", *EnergyRecord.__dataclass_fields__))
_CELL_KEYS = frozenset(
    (
        "schema_version",
        "stage",
        "topology",
        "mode",
        "purpose",
        "source_centre",
        "dt",
        "steps",
        "config",
        "coupling_sites",
        "supplied_edges",
    )
)


class ArtifactError(RuntimeError):
    """Raised when a scientific artifact cannot be written or validated."""


def _reject_json_constant(value: str) -> None:
    raise ArtifactError(f"non-finite JSON constant is forbidden: {value}")


def _decode_json(text: str, *, source: Path) -> Any:
    try:
        return json.loads(text, parse_constant=_reject_json_constant)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        if isinstance(error, ArtifactError):
            raise
        raise ArtifactError(f"invalid JSON in {source}") from error


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ArtifactError("value is not canonical JSON") from error


def read_json(path: str | Path) -> Any:
    """Read UTF-8 JSON while rejecting JavaScript-style NaN and infinities."""

    source = Path(path)
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ArtifactError(f"cannot read JSON artifact: {source}") from error
    return _decode_json(text, source=source)


def atomic_write_json(path: str | Path, value: Any) -> None:
    """Atomically write canonical JSON and verify the decoded value immediately."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded = _canonical_json_bytes(value) + b"\n"
    expected = _decode_json(encoded.decode("utf-8"), source=target)
    existed_before = target.exists()
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=target.parent, prefix=f".{target.name}.", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        if not temporary.exists():
            temporary = None
        try:
            actual = read_json(target)
        except ArtifactError as error:
            raise ArtifactError(f"atomic JSON readback failed: {target}") from error
        if actual != expected:
            raise ArtifactError(f"atomic JSON readback mismatch: {target}")
    except Exception as error:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        if not existed_before:
            target.unlink(missing_ok=True)
        if isinstance(error, ArtifactError):
            raise
        raise ArtifactError(
            f"atomic JSON write or readback failed: {target}"
        ) from error


def _config_json(config: P0Config) -> dict[str, Any]:
    return {
        "grid_shape": list(config.grid_shape),
        "c": config.c,
        "k_b": config.k_b,
        "g": config.g,
        "dt": config.dt,
        "sigma": config.sigma,
        "steps": config.steps,
        "frame_stride": config.frame_stride,
        "source_centres": [list(centre) for centre in config.source_centres],
    }


def _cell_json(cell: RunCell) -> dict[str, Any]:
    return {
        "topology": cell.topology.value,
        "mode": cell.mode.value,
        "purpose": cell.purpose.value,
        "source_centre": list(cell.source_centre),
        "dt": cell.dt,
        "steps": cell.steps,
    }


def write_run_manifest(
    output_dir: str | Path,
    *,
    run_id: str,
    config: P0Config,
    cells: Iterable[RunCell],
    scientific_core_sha256: str,
) -> None:
    """Write the frozen run identity before any per-cell records exist."""

    root = Path(output_dir)
    target = root / "run.json"
    if target.exists():
        raise ArtifactError(f"run manifest already exists: {target}")
    if not run_id:
        raise ArtifactError("run_id must be non-empty")
    if not _SHA256.fullmatch(scientific_core_sha256):
        raise ArtifactError("scientific_core_sha256 must be a lowercase SHA-256")
    ordered_cells = tuple(cells)
    slugs = [cell.slug for cell in ordered_cells]
    if len(slugs) != len(set(slugs)):
        raise ArtifactError("run manifest cell slugs must be unique")
    atomic_write_json(
        target,
        {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "preregistration_sha256": PREREGISTRATION_SHA256,
            "preregistration_git_blob": PREREGISTRATION_GIT_BLOB,
            "addendum_sha256": ADDENDUM_SHA256,
            "addendum_git_blob": ADDENDUM_GIT_BLOB,
            "scientific_core_sha256": scientific_core_sha256,
            "config": _config_json(config),
            "cell_order": slugs,
            "observation_schema_version": OBSERVATION_SCHEMA_VERSION,
            "display_scale": DISPLAY_SCALE,
        },
    )


def _integer(value: Any, *, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ArtifactError(f"{label} must be an integer >= {minimum}")
    return value


def _finite_float(value: Any, *, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ArtifactError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ArtifactError(f"{label} must be finite")
    return result


def _int_matrix(value: Any, *, label: str) -> list[list[int]]:
    array = np.asarray(value)
    if array.ndim != 2 or array.shape[1:] != (2,) or array.dtype.kind not in "iu":
        raise ArtifactError(f"{label} must be an integer (n, 2) array")
    return [[int(item) for item in row] for row in array]


class CellJournal:
    """A newly-created, append-only journal for one P0 execution cell."""

    def __init__(
        self,
        cell_dir: str | Path,
        *,
        stage: str,
        cell: RunCell,
        config: P0Config,
        coupling_sites: np.ndarray,
        supplied_edges: np.ndarray,
    ) -> None:
        if stage not in ("A", "B"):
            raise ArtifactError("stage must be A or B")
        sites = _int_matrix(coupling_sites, label="coupling_sites")
        edges = _int_matrix(supplied_edges, label="supplied_edges")
        if config == P0Config.registered() and len(sites) != 6:
            raise ArtifactError(
                "registered journal requires field (32,32) and matter (6,) shapes"
            )
        matter_size = len(sites)
        if any(index < 0 or index >= matter_size for edge in edges for index in edge):
            raise ArtifactError("supplied_edges contains an invalid matter index")
        if any(
            x < 0 or y < 0 or x >= config.grid_shape[0] or y >= config.grid_shape[1]
            for x, y in sites
        ):
            raise ArtifactError("coupling_sites contains an invalid field index")

        self.cell_dir = Path(cell_dir)
        if self.cell_dir.exists():
            raise ArtifactError(f"cell journal already exists: {self.cell_dir}")
        try:
            self.cell_dir.mkdir(parents=True, exist_ok=False)
            self.snapshots_dir = self.cell_dir / "snapshots"
            self.snapshots_dir.mkdir()
            self.energy_path = self.cell_dir / "energy.jsonl"
            self.snapshot_manifest_path = self.snapshots_dir / "manifest.jsonl"
            self.energy_path.touch(exist_ok=False)
            self.snapshot_manifest_path.touch(exist_ok=False)
            atomic_write_json(
                self.cell_dir / "cell.json",
                {
                    "schema_version": SCHEMA_VERSION,
                    "stage": stage,
                    **_cell_json(cell),
                    "config": _config_json(config),
                    "coupling_sites": sites,
                    "supplied_edges": edges,
                },
            )
        except Exception as error:
            if isinstance(error, ArtifactError):
                raise
            raise ArtifactError(
                f"cannot create cell journal: {self.cell_dir}"
            ) from error

        self.cell = cell
        self.config = config
        self._field_shape = config.grid_shape
        self._matter_shape = (matter_size,)
        self._next_energy_tick = 0
        self._last_snapshot_tick: int | None = None

    @staticmethod
    def _append_line(path: Path, value: Mapping[str, Any]) -> None:
        encoded = _canonical_json_bytes(value) + b"\n"
        try:
            with path.open("ab") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError as error:
            raise ArtifactError(f"cannot append journal record: {path}") from error

    def append_energy(self, record: EnergyRecord) -> None:
        if record.tick != self._next_energy_tick:
            raise ArtifactError("energy ticks must be contiguous from zero")
        simulation_time = _finite_float(record.simulation_time, label="simulation_time")
        values: dict[str, float | None] = {}
        all_finite = True
        for name in tuple(EnergyRecord.__dataclass_fields__)[2:-1]:
            raw = getattr(record, name)
            if raw is None:
                values[name] = None
                all_finite = False
            else:
                number = float(raw)
                if math.isfinite(number):
                    values[name] = number
                else:
                    values[name] = None
                    all_finite = False
        finite = bool(record.finite) and all_finite
        self._append_line(
            self.energy_path,
            {
                "schema_version": SCHEMA_VERSION,
                "tick": record.tick,
                "simulation_time": simulation_time,
                **values,
                "finite": finite,
            },
        )
        self._next_energy_tick += 1

    def append_snapshot(self, snapshot: P0StateSnapshot) -> None:
        tick = _integer(snapshot.tick, label="snapshot tick")
        if self._last_snapshot_tick is not None and tick <= self._last_snapshot_tick:
            raise ArtifactError("snapshot ticks must be strictly increasing")
        simulation_time = _finite_float(
            snapshot.simulation_time, label="snapshot simulation_time"
        )
        arrays = {
            "u": snapshot.state.u,
            "p": snapshot.state.p,
            "q": snapshot.state.q,
            "r": snapshot.state.r,
        }
        expected_shapes = {
            "u": self._field_shape,
            "p": self._field_shape,
            "q": self._matter_shape,
            "r": self._matter_shape,
        }
        for name, array in arrays.items():
            if array.dtype != np.dtype(np.float64):
                raise ArtifactError(f"snapshot {name} has wrong dtype")
            if array.shape != expected_shapes[name]:
                raise ArtifactError(f"snapshot {name} has wrong shape")

        filename = f"snapshot-{tick:010d}.npz"
        target = self.snapshots_dir / filename
        if target.exists():
            raise ArtifactError(f"snapshot already exists: {target}")
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w+b", dir=self.snapshots_dir, prefix=".snapshot-", delete=False
            ) as stream:
                temporary = Path(stream.name)
                np.savez(stream, **arrays)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)
            temporary = None
            self._append_line(
                self.snapshot_manifest_path,
                {
                    "schema_version": SCHEMA_VERSION,
                    "tick": tick,
                    "simulation_time": simulation_time,
                    "file": filename,
                },
            )
        except Exception as error:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            if isinstance(error, ArtifactError):
                raise
            raise ArtifactError(f"cannot append snapshot: {target}") from error
        self._last_snapshot_tick = tick

    def append_trajectory(self, trajectory: Trajectory) -> None:
        if trajectory.cell != self.cell:
            raise ArtifactError("trajectory cell does not match journal cell")
        for record in trajectory.records:
            self.append_energy(record)
        for snapshot in trajectory.snapshots:
            self.append_snapshot(snapshot)


def _load_cell_manifest(cell_dir: Path) -> dict[str, Any]:
    value = read_json(cell_dir / "cell.json")
    if not isinstance(value, dict) or set(value) != _CELL_KEYS:
        raise ArtifactError(f"invalid cell.json schema: {cell_dir}")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ArtifactError(f"unsupported cell schema: {cell_dir}")
    if value["stage"] not in ("A", "B"):
        raise ArtifactError(f"invalid cell stage: {cell_dir}")
    return value


def iter_energy_records(cell_dir: str | Path) -> Iterator[EnergyRecord]:
    """Reload and validate the append-only energy ledger in tick order."""

    path = Path(cell_dir) / "energy.jsonl"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise ArtifactError(f"cannot read energy journal: {path}") from error
    for expected_tick, line in enumerate(lines):
        value = _decode_json(line, source=path)
        if not isinstance(value, dict) or set(value) != _ENERGY_KEYS:
            raise ArtifactError(f"invalid energy record schema: {path}")
        if value["schema_version"] != SCHEMA_VERSION:
            raise ArtifactError(f"unsupported energy schema: {path}")
        tick = _integer(value["tick"], label="energy tick")
        if tick != expected_tick:
            raise ArtifactError("energy ticks must be contiguous from zero")
        simulation_time = _finite_float(
            value["simulation_time"], label="energy simulation_time"
        )
        optional: dict[str, float | None] = {}
        names = tuple(EnergyRecord.__dataclass_fields__)[2:-1]
        for name in names:
            raw = value[name]
            optional[name] = None if raw is None else _finite_float(raw, label=name)
        finite = value["finite"]
        if not isinstance(finite, bool):
            raise ArtifactError("energy finite must be Boolean")
        if finite != all(item is not None for item in optional.values()):
            raise ArtifactError("energy finite flag is inconsistent with its values")
        yield EnergyRecord(tick, simulation_time, **optional, finite=finite)


def iter_snapshots(cell_dir: str | Path) -> Iterator[P0StateSnapshot]:
    """Reload snapshots after validating schema, inventory, dtype, and shape."""

    root = Path(cell_dir)
    cell = _load_cell_manifest(root)
    config = cell["config"]
    try:
        field_shape = tuple(config["grid_shape"])
    except (KeyError, TypeError) as error:
        raise ArtifactError(f"invalid configuration in cell.json: {root}") from error
    if len(field_shape) != 2 or any(
        isinstance(item, bool) or not isinstance(item, int) for item in field_shape
    ):
        raise ArtifactError(f"invalid field shape in cell.json: {root}")
    sites = _int_matrix(cell["coupling_sites"], label="coupling_sites")
    matter_shape = (len(sites),)
    manifest_path = root / "snapshots" / "manifest.jsonl"
    try:
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise ArtifactError(
            f"cannot read snapshot manifest: {manifest_path}"
        ) from error

    entries: list[dict[str, Any]] = []
    last_tick: int | None = None
    for line in lines:
        value = _decode_json(line, source=manifest_path)
        if not isinstance(value, dict) or set(value) != _SNAPSHOT_MANIFEST_KEYS:
            raise ArtifactError(f"invalid snapshot manifest schema: {manifest_path}")
        if value["schema_version"] != SCHEMA_VERSION:
            raise ArtifactError(f"unsupported snapshot schema: {manifest_path}")
        tick = _integer(value["tick"], label="snapshot tick")
        if last_tick is not None and tick <= last_tick:
            raise ArtifactError("snapshot ticks must be strictly increasing")
        expected_file = f"snapshot-{tick:010d}.npz"
        if value["file"] != expected_file:
            raise ArtifactError("snapshot manifest/file mismatch")
        _finite_float(value["simulation_time"], label="snapshot simulation_time")
        entries.append(value)
        last_tick = tick

    snapshots_dir = root / "snapshots"
    actual_files = {path.name for path in snapshots_dir.glob("*.npz")}
    expected_files = {entry["file"] for entry in entries}
    if actual_files != expected_files:
        raise ArtifactError("snapshot manifest/file mismatch")

    expected_shapes = {
        "u": field_shape,
        "p": field_shape,
        "q": matter_shape,
        "r": matter_shape,
    }
    for entry in entries:
        source = snapshots_dir / entry["file"]
        try:
            with np.load(source, allow_pickle=False) as archive:
                if set(archive.files) != _SNAPSHOT_KEYS:
                    raise ArtifactError(f"snapshot keys mismatch: {source}")
                arrays = {
                    name: np.array(archive[name], copy=True) for name in _SNAPSHOT_KEYS
                }
        except ArtifactError:
            raise
        except (OSError, ValueError) as error:
            raise ArtifactError(f"cannot read snapshot: {source}") from error
        for name, array in arrays.items():
            if array.dtype != np.dtype(np.float64):
                raise ArtifactError(f"snapshot {name} dtype mismatch: {source}")
            if array.shape != expected_shapes[name]:
                raise ArtifactError(f"snapshot {name} shape mismatch: {source}")
        yield P0StateSnapshot(
            tick=entry["tick"],
            simulation_time=float(entry["simulation_time"]),
            state=P0State(arrays["u"], arrays["p"], arrays["q"], arrays["r"]),
        )


def _digest_part(hasher: Any, label: str, payload: bytes) -> None:
    label_bytes = label.encode("utf-8")
    hasher.update(len(label_bytes).to_bytes(8, "big"))
    hasher.update(label_bytes)
    hasher.update(len(payload).to_bytes(8, "big"))
    hasher.update(payload)


def _scientific_manifest(value: Mapping[str, Any]) -> dict[str, Any]:
    required = (
        "schema_version",
        "preregistration_sha256",
        "preregistration_git_blob",
        "addendum_sha256",
        "addendum_git_blob",
        "scientific_core_sha256",
        "config",
        "cell_order",
    )
    if any(name not in value for name in required):
        raise ArtifactError("run.json is missing scientific identity fields")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ArtifactError("unsupported run manifest schema")
    if not _SHA256.fullmatch(str(value["scientific_core_sha256"])):
        raise ArtifactError("run.json has invalid scientific_core_sha256")
    return {name: value[name] for name in required if name != "cell_order"}


def scientific_digest(output_dir: str | Path) -> str:
    """Hash decoded scientific values, excluding run/view/result metadata."""

    root = Path(output_dir)
    manifest = read_json(root / "run.json")
    if not isinstance(manifest, dict):
        raise ArtifactError("run.json must contain an object")
    scientific_manifest = _scientific_manifest(manifest)
    cell_order = manifest["cell_order"]
    if (
        not isinstance(cell_order, list)
        or any(not isinstance(slug, str) or not slug for slug in cell_order)
        or len(cell_order) != len(set(cell_order))
    ):
        raise ArtifactError("run.json has invalid cell_order")

    actual_cell_dirs = {
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / "cell.json").is_file()
    }
    if actual_cell_dirs != set(cell_order):
        raise ArtifactError("run manifest/cell directory mismatch")

    hasher = sha256()
    _digest_part(hasher, "run", _canonical_json_bytes(scientific_manifest))
    for slug in sorted(cell_order):
        cell_dir = root / slug
        cell_manifest = _load_cell_manifest(cell_dir)
        _digest_part(hasher, f"cell:{slug}", _canonical_json_bytes(cell_manifest))
        for record in iter_energy_records(cell_dir):
            value = {"schema_version": SCHEMA_VERSION, **asdict(record)}
            _digest_part(
                hasher,
                f"energy:{slug}:{record.tick}",
                _canonical_json_bytes(value),
            )
        for snapshot in iter_snapshots(cell_dir):
            metadata = {
                "schema_version": SCHEMA_VERSION,
                "tick": snapshot.tick,
                "simulation_time": snapshot.simulation_time,
            }
            _digest_part(
                hasher,
                f"snapshot:{slug}:{snapshot.tick}",
                _canonical_json_bytes(metadata),
            )
            for name in ("u", "p", "q", "r"):
                array = getattr(snapshot.state, name)
                shape = _canonical_json_bytes(list(array.shape))
                _digest_part(
                    hasher,
                    f"array:{slug}:{snapshot.tick}:{name}:shape",
                    shape,
                )
                _digest_part(
                    hasher,
                    f"array:{slug}:{snapshot.tick}:{name}:float64-c-order",
                    array.tobytes(order="C"),
                )
    return hasher.hexdigest()
