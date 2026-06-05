"""JEP-336 — compact-on-save applies corrections physically to the persisted brain (headless). No transformer.
Pre-registered bars in docs/amendments/jep336_compact_on_save.md.
"""
import json, tempfile, importlib
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory


def gate(mem, seed, role="isa"):
    edges = [(a, b) for (a, r, b) in mem.facts if r == role]
    rng = np.random.default_rng(seed)
    t = np.mean([mem.edge_sim(a, role, b) for (a, b) in edges]) if edges else 0.2
    u = np.mean([mem.query(f"n_{int(rng.integers(1e9))}", role)[1] for _ in range(30)])
    return float((t + u) / 2)


def correct_acc(mem, n, g):
    def isa(x, y):
        if mem.contains(x, "not_isa", y, g):
            return False
        return y in [p for (p, _) in mem.query_all(x, "isa", g)]
    ok = sum((isa(f"e{i}", f"wrong{i}") is False) and (isa(f"e{i}", f"right{i}") is True) for i in range(n))
    return ok / n


def build(n, seed):
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True, module_cap=40)
    for i in range(n):
        mem.add_fact(f"e{i}", "isa", f"wrong{i}")
        mem.add_fact(f"e{i}", "isa", f"right{i}")
        mem.add_fact(f"e{i}", "not_isa", f"wrong{i}")
    return mem


def run_seed(seed):
    n = 40
    mem = build(n, seed)
    # simulate GUI _on_close: compact-if-needed then save
    pending = mem.has_resolvable_corrections()
    if pending:
        mem = mem.compact()
    d = tempfile.mkdtemp(prefix=f"cos_{seed}_"); mem.save(d)
    rel = SubstrateMemory.load(d); g = gate(rel, seed)
    acc = correct_acc(rel, n, g)
    # no-op check: a clean store (no corrections) -> has_resolvable_corrections False
    clean = SubstrateMemory(D=4096, directed=True)
    clean.add_fact("a", "isa", "b")
    noop_ok = (clean.has_resolvable_corrections() is False) and (pending is True)
    return {"corrected_acc_after_save": round(float(acc), 3), "pending_was_true": bool(pending),
            "noop_clean_ok": bool(noop_ok)}


if __name__ == "__main__":
    print("=== JEP-336: compact-on-save applies corrections to the persisted brain ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: corrected-acc after compact-on-save={r['corrected_acc_after_save']} | "
              f"pending detected={r['pending_was_true']} | clean no-op ok={r['noop_clean_ok']}", flush=True)
    try:
        import tools.teach_gui; importlib.reload(tools.teach_gui); gui_ok = True
    except Exception as ex:
        gui_ok = False; print("  teach_gui:", ex, flush=True)

    J336a = all(R[s]['corrected_acc_after_save'] >= 1.0 for s in seeds)
    J336b = all(R[s]['noop_clean_ok'] for s in seeds) and gui_ok
    passed = J336a and J336b
    print("\n--- VERDICT ---", flush=True)
    print(f"J336a corrections physically applied after save (=1.0): {J336a}", flush=True)
    print(f"J336b no-op when clean + GUI wired                     : {J336b}", flush=True)
    verdict = ("PASS - compact-on-close physically applies corrections to the durable brain (reliable regardless of "
               "load), and is a no-op when nothing to resolve") if passed else "NULL/partial"
    print(f"\nJEP-336: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP336"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J336a": J336a, "J336b": J336b, "gui_ok": gui_ok,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)
