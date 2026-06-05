"""JEP-473 — temporal sequences: 'then' chains + first/last endpoints. Pre-registered bars in
docs/amendments/jep473_temporal_sequence.md.
"""
import json
from pathlib import Path
import tempfile
from world.conversation import Conversation


def run(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(), seed=seed)  # clean-room (lesson #16)
    c.say("First sunrise, then noon, then sunset.")
    return dict(
        transitive=str(c.say("is sunrise before sunset?")),
        first=str(c.say("what happened first?")),
        last=str(c.say("what happened last?")),
    )


if __name__ == "__main__":
    print("=== JEP-473: temporal 'then' sequences + endpoints ===", flush=True)
    seeds = [0, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: sunrise<sunset={R[s]['transitive']} | first={R[s]['first']} | last={R[s]['last']}", flush=True)

    J473a = all(R[s]['transitive'].lower().startswith("yes") for s in seeds)
    J473b = all("sunrise" in R[s]['first'].lower() and "sunset" in R[s]['last'].lower() for s in seeds)
    passed = J473a and J473b

    print("\n--- VERDICT (suites = pytest separate) ---", flush=True)
    print(f"J473a then-chain transitive (sunrise<sunset): {J473a}", flush=True)
    print(f"J473b endpoints (first=sunrise, last=sunset): {J473b}", flush=True)
    verdict = ("PASS - the brain ingests 'then' sequences and answers first/last endpoints"
               if passed else "NULL/partial")
    print(f"\nJEP-473: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP473"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"R": R, "passed": passed, "J473a": J473a, "J473b": J473b},
                                                 indent=2, default=str))
    print("DONE", flush=True)
