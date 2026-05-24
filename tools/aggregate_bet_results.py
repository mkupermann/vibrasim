"""Aggregate all BET-XXX result.json files into a single summary JSON.

Reads ~/.eqmod/bet/BET-*/result.json, extracts verdict + key measurements,
writes consolidated summary to ~/.eqmod/bet/summary.json.

Usage: python tools/aggregate_bet_results.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

BET_ROOT = Path.home() / ".eqmod/bet"
SUMMARY_PATH = BET_ROOT / "summary.json"


def _extract_measurements_from_log_tail(log_tail: str) -> dict:
    """Some BET-XXX result.jsons are dispatcher-wrapped with measurements embedded
    in log_tail string. Parse them out best-effort."""
    out = {}
    match = re.search(r'"measurements":\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)', log_tail, re.DOTALL)
    if match:
        # Just return raw fragment
        out["measurements_raw"] = match.group(1)[:2000]
    return out


def aggregate() -> dict:
    summary = {
        "by_id": {},
        "stats": {
            "total_iterations": 0,
            "passed": 0,
            "null": 0,
            "failed": 0,
        },
    }
    if not BET_ROOT.exists():
        return summary

    for bet_dir in sorted(BET_ROOT.glob("BET-*")):
        if not bet_dir.is_dir():
            continue
        result_file = bet_dir / "result.json"
        if not result_file.exists():
            continue
        try:
            data = json.loads(result_file.read_text())
        except Exception as e:
            summary["by_id"][bet_dir.name] = {"error": str(e)}
            continue

        verdict = data.get("verdict", "unknown")
        item_id = data.get("item_id", bet_dir.name)
        hypothesis = data.get("hypothesis", "")
        measurements = data.get("measurements")

        entry = {
            "verdict": verdict,
            "hypothesis_first_line": hypothesis.split("\n")[0] if hypothesis else "",
            "thresholds": data.get("thresholds", {}),
        }

        if measurements:
            # Take a compact subset of measurements
            compact = {}
            for k, v in measurements.items():
                if isinstance(v, (int, float, bool, str)):
                    compact[k] = v
                elif isinstance(v, list) and len(v) <= 10:
                    compact[k] = v
                elif isinstance(v, dict) and len(v) <= 10:
                    compact[k] = v
            entry["measurements"] = compact
        else:
            # Some BET-XXX have measurements embedded in log_tail
            log_tail = data.get("log_tail", "")
            if log_tail:
                entry.update(_extract_measurements_from_log_tail(log_tail))

        summary["by_id"][item_id] = entry
        summary["stats"]["total_iterations"] += 1
        if verdict == "passed":
            summary["stats"]["passed"] += 1
        elif verdict == "null":
            summary["stats"]["null"] += 1
        elif verdict == "failed":
            summary["stats"]["failed"] += 1

    return summary


def main():
    summary = aggregate()
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))
    s = summary["stats"]
    print(f"Aggregated {s['total_iterations']} iterations:")
    print(f"  passed: {s['passed']}")
    print(f"  null:   {s['null']}")
    print(f"  failed: {s['failed']}")
    print(f"Summary written to: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
