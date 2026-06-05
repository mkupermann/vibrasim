"""JEP-295 — persistent, growing substrate memory (per Michael: don't die when the program closes; grow like a brain).

Bars (pre-registered in docs/amendments/jep295_persistent_memory.md):
  J295a persistence    : teach -> save -> load into a FRESH object -> recall unchanged (facts>=.95, letters>=.90)
  J295b grow w/o forget: 3 save/load cycles each adding facts+letters -> ALL accumulated recall >=.90 at the end
  J295c cross-process  : a SEPARATE python subprocess reading only the folder recovers facts >=.95 (it IS the file)

No transformer, no pretrained model. Run: PYTHONPATH=. .venv/Scripts/python.exe tools/run_jep295_persistent_memory.py
"""
import json, os, sys, tempfile, subprocess, string
from pathlib import Path
import numpy as np

from world.substrate_memory import SubstrateMemory

# a small glyph renderer (scale-normalized, matches the teaching tool) so letters persist too
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from teach_gui import render_letter  # noqa: E402

FACTS_1 = [("germany", "has", "politics"), ("hungary", "has", "politics"),
           ("germanpolitics", "is", "corrupt"), ("hungarianpolitics", "is", "clean"),
           ("poodle", "isa", "dog"), ("dog", "isa", "mammal"),
           ("salmon", "isa", "fish"), ("paris", "capitalof", "france"),
           ("heart", "partof", "dog"), ("berlin", "capitalof", "germany"),
           ("water", "madeof", "hydrogen"), ("sun", "isa", "star")]
FACTS_2 = [("rome", "capitalof", "italy"), ("cat", "isa", "mammal"), ("oak", "isa", "tree")]
FACTS_3 = [("tokyo", "capitalof", "japan"), ("whale", "isa", "mammal")]


def facts_acc(mem, facts):
    ok = sum(mem.query(e, r)[0] == v for (e, r, v) in facts)
    return ok / len(facts)


def letters_acc(mem, letters, seed):
    rng = np.random.default_rng(seed + 999)
    ok = tot = 0
    for ch in letters:
        for _ in range(5):
            tot += 1; ok += (mem.recognize("write", render_letter(ch, rng).ravel())[0] == ch)
    return ok / tot


def teach_letters(mem, letters, seed):
    rng = np.random.default_rng(seed)
    for ch in letters:
        for _ in range(5):
            mem.teach_percept("write", ch, render_letter(ch, rng).ravel())


CROSS_PROC = r'''
import sys, json
sys.path.insert(0, r"{repo}")
from world.substrate_memory import SubstrateMemory
m = SubstrateMemory.load(r"{d}")
facts = {facts}
ok = sum(m.query(e, r)[0] == v for (e, r, v) in facts)
print(json.dumps({{"acc": ok / len(facts), "n_facts": len(m.facts)}}))
'''


def run_seed(seed, repo):
    d = tempfile.mkdtemp(prefix=f"brain_{seed}_")
    L1 = list("ABCDEFGH")

    # --- session 1: teach, then SAVE and drop the object ---
    m = SubstrateMemory(D=4096, tau=0.12)
    for (e, r, v) in FACTS_1:
        m.add_fact(e, r, v)
    teach_letters(m, L1, seed)
    pre_f, pre_l = facts_acc(m, FACTS_1), letters_acc(m, L1, seed)
    m.save(d)
    del m

    # --- J295a: load into a FRESH object, recall must match ---
    m2 = SubstrateMemory.load(d)
    a_f, a_l = facts_acc(m2, FACTS_1), letters_acc(m2, L1, seed)
    J295a = (a_f >= 0.95 and a_l >= 0.90 and abs(a_f - pre_f) < 1e-9)

    # --- J295b: grow across 2 more save/load cycles, never forgetting ---
    L2, L3 = list("IJK"), list("LM")
    m2.save(d); del m2
    m3 = SubstrateMemory.load(d)
    for (e, r, v) in FACTS_2:
        m3.add_fact(e, r, v)
    teach_letters(m3, L2, seed + 1)
    m3.save(d); del m3
    m4 = SubstrateMemory.load(d)
    for (e, r, v) in FACTS_3:
        m4.add_fact(e, r, v)
    teach_letters(m4, L3, seed + 2)
    m4.save(d); del m4
    m5 = SubstrateMemory.load(d)
    all_facts = FACTS_1 + FACTS_2 + FACTS_3
    all_letters = L1 + L2 + L3
    g_f, g_l = facts_acc(m5, all_facts), letters_acc(m5, all_letters, seed)
    J295b = (g_f >= 0.90 and g_l >= 0.90)

    # --- J295c: a SEPARATE subprocess reads only the folder ---
    code = CROSS_PROC.format(repo=repo, d=d, facts=repr(all_facts))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         env={**os.environ, "PYTHONPATH": repo})
    try:
        cp = json.loads(out.stdout.strip().splitlines()[-1])
        J295c = cp["acc"] >= 0.95
    except Exception:
        cp = {"acc": -1, "err": out.stderr[-300:]}; J295c = False

    return {"pre_f": pre_f, "a_f": a_f, "a_l": a_l, "g_f": g_f, "g_l": g_l, "n_all": len(all_facts),
            "cross_proc": cp, "J295a": J295a, "J295b": J295b, "J295c": J295c, "dir": d}


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-295: persistent, growing substrate memory ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s, repo) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: load facts={r['a_f']:.2f} letters={r['a_l']:.2f} | grown({r['n_all']} facts) "
              f"facts={r['g_f']:.2f} letters={r['g_l']:.2f} | cross-proc acc={r['cross_proc']['acc']}", flush=True)

    J295a = all(R[s]["J295a"] for s in seeds)
    J295b = all(R[s]["J295b"] for s in seeds)
    J295c = all(R[s]["J295c"] for s in seeds)
    passed = J295a and J295b and J295c
    print("\n--- VERDICT ---", flush=True)
    print(f"J295a persistence (fresh-object reload unchanged)     : {J295a}", flush=True)
    print(f"J295b grows without forgetting (3 cycles, all recall) : {J295b}", flush=True)
    print(f"J295c real cross-process persistence (subprocess)     : {J295c}", flush=True)
    verdict = ("PASS - the substrate memory is a durable folder of files; it survives close+reopen, grows across "
               "sessions without forgetting, and a separate program reconstructs it") if passed else "NULL/partial"
    print(f"\nJEP-295: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP295"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds},
                                                  "J295a": J295a, "J295b": J295b, "J295c": J295c,
                                                  "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
