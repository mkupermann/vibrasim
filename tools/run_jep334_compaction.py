"""JEP-334 — store compaction reclaims capacity from corrected facts while preserving answers. No transformer.
Pre-registered bars in docs/amendments/jep334_compaction.md.
"""
import json, tempfile
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery


def build_with_corrections(seed, n_corr):
    """A taxonomy + properties + an exception + n_corr DIRECT corrections (wrong fact then its negation)."""
    rng = np.random.default_rng(seed)
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True, module_cap=40)
    for c, p in [("poodle", "dog"), ("dog", "mammal"), ("mammal", "animal"), ("penguin", "bird"), ("bird", "animal")]:
        mem.add_fact(c, "isa", p)
    mem.add_fact("bird", "hasprop", "fly")
    mem.add_fact("penguin", "not_hasprop", "fly")            # EXCEPTION (inherited fly) -> must SURVIVE compaction
    # n_corr direct corrections: teach wrong isa then negate it
    for i in range(n_corr):
        mem.add_fact(f"e{i}", "isa", f"wrong{i}")
        mem.add_fact(f"e{i}", "isa", f"right{i}")
        mem.add_fact(f"e{i}", "not_isa", f"wrong{i}")        # correction
    return mem


def answers(mem, seed, n_corr):
    bq = BrainQuery(mem, seed=seed)
    out = {}
    out["poodle_animal"] = bq.is_a("poodle", "animal")
    out["penguin_fly"] = bq.has_property("penguin", "fly")   # exception -> False
    for i in range(min(n_corr, 8)):
        out[f"e{i}_wrong"] = bq.is_a(f"e{i}", f"wrong{i}")   # corrected -> False
        out[f"e{i}_right"] = bq.is_a(f"e{i}", f"right{i}")   # True
    return out


def run_seed(seed):
    n_corr = 20
    mem = build_with_corrections(seed, n_corr)
    pre = answers(mem, seed, n_corr); pre_facts = len(mem.facts); pre_mods = len(mem.modules)

    comp = mem.compact()
    post = answers(comp, seed, n_corr); post_facts = len(comp.facts); post_mods = len(comp.modules)
    preserved = np.mean([pre[k] == post[k] for k in pre])

    d = tempfile.mkdtemp(prefix=f"comp_{seed}_"); comp.save(d); rel = SubstrateMemory.load(d)
    rpost = answers(rel, seed, n_corr)
    persist = all(rpost[k] == post[k] for k in post)

    return {"preserved": round(float(preserved), 3), "pre_facts": pre_facts, "post_facts": post_facts,
            "pre_modules": pre_mods, "post_modules": post_mods, "persist": bool(persist),
            "exception_kept": (post["penguin_fly"] is False)}


if __name__ == "__main__":
    print("=== JEP-334: store compaction reclaims capacity, preserves answers ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: answers preserved={r['preserved']} | facts {r['pre_facts']}->{r['post_facts']} | "
              f"modules {r['pre_modules']}->{r['post_modules']} | exception kept={r['exception_kept']} "
              f"persists={r['persist']}", flush=True)
    J334a = all(R[s]['preserved'] >= 0.98 and R[s]['exception_kept'] for s in seeds)
    J334b = all(R[s]['post_facts'] < R[s]['pre_facts'] and R[s]['post_modules'] <= R[s]['pre_modules'] for s in seeds)
    J334c = all(R[s]['persist'] for s in seeds)
    passed = J334a and J334b and J334c
    print("\n--- VERDICT ---", flush=True)
    print(f"J334a answers preserved incl exception (>=.98): {J334a}", flush=True)
    print(f"J334b capacity reclaimed (fewer facts/modules) : {J334b}", flush=True)
    print(f"J334c compacted store persists                 : {J334c}", flush=True)
    verdict = ("PASS - compaction reclaims capacity from resolved corrections while preserving every answer, "
               "keeping exceptions") if passed else "NULL/partial"
    print(f"\nJEP-334: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP334"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J334a": J334a, "J334b": J334b, "J334c": J334c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
