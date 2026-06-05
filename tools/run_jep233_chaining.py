"""JEP-233 — does the substrate do TRANSITIVE is-a inference by CHAINING retrievals?

Iterate JEP-232's key->value retrieval: retrieve parent(child), present the result as the next key, repeat —
walking the is-a chain c0->c1->...->cn through energy relaxation. Two re-clamp modes: 'decode' (clean-up each hop)
and 'raw' (re-clamp settled value bits directly, substrate-only). Established iterated associative recall.

Pre-registered bars in docs/amendments/jep233_substrate_transitive_chaining.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from tools.run_jep232_relation_store import KEY, VAL, N, codes, store, make_facts


def decode(val_bits, code):
    sims = np.array([np.sign(val_bits) @ code[k] for k in range(len(code))])
    return int(np.argmax(sims))


def k_hop(net, start, code, k, mode, seed):
    """Walk k is-a hops from concept `start`. mode in {'decode','raw'}. Returns the decoded end concept."""
    rng = np.random.default_rng(seed + start)
    key_bits = code[start].astype(np.float64)
    for _ in range(k):
        net.state = rng.choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), key_bits, steps=40)
        val = s[KEY:KEY + VAL]
        if mode == "decode":
            key_bits = code[decode(val, code)].astype(np.float64)   # clean-up: re-clamp the nearest clean code
        else:
            key_bits = np.sign(val).astype(np.float64)              # raw: re-clamp the settled value bits directly
    return decode(key_bits, code)            # key_bits now holds the k-th ancestor's representation


def hop_recall(net, facts, code, k, mode, seed):
    """Fraction of chain starts c_i whose k-hop walk lands on c_{i+k} (the true k-th ancestor)."""
    n = len(facts) + 1                       # concepts 0..len(facts)
    starts = [i for i in range(n) if i + k < n]
    if not starts:
        return 0.0
    ok = 0
    for i in starts:
        end = k_hop(net, i, code, k, mode, seed)
        if end == i + k:
            ok += 1
    return ok / len(starts)


def run_seed(seed, K=12):
    nc = K + 1
    code = codes(nc, seed)
    facts = make_facts(K, nc)
    net = store(facts, code, seed, train=True)
    ctl = store(facts, code, seed, train=False)
    return {
        "decode_k2": hop_recall(net, facts, code, 2, "decode", seed),
        "decode_k3": hop_recall(net, facts, code, 3, "decode", seed),
        "raw_k2":    hop_recall(net, facts, code, 2, "raw", seed),
        "raw_k3":    hop_recall(net, facts, code, 3, "raw", seed),
        "control_k2": hop_recall(ctl, facts, code, 2, "decode", seed),
    }


if __name__ == "__main__":
    print("=== JEP-233: transitive is-a inference by chaining substrate retrievals ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: decode k2={r['decode_k2']:.2f} k3={r['decode_k3']:.2f} | "
              f"raw k2={r['raw_k2']:.2f} k3={r['raw_k3']:.2f} | control k2={r['control_k2']:.2f}", flush=True)

    J233a = all(R[s]['decode_k2'] >= 0.85 for s in seeds)
    J233b = all(R[s]['decode_k3'] >= 0.85 for s in seeds)
    J233c = all(R[s]['raw_k2'] >= 0.70 for s in seeds)
    J233d = all(R[s]['control_k2'] <= 0.40 for s in seeds)
    passed = J233a and J233b and J233c and J233d

    print("\n--- VERDICT ---", flush=True)
    print(f"J233a 2-hop decode (>=0.85): {J233a}", flush=True)
    print(f"J233b 3-hop decode (>=0.85): {J233b}", flush=True)
    print(f"J233c 2-hop raw    (>=0.70): {J233c}", flush=True)
    print(f"J233d control fails (<=0.40): {J233d}", flush=True)
    verdict = ("PASS - the substrate performs transitive is-a inference by iterated retrieval") if passed else "NULL/partial"
    print(f"\nJEP-233: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP233"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J233a": J233a, "J233b": J233b,
         "J233c": J233c, "J233d": J233d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
