"""JEP-449 — affective memory enhancement DEPLOYED in the live Conversation: an emotionally-tagged
fact survives interference where a matched neutral fact is lost; works whether affect is taught
before or after the fact. Pre-registered bars in docs/amendments/jep449_deploy_affective_memory.md.
"""
import json
from pathlib import Path
import numpy as np

from world.substrate_memory import SubstrateMemory


def _scenario(seed, affect_first):
    """Single-module store; one emotional + one neutral fact, then interference. affect_first toggles
    whether valence is set before or after the emotional fact is stored."""
    rng = np.random.default_rng(seed)
    sm = SubstrateMemory(D=4096, module_cap=100000)
    if affect_first:
        sm.valence["dragon"] = -3.0
        sm.add_fact("dragon", "has", "fire")
    else:
        sm.add_fact("dragon", "has", "fire")
        sm.learn_valence("dragon", -3.0)          # reinforces the already-stored fact
    sm.add_fact("table", "has", "wood")            # neutral, matched
    for i in range(300):                            # interference
        sm.add_fact(f"x{i}", "has", f"y{i}")
    emo = (sm.query("dragon", "has")[0] == "fire")
    neu = (sm.query("table", "has")[0] == "wood")
    return emo, neu


def run(seed):
    emo_a, neu_a = _scenario(seed, affect_first=True)
    emo_b, neu_b = _scenario(seed, affect_first=False)
    return dict(affect_first=dict(emo=emo_a, neu=neu_a), affect_after=dict(emo=emo_b, neu=neu_b))


if __name__ == "__main__":
    print("=== JEP-449: affective memory enhancement deployed (live store) ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: affect-first emo={R[s]['affect_first']['emo']} neu={R[s]['affect_first']['neu']} | "
              f"affect-after emo={R[s]['affect_after']['emo']} neu={R[s]['affect_after']['neu']}", flush=True)

    J449a = all(R[s]['affect_first']['emo'] and not R[s]['affect_first']['neu'] for s in seeds)
    J449c = all(R[s]['affect_after']['emo'] and not R[s]['affect_after']['neu'] for s in seeds)
    passed = J449a and J449c    # J449b (suite green) checked separately via pytest
    print("\n--- VERDICT (J449b = pytest, run separately) ---", flush=True)
    print(f"J449a affect-first: emotional kept, neutral lost : {J449a}", flush=True)
    print(f"J449c affect-after: emotional kept, neutral lost : {J449c}", flush=True)
    verdict = ("PASS - emotional facts survive interference in the live store (either teaching order); "
               "matched neutral facts do not") if passed else "NULL/partial"
    print(f"\nJEP-449: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP449"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": {str(s): R[s] for s in seeds}, "passed": passed,
                                                  "J449a": J449a, "J449c": J449c}, indent=2, default=str))
    print("DONE", flush=True)
