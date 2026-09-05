import json

import pytest

from vibrasim2.p0.energy import EnergyRecord
from vibrasim2.p1.input import (
    InputValidationError,
    trace_from_records,
    validate_input_result,
    validate_recomputed_peak,
)
from vibrasim2.p1.registration import P0_INPUT_DIGEST


def record(tick, h_matter, *, dt=0.5, total=2.0):
    return EnergyRecord(
        tick=tick,
        simulation_time=tick * dt,
        h_field=total - h_matter,
        h_matter=h_matter,
        h_coupling=0.0,
        h_total=total,
        p_field_from_coupling=0.0,
        p_matter_from_coupling=0.0,
        integral_field_power=0.0,
        integral_matter_power=0.0,
        finite=True,
    )


def test_declared_input_digest_must_match_fixed_p0(tmp_path):
    (tmp_path / "result.json").write_text(
        json.dumps({"scientific_digest": "0" * 64, "cell_metrics": {}}),
        encoding="utf-8",
    )
    with pytest.raises(InputValidationError, match="digest"):
        validate_input_result(tmp_path)


def test_trace_uses_initial_total_as_fixed_denominator():
    trace = trace_from_records(
        (record(0, 0.0), record(1, 0.5), record(2, 1.0)),
        expected_steps=2,
        dt=0.5,
    )
    assert trace.times.tolist() == [0.0, 0.5, 1.0]
    assert trace.values.tolist() == [0.0, 0.25, 0.5]


def test_trace_rejects_wrong_tick_sequence():
    with pytest.raises(InputValidationError, match="tick"):
        trace_from_records(
            (record(0, 0.0), record(2, 1.0)), expected_steps=1, dt=0.5
        )


def test_recomputed_peak_must_match_recorded_p0_value():
    result = {
        "scientific_digest": P0_INPUT_DIGEST,
        "cell_metrics": {"cell": {"a_b": 0.4}},
    }
    trace = trace_from_records(
        (record(0, 0.0), record(1, 1.0)), expected_steps=1, dt=0.5
    )
    with pytest.raises(InputValidationError, match="A_B"):
        validate_recomputed_peak("cell", trace, result)
