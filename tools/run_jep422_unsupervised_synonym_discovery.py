"""JEP-422 — frontier probe: can the substrate DISCOVER synonyms unsupervised via relational-profile (distributional)
similarity? Established method (Jaccard / distributional hypothesis), named as such. No transformer.
Pre-registered bars in docs/amendments/jep422_unsupervised_synonym_discovery.md.
"""
import json
from pathlib import Path
import numpy as np


def build_world(seed, overlap, n_contexts=40, n_pairs=8, n_random=8):
    """Each entity participates in a set of (role, value) contexts. A TRUE synonym pair shares `overlap` fraction of
    contexts; the rest are private. Random pairs share contexts only by chance. Returns profiles (entity -> set)."""
    rng = np.random.default_rng(seed)
    contexts = [f"ctx{i}" for i in range(n_contexts)]
    profiles = {}
    # true synonym pairs: a, a' share `overlap` of a's contexts
    base_k = 12
    truth = []
    for p in range(n_pairs):
        base = set(rng.choice(n_contexts, base_k, replace=False).tolist())
        shared_k = int(round(overlap * base_k))
        shared = set(list(base)[:shared_k])
        # the synonym keeps the shared, swaps the rest for fresh contexts
        priv2 = set(rng.choice(n_contexts, base_k - shared_k, replace=False).tolist()) - base
        prof_a = base
        prof_b = shared | priv2
        profiles[f"word_a{p}"] = prof_a
        profiles[f"word_b{p}"] = prof_b
        truth.append((f"word_a{p}", f"word_b{p}"))
    # random independent entities (non-synonyms)
    rand_entities = []
    for r in range(n_random + n_pairs):
        e = f"rand{r}"
        profiles[e] = set(rng.choice(n_contexts, base_k, replace=False).tolist())
        rand_entities.append(e)
    return profiles, truth, rand_entities


def jaccard(a, b):
    u = len(a | b)
    return len(a & b) / u if u else 0.0


def run_seed(seed, overlap):
    profiles, truth, rand_entities = build_world(seed, overlap)
    true_sims = [jaccard(profiles[a], profiles[b]) for (a, b) in truth]
    # random pairs (entities NOT synonyms of each other)
    rng = np.random.default_rng(seed + 1)
    rand_sims = []
    keys = list(profiles.keys())
    truth_set = {frozenset(p) for p in truth}
    for _ in range(200):
        x, y = rng.choice(keys, 2, replace=False)
        if frozenset((x, y)) in truth_set:
            continue
        rand_sims.append(jaccard(profiles[x], profiles[y]))
    return {"true_min": round(float(min(true_sims)), 3), "true_med": round(float(np.median(true_sims)), 3),
            "rand_max": round(float(max(rand_sims)), 3), "rand_p95": round(float(np.percentile(rand_sims, 95)), 3),
            "separable": bool(min(true_sims) > max(rand_sims))}


if __name__ == "__main__":
    print("=== JEP-422: unsupervised synonym discovery via relational-profile similarity ===", flush=True)
    seeds = [0, 7]
    hi = {s: run_seed(s, 0.9) for s in seeds}
    real = {s: run_seed(s, 0.55) for s in seeds}
    for s in seeds:
        print(f"  seed {s} overlap=0.9 : true[min={hi[s]['true_min']},med={hi[s]['true_med']}] "
              f"rand[max={hi[s]['rand_max']},p95={hi[s]['rand_p95']}] separable={hi[s]['separable']}", flush=True)
        print(f"  seed {s} overlap=0.55: true[min={real[s]['true_min']},med={real[s]['true_med']}] "
              f"rand[max={real[s]['rand_max']},p95={real[s]['rand_p95']}] separable={real[s]['separable']}", flush=True)

    # break-point curve
    print("  break-point curve (clean separation true_min > rand_max?):", flush=True)
    curve = {}
    for ov in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        sep = all(run_seed(s, ov)["separable"] for s in seeds)
        curve[ov] = sep
        print(f"    overlap={ov}: separable={sep}", flush=True)
    min_sep = next((ov for ov in sorted(curve) if curve[ov]), None)

    J422a = all(hi[s]["separable"] for s in seeds)
    J422b_null = all(not real[s]["separable"] for s in seeds)     # predicted: NOT separable at realistic overlap
    print("\n--- VERDICT ---", flush=True)
    print(f"J422a high-overlap (0.9) separable      : {J422a}  (predicted True)", flush=True)
    print(f"J422b realistic-overlap (0.55) NOT sep. : {J422b_null}  (predicted True = unsupervised discovery fails)",
          flush=True)
    print(f"J422c min overlap for clean separation  : {min_sep}", flush=True)
    if J422a and J422b_null:
        verdict = (f"PASS (prediction HIT) - unsupervised synonym DISCOVERY works only at near-identical usage "
                   f"(overlap>= {min_sep}); at realistic partial overlap (0.55) true synonyms are NOT separable from "
                   "random pairs. So distributional/relational-profile similarity over a small symbolic store CANNOT "
                   "reliably discover synonyms -- it needs the massive co-occurrence statistics LLMs/word2vec use. The "
                   "frontier limit, quantified. Established method (distributional hypothesis); NOT new science.")
    elif J422a and not J422b_null:
        verdict = ("SURPRISE - true synonyms ARE separable even at 0.55 overlap: unsupervised discovery works better "
                   "than predicted in this regime. Investigate before trusting (likely the synthetic overlap is too "
                   "clean vs real usage).")
    else:
        verdict = "NULL/partial - even high overlap not separable; see rows."
    print(f"\nJEP-422: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP422"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"hi": hi, "real": real, "curve": curve, "min_sep": min_sep,
                                                  "J422a": J422a, "J422b_null": J422b_null}, default=str))
    print("DONE", flush=True)
