import shutil
from dataclasses import replace
from types import MappingProxyType

import numpy as np
import pytest

from vibrasim2.p0 import verdict as verdict_module
from vibrasim2.p0.artifacts import (
    ArtifactError,
    CellJournal,
    atomic_write_json,
    read_json,
    write_run_manifest,
)
from vibrasim2.p0.energy import EnergyRecord
from vibrasim2.p0.fixtures import (
    coupling_sites,
    edges_for,
    registered_stage_a_cells,
    reproduction_cells,
)
from vibrasim2.p0.types import (
    ChannelMode,
    P0Config,
    P0State,
    P0StateSnapshot,
    RunPurpose,
    Topology,
    Verdict,
)
from vibrasim2.p0.verdict import (
    REGISTERED_PREDICATES,
    P0Evidence,
    build_evidence,
    decide_verdict,
    evaluate_stage_a,
    validate_registered_artifacts,
)


def passing_evidence() -> P0Evidence:
    return P0Evidence(
        configuration_matches=True,
        all_values_finite=True,
        initial_energy_matches=True,
        stability_bound_holds=True,
        valid_arm_energy_gates_hold=True,
        valid_arm_identity_gates_hold=True,
        exercised_channel_holds=True,
        timestep_convergence_holds=True,
        broken_pair_sensitivity_holds=True,
        topology_difference_holds=True,
        topology_sign_holds=True,
        decoupled_zero_holds=True,
        deterministic_rerun_holds=True,
    )


FAIL_FIELDS = (
    "configuration_matches",
    "all_values_finite",
    "initial_energy_matches",
    "stability_bound_holds",
)
INCONCLUSIVE_FIELDS = (
    "valid_arm_energy_gates_hold",
    "valid_arm_identity_gates_hold",
    "exercised_channel_holds",
    "timestep_convergence_holds",
    "broken_pair_sensitivity_holds",
)
STAGE_B_FIELDS = (
    "topology_difference_holds",
    "topology_sign_holds",
    "decoupled_zero_holds",
    "deterministic_rerun_holds",
)


@pytest.mark.parametrize("field", FAIL_FIELDS)
def test_fail_precedes_every_other_outcome(field):
    evidence = replace(
        passing_evidence(),
        **{field: False, INCONCLUSIVE_FIELDS[0]: False, STAGE_B_FIELDS[0]: False},
    )

    assert decide_verdict(evidence) is Verdict.FAIL


@pytest.mark.parametrize("field", INCONCLUSIVE_FIELDS)
def test_inconclusive_precedes_stage_b_effect(field):
    evidence = replace(
        passing_evidence(),
        **{field: False, STAGE_B_FIELDS[0]: False},
    )

    assert decide_verdict(evidence) is Verdict.INCONCLUSIVE


def test_every_registered_effect_passes():
    assert decide_verdict(passing_evidence()) is Verdict.PASS


@pytest.mark.parametrize("field", STAGE_B_FIELDS)
def test_clean_valid_run_without_stage_b_effect_is_null(field):
    assert decide_verdict(replace(passing_evidence(), **{field: False})) is Verdict.NULL


@pytest.mark.parametrize(
    ("predicate", "boundary", "expected"),
    (
        ("initial_energy", 1e-12, True),
        ("stability", 0.25, False),
        ("energy_drift", 0.005, False),
        ("identity_residual", 0.005, False),
        ("exercised_channel", 0.01, False),
        ("timestep_delta", 0.002, False),
        ("broken_pair_drift", 0.05, False),
        ("topology_contrast", 0.02, False),
        ("decoupled_matter", 1e-12, False),
        ("rerun_delta", 1e-12, False),
    ),
)
def test_exact_registered_boundaries(predicate, boundary, expected):
    assert REGISTERED_PREDICATES[predicate](boundary) is expected


@pytest.mark.parametrize(
    ("predicate", "boundary", "direction"),
    (
        ("initial_energy", 1e-12, "maximum"),
        ("stability", 0.25, "maximum"),
        ("energy_drift", 0.005, "maximum"),
        ("identity_residual", 0.005, "maximum"),
        ("exercised_channel", 0.01, "minimum"),
        ("timestep_delta", 0.002, "maximum"),
        ("broken_pair_drift", 0.05, "minimum"),
        ("topology_contrast", 0.02, "magnitude_minimum"),
        ("decoupled_matter", 1e-12, "maximum"),
        ("rerun_delta", 1e-12, "maximum"),
    ),
)
def test_registered_predicates_distinguish_adjacent_floats(
    predicate, boundary, direction
):
    below = np.nextafter(boundary, -np.inf)
    above = np.nextafter(boundary, np.inf)
    check = REGISTERED_PREDICATES[predicate]

    if direction == "maximum":
        assert check(below) is True
        assert check(above) is False
    elif direction == "minimum":
        assert check(below) is False
        assert check(above) is True
    else:
        assert check(below) is False
        assert check(above) is True
        assert check(-below) is False
        assert check(-above) is True


def test_registered_predicates_are_immutable_and_accept_no_threshold_override():
    assert isinstance(REGISTERED_PREDICATES, MappingProxyType)
    with pytest.raises(TypeError):
        REGISTERED_PREDICATES["energy_drift"] = lambda _: True
    with pytest.raises(TypeError):
        REGISTERED_PREDICATES["energy_drift"](0.1, threshold=1.0)


def test_stage_a_proceeds_only_after_all_stage_a_gates_hold():
    gate = evaluate_stage_a(passing_evidence())

    assert gate.proceed is True
    assert gate.provisional_verdict is None
    assert gate.reasons == ()


@pytest.mark.parametrize("field", FAIL_FIELDS)
def test_stage_a_returns_fail_with_an_ordered_reason(field):
    evidence = replace(passing_evidence(), **{field: False})

    gate = evaluate_stage_a(evidence)

    assert gate.proceed is False
    assert gate.provisional_verdict is Verdict.FAIL
    assert gate.reasons == (field,)


def test_stage_a_lists_all_reasons_in_registered_precedence_order():
    evidence = replace(
        passing_evidence(),
        stability_bound_holds=False,
        configuration_matches=False,
        broken_pair_sensitivity_holds=False,
        valid_arm_energy_gates_hold=False,
    )

    gate = evaluate_stage_a(evidence)

    assert gate.proceed is False
    assert gate.provisional_verdict is Verdict.FAIL
    assert gate.reasons == (
        "configuration_matches",
        "stability_bound_holds",
        "valid_arm_energy_gates_hold",
        "broken_pair_sensitivity_holds",
    )


@pytest.mark.parametrize("field", INCONCLUSIVE_FIELDS)
def test_stage_a_returns_inconclusive_for_validity_or_sensitivity_failure(field):
    gate = evaluate_stage_a(replace(passing_evidence(), **{field: False}))

    assert gate.proceed is False
    assert gate.provisional_verdict is Verdict.INCONCLUSIVE
    assert gate.reasons == (field,)


def test_stage_a_does_not_consider_stage_b_effect_fields():
    evidence = replace(
        passing_evidence(),
        **{field: False for field in STAGE_B_FIELDS},
    )

    assert evaluate_stage_a(evidence).proceed is True


def write_registered_manifest_fixture(root, include_reproduction):
    config = P0Config.registered()
    stage_a = registered_stage_a_cells(config)
    stage_b = reproduction_cells(config)
    write_run_manifest(
        root,
        run_id="registered-test-fixture",
        config=config,
        cells=stage_a + stage_b,
        scientific_core_sha256="1" * 64,
    )
    for stage, cells in (("A", stage_a), ("B", stage_b)):
        if stage == "B" and not include_reproduction:
            continue
        for cell in cells:
            CellJournal(
                root / cell.slug,
                stage=stage,
                cell=cell,
                config=config,
                coupling_sites=coupling_sites(),
                supplied_edges=edges_for(cell.topology),
            )
    return root


@pytest.mark.parametrize("include_reproduction", (False, True))
def test_registered_artifact_matrix_matches_exactly(tmp_path, include_reproduction):
    write_registered_manifest_fixture(tmp_path, include_reproduction)

    assert (
        validate_registered_artifacts(
            tmp_path, include_reproduction=include_reproduction
        )
        is True
    )


CONFIG_MUTATIONS = {
    "grid_shape": [33, 32],
    "c": 1.1,
    "k_b": 0.6,
    "g": 1.1,
    "dt": 0.04,
    "sigma": 2.1,
    "steps": 1999,
    "frame_stride": 11,
    "source_centres": [[5, 16], [16, 4], [4, 4]],
}


def _write_changed_json(path, mutate):
    value = read_json(path)
    mutate(value)
    atomic_write_json(path, value)


@pytest.mark.parametrize(
    "mutation",
    (
        *(f"run_config:{field}" for field in CONFIG_MUTATIONS),
        *(f"cell_config:{field}" for field in CONFIG_MUTATIONS),
        "stage",
        "topology",
        "mode",
        "purpose",
        "source_centre",
        "dt",
        "steps",
        "cell_order",
        "coupling_sites",
        "supplied_edges",
        "extra_cell",
    ),
)
def test_configuration_gate_rejects_every_readable_mutation(tmp_path, mutation):
    root = write_registered_manifest_fixture(tmp_path / "run", True)
    config = P0Config.registered()
    first = registered_stage_a_cells(config)[0]
    manifest_path = root / "run.json"
    cell_path = root / first.slug / "cell.json"

    if mutation.startswith("run_config:"):
        field = mutation.partition(":")[2]
        _write_changed_json(
            manifest_path,
            lambda value: value["config"].__setitem__(field, CONFIG_MUTATIONS[field]),
        )
    elif mutation.startswith("cell_config:"):
        field = mutation.partition(":")[2]
        _write_changed_json(
            cell_path,
            lambda value: value["config"].__setitem__(field, CONFIG_MUTATIONS[field]),
        )
    elif mutation == "stage":
        _write_changed_json(cell_path, lambda value: value.__setitem__("stage", "B"))
    elif mutation == "topology":
        _write_changed_json(
            cell_path, lambda value: value.__setitem__("topology", "branch")
        )
    elif mutation == "mode":
        _write_changed_json(
            cell_path, lambda value: value.__setitem__("mode", "no_bonds")
        )
    elif mutation == "purpose":
        _write_changed_json(
            cell_path, lambda value: value.__setitem__("purpose", "sensitivity")
        )
    elif mutation == "source_centre":
        _write_changed_json(
            cell_path, lambda value: value.__setitem__("source_centre", [5, 16])
        )
    elif mutation == "dt":
        _write_changed_json(cell_path, lambda value: value.__setitem__("dt", 0.04))
    elif mutation == "steps":
        _write_changed_json(cell_path, lambda value: value.__setitem__("steps", 1999))
    elif mutation == "cell_order":
        _write_changed_json(manifest_path, lambda value: value["cell_order"].reverse())
    elif mutation == "coupling_sites":
        _write_changed_json(
            cell_path,
            lambda value: value["coupling_sites"].__setitem__(0, [12, 16]),
        )
    elif mutation == "supplied_edges":
        _write_changed_json(
            cell_path,
            lambda value: value["supplied_edges"].__setitem__(0, [0, 2]),
        )
    else:
        shutil.copytree(root / first.slug, root / "extra-readable-cell")

    configuration_matches = validate_registered_artifacts(
        root, include_reproduction=True
    )
    evidence = replace(passing_evidence(), configuration_matches=configuration_matches)

    assert configuration_matches is False
    assert decide_verdict(evidence) is Verdict.FAIL


def test_missing_declared_cell_is_an_operational_error(tmp_path):
    root = write_registered_manifest_fixture(tmp_path, False)
    missing = registered_stage_a_cells(P0Config.registered())[0]
    shutil.rmtree(root / missing.slug)

    with pytest.raises(ArtifactError, match="missing"):
        validate_registered_artifacts(root, include_reproduction=False)


def test_duplicate_declared_cell_slug_is_an_operational_error(tmp_path):
    root = write_registered_manifest_fixture(tmp_path, False)
    manifest_path = root / "run.json"
    _write_changed_json(
        manifest_path,
        lambda value: value["cell_order"].append(value["cell_order"][0]),
    )

    with pytest.raises(ArtifactError, match="duplicate"):
        validate_registered_artifacts(root, include_reproduction=False)


@pytest.mark.parametrize("target", ("run", "cell"))
def test_malformed_required_json_is_an_operational_error(tmp_path, target):
    root = write_registered_manifest_fixture(tmp_path, False)
    if target == "run":
        path = root / "run.json"
    else:
        first = registered_stage_a_cells(P0Config.registered())[0]
        path = root / first.slug / "cell.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(ArtifactError):
        validate_registered_artifacts(root, include_reproduction=False)


def test_unreadable_required_manifest_is_an_operational_error(tmp_path, monkeypatch):
    root = write_registered_manifest_fixture(tmp_path, False)
    target = root / "run.json"
    real_read_json = verdict_module.read_json

    def fail_one_read(path):
        if path == target:
            raise ArtifactError("cannot read required manifest")
        return real_read_json(path)

    monkeypatch.setattr(verdict_module, "read_json", fail_one_read)

    with pytest.raises(ArtifactError, match="cannot read"):
        validate_registered_artifacts(root, include_reproduction=False)


def _record(tick, dt, *, a_value, total=1.0, initial=False):
    matter = 0.0 if initial else a_value
    coupling = 0.1
    return EnergyRecord(
        tick=tick,
        simulation_time=tick * dt,
        h_field=total - matter - coupling,
        h_matter=matter,
        h_coupling=coupling,
        h_total=total,
        p_field_from_coupling=0.0,
        p_matter_from_coupling=0.0,
        integral_field_power=0.0,
        integral_matter_power=0.0,
        finite=True,
    )


def _registered_records(cell):
    source_index = P0Config.registered().source_centres.index(cell.source_centre)
    cycle_value = 0.20 + 0.05 * source_index
    if cell.purpose is RunPurpose.REPRODUCTION:
        a_value = cycle_value if cell.topology is Topology.CYCLE else cycle_value - 0.03
    elif cell.purpose is RunPurpose.CONVERGENCE:
        a_value = (
            cycle_value + 0.001
            if cell.topology is Topology.CYCLE
            else cycle_value - 0.029
        )
    elif cell.mode is ChannelMode.DECOUPLED:
        a_value = 0.0
    elif cell.mode is ChannelMode.FULL:
        a_value = cycle_value if cell.topology is Topology.CYCLE else cycle_value - 0.03
    else:
        a_value = 0.10
    total = 1.06 if cell.mode is ChannelMode.BROKEN_PAIR else 1.0
    return tuple(
        _record(
            tick,
            cell.dt,
            a_value=a_value,
            total=1.0 if tick == 0 else total,
            initial=tick == 0,
        )
        for tick in range(cell.steps + 1)
    )


def _finite_snapshot():
    config = P0Config.registered()
    return P0StateSnapshot(
        tick=0,
        simulation_time=0.0,
        state=P0State(
            np.zeros(config.grid_shape),
            np.zeros(config.grid_shape),
            np.zeros(6),
            np.zeros(6),
        ),
    )


def test_build_evidence_reloads_all_registered_metrics_and_passes(
    tmp_path, monkeypatch
):
    root = write_registered_manifest_fixture(tmp_path, True)
    cells = {
        cell.slug: cell
        for cell in registered_stage_a_cells(P0Config.registered())
        + reproduction_cells(P0Config.registered())
    }
    monkeypatch.setattr(
        verdict_module,
        "iter_energy_records",
        lambda cell_dir: iter(_registered_records(cells[cell_dir.name])),
    )
    monkeypatch.setattr(
        verdict_module,
        "iter_snapshots",
        lambda _cell_dir: iter((_finite_snapshot(),)),
    )

    evidence = build_evidence(root, include_reproduction=True)

    assert evidence == passing_evidence()
    assert decide_verdict(evidence) is Verdict.PASS


def test_stage_a_evidence_does_not_require_reproduction(tmp_path, monkeypatch):
    root = write_registered_manifest_fixture(tmp_path, False)
    cells = {
        cell.slug: cell for cell in registered_stage_a_cells(P0Config.registered())
    }
    monkeypatch.setattr(
        verdict_module,
        "iter_energy_records",
        lambda cell_dir: iter(_registered_records(cells[cell_dir.name])),
    )
    monkeypatch.setattr(
        verdict_module,
        "iter_snapshots",
        lambda _cell_dir: iter((_finite_snapshot(),)),
    )

    evidence = build_evidence(root, include_reproduction=False)

    assert evidence.deterministic_rerun_holds is False
    assert evaluate_stage_a(evidence).proceed is True


def test_nonfinite_reloaded_snapshot_is_a_fail_class_result(tmp_path, monkeypatch):
    root = write_registered_manifest_fixture(tmp_path, False)
    cells = {
        cell.slug: cell for cell in registered_stage_a_cells(P0Config.registered())
    }
    snapshot = _finite_snapshot()
    u = snapshot.state.u.copy()
    u[0, 0] = np.nan
    nonfinite = replace(snapshot, state=replace(snapshot.state, u=u))
    monkeypatch.setattr(
        verdict_module,
        "iter_energy_records",
        lambda cell_dir: iter(_registered_records(cells[cell_dir.name])),
    )
    monkeypatch.setattr(
        verdict_module, "iter_snapshots", lambda _cell_dir: iter((nonfinite,))
    )

    evidence = build_evidence(root, include_reproduction=False)

    assert evidence.all_values_finite is False
    assert decide_verdict(evidence) is Verdict.FAIL


def test_empty_required_energy_ledger_has_no_scientific_verdict(tmp_path):
    root = write_registered_manifest_fixture(tmp_path, False)

    with pytest.raises(ArtifactError, match="energy"):
        build_evidence(root, include_reproduction=False)
