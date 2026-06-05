"""JEP-314 — analogical retrieval (Kanerva 'dollar of Mexico'): role-bound country records + analogy mapping."""
import json, itertools
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle, sim, CleanupMemory

D = 4096
DATA = {
    "usa": {"capital": "washington", "currency": "dollar", "language": "english"},
    "mexico": {"capital": "mexicocity", "currency": "peso", "language": "spanish"},
    "france": {"capital": "paris", "currency": "franc", "language": "french"},
    "germany": {"capital": "berlin", "currency": "mark", "language": "german"},
    "japan": {"capital": "tokyo", "currency": "yen", "language": "japanese"},
}
ROLES = ["capital", "currency", "language"]


def run_seed(seed):
    rng = np.random.default_rng(seed)
    role = {r: rand_hv(D, rng) for r in ROLES}
    vals = {v: rand_hv(D, rng) for c in DATA for v in DATA[c].values()}
    rec = {c: bundle([bind(role[r], vals[DATA[c][r]]) for r in ROLES]) for c in DATA}
    clean = CleanupMemory()
    for v, hv in vals.items():
        clean.add(v, hv)

    # J314b: direct retrieval (capital of france -> paris)
    direct_ok = 0; direct_tot = 0
    for c in DATA:
        for r in ROLES:
            direct_tot += 1
            got = clean.cleanup(bind(rec[c], role[r]))[0]
            direct_ok += (got == DATA[c][r])

    # J314a: analogy ("<src_value> is to <src> as ? is to <tgt>")
    an_ok = 0; an_tot = 0
    for src, tgt in itertools.permutations(DATA, 2):
        M = bind(rec[src], rec[tgt])                      # source->target mapping
        for r in ROLES:
            an_tot += 1
            probe = bind(vals[DATA[src][r]], M)           # src's attribute carried through the mapping
            got = clean.cleanup(probe)[0]
            an_ok += (got == DATA[tgt][r])
    return {"direct_acc": round(direct_ok / direct_tot, 3), "analogy_acc": round(an_ok / an_tot, 3),
            "n_analogy": an_tot}


if __name__ == "__main__":
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"JEP314 seed {s}: direct acc={R[s]['direct_acc']} analogy acc={R[s]['analogy_acc']} "
              f"({R[s]['n_analogy']} analogies)", flush=True)
    J314a = all(R[s]['analogy_acc'] >= 0.90 for s in seeds)
    J314b = all(R[s]['direct_acc'] >= 0.95 for s in seeds)
    passed = J314a and J314b
    print(f"JEP-314: {'PASS' if passed else 'NULL/partial'} (J314a={J314a} J314b={J314b})", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP314"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J314a": J314a, "J314b": J314b, "passed": passed}, default=str))
    print("DONE", flush=True)
