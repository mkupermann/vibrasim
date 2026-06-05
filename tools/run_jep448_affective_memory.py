"""JEP-448 — affective memory enhancement: facts whose entity carries strong valence are stored with
a higher binding weight, so they survive interference better than neutral facts ("strong-energy
connections grow stronger" — Michael; Cahill-McGaugh emotional memory). Uses the existing
add_fact(weight=) lever. Pre-registered bars in docs/amendments/jep448_affective_memory.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import SubstrateMemory

K = 1.0
N_EMO, N_NEU, N_INTERF = 30, 30, 300


def _build(seed, boost):
    rng = np.random.default_rng(seed)
    sm = SubstrateMemory(D=4096, module_cap=100000)     # force a single, heavily-superposed module
    emo, neu = [], []
    for i in range(N_EMO):
        e, v = f"emo{i}", f"eval{i}"
        val = 2.0 if rng.integers(2) == 0 else -2.0
        sm.valence[e] = val
        w = (1.0 + K * abs(val)) if boost else 1.0
        sm.add_fact(e, "fact", v, weight=w)
        emo.append((e, v))
    for i in range(N_NEU):
        e, v = f"neu{i}", f"nval{i}"
        sm.add_fact(e, "fact", v, weight=1.0)
        neu.append((e, v))
    for i in range(N_INTERF):                            # interference load
        sm.add_fact(f"intf{i}", "fact", f"ival{i}", weight=1.0)
    return sm, emo, neu


def _recall(sm, items):
    ok = 0
    for e, v in items:
        got, _ = sm.query(e, "fact")
        ok += (got == v)
    return ok / len(items)


def run(seed):
    sm_b, emo_b, neu_b = _build(seed, boost=True)
    sm_c, emo_c, neu_c = _build(seed, boost=False)
    return dict(
        boost_emo=_recall(sm_b, emo_b), boost_neu=_recall(sm_b, neu_b),
        ctrl_emo=_recall(sm_c, emo_c), ctrl_neu=_recall(sm_c, neu_c),
    )


if __name__ == "__main__":
    print("=== JEP-448: affective memory enhancement (strong-energy facts survive interference) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: BOOST emo={R[s]['boost_emo']:.3f} neu={R[s]['boost_neu']:.3f} | "
              f"CONTROL emo={R[s]['ctrl_emo']:.3f} neu={R[s]['ctrl_neu']:.3f}", flush=True)

    J448a = all(R[s]['boost_emo'] >= R[s]['boost_neu'] + 0.15 for s in seeds)
    J448b = all(abs(R[s]['ctrl_emo'] - R[s]['ctrl_neu']) <= 0.05 for s in seeds)
    boost_overall = {s: (R[s]['boost_emo'] + R[s]['boost_neu']) / 2 for s in seeds}
    ctrl_overall = {s: (R[s]['ctrl_emo'] + R[s]['ctrl_neu']) / 2 for s in seeds}
    J448c = all(boost_overall[s] >= ctrl_overall[s] - 0.05 for s in seeds)
    passed = J448a and J448b and J448c

    print("\n--- VERDICT ---", flush=True)
    print(f"J448a affect enhances memory (emo>=neu+0.15) : {J448a}", flush=True)
    print(f"J448b control symmetric (|emo-neu|<=0.05)    : {J448b}", flush=True)
    print(f"J448c no net cost (boost>=ctrl-0.05)         : {J448c}", flush=True)
    verdict = ("PASS - strong-energy (emotional) facts are recalled more robustly under interference, "
               "and only via the affect-derived weight: strong connections grow stronger") if passed else "NULL/partial"
    print(f"\nJEP-448: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP448"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J448a": J448a, "J448b": J448b, "J448c": J448c}, indent=2, default=str))
    print("DONE", flush=True)
