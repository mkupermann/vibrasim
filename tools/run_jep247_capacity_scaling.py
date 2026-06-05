"""JEP-247 — does the substrate relational-store capacity scale linearly with size? (verifying the claim)

Parametrized JEP-232 store (KEY=VALUE=M, N=2M); for several M, find the capacity cliff (largest K with recall>=0.95)
and check linearity. Verifies the 'scalable linearly' claim. Established (heteroassociative Hopfield capacity), named.

Pre-registered bars in docs/amendments/jep247_capacity_scaling.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet


def codes(M, n, seed):
    rng = np.random.default_rng(seed)
    return [rng.choice([-1.0, 1.0], M) for _ in range(n)]


def store(M, facts, code, seed):
    N = 2 * M
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    pats = [np.concatenate([code[c], code[p]]) for c, p in facts]
    for _ in range(140):
        net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    return net


def recall(M, K, seed):
    N = 2 * M
    code = codes(M, K + 1, seed)
    facts = [(i, i + 1) for i in range(K)]
    net = store(M, facts, code, seed)
    ok = 0
    for c, p in facts:
        net.state = np.random.default_rng(seed + c).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(M), code[c], steps=40)
        val = np.sign(s[M:2 * M])
        sims = np.array([val @ code[k] for k in range(len(code))]); sims[c] = -np.inf
        ok += int(np.argmax(sims)) == p
    return ok / K


def capacity(M, seed):
    """Largest K with recall >= 0.95 (scan upward until it drops; the cliff is sharp)."""
    cap = 0
    for K in range(4, 4 * M, 4):
        r = recall(M, K, seed)
        if r >= 0.95:
            cap = K
        else:
            # refine downward by 2 between cap and K
            for K2 in (cap + 2,):
                if K2 < K and recall(M, K2, seed) >= 0.95:
                    cap = K2
            break
    return cap


def run_seed(seed):
    out = {}
    for M in (40, 60, 80):
        cap = capacity(M, seed)
        over = recall(M, cap + 4, seed)        # recall just past capacity (cliff check)
        out[M] = {"capacity": cap, "ratio": round(cap / M, 3), "recall_over": round(over, 2)}
    return out


if __name__ == "__main__":
    print("=== JEP-247: capacity scaling of the substrate relational store ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: " + " | ".join(
            f"M={M} cap={r[M]['capacity']} (cap/M={r[M]['ratio']}, recall@cap+4={r[M]['recall_over']})"
            for M in (40, 60, 80)), flush=True)

    J247a = all(R[s][80]['capacity'] > R[s][60]['capacity'] > R[s][40]['capacity'] for s in seeds)
    def ratios(s): return [R[s][M]['capacity'] / M for M in (40, 60, 80)]
    J247b = all((max(ratios(s)) / max(min(ratios(s)), 1e-9)) <= 1.5 for s in seeds)
    J247c = all(16 <= R[s][40]['capacity'] <= 24 for s in seeds)
    J247d = all(R[s][M]['recall_over'] < 0.7 for s in seeds for M in (40, 60, 80))
    passed = J247a and J247b and J247c

    print("\n--- VERDICT ---", flush=True)
    print(f"J247a capacity grows with size      : {J247a}", flush=True)
    print(f"J247b growth ~linear (ratio max/min<=1.5): {J247b}", flush=True)
    print(f"J247c M=40 reproduces ~20 [16,24]   : {J247c}", flush=True)
    print(f"J247d sharp cliff at every scale    : {J247d}", flush=True)
    verdict = ("PASS - the substrate relational-store capacity scales ~linearly with value-slot size "
               "(the 'scalable linearly' claim VERIFIED)") if passed else "NULL/partial - claim corrected to measured scaling"
    print(f"\nJEP-247: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP247"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J247a": J247a, "J247b": J247b,
         "J247c": J247c, "J247d": J247d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
