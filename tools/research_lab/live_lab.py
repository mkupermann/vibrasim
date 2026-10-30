"""Real-time research lab server.

Serves a scientific dashboard and streams ACTUAL experiment state as the
integrator runs. No mocked series. Progress is completed_steps/total_steps.

Usage:
  python tools/research_lab/live_lab.py
  open http://127.0.0.1:8765
"""
from __future__ import annotations

import json
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core import (  # noqa: E402
    N_STEPS, make_state, run_competition, step_law_R, step_law_L,
    _structured_pulse,
)
from forecast import ForecastJournal, ExperimentScore, check  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765
OUT = ROOT / "results"
LOCK = threading.Lock()
STATE: dict = {
    "phase": "starting",
    "message": "boot",
    "progress": 0.0,
    "current": "",
    "experiments": [],
    "live": {},
    "log": [],
    "started": datetime.now(timezone.utc).isoformat(),
    "method_version": 1,
    "finished": False,
    "cycle": 0,
}

# 3D scene grid (matches index.html field plane)
FN = 24


def emit_scene(sites, bond_live: bool, bond=(0, 1), field=None, t: float = 0.0) -> None:
    """Publish 3D scene payload. sites: list of dicts x,y,z,energy,reservoir."""
    if field is None:
        # analytic field bump under the site pair — replaced by live values when present
        field = []
        for j in range(FN):
            for i in range(FN):
                x = (i / (FN - 1) - 0.5) * 24
                z = (j / (FN - 1) - 0.5) * 24
                h = 0.0
                for s in sites:
                    dx, dz = x - s["x"], z - s["z"]
                    h += s.get("energy", 0.3) * np.exp(-(dx * dx + dz * dz) / 18.0)
                field.append(float(min(1.5, h)))
    set_live(scene={
        "sites": sites,
        "bond": {"a": bond[0], "b": bond[1], "live": bool(bond_live)},
        "field": field,
        "t": float(t),
    })


def log(msg: str) -> None:
    with LOCK:
        STATE["log"].append({
            "t": datetime.now(timezone.utc).isoformat(),
            "msg": msg,
        })
        STATE["log"] = STATE["log"][-200:]
        STATE["message"] = msg


def set_live(**kwargs) -> None:
    with LOCK:
        STATE["live"].update(kwargs)


def set_progress(frac: float, current: str, phase: str) -> None:
    # Map phase-local frac into overall cycle progress so the bar always moves.
    bands = {
        "E1_LawR": (0.00, 0.40),
        "E2_Competition": (0.40, 0.70),
        "E3_Lock": (0.70, 1.00),
    }
    lo, hi = bands.get(phase, (0.0, 1.0))
    with LOCK:
        STATE["progress"] = float(lo + (hi - lo) * max(0.0, min(1.0, frac)))
        STATE["current"] = current
        STATE["phase"] = phase


def slope(xs, ys) -> float:
    x = np.asarray(xs, float)
    y = np.asarray(ys, float)
    if np.allclose(x, x[0]):
        return 0.0
    return float(np.polyfit(x, y, 1)[0])


def run_e1(journal: ForecastJournal) -> dict:
    """Law R resonance — stream S(chi) as it is computed."""
    chis = [-0.8, -0.5, -0.3, -0.15, 0.0, 0.15, 0.3, 0.5, 0.8, 1.2]
    seeds = list(range(5))
    values = []
    values_off = []
    total_units = len(chis) * len(seeds) * 2
    unit = 0

    for drive_on, bucket in ((True, values), (False, values_off)):
        label = "drive-on" if drive_on else "drive-off"
        for chi in chis:
            acc = []
            for seed in seeds:
                s = make_state(seed)
                for step in range(N_STEPS):
                    step_law_R(s, chi, drive_on=drive_on)
                    if step % 20 == 0 or step == N_STEPS - 1:
                        frac = (unit + (step + 1) / N_STEPS) / total_units
                        set_progress(frac, f"E1 Law R chi={chi:+.2f} {label} seed={seed}",
                                     "E1_LawR")
                        set_live(
                            e1_chis=chis,
                            e1_S=values.copy(),
                            e1_S_off=values_off.copy(),
                            e1_current_chi=chi,
                            e1_seed=seed,
                            e1_live_bond_time=s.bond_time,
                            e1_captured=s.captured,
                            e1_label=label,
                            e1_step=step,
                            e1_steps_total=N_STEPS,
                        )
                        emit_scene(
                            sites=[
                                {"x": -2.8, "y": 1.0 + float(s.u[0]), "z": 0.0,
                                 "energy": float(abs(s.u[0])) + 0.2,
                                 "reservoir": float(s.res[0])},
                                {"x": 2.8, "y": 1.0 + float(s.u[1]), "z": 0.0,
                                 "energy": float(abs(s.u[1])) + 0.2,
                                 "reservoir": float(s.res[1])},
                            ],
                            bond_live=s.bond_age >= 0.0,
                            bond=(0, 1),
                            t=s.t,
                        )
                acc.append(s.bond_time)
                unit += 1
            bucket.append(float(np.mean(acc)))
            log(f"E1 {label} chi={chi:+.2f}  S={bucket[-1]:.3f}")
            set_live(e1_S=values.copy(), e1_S_off=values_off.copy())

    peak_i = int(np.argmax(values))
    peak_chi = chis[peak_i]
    left = slope(chis[: peak_i + 1], values[: peak_i + 1]) if peak_i > 0 else 0.0
    right = slope(chis[peak_i:], values[peak_i:]) if peak_i < len(chis) - 1 else 0.0
    spread = float(max(values) - min(values))
    spread_off = float(max(values_off) - min(values_off))

    checks = [
        check("F1.1", "peak |chi*| <= 0.5", abs(peak_chi) <= 0.5, peak_chi, "|chi*|<=0.5"),
        check("F1.2", "left>0 and right<0",
              (peak_i > 0 and left > 0) and (peak_i < len(chis) - 1 and right < 0),
              {"left": round(left, 4), "right": round(right, 4)}, "left>0, right<0"),
        check("F1.3", "peak-trough >= 5", spread >= 5.0, round(spread, 3), ">=5"),
        check("F1.4", "drive-off collapses peak", spread_off < 2.0, round(spread_off, 3), "<2"),
    ]
    score = journal.record(ExperimentScore(
        name="E1_LawR", checks=checks, method_version=journal.method_version,
        scored_at=datetime.now(timezone.utc).isoformat(),
    ))
    result = {
        "name": "E1_LawR", "chis": chis, "S": values, "S_drive_off": values_off,
        "peak_chi": peak_chi, "left_slope": left, "right_slope": right,
        "spread": spread, "spread_drive_off": spread_off,
        "score": score.to_dict(),
    }
    with LOCK:
        STATE["experiments"].append(result)
        STATE["method_version"] = journal.method_version
    return result


def run_e2(journal: ForecastJournal) -> dict:
    """Competition under shared budget (uses core.run_competition)."""
    results = {}
    variants = [
        ("feedback_on", True, False),
        ("feedback_off", False, False),
        ("swapped", True, True),
    ]
    for idx, (name, feedback, swap) in enumerate(variants):
        def on_step(frac, label, _idx=idx, _name=name):
            set_progress((_idx + frac) / len(variants), label, "E2_Competition")
            set_live(e2_variant=_name)

        summary = run_competition(feedback=feedback, swap=swap, on_step=on_step)
        # strip heavy history from the scored summary copy
        results[name] = {k: summary[k] for k in summary if k != "history"}
        hist = summary.get("history", [])
        set_live(
            e2_variant=name,
            e2_t=summary.get("A_bond_time", 0),
            e2_shared=hist[-1]["shared"] if hist else 0,
            e2_S_A=summary["A_bond_time"],
            e2_S_B=summary["B_bond_time"],
            e2_res_A=hist[-1].get("res_A", 0) if hist else 0,
            e2_res_B=hist[-1].get("res_B", 0) if hist else 0,
            e2_live_A=hist[-1].get("live_A", 0) if hist else 0,
            e2_live_B=hist[-1].get("live_B", 0) if hist else 0,
            e2_history=hist[::20],
        )
        log(f"E2 {name}: winner={summary['winner']} gap={summary['share_gap']:.3f}")

    base = results["feedback_on"]
    cut = results["feedback_off"]
    swapped = results["swapped"]
    cap_total = base["captured_A"] + base["captured_B"] + 1e-12
    cap_share_A = base["captured_A"] / cap_total
    winner = base["winner"]
    winner_cap = cap_share_A if winner == "A" else 1.0 - cap_share_A

    checks = [
        check("F2.1", "feedback-on share gap >= 0.15", base["share_gap"] >= 0.15,
              round(base["share_gap"], 4), ">=0.15"),
        check("F2.2", "winner has higher captured income share", winner_cap > 0.5,
              {"winner": winner, "winner_capture_share": round(winner_cap, 4)},
              ">0.5"),
        check("F2.3", "cut feedback shrinks gap < 0.08", cut["share_gap"] < 0.08,
              round(cut["share_gap"], 4), "<0.08"),
        check("F2.4", "swap flips ranking",
              base["winner"] != swapped["winner"] and base["winner"] != "tie",
              {"base": base["winner"], "swap": swapped["winner"]}, "flips"),
    ]
    score = journal.record(ExperimentScore(
        name="E2_Competition", checks=checks, method_version=journal.method_version,
        scored_at=datetime.now(timezone.utc).isoformat(),
    ))
    result = {
        "name": "E2_Competition",
        "feedback_on": base, "feedback_off": cut, "swapped": swapped,
        "score": score.to_dict(),
    }
    with LOCK:
        STATE["experiments"].append(result)
        STATE["method_version"] = journal.method_version
    return result


def run_e3(journal: ForecastJournal) -> dict:
    """Lock sign."""
    kfs = [0.0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2]
    seeds = list(range(5))

    def curve(driven: bool, dissipative: bool, tag: str, tag_i: int) -> list[float]:
        out = []
        n_curves = 3
        for kf in kfs:
            acc = []
            for seed in seeds:
                s = make_state(seed) if driven else _structured_pulse(seed)
                for step in range(N_STEPS):
                    step_law_L(s, kf, driven=driven, dissipative=dissipative)
                    if step % 20 == 0 or step == N_STEPS - 1:
                        frac = (tag_i + (len(out) + (step + 1) / N_STEPS) / len(kfs)) / n_curves
                        set_progress(
                            min(1.0, frac),
                            f"E3 Lock {tag} k_f={kf:.2f} seed={seed}",
                            "E3_Lock",
                        )
                        set_live(
                            e3_kfs=kfs,
                            e3_closed=curves.get("closed", []),
                            e3_driven=curves.get("driven", []),
                            e3_cons=curves.get("cons", []),
                            e3_current=kf,
                            e3_live=s.bond_time,
                            e3_tag=tag,
                        )
                acc.append(s.bond_time)
            out.append(float(np.mean(acc)))
            log(f"E3 {tag} k_f={kf:.2f} S={out[-1]:.3f}")
            curves[tag] = out
            set_live(e3_closed=curves.get("closed", []),
                     e3_driven=curves.get("driven", []),
                     e3_cons=curves.get("cons", []))
        return out

    curves: dict = {}
    closed = curve(False, True, "closed", 0)
    driven = curve(True, True, "driven", 1)
    cons = curve(True, False, "cons", 2)

    deltas = [closed[i] - closed[0] for i in range(1, len(kfs))] + \
             [driven[i] - driven[0] for i in range(1, len(kfs))]
    f31 = all(d <= 1e-9 for d in deltas)
    drop_c = closed[0] - closed[-1]
    drop_d = driven[0] - driven[-1]
    f32 = drop_c >= drop_d - 1e-9
    cons_d = [cons[i] - driven[i] for i in range(len(kfs))]
    f33 = any(d >= 1.0 for d in cons_d[1:])

    checks = [
        check("F3.1", "lock deltas <= 0", f31, {"max_delta": round(max(deltas), 4)}, "<=0"),
        check("F3.2", "closed drop >= driven", f32,
              {"closed": round(drop_c, 3), "driven": round(drop_d, 3)}, "closed>=driven"),
        check("F3.3", "conservative S >= dissipative at some k_f>0", f33,
              {"cons_minus_diss": [round(x, 3) for x in cons_d]}, "cons-diss >= 1"),
    ]
    score = journal.record(ExperimentScore(
        name="E3_Lock", checks=checks, method_version=journal.method_version,
        scored_at=datetime.now(timezone.utc).isoformat(),
    ))
    result = {
        "name": "E3_Lock", "kfs": kfs,
        "S_closed_dissipative": closed,
        "S_driven_dissipative": driven,
        "S_driven_conservative": cons,
        "score": score.to_dict(),
    }
    with LOCK:
        STATE["experiments"].append(result)
        STATE["method_version"] = journal.method_version
    return result


def runner() -> None:
    """Continuous lab loop: never parks at 100%; each cycle re-runs the suite."""
    OUT.mkdir(parents=True, exist_ok=True)
    journal = ForecastJournal(OUT / "forecast_journal.json")
    cycle = 0
    log("Research lab runner start (continuous loop)")
    while True:
        cycle += 1
        with LOCK:
            STATE["cycle"] = cycle
            STATE["finished"] = False
            STATE["progress"] = 0.0
            STATE["experiments"] = []
            STATE["overall_score"] = None
        log(f"—— cycle {cycle} start ——")
        set_progress(0.0, f"cycle {cycle} / E1", "E1_LawR")
        try:
            r1 = run_e1(journal)
            r2 = run_e2(journal)
            r3 = run_e3(journal)
            payload = {
                "claim": "organisation must change the field that funds it",
                "generated": datetime.now(timezone.utc).isoformat(),
                "cycle": cycle,
                "experiments": [r1, r2, r3],
                "method_version": journal.method_version,
                "method_notes": journal.method_notes,
            }
            (OUT / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
            overall = float(np.mean([e["score"]["score"] for e in payload["experiments"]]))
            log(f"cycle {cycle} DONE score={overall:.2f} method_v{journal.method_version}")
            with LOCK:
                STATE["overall_score"] = overall
                STATE["progress"] = 1.0
                STATE["phase"] = "cycle_complete"
                STATE["finished"] = True
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR cycle {cycle}: {type(exc).__name__}: {exc}")
            with LOCK:
                STATE["phase"] = "error"
        # brief pause so the dashboard can show 100% of THIS cycle, then restart
        time.sleep(1.5)
        with LOCK:
            STATE["finished"] = False
            STATE["progress"] = 0.0


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quiet
        return

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = (ROOT / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/state"):
            with LOCK:
                blob = json.dumps(STATE).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(blob)))
            self.end_headers()
            self.wfile.write(blob)
        else:
            self.send_response(404)
            self.end_headers()


def main() -> None:
    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Live research lab on http://{HOST}:{PORT}")
    print("Dashboard shows only values written by the running integrator.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstop")
        server.shutdown()


if __name__ == "__main__":
    main()
