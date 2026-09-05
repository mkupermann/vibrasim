"""Strict read-only loading of the fixed P0 energy traces."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from vibrasim2.p0.artifacts import iter_energy_records
from vibrasim2.p0.energy import EnergyRecord

from .registration import P0_INPUT_DIGEST
from .types import SourcePairs, Trace, TracePair

SOURCES = ((4, 16), (16, 4), (4, 4))


class InputValidationError(ValueError):
    """Raised before analysis when fixed P0 input is not exact and complete."""


def _is_redirected(path: Path) -> bool:
    resolved = path.absolute()
    for component in (resolved, *resolved.parents):
        try:
            if component.is_symlink() or (
                hasattr(component, "is_junction") and component.is_junction()
            ):
                return True
        except OSError:
            return True
    return False


def validate_input_result(root: str | Path) -> dict[str, Any]:
    path = Path(root)
    if _is_redirected(path):
        raise InputValidationError("redirected P0 input is forbidden")
    try:
        result = json.loads((path / "result.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise InputValidationError("cannot read P0 result.json") from error
    if not isinstance(result, dict) or result.get("scientific_digest") != P0_INPUT_DIGEST:
        raise InputValidationError("P0 input digest mismatch")
    if result.get("verdict") != "NULL" or not isinstance(
        result.get("cell_metrics"), dict
    ):
        raise InputValidationError("P0 result is not the fixed completed NULL")
    return result


def trace_from_records(
    records: Iterable[EnergyRecord], *, expected_steps: int, dt: float
) -> Trace:
    values = tuple(records)
    if len(values) != expected_steps + 1:
        raise InputValidationError("energy tick count mismatch")
    if not values or values[0].h_total is None:
        raise InputValidationError("initial total energy is missing")
    denominator = float(values[0].h_total)
    if not math.isfinite(denominator) or denominator <= 0:
        raise InputValidationError("initial total energy must be positive and finite")
    times: list[float] = []
    ratios: list[float] = []
    for tick, record in enumerate(values):
        if record.tick != tick:
            raise InputValidationError("energy tick sequence mismatch")
        expected_time = tick * dt
        if not math.isclose(
            float(record.simulation_time), expected_time, rel_tol=0, abs_tol=1e-12
        ):
            raise InputValidationError("energy timestamp mismatch")
        if not record.finite or record.h_matter is None:
            raise InputValidationError("energy trace contains a non-finite value")
        ratio = float(record.h_matter) / denominator
        if not math.isfinite(ratio):
            raise InputValidationError("matter-energy ratio is non-finite")
        times.append(expected_time)
        ratios.append(ratio)
    return Trace(np.asarray(times, dtype=np.float64), np.asarray(ratios, dtype=np.float64))


def validate_recomputed_peak(slug: str, trace: Trace, result: dict[str, Any]) -> None:
    try:
        recorded = float(result["cell_metrics"][slug]["a_b"])
    except (KeyError, TypeError, ValueError) as error:
        raise InputValidationError(f"missing recorded A_B for {slug}") from error
    if not math.isclose(float(trace.values.max()), recorded, rel_tol=0, abs_tol=1e-12):
        raise InputValidationError(f"recomputed A_B mismatch for {slug}")


def _slug(purpose: str, topology: str, source: tuple[int, int], dt: str) -> str:
    return f"{purpose}-full-{topology}-x{source[0]}-y{source[1]}-dt{dt}"


def _load(root: Path, slug: str, *, steps: int, dt: float, result: dict[str, Any]) -> Trace:
    try:
        trace = trace_from_records(
            iter_energy_records(root / slug), expected_steps=steps, dt=dt
        )
    except Exception as error:
        if isinstance(error, InputValidationError):
            raise
        raise InputValidationError(f"cannot load required trace: {slug}") from error
    validate_recomputed_peak(slug, trace, result)
    return trace


def load_registered_pairs(root: str | Path) -> tuple[SourcePairs, ...]:
    path = Path(root)
    result = validate_input_result(path)
    pairs: list[SourcePairs] = []
    for source in SOURCES:
        coarse = {
            topology: _load(
                path,
                _slug("primary", topology, source, "0.05"),
                steps=2000,
                dt=0.05,
                result=result,
            )
            for topology in ("cycle", "branch")
        }
        convergence = {
            topology: _load(
                path,
                _slug("convergence", topology, source, "0.025"),
                steps=4000,
                dt=0.025,
                result=result,
            )
            for topology in ("cycle", "branch")
        }
        pairs.append(
            SourcePairs(
                source,
                TracePair(coarse["cycle"], coarse["branch"]),
                TracePair(convergence["cycle"], convergence["branch"]),
            )
        )
    return tuple(pairs)
