"""E6 — P2 constitutive reduction forecast scoring."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core import run_p2mini  # noqa: E402
from forecast import ExperimentScore, ForecastJournal, check  # noqa: E402

OUT = ROOT / "results"


def main() -> int:
    kfs = [0.0, 0.05, 0.2, 0.5, 1.0, 2.0]
    print("E6 P2 reduction (closed box)")
    no_fb = {kf: run_p2mini(kf, feedback=False, driven=False, kf_damp=0.0) for kf in kfs}
    fb_cons = {kf: run_p2mini(kf, feedback=True, driven=False, kf_damp=0.0) for kf in kfs}
    fb_diss = {kf: run_p2mini(kf, feedback=True, driven=False, kf_damp=0.5) for kf in kfs}

    for kf in kfs:
        print(f"  k_f={kf:4.2f}  no_fb={no_fb[kf]:7.3f}  "
              f"cons={fb_cons[kf]:7.3f}  diss={fb_diss[kf]:7.3f}  "
              f"Δcons={fb_cons[kf]-no_fb[kf]:+7.3f}  Δdiss={fb_diss[kf]-no_fb[kf]:+7.3f}")

    deltas_cons = [fb_cons[kf] - no_fb[kf] for kf in kfs if kf > 0]
    deltas_diss = [fb_diss[kf] - no_fb[kf] for kf in kfs if kf > 0]
    mean_cons = sum(deltas_cons) / len(deltas_cons)
    mean_diss = sum(deltas_diss) / len(deltas_diss)

    f61 = all(d <= 1e-9 for d in deltas_cons)
    f62 = mean_cons < 0
    # F6.3: conservative less negative than dissipative
    f63 = mean_cons > mean_diss

    journal = ForecastJournal(OUT / "forecast_journal.json")
    checks = [
        check("F6.1", "all k_f>0 Δcons <= 0 (closed)", f61,
              {"deltas_cons": [round(x, 3) for x in deltas_cons]}, "<=0"),
        check("F6.2", "mean Δcons < 0 (P2 sign)", f62,
              round(mean_cons, 3), "<0"),
        check("F6.3", "conservative less negative than dissipative", f63,
              {"mean_cons": round(mean_cons, 3), "mean_diss": round(mean_diss, 3)},
              "mean_cons > mean_diss"),
    ]
    score = journal.record(ExperimentScore(
        name="E6_P2Reduction", checks=checks,
        method_version=journal.method_version,
        scored_at=datetime.now(timezone.utc).isoformat(),
    ))
    print(f"E6 score={score.score:.2f}  mean_Δcons={mean_cons:.3f}  mean_Δdiss={mean_diss:.3f}")
    result = {
        "name": "E6_P2Reduction",
        "kfs": kfs,
        "no_feedback": no_fb,
        "full_conservative": fb_cons,
        "full_dissipative": fb_diss,
        "mean_delta_cons": mean_cons,
        "mean_delta_diss": mean_diss,
        "score": score.to_dict(),
    }
    path = OUT / "results.json"
    if path.exists():
        payload = json.loads(path.read_text())
    else:
        payload = {"experiments": []}
    # replace or append E6
    payload["experiments"] = [e for e in payload.get("experiments", []) if e.get("name") != "E6_P2Reduction"]
    payload["experiments"].append(result)
    payload["generated"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {path}")
    return 0 if score.all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
