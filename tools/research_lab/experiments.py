"""Run the three charter-aligned experiments and score forecasts.

Usage:
  python tools/research_lab/experiments.py
"""
from __future__ import annotations

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core import (  # noqa: E402
    N_STEPS, run_competition, run_law_R_curve, run_lock_curve,
)
from forecast import ForecastJournal, check  # noqa: E402

OUT = ROOT / "results"
JOURNAL = OUT / "forecast_journal.json"


def slope(xs, ys) -> float:
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    if np.allclose(x, x[0]):
        return 0.0
    return float(np.polyfit(x, y, 1)[0])


def exp1_law_R(journal: ForecastJournal, on_progress=None) -> dict:
    chis = [-0.8, -0.5, -0.3, -0.15, 0.0, 0.15, 0.3, 0.5, 0.8, 1.2]
    t0 = time.perf_counter()
    values = run_law_R_curve(chis, on_step=on_progress)
    values_off = run_law_R_curve(chis, drive_on=False, on_step=on_progress)
    elapsed = time.perf_counter() - t0

    peak_i = int(np.argmax(values))
    peak_chi = chis[peak_i]
    left = slope(chis[: peak_i + 1], values[: peak_i + 1]) if peak_i > 0 else 0.0
    right = slope(chis[peak_i:], values[peak_i:]) if peak_i < len(chis) - 1 else 0.0
    spread = float(max(values) - min(values))
    spread_off = float(max(values_off) - min(values_off))

    checks = [
        check("F1.1", "peak |chi*| <= 0.5", abs(peak_chi) <= 0.5, peak_chi, "|chi*|<=0.5"),
        check("F1.2", "left>0 and right<0", (peak_i > 0 and left > 0) and (peak_i < len(chis)-1 and right < 0),
              {"left": left, "right": right}, "left>0, right<0"),
        check("F1.3", "peak-trough >= 5", spread >= 5.0, spread, ">=5"),
        check("F1.4", "drive-off collapses peak", spread_off < 2.0, spread_off, "<2"),
    ]
    score = journal.record(__import__("forecast").ExperimentScore(
        name="E1_LawR",
        checks=checks,
        method_version=journal.method_version,
        scored_at=datetime.now(timezone.utc).isoformat(),
    ))
    return {
        "name": "E1_LawR",
        "chis": chis,
        "S": values,
        "S_drive_off": values_off,
        "peak_chi": peak_chi,
        "left_slope": left,
        "right_slope": right,
        "spread": spread,
        "spread_drive_off": spread_off,
        "score": score.to_dict(),
        "elapsed_seconds": elapsed,
    }


def exp2_competition(journal: ForecastJournal, on_progress=None) -> dict:
    t0 = time.perf_counter()
    base = run_competition(feedback=True, swap=False, on_step=on_progress)
    cut = run_competition(feedback=False, swap=False, on_step=on_progress)
    swapped = run_competition(feedback=True, swap=True, on_step=on_progress)
    elapsed = time.perf_counter() - t0

    # F2.2: winner should be the one with higher capture_gain when feedback on
    # base: A has higher transport, B has higher capture. Winner predicted: B
    # if capture matters more under shared delivery — actually A draws more
    # transport share. The forecast says "winner raises own capture share".
    capture_share_A = base["captured_A"] / (base["captured_A"] + base["captured_B"] + 1e-12)
    capture_share_B = 1.0 - capture_share_A
    winner = base["winner"]
    winner_capture_share = capture_share_A if winner == "A" else capture_share_B

    checks = [
        check("F2.1", "feedback-on share gap >= 0.15", base["share_gap"] >= 0.15,
              base["share_gap"], ">=0.15"),
        check("F2.2", "winner has higher captured income share",
              winner_capture_share > 0.5,
              {"winner": winner, "capture_share_winner": round(winner_capture_share, 4),
               "captured_A": round(base["captured_A"], 4),
               "captured_B": round(base["captured_B"], 4)},
              "winner income share > 0.5"),
        check("F2.3", "cut feedback shrinks gap < 0.08", cut["share_gap"] < 0.08,
              cut["share_gap"], "<0.08"),
        check("F2.4", "swap flips ranking",
              (base["winner"] != "tie" and swapped["winner"] != "tie"
               and base["winner"] != swapped["winner"]),
              {"base": base["winner"], "swap": swapped["winner"]},
              "ranking flips"),
    ]
    score = journal.record(__import__("forecast").ExperimentScore(
        name="E2_Competition",
        checks=checks,
        method_version=journal.method_version,
        scored_at=datetime.now(timezone.utc).isoformat(),
    ))
    return {
        "name": "E2_Competition",
        "feedback_on": {k: base[k] for k in base if k != "history"},
        "feedback_off": {k: cut[k] for k in cut if k != "history"},
        "swapped": {k: swapped[k] for k in swapped if k != "history"},
        "history_on_tail": base["history"][::50],
        "score": score.to_dict(),
        "elapsed_seconds": elapsed,
    }


def exp3_lock(journal: ForecastJournal, on_progress=None) -> dict:
    kfs = [0.0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2]
    t0 = time.perf_counter()
    closed = run_lock_curve(kfs, driven=False, dissipative=True, on_step=on_progress)
    driven = run_lock_curve(kfs, driven=True, dissipative=True, on_step=on_progress)
    conservative = run_lock_curve(kfs, driven=True, dissipative=False, on_step=on_progress)
    elapsed = time.perf_counter() - t0

    # F3.1: S(k_f) - S(0) <= 0 for all k_f > 0
    deltas_closed = [closed[i] - closed[0] for i in range(1, len(kfs))]
    deltas_driven = [driven[i] - driven[0] for i in range(1, len(kfs))]
    f31 = all(d <= 1e-9 for d in deltas_closed + deltas_driven)

    # F3.2: closed box drop >= driven drop
    drop_closed = closed[0] - closed[-1]
    drop_driven = driven[0] - driven[-1]
    f32 = drop_closed >= drop_driven - 1e-9

    # F3.3: conservative-only spring is NOT a pure lock — it should be
    # less damaging than dissipative at the same k_f.
    cons_vs_diss = [conservative[i] - driven[i] for i in range(len(kfs))]
    f33 = any(d >= 1.0 for d in cons_vs_diss[1:])

    checks = [
        check("F3.1", "lock drop <= 0 vs no-lock", f31,
              {"closed_deltas": deltas_closed, "driven_deltas": deltas_driven},
              "all deltas <= 0"),
        check("F3.2", "closed-box drop >= driven drop", f32,
              {"drop_closed": drop_closed, "drop_driven": drop_driven},
              "closed >= driven"),
        check("F3.3", "conservative S >= dissipative at some k_f>0", f33,
              {"cons_minus_diss": [round(x, 3) for x in cons_vs_diss]},
              "exists k_f>0 with cons-diss >= 1"),
    ]
    score = journal.record(__import__("forecast").ExperimentScore(
        name="E3_Lock",
        checks=checks,
        method_version=journal.method_version,
        scored_at=datetime.now(timezone.utc).isoformat(),
    ))
    return {
        "name": "E3_Lock",
        "kfs": kfs,
        "S_closed_dissipative": closed,
        "S_driven_dissipative": driven,
        "S_driven_conservative": conservative,
        "drop_closed": drop_closed,
        "drop_driven": drop_driven,
        "score": score.to_dict(),
        "elapsed_seconds": elapsed,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    journal = ForecastJournal(JOURNAL)

    def prog(frac, label):
        # live console progress; live_lab reads the JSON files instead
        pass

    print("Running E1 Law R ...")
    r1 = exp1_law_R(journal, prog)
    print(f"  score={r1['score']['score']:.2f} peak={r1['peak_chi']:+.2f} "
          f"spread={r1['spread']:.1f}")

    print("Running E2 Competition ...")
    r2 = exp2_competition(journal, prog)
    print(f"  score={r2['score']['score']:.2f} "
          f"on_gap={r2['feedback_on']['share_gap']:.3f} "
          f"off_gap={r2['feedback_off']['share_gap']:.3f}")

    print("Running E3 Lock ...")
    r3 = exp3_lock(journal, prog)
    print(f"  score={r3['score']['score']:.2f} "
          f"drop_closed={r3['drop_closed']:.1f}")

    payload = {
        "claim": "organisation must change the field that funds it",
        "generated": datetime.now(timezone.utc).isoformat(),
        "experiments": [r1, r2, r3],
        "method_version": journal.method_version,
        "method_notes": journal.method_notes,
    }
    (OUT / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # markdown summary
    lines = [
        "# Research lab results",
        "",
        f"Generated {payload['generated']}",
        "",
    ]
    for exp in payload["experiments"]:
        s = exp["score"]
        lines.append(f"## {exp['name']} — score {s['score']:.2f}")
        for c in s["checks"]:
            mark = "PASS" if c["passed"] else "MISS"
            lines.append(f"- [{mark}] `{c['id']}` {c['description']}: observed={c['observed']}")
        if s.get("notes"):
            lines.append(f"- Forecast note: {s['notes']}")
        lines.append("")
    (OUT / "results.md").write_text("\n".join(lines), encoding="utf-8")

    overall = np.mean([e["score"]["score"] for e in payload["experiments"]])
    print(f"\nOverall forecast score: {overall:.2f}")
    print(f"Method version: {journal.method_version}")
    print(f"Wrote {OUT / 'results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
