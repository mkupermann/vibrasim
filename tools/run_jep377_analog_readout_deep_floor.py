"""JEP-377 — does a magnitude-preserving (analog) readout close the deep-recall floor? No transformer.
Pre-registered bars in docs/amendments/jep377_analog_readout_deep_floor.md.
Controlled comparison of sign vs analog cleanup on the SAME consolidated store; deployed store unchanged.
"""
import json, tempfile
from pathlib import Path
import numpy as np
from world.conversation import Conversation
from world.substrate_memory import bind
from tools.run_jep372_live_conversation_consolidation import nm, build_taxonomy_doc, ancestors


def sims_for_readout(m, x, role, z, analog):
    """Single-hop similarity of edge (x, role, z) under sign or analog readout (max over routed modules)."""
    key = bind(m._vec(x), m._vec(role))
    vv = m._vec(z)
    best = -1e9
    for mod in m._route(x, role):
        raw = m.modules[mod]
        vec = (raw / (np.linalg.norm(raw) + 1e-12)) if analog else np.sign(raw)
        if not analog:
            vec[vec == 0] = 1.0
        r = vec * key
        if m.directed:
            r = np.roll(r, -1)
        best = max(best, float(r @ vv / m.D))
    return best if best > -1e8 else 0.0


def collect(m, parent, N, seed):
    """Collect (sim_true, sim_false) for deep ancestor edges and non-ancestor pairs, under both readouts."""
    rng = np.random.default_rng(seed + 100)
    leaves = [k for k in range(N) if k not in set(parent.values())]; rng.shuffle(leaves)
    samp = leaves[:40]
    out = {"sign": {"true": [], "false": []}, "analog": {"true": [], "false": []}}
    for x in samp:
        anc = ancestors(parent, x)
        if not anc:
            continue
        z_true = anc[min(len(anc) - 1, int(rng.integers(0, len(anc))))]
        non = [y for y in range(N) if y != x and y not in set(anc)]
        z_false = int(rng.choice(non)) if non else None
        for analog, key in ((False, "sign"), (True, "analog")):
            out[key]["true"].append(sims_for_readout(m, nm(x), "isa", nm(z_true), analog))
            if z_false is not None:
                out[key]["false"].append(sims_for_readout(m, nm(x), "isa", nm(z_false), analog))
    return out


def best_min_metric(true_s, false_s):
    """Sweep the gate; return the max over gates of min(deep_recall, neg_accuracy), plus that gate."""
    cand = sorted(set(true_s + false_s))
    best, bg = -1, None
    for g in cand:
        deep = np.mean([t >= g for t in true_s])
        neg = np.mean([f < g for f in false_s])
        if min(deep, neg) > best:
            best, bg = min(deep, neg), g
    return round(best, 3), bg


def run_seed(seed, N=300):
    rng = np.random.default_rng(seed)
    parent, depth, doc = build_taxonomy_doc(N, rng)
    conv = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"j377_{seed}_"), seed=seed)
    conv.read_text(doc)                                  # auto-consolidates (sign store; we read it both ways)
    m = conv.sm
    s = collect(m, parent, N, seed)
    res = {}
    for key in ("sign", "analog"):
        bm, bg = best_min_metric(s[key]["true"], s[key]["false"])
        tmed = float(np.median(s[key]["true"]))
        fp95 = float(np.percentile(s[key]["false"], 95))
        margin = (tmed - fp95) / (abs(fp95) + 1e-12)
        res[key] = {"best_min": bm, "gate": bg, "true_med": round(tmed, 4), "false_p95": round(fp95, 4),
                    "margin": round(margin, 3)}
    return res


if __name__ == "__main__":
    print("=== JEP-377: analog vs sign readout on the deep-recall floor ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: SIGN  best min(deep,neg)={r['sign']['best_min']} (margin {r['sign']['margin']}) | "
              f"ANALOG best min(deep,neg)={r['analog']['best_min']} (margin {r['analog']['margin']})", flush=True)

    J377a = all(R[s]['analog']['best_min'] >= 0.95 for s in seeds)
    J377b = all(R[s]['analog']['best_min'] > R[s]['sign']['best_min'] for s in seeds)
    J377c = all(R[s]['analog']['margin'] > R[s]['sign']['margin'] for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"J377a analog clears min(deep,neg)>=0.95 : {J377a}", flush=True)
    print(f"J377b analog > sign                     : {J377b}", flush=True)
    print(f"J377c analog separation margin > sign   : {J377c}", flush=True)
    if J377a and J377b:
        verdict = ("PASS - a magnitude-preserving (analog) readout separates the true/false single-hop distributions "
                   "where sign cannot, clearing min(deep,neg)>=0.95: the deep-recall floor is a SIGN-QUANTIZATION "
                   "effect, closable by an analog cleanup on the durable store (scoped future change justified).")
    elif J377b or J377c:
        verdict = ("PARTIAL - analog separates better than sign but does not clear 0.95: the residual is DILUTION-"
                   "bound (deepest nodes carry ~10 ancestors), so the fix is reduced per-key load, not readout. Honest "
                   "narrowing, not a solve.")
    else:
        verdict = "NULL - analog readout does not beat sign here; the floor is not a quantization effect. See rows."
    print(f"\nJEP-377: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP377"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J377a": J377a, "J377b": J377b, "J377c": J377c},
                                                 default=str))
    print("DONE", flush=True)
