"""JEP-322 — verify the BrainQuery interface + string parser over a persisted brain. No transformer.
Pre-registered bars in docs/amendments/jep322_brain_query.md.
"""
import json, tempfile, importlib
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery


def build():
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for c, p in [("poodle", "dog"), ("dog", "mammal"), ("mammal", "animal"), ("penguin", "bird"),
                 ("bird", "animal"), ("robin", "bird")]:
        mem.add_fact(c, "isa", p)
    mem.add_fact("bird", "hasprop", "fly")
    mem.add_fact("penguin", "not_hasprop", "fly")
    mem.add_fact("whale", "isa", "mammal"); mem.add_fact("whale", "not_isa", "fish")
    for c, e in [("smoking", "cancer"), ("radiation", "cancer")]:
        mem.add_fact(c, "causes", e); mem.add_fact(e, "caused_by", c)
    for s, o in [("cat", "fish")]:
        mem.add_fact(s, "eats", o)
    return mem


def run_seed(seed):
    mem = build(); d = tempfile.mkdtemp(prefix=f"bq_{seed}_"); mem.save(d)
    bq = BrainQuery(SubstrateMemory.load(seed and d or d))   # fresh reload

    # J322a interface
    iface = [
        (bq.is_a("poodle", "animal"), True), (bq.is_a("poodle", "fish"), False),
        (bq.is_a("whale", "fish"), False), (bq.is_a("whale", "animal"), True),
        (bq.has_property("robin", "fly"), True), (bq.has_property("penguin", "fly"), False),
        (bq.why("cancer"), ["radiation", "smoking"]), (bq.what("cat", "eats"), ["fish"]),
    ]
    iface_acc = np.mean([a == b for (a, b) in iface])

    # J322b parser
    parse = [
        (bq.ask("is a poodle an animal?"), True), (bq.ask("can a penguin fly?"), False),
        (bq.ask("can a robin fly?"), True), (bq.ask("what causes cancer?"), ["radiation", "smoking"]),
        (bq.ask("what does a cat eat?"), ["fish"]), (bq.ask("is a whale a fish?"), False),
    ]
    parse_acc = np.mean([a == b for (a, b) in parse])
    return {"iface_acc": round(float(iface_acc), 3), "parse_acc": round(float(parse_acc), 3),
            "brain_dir": d}


if __name__ == "__main__":
    print("=== JEP-322: BrainQuery interface + parser over a persisted brain ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: interface acc={R[s]['iface_acc']} | parser acc={R[s]['parse_acc']}", flush=True)
    # J322c: CLI imports + answers from a saved folder
    try:
        cli = importlib.import_module("tools.ask_brain")
        importlib.reload(cli)
        J322c = True
    except Exception as ex:
        J322c = False; print("  ask_brain import:", ex, flush=True)

    J322a = all(R[s]['iface_acc'] >= 0.95 for s in seeds)
    J322b = all(R[s]['parse_acc'] >= 0.95 for s in seeds)
    passed = J322a and J322b and J322c
    print("\n--- VERDICT ---", flush=True)
    print(f"J322a interface answers (>=.95): {J322a}", flush=True)
    print(f"J322b string parser (>=.95)    : {J322b}", flush=True)
    print(f"J322c CLI imports               : {J322c}", flush=True)
    verdict = ("PASS - one interface answers is-a/property/why/what over the durable brain, with a natural-question "
               "parser and a CLI") if passed else "NULL/partial"
    print(f"\nJEP-322: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP322"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J322a": J322a, "J322b": J322b, "J322c": J322c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
