"""Command line entry point for the single registered V2-P2 run."""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

from .budget import finish_run, start_run
from .registration import P2_BUDGET_PATH
from .runner import run_registered_p2
from .viewer import make_p2_observer_factory


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    run = subcommands.add_parser("run", help="execute the single frozen P2 matrix")
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("--observe", action="store_true")
    args = parser.parse_args(argv)
    repository_root = Path(__file__).resolve().parents[2]
    run_id = f"v2-p2-{uuid.uuid4().hex}"
    lease = None
    try:
        lease = start_run(repository_root / P2_BUDGET_PATH, repository_root, run_id)
        observer_factory = (
            make_p2_observer_factory(args.output_dir) if args.observe else None
        )
        result = run_registered_p2(
            args.output_dir,
            observer_factory=observer_factory,
            run_id=run_id,
        )
        finish_run(lease, completed=True)
    except Exception as exc:
        if lease is not None:
            try:
                finish_run(lease, completed=False)
            except Exception:
                pass
        print(f"V2-P2 run failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"V2-P2 {result.verdict.value} digest={result.scientific_digest} "
        f"output={result.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
