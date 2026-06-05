"""JEP-245 — is the substrate relational store MEMORY or GENERALIZATION? (the honest boundary)

Probes: (a) stored multi-hop is_a via chaining (deductive closure); (b) held-out BRIDGE edge -> chain breaks at the
hole (no inductive inference with random codes); (c) held-out DIRECT edge unrecoverable; (d) COMPOSITIONAL codes
(child bundles parent) answer is_a by overlap even across the hole -> generalization lives in the CODES. Energy-gated
chains (JEP-244). Established (transitive closure, orthogonal-code memory, VSA bundling), named.

Pre-registered bars in docs/amendments/jep245_substrate_memory_vs_generalization.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from tools.run_jep232_relation_store import KEY, VAL, N


def rand_codes(n, seed):
    rng = np.random.default_rng(seed)
    return [rng.choice([-1.0, 1.0], KEY) for _ in range(n)]


def compositional_codes(n, seed):
    """c_i = sign( sig_i + parent_code ); built top-down so a child's code carries all ancestor signatures."""
    rng = np.random.default_rng(seed + 1)
    sig = [rng.choice([-1.0, 1.0], KEY) for _ in range(n)]
    code = [None] * n
    code[n - 1] = sig[n - 1].astype(np.float64)                 # root
    for i in range(n - 2, -1, -1):                              # child i -> parent i+1
        code[i] = np.sign(sig[i] + code[i + 1])
    return code, sig


def store(edges, code, seed):
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    pats = [np.concatenate([code[c], code[p]]) for c, p in edges]
    for _ in range(140):
        net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    e_cut = 0.7 * float(np.median([net.energy(p) for p in pats]))
    return net, e_cut


def egate_chain(net, x, code, e_cut, seed, max_depth=8):
    reach, seen, cur = set(), {x}, x
    for d in range(max_depth):
        net.state = np.random.default_rng(seed + d).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), code[cur], steps=40)
        if net.energy(s) > e_cut:
            break
        val = np.sign(s[KEY:KEY + VAL])
        nxt = int(np.argmax([val @ code[k] for k in range(len(code))]))
        if nxt in seen:
            break
        reach.add(nxt); seen.add(nxt); cur = nxt
    return reach


def run_seed(seed):
    n = 5                                  # chain c0->c1->c2->c3->c4
    code = rand_codes(n, seed)
    all_edges = [(i, i + 1) for i in range(n - 1)]

    # (a) stored multi-hop
    net, cut = store(all_edges, code, seed)
    a = 4 in egate_chain(net, 0, code, cut, seed)

    # (b) held-out BRIDGE: remove c2->c3
    bridge_edges = [e for e in all_edges if e != (2, 3)]
    net_b, cut_b = store(bridge_edges, code, seed)
    b = 4 not in egate_chain(net_b, 0, code, cut_b, seed)           # should NOT reach c4 (chain stops at c2)

    # (c) held-out DIRECT: never store (1,2); store (0,1),(2,3),(3,4) + a decoy (1,4)
    direct_edges = [(0, 1), (2, 3), (3, 4), (1, 4)]
    net_c, cut_c = store(direct_edges, code, seed)
    c = 2 not in egate_chain(net_c, 1, code, cut_c, seed)           # is_a(c1,c2) never stored -> not inferable

    # (d) COMPOSITIONAL codes answer is_a(c0,c4) by OVERLAP even with the bridge removed
    ccode, sig = compositional_codes(n, seed)
    # is_a(x,y) by overlap of x's code with y's SIGNATURE (ancestor signatures are bundled into descendants)
    def isa_overlap(x, y):
        return float(np.sign(ccode[x]) @ sig[y])   # x's code overlap with y's signature (high if y is an ancestor of x)
    thr = 0.30 * KEY
    d_pos = isa_overlap(0, 4) >= thr                               # c0 is-a c4 (ancestor) -> high overlap
    d_neg = isa_overlap(4, 0) < thr                                # c4 is NOT is-a c0 (non-ancestor) -> low overlap
    d = d_pos and d_neg
    return {"a": bool(a), "b": bool(b), "c": bool(c), "d": bool(d),
            "comp_overlap_anc": round(isa_overlap(0, 4) / KEY, 2), "comp_overlap_non": round(isa_overlap(4, 0) / KEY, 2)}


if __name__ == "__main__":
    print("=== JEP-245: substrate store -- memory vs generalization ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: (a) stored multi-hop works={r['a']} | (b) held-out bridge breaks chain={r['b']} | "
              f"(c) held-out direct unrecoverable={r['c']} | (d) compositional codes generalize={r['d']} "
              f"(anc overlap {r['comp_overlap_anc']}, non-anc {r['comp_overlap_non']})", flush=True)

    J245a = all(R[s]['a'] for s in seeds)
    J245b = all(R[s]['b'] for s in seeds)
    J245c = all(R[s]['c'] for s in seeds)
    J245d = all(R[s]['d'] for s in seeds)
    passed = J245a and J245b and J245c and J245d

    print("\n--- VERDICT ---", flush=True)
    print(f"J245a deductive closure via chaining works : {J245a}", flush=True)
    print(f"J245b held-out bridge breaks the chain     : {J245b}", flush=True)
    print(f"J245c held-out direct edge unrecoverable   : {J245c}", flush=True)
    print(f"J245d compositional codes generalize       : {J245d}", flush=True)
    verdict = ("PASS - the substrate store is MEMORY+deductive-closure with random codes; GENERALIZATION lives in the "
               "CODES (structured), not the attractor store") if passed else "NULL/partial"
    print(f"\nJEP-245: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP245"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J245a": J245a, "J245b": J245b,
         "J245c": J245c, "J245d": J245d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
