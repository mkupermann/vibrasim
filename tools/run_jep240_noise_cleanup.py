"""JEP-240 — substrate multi-hop chaining under cue noise: is attractor CLEANUP the native (partial) cure?

Inject KEY-cue bit-flip noise at each hop; walk k hops 'raw' (re-clamp settled value bits) vs 'cleanup' (decode to
nearest clean code, re-clamp that). Compare k-hop recall vs depth. Connects the substrate-relational arc to the
universal compounding-vs-cleanup insight (JEP-137/138/140/158). Established (Hopfield basins, cleanup memory).

Pre-registered bars in docs/amendments/jep240_substrate_noise_cleanup.md.
"""
import json
from pathlib import Path
import numpy as np

from tools.run_jep232_relation_store import KEY, VAL, N, codes, store, make_facts


def flip(bits, f, rng):
    out = bits.copy()
    idx = np.where(rng.random(len(bits)) < f)[0]
    out[idx] *= -1
    return out


def decode(val, code):
    return int(np.argmax([np.sign(val) @ code[k] for k in range(len(code))]))


def k_hop(net, start, code, k, mode, f, seed):
    """Walk k hops from `start` with cue-noise fraction f; return decoded end concept."""
    rng = np.random.default_rng(seed + start * 131)
    key = code[start].astype(np.float64)
    for _ in range(k):
        net.state = rng.choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), flip(key, f, rng), steps=40)     # noisy cue
        val = s[KEY:KEY + VAL]
        key = code[decode(val, code)].astype(np.float64) if mode == "cleanup" else np.sign(val).astype(np.float64)
    return decode(key, code)


def hop_recall(net, facts, code, k, mode, f, seed):
    starts = [i for (i, _) in facts if i + k <= len(facts)]
    if not starts:
        return 1.0
    return np.mean([k_hop(net, i, code, k, mode, f, seed) == i + k for i in starts])


def run_seed(seed, K=12):
    code = codes(K + 1, seed)
    facts = make_facts(K, K + 1)
    net = store(facts, code, seed, train=True)

    # J240a: find f* with single-hop recall in [0.78, 0.92]
    fstar, single = None, None
    for f in [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
        r = hop_recall(net, facts, code, 1, "cleanup", f, seed)
        if 0.78 <= r <= 0.92:
            fstar, single = f, r
            break
    if fstar is None:                      # fallback: pick the f closest to 0.85
        cand = [(abs(hop_recall(net, facts, code, 1, "cleanup", f, seed) - 0.85), f) for f in
                [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]]
        fstar = min(cand)[1]; single = hop_recall(net, facts, code, 1, "cleanup", fstar, seed)

    raw = {k: float(hop_recall(net, facts, code, k, "raw", fstar, seed)) for k in (1, 2, 3, 4)}
    cln = {k: float(hop_recall(net, facts, code, k, "cleanup", fstar, seed)) for k in (1, 2, 3, 4)}
    return {"fstar": fstar, "single": float(single), "raw": raw, "cleanup": cln}


if __name__ == "__main__":
    print("=== JEP-240: substrate multi-hop chaining under cue noise (cleanup vs raw) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: f*={r['fstar']} single-hop={r['single']:.2f}", flush=True)
        print(f"    raw     k1..4: {[round(r['raw'][k],2) for k in (1,2,3,4)]}", flush=True)
        print(f"    cleanup k1..4: {[round(r['cleanup'][k],2) for k in (1,2,3,4)]}", flush=True)

    J240a = all(0.78 <= R[s]['single'] <= 0.92 for s in seeds)
    J240b = all(R[s]['raw'][1] - R[s]['raw'][4] >= 0.15 for s in seeds)
    J240c = all(R[s]['cleanup'][4] - R[s]['raw'][4] >= 0.10 for s in seeds)
    J240d = all(R[s]['cleanup'][4] < R[s]['cleanup'][1] for s in seeds)
    passed = J240a and J240b and J240c and J240d

    print("\n--- VERDICT ---", flush=True)
    print(f"J240a single-hop noise calibrated [.78,.92]: {J240a}", flush=True)
    print(f"J240b compounding real (raw k1-k4 >=.15)   : {J240b}", flush=True)
    print(f"J240c cleanup mitigates (cln-raw@k4 >=.10) : {J240c}", flush=True)
    print(f"J240d cleanup only partial (cln k4<k1)     : {J240d}", flush=True)
    verdict = ("PASS - the substrate's attractor cleanup is the native PARTIAL cure for multi-hop compounding "
               "under noise (mitigates drift, not discrete errors)") if passed else "NULL/partial"
    print(f"\nJEP-240: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP240"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J240a": J240a, "J240b": J240b,
         "J240c": J240c, "J240d": J240d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
