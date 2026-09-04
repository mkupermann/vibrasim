"""Registered P0 evidence gates and pure ordered verdict selection."""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import numpy as np

from .artifacts import (
    ArtifactError,
    iter_energy_records,
    iter_snapshots,
    read_json,
)
from .energy import (
    EnergyRecord,
)
from .energy import (
    a_b as trace_a_b,
)
from .energy import (
    coupling_identity_residual as trace_coupling_identity_residual,
)
from .energy import (
    max_material_energy_ratio as trace_max_material_energy_ratio,
)
from .energy import (
    max_relative_energy_drift as trace_max_relative_energy_drift,
)
from .fixtures import (
    coupling_sites,
    edges_for,
    omega_upper,
    registered_stage_a_cells,
    reproduction_cells,
)
from .types import ChannelMode, P0Config, RunCell, RunPurpose, Topology, Verdict

ENERGY_DRIFT_MAX = 0.005
IDENTITY_RESIDUAL_MAX = 0.005
EXERCISED_CHANNEL_MIN = 0.01
DT_HALF_DELTA_MAX = 0.002
BROKEN_PAIR_DRIFT_MIN = 0.05
TOPOLOGY_CONTRAST_MIN = 0.02
INITIAL_ENERGY_TOL = 1e-12
DECOUPLED_MATTER_TOL = 1e-12
RERUN_A_B_TOL = 1e-12
STABILITY_PRODUCT_MAX = 0.25


@dataclass(frozen=True)
class CellMetrics:
    a_b: float
    max_relative_energy_drift: float
    coupling_identity_residual: float
    max_material_energy_ratio: float
    initial_energy: float
    max_matter_energy: float
    finite: bool


@dataclass(frozen=True)
class P0Evidence:
    configuration_matches: bool
    all_values_finite: bool
    initial_energy_matches: bool
    stability_bound_holds: bool
    valid_arm_energy_gates_hold: bool
    valid_arm_identity_gates_hold: bool
    exercised_channel_holds: bool
    timestep_convergence_holds: bool
    broken_pair_sensitivity_holds: bool
    topology_difference_holds: bool
    topology_sign_holds: bool
    decoupled_zero_holds: bool
    deterministic_rerun_holds: bool


@dataclass(frozen=True)
class StageAGate:
    proceed: bool
    provisional_verdict: Verdict | None
    reasons: tuple[str, ...]


def _initial_energy(delta: float) -> bool:
    return bool(delta <= INITIAL_ENERGY_TOL)


def _stability(product: float) -> bool:
    return bool(product < STABILITY_PRODUCT_MAX)


def _energy_drift(value: float) -> bool:
    return bool(value < ENERGY_DRIFT_MAX)


def _identity_residual(value: float) -> bool:
    return bool(value < IDENTITY_RESIDUAL_MAX)


def _exercised_channel(value: float) -> bool:
    return bool(value > EXERCISED_CHANNEL_MIN)


def _timestep_delta(value: float) -> bool:
    return bool(value < DT_HALF_DELTA_MAX)


def _broken_pair_drift(value: float) -> bool:
    return bool(value > BROKEN_PAIR_DRIFT_MIN)


def _topology_contrast(value: float) -> bool:
    return bool(abs(value) > TOPOLOGY_CONTRAST_MIN)


def _decoupled_matter(value: float) -> bool:
    return bool(value < DECOUPLED_MATTER_TOL)


def _rerun_delta(value: float) -> bool:
    return bool(value < RERUN_A_B_TOL)


REGISTERED_PREDICATES: MappingProxyType[str, Callable[[float], bool]] = (
    MappingProxyType(
        {
            "initial_energy": _initial_energy,
            "stability": _stability,
            "energy_drift": _energy_drift,
            "identity_residual": _identity_residual,
            "exercised_channel": _exercised_channel,
            "timestep_delta": _timestep_delta,
            "broken_pair_drift": _broken_pair_drift,
            "topology_contrast": _topology_contrast,
            "decoupled_matter": _decoupled_matter,
            "rerun_delta": _rerun_delta,
        }
    )
)


_FAIL_FIELDS = (
    "configuration_matches",
    "all_values_finite",
    "initial_energy_matches",
    "stability_bound_holds",
)
_INCONCLUSIVE_FIELDS = (
    "valid_arm_energy_gates_hold",
    "valid_arm_identity_gates_hold",
    "exercised_channel_holds",
    "timestep_convergence_holds",
    "broken_pair_sensitivity_holds",
)
_STAGE_B_FIELDS = (
    "topology_difference_holds",
    "topology_sign_holds",
    "decoupled_zero_holds",
    "deterministic_rerun_holds",
)


def _failed_fields(evidence: P0Evidence, fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(field for field in fields if not getattr(evidence, field))


def evaluate_stage_a(evidence: P0Evidence) -> StageAGate:
    """Evaluate only the registered Stage-A stop/go gates."""

    fail_reasons = _failed_fields(evidence, _FAIL_FIELDS)
    inconclusive_reasons = _failed_fields(evidence, _INCONCLUSIVE_FIELDS)
    reasons = fail_reasons + inconclusive_reasons
    if fail_reasons:
        return StageAGate(False, Verdict.FAIL, reasons)
    if inconclusive_reasons:
        return StageAGate(False, Verdict.INCONCLUSIVE, reasons)
    return StageAGate(True, None, ())


def decide_verdict(evidence: P0Evidence) -> Verdict:
    """Return the registered verdict without file I/O or threshold overrides."""

    if _failed_fields(evidence, _FAIL_FIELDS):
        return Verdict.FAIL
    if _failed_fields(evidence, _INCONCLUSIVE_FIELDS):
        return Verdict.INCONCLUSIVE
    if not _failed_fields(evidence, _STAGE_B_FIELDS):
        return Verdict.PASS
    return Verdict.NULL


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
        "source_centres": [list(source) for source in config.source_centres],
    }


def _cell_manifest_json(
    cell: RunCell, *, stage: str, config: P0Config
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "stage": stage,
        "topology": cell.topology.value,
        "mode": cell.mode.value,
        "purpose": cell.purpose.value,
        "source_centre": list(cell.source_centre),
        "dt": cell.dt,
        "steps": cell.steps,
        "config": _config_json(config),
        "coupling_sites": coupling_sites().tolist(),
        "supplied_edges": edges_for(cell.topology).tolist(),
    }


def _required_mapping(
    value: Any, *, label: str, fields: Iterable[str]
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ArtifactError(f"{label} must contain an object")
    missing = tuple(field for field in fields if field not in value)
    if missing:
        raise ArtifactError(f"{label} is missing required fields: {', '.join(missing)}")
    return value


def validate_registered_artifacts(
    output_dir: str | Path, *, include_reproduction: bool
) -> bool:
    """Validate the complete registered manifest matrix before metric evaluation.

    Structurally missing or unreadable artifacts raise ``ArtifactError``. A fully
    readable departure from the registered experiment instead returns ``False``
    so the pure verdict layer can classify it as ``FAIL``.
    """

    root = Path(output_dir)
    config = P0Config.registered()
    stage_a = registered_stage_a_cells(config)
    stage_b = reproduction_cells(config)
    declared_cells = stage_a + stage_b
    executed_cells = stage_a + (stage_b if include_reproduction else ())

    run = _required_mapping(
        read_json(root / "run.json"),
        label="run.json",
        fields=("schema_version", "config", "cell_order"),
    )
    cell_order = run["cell_order"]
    if not isinstance(cell_order, list) or any(
        not isinstance(slug, str) or not slug for slug in cell_order
    ):
        raise ArtifactError("run.json cell_order must be a list of non-empty slugs")
    if len(cell_order) != len(set(cell_order)):
        raise ArtifactError("run.json contains a duplicate declared cell slug")
    if not isinstance(run["config"], dict):
        raise ArtifactError("run.json config must contain an object")

    configuration_matches = (
        run["schema_version"] == 1
        and run["config"] == _config_json(config)
        and cell_order == [cell.slug for cell in declared_cells]
    )

    expected_by_slug = {cell.slug: cell for cell in executed_cells}
    try:
        actual_directories = {
            path.name: path for path in root.iterdir() if path.is_dir()
        }
    except OSError as error:
        raise ArtifactError(
            f"cannot enumerate registered run directory: {root}"
        ) from error
    missing = tuple(slug for slug in expected_by_slug if slug not in actual_directories)
    if missing:
        raise ArtifactError(f"missing declared cell directory: {missing[0]}")
    if set(actual_directories) != set(expected_by_slug):
        configuration_matches = False

    required_cell_fields = tuple(
        _cell_manifest_json(executed_cells[0], stage="A", config=config)
    )
    for slug, cell_dir in actual_directories.items():
        manifest = _required_mapping(
            read_json(cell_dir / "cell.json"),
            label=f"{slug}/cell.json",
            fields=required_cell_fields,
        )
        expected_cell = expected_by_slug.get(slug)
        if expected_cell is None:
            configuration_matches = False
            continue
        expected_stage = (
            "B" if expected_cell.purpose is RunPurpose.REPRODUCTION else "A"
        )
        if manifest != _cell_manifest_json(
            expected_cell, stage=expected_stage, config=config
        ):
            configuration_matches = False

    return configuration_matches


def _all_record_values_finite(records: tuple[EnergyRecord, ...]) -> bool:
    scalar_names = tuple(EnergyRecord.__dataclass_fields__)[1:-1]
    return all(
        record.finite
        and all(
            value is not None and math.isfinite(float(value))
            for value in (getattr(record, name) for name in scalar_names)
        )
        for record in records
    )


def _load_cell_metrics(cell_dir: Path, cell: RunCell) -> CellMetrics:
    records = tuple(iter_energy_records(cell_dir))
    if not records:
        raise ArtifactError(f"missing required energy records: {cell.slug}")
    if records[0].tick != 0 or any(
        record.tick != tick for tick, record in enumerate(records)
    ):
        raise ArtifactError(f"invalid energy tick sequence: {cell.slug}")
    if records[-1].finite and records[-1].tick != cell.steps:
        raise ArtifactError(f"incomplete energy records: {cell.slug}")

    snapshots = tuple(iter_snapshots(cell_dir))
    if not snapshots:
        raise ArtifactError(f"missing required snapshots: {cell.slug}")
    snapshot_finite = all(
        all(
            np.isfinite(getattr(snapshot.state, name)).all()
            for name in ("u", "p", "q", "r")
        )
        for snapshot in snapshots
    )
    record_finite = _all_record_values_finite(records)
    finite = record_finite and snapshot_finite
    initial_energy = (
        float(records[0].h_total) if records[0].h_total is not None else math.nan
    )
    if not record_finite:
        return CellMetrics(
            a_b=math.nan,
            max_relative_energy_drift=math.nan,
            coupling_identity_residual=math.nan,
            max_material_energy_ratio=math.nan,
            initial_energy=initial_energy,
            max_matter_energy=math.nan,
            finite=False,
        )
    try:
        return CellMetrics(
            a_b=trace_a_b(records),
            max_relative_energy_drift=trace_max_relative_energy_drift(records),
            coupling_identity_residual=trace_coupling_identity_residual(records),
            max_material_energy_ratio=trace_max_material_energy_ratio(records),
            initial_energy=initial_energy,
            max_matter_energy=max(
                float(record.h_matter)
                for record in records
                if record.h_matter is not None
            ),
            finite=finite,
        )
    except (ValueError, TypeError) as error:
        raise ArtifactError(
            f"cannot construct metrics for cell: {cell.slug}"
        ) from error


def _metric_key(
    cell: RunCell,
) -> tuple[RunPurpose, ChannelMode, Topology, tuple[int, int]]:
    return cell.purpose, cell.mode, cell.topology, cell.source_centre


def build_evidence(output_dir: str | Path, *, include_reproduction: bool) -> P0Evidence:
    """Reload registered artifacts and apply every fixed P0 evidence predicate."""

    root = Path(output_dir)
    configuration_matches = validate_registered_artifacts(
        root, include_reproduction=include_reproduction
    )
    config = P0Config.registered()
    stage_a = registered_stage_a_cells(config)
    executed_cells = stage_a + (
        reproduction_cells(config) if include_reproduction else ()
    )
    metrics = {
        _metric_key(cell): _load_cell_metrics(root / cell.slug, cell)
        for cell in executed_cells
    }

    def metric(
        purpose: RunPurpose,
        mode: ChannelMode,
        topology: Topology,
        source: tuple[int, int],
    ) -> CellMetrics:
        return metrics[(purpose, mode, topology, source)]

    primary_pairs = tuple(
        (
            metric(RunPurpose.PRIMARY, ChannelMode.FULL, Topology.CYCLE, source),
            metric(RunPurpose.PRIMARY, ChannelMode.FULL, Topology.BRANCH, source),
        )
        for source in config.source_centres
    )
    valid_arms = tuple(
        item
        for source in config.source_centres
        for item in (
            metric(RunPurpose.PRIMARY, ChannelMode.FULL, Topology.CYCLE, source),
            metric(RunPurpose.PRIMARY, ChannelMode.FULL, Topology.BRANCH, source),
            metric(RunPurpose.PRIMARY, ChannelMode.NO_BONDS, Topology.CYCLE, source),
            metric(RunPurpose.PRIMARY, ChannelMode.DECOUPLED, Topology.CYCLE, source),
        )
    )
    convergence_pairs = tuple(
        (
            metric(RunPurpose.CONVERGENCE, ChannelMode.FULL, Topology.CYCLE, source),
            metric(RunPurpose.CONVERGENCE, ChannelMode.FULL, Topology.BRANCH, source),
        )
        for source in config.source_centres
    )
    primary_contrasts = tuple(cycle.a_b - branch.a_b for cycle, branch in primary_pairs)

    initial_energy_matches = all(
        REGISTERED_PREDICATES["initial_energy"](
            abs(cycle.initial_energy - branch.initial_energy)
        )
        for cycle, branch in primary_pairs
    )
    stability_bound_holds = all(
        REGISTERED_PREDICATES["stability"](cell.dt * omega_upper(config, cell.topology))
        for cell in stage_a
    )
    valid_arm_energy_gates_hold = all(
        REGISTERED_PREDICATES["energy_drift"](item.max_relative_energy_drift)
        for item in valid_arms
    )
    valid_arm_identity_gates_hold = all(
        REGISTERED_PREDICATES["identity_residual"](item.coupling_identity_residual)
        for item in valid_arms
    )
    exercised_channel_holds = all(
        REGISTERED_PREDICATES["exercised_channel"](item.max_material_energy_ratio)
        for pair in primary_pairs
        for item in pair
    )
    timestep_convergence_holds = all(
        REGISTERED_PREDICATES["timestep_delta"](abs(primary.a_b - converged.a_b))
        for primary_pair, converged_pair in zip(
            primary_pairs, convergence_pairs, strict=True
        )
        for primary, converged in zip(primary_pair, converged_pair, strict=True)
    ) and all(
        REGISTERED_PREDICATES["timestep_delta"](
            abs(
                (primary_cycle.a_b - primary_branch.a_b)
                - (converged_cycle.a_b - converged_branch.a_b)
            )
        )
        for (primary_cycle, primary_branch), (
            converged_cycle,
            converged_branch,
        ) in zip(primary_pairs, convergence_pairs, strict=True)
    )
    broken_pair_sensitivity_holds = all(
        any(
            REGISTERED_PREDICATES["broken_pair_drift"](
                metric(
                    RunPurpose.SENSITIVITY,
                    ChannelMode.BROKEN_PAIR,
                    topology,
                    source,
                ).max_relative_energy_drift
            )
            for source in config.source_centres
        )
        for topology in (Topology.CYCLE, Topology.BRANCH)
    )
    topology_difference_holds = all(
        REGISTERED_PREDICATES["topology_contrast"](contrast)
        for contrast in primary_contrasts
    )
    topology_sign_holds = all(contrast > 0.0 for contrast in primary_contrasts) or all(
        contrast < 0.0 for contrast in primary_contrasts
    )
    decoupled_zero_holds = all(
        REGISTERED_PREDICATES["decoupled_matter"](
            metric(
                RunPurpose.PRIMARY,
                ChannelMode.DECOUPLED,
                Topology.CYCLE,
                source,
            ).max_matter_energy
        )
        for source in config.source_centres
    )
    deterministic_rerun_holds = include_reproduction and all(
        REGISTERED_PREDICATES["rerun_delta"](
            abs(
                primary.a_b
                - metric(
                    RunPurpose.REPRODUCTION,
                    ChannelMode.FULL,
                    topology,
                    source,
                ).a_b
            )
        )
        for source, pair in zip(config.source_centres, primary_pairs, strict=True)
        for topology, primary in zip(
            (Topology.CYCLE, Topology.BRANCH), pair, strict=True
        )
    )

    return P0Evidence(
        configuration_matches=configuration_matches,
        all_values_finite=all(item.finite for item in metrics.values()),
        initial_energy_matches=initial_energy_matches,
        stability_bound_holds=stability_bound_holds,
        valid_arm_energy_gates_hold=valid_arm_energy_gates_hold,
        valid_arm_identity_gates_hold=valid_arm_identity_gates_hold,
        exercised_channel_holds=exercised_channel_holds,
        timestep_convergence_holds=timestep_convergence_holds,
        broken_pair_sensitivity_holds=broken_pair_sensitivity_holds,
        topology_difference_holds=topology_difference_holds,
        topology_sign_holds=topology_sign_holds,
        decoupled_zero_holds=decoupled_zero_holds,
        deterministic_rerun_holds=deterministic_rerun_holds,
    )
