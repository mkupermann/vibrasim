"""Non-bypassable command-line boundary for the registered V2-P0 run."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .artifacts import ArtifactError
from .budget import BudgetError
from .runner import (
    ObservationSinkFactory,
    PostRunBudgetError,
    RegistrationError,
    run_registered_p0,
)


def resolve_observer_factory(
    observe: bool, output_dir: Path
) -> ObservationSinkFactory | None:
    if not observe:
        return None
    from vibrasim2.viewer_process import make_registered_observer_factory

    return make_registered_observer_factory(output_dir)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vibrasim2-p0",
        description="Execute the frozen registered V2-P0 reciprocal-channel verifier.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="start the registered V2-P0 matrix")
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument(
        "--observe",
        action="store_true",
        help="attach the optional lossy observer without changing scientific identity",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_dir = args.output_dir.resolve()
    try:
        observer_factory = resolve_observer_factory(args.observe, output_dir)
    except Exception as error:  # noqa: BLE001 - observer setup has no verdict
        print(f"NO SCIENTIFIC VERDICT: {error}", file=sys.stderr)
        return 1
    try:
        if observer_factory is None:
            result = run_registered_p0(output_dir)
        else:
            result = run_registered_p0(output_dir, observer_factory=observer_factory)
    except PostRunBudgetError as error:
        print(
            "SCIENTIFIC VERDICT RECORDED — BUDGET STOP: "
            f"{error.verdict.value} at {error.result_path} ({error.ledger_status})",
            file=sys.stderr,
        )
        return 1
    except (
        ArtifactError,
        BudgetError,
        RegistrationError,
        OSError,
        ValueError,
    ) as error:
        print(f"NO SCIENTIFIC VERDICT: {error}", file=sys.stderr)
        return 1
    print(
        f"VERDICT {result.verdict.value}\nSCIENTIFIC DIGEST {result.scientific_digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
