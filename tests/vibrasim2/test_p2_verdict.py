from dataclasses import replace

from vibrasim2.p2.fixtures import registered_cells
from vibrasim2.p2.trajectory import TimedBondEvent
from vibrasim2.p2.types import P2Arm, P2Config, P2Purpose, Verdict
from vibrasim2.p2.verdict import CellOutcome, build_evidence, decide_verdict


def outcomes(*, primary_contrast=30.0, convergence_contrast=30.0):
    config = P2Config.registered()
    values = []
    full_each = 40.0
    control_each = full_each - primary_contrast / 3
    conv_full_each = 40.0
    conv_control_each = conv_full_each - convergence_contrast / 3
    events = (TimedBondEvent(1, 0.025, "formed", 0, 1),)
    for cell in registered_cells(config):
        if cell.purpose is P2Purpose.PRIMARY:
            bond_time = {
                P2Arm.FULL: full_each,
                P2Arm.NO_CAPTURE: 0.0,
                P2Arm.NO_FIELD_FEEDBACK: control_each,
            }[cell.arm]
        elif cell.purpose is P2Purpose.CONVERGENCE:
            bond_time = conv_full_each if cell.arm is P2Arm.FULL else conv_control_each
        else:
            bond_time = full_each
        values.append(
            CellOutcome(
                cell=cell,
                bond_time=bond_time,
                max_absolute_energy_drift=1e-5,
                finite=True,
                events=events if cell.arm is P2Arm.FULL else (),
            )
        )
    return config, tuple(values)


def test_all_frozen_gates_produce_pass():
    config, values = outcomes()
    evidence = build_evidence(values, config)

    assert evidence.primary_contrast == 30.0
    assert evidence.scientific_contrast_holds
    assert evidence.negative_control_holds
    assert evidence.convergence_holds
    assert evidence.reproduction_holds
    assert evidence.energy_holds
    assert decide_verdict(evidence) is Verdict.PASS


def test_valid_below_threshold_is_null_not_inconclusive():
    config, values = outcomes(primary_contrast=29.9, convergence_contrast=29.9)
    evidence = build_evidence(values, config)

    assert decide_verdict(evidence) is Verdict.NULL


def test_numerical_failure_is_inconclusive_even_when_scientific_gate_passes():
    config, values = outcomes(primary_contrast=40.0, convergence_contrast=20.0)
    evidence = build_evidence(values, config)

    assert not evidence.convergence_holds
    assert decide_verdict(evidence) is Verdict.INCONCLUSIVE


def test_reproduction_requires_exact_events_and_bond_time_tolerance():
    config, values = outcomes()
    index = next(
        i for i, value in enumerate(values)
        if value.cell.purpose is P2Purpose.REPRODUCTION
    )
    changed = list(values)
    changed[index] = replace(changed[index], bond_time=changed[index].bond_time + 2e-12)

    evidence = build_evidence(tuple(changed), config)

    assert not evidence.reproduction_holds
    assert decide_verdict(evidence) is Verdict.INCONCLUSIVE


def test_artifact_failure_has_fail_precedence():
    config, values = outcomes()
    evidence = replace(build_evidence(values, config), artifact_valid=False)

    assert decide_verdict(evidence) is Verdict.FAIL


def test_missing_or_duplicate_cell_is_artifact_failure():
    config, values = outcomes()

    evidence = build_evidence(values[:-1], config)

    assert not evidence.artifact_valid
    assert decide_verdict(evidence) is Verdict.FAIL
