"""JEP-241 — does REDUNDANT AGGREGATION cure substrate multi-hop compounding where cleanup failed?

Per-hop majority-vote over R independent noisy retrievals (different flip masks), re-clamp the voted clean code.
Tests aggregation as the robust substrate cure for compounding under cue noise, completing the conceptual arc
opened by the JEP-240 NULL. Established (ensemble/majority voting, error-correcting redundancy).

Pre-registered bars in docs/amendments/jep241_substrate_aggregation_cure.md.
"""
import json
from collections import Counter
from pathlib import Path
import numpy as np

from tools.run_jep232_relation_store import KEY, VAL, N, codes, store, make_facts
from tools.run_jep240_noise_cleanup import flip, decode


def vote_hop(net, key_clean, code, R, f, rng):
    """R independent noisy retrievals from a clean key; majority-vote the decoded parent; return its clean code."""
    votes = []
    for _ in range(R):
        net.state = rng.choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), flip(key_clean, f, rng), steps=40)
        votes.append(decode(s[KEY:KEY + VAL], code))
    win = Counter(votes).most_common(1)[0][0]
    return win, code[win].astype(np.float64)


def k_hop_vote(net, start, code, k, R, f, seed):
    rng = np.random.default_rng(seed + start * 911)
    key = code[start].astype(np.float64)
    end = start
    for _ in range(k):
        end, key = vote_hop(net, key, code, R, f, rng)
    return end


def hop_recall_vote(net, facts, code, k, R, f, seed):
    starts = [i for (i, _) in facts if i + k <= len(facts)]
    if not starts:
        return 1.0
    return float(np.mean([k_hop_vote(net, i, code, k, R, f, seed) == i + k for i in starts]))


def cleanup_recall(net, facts, code, k, f, seed):
    """Single-path cleanup (R=1, decode-and-reclamp) — the JEP-240 baseline."""
    from tools.run_jep240_noise_cleanup import hop_recall
    return hop_recall(net, facts, code, k, "cleanup", f, seed)


def run_seed(seed, K=12):
    code = codes(K + 1, seed)
    facts = make_facts(K, K + 1)
    net = store(facts, code, seed, train=True)

    # fixed f giving single-retrieval single-hop ~0.6-0.85
    f = None
    for cand in [0.25, 0.30, 0.35, 0.40]:
        r = hop_recall_vote(net, facts, code, 1, 1, cand, seed)
        if 0.55 <= r <= 0.85:
            f = cand; break
    if f is None:
        f = 0.30

    out = {"f": f, "single_R1": hop_recall_vote(net, facts, code, 1, 1, f, seed),
           "single_R7": hop_recall_vote(net, facts, code, 1, 7, f, seed),
           "cleanup_k4": cleanup_recall(net, facts, code, 4, f, seed)}
    for R in (1, 3, 7):
        out[f"k4_R{R}"] = hop_recall_vote(net, facts, code, 4, R, f, seed)
    return out


if __name__ == "__main__":
    print("=== JEP-241: redundant aggregation cures substrate multi-hop compounding ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: f={r['f']} single-hop R1={r['single_R1']:.2f} R7={r['single_R7']:.2f} | "
              f"4-hop R1={r['k4_R1']:.2f} R3={r['k4_R3']:.2f} R7={r['k4_R7']:.2f} | "
              f"single-path cleanup 4-hop={r['cleanup_k4']:.2f}", flush=True)

    J241a = all(R[s]['single_R7'] - R[s]['single_R1'] >= 0.10 for s in seeds)
    J241b = all(R[s]['k4_R7'] >= 0.70 for s in seeds)
    J241c = all(R[s]['k4_R7'] > R[s]['k4_R3'] > R[s]['k4_R1'] for s in seeds)
    J241d = all(R[s]['k4_R7'] - R[s]['cleanup_k4'] >= 0.20 for s in seeds)
    passed = J241a and J241b and J241c and J241d

    print("\n--- VERDICT ---", flush=True)
    print(f"J241a aggregation lifts single-hop (>=.10): {J241a}", flush=True)
    print(f"J241b aggregation cures 4-hop (>=0.70)    : {J241b}", flush=True)
    print(f"J241c monotone in redundancy (R7>R3>R1)   : {J241c}", flush=True)
    print(f"J241d aggregation beats cleanup (>=.20)   : {J241d}", flush=True)
    verdict = ("PASS - redundant aggregation is the robust substrate cure for multi-hop compounding (closes the "
               "conceptual arc the JEP-240 NULL opened)") if passed else "NULL/partial"
    print(f"\nJEP-241: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP241"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J241a": J241a, "J241b": J241b,
         "J241c": J241c, "J241d": J241d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
