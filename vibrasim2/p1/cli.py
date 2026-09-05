"""Guarded command-line boundary for the registered P1 audit."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from .artifacts import ArtifactError, write_audit
from .audit import audit_registered_run
from .budget import (
    P1BudgetError,
    assert_p1_budget_allows_audit,
    finish_p1_interval,
    start_p1_interval,
)
from .input import InputValidationError
from .registration import P1_BUDGET_PATH, P1_OUTPUT_ROOT

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class CliError(ValueError):
    """Raised before analysis when CLI path constraints are not satisfied."""


def _redirected(path: Path) -> bool:
    for component in (path, *path.parents):
        if not os.path.lexists(component):
            continue
        try:
            if component.is_symlink() or (
                hasattr(component, "is_junction") and component.is_junction()
            ):
                return True
        except OSError:
            return True
    return False


def validate_output_path(output_dir: str | Path) -> Path:
    root = P1_OUTPUT_ROOT
    if not root.is_absolute():
        root = REPOSITORY_ROOT / root
    root = root.absolute()
    output = Path(output_dir).absolute()
    if output.exists() or os.path.lexists(output):
        raise CliError("P1 output path must not exist")
    if output.parent != root:
        raise CliError("P1 output must be a direct child of the fixed output root")
    if _redirected(root) or _redirected(output):
        raise CliError("redirected P1 output is forbidden")
    return output


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vibrasim2-p1", description="Audit the fixed P0 time structure."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--input-dir", type=Path, required=True)
    audit.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    lease = None
    ledger = P1_BUDGET_PATH
    if not ledger.is_absolute():
        ledger = REPOSITORY_ROOT / ledger
    try:
        output = validate_output_path(args.output_dir)
        assert_p1_budget_allows_audit(ledger)
        lease = start_p1_interval(
            ledger, "scientific_audit", "v2-p1-mechanism-audit"
        )
        result = audit_registered_run(args.input_dir.absolute())
        digest = write_audit(output, result)
        finish_p1_interval(ledger, lease, "completed")
    except (ArtifactError, CliError, InputValidationError, P1BudgetError, OSError) as error:
        if lease is not None:
            try:
                finish_p1_interval(ledger, lease, "failed")
            except P1BudgetError:
                pass
        print(f"NO P1 DIAGNOSTIC: {error}", file=sys.stderr)
        return 1
    print(f"P1 OUTCOME {result.outcome.value}\nAUDIT DIGEST {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
