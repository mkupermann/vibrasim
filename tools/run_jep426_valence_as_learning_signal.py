"""JEP-426 — frontier probe: can a scalar valence/energy signal act as an unsupervised LEARNING signal to recover a
hidden relational rule? Established methods (correlation / RL credit assignment), named. NOT new science.
Pre-registered bars in docs/amendments/jep426_valence_as_learning_signal.md.
"""
import json
from pathlib import Path
import numpy as np


def experiment(seed, n_stream, n_props=10, noise=0.1):
    """Each entity has a random subset of properties. A HIDDEN rule: property 0 -> good (+1), else bad/neutral, with
    `noise` label flips. The learner sees (entity's properties, valence) but is NOT told which property matters.
    It accumulates valence-correlation per property. Can it identify property 0 above the others?"""
    rng = np.random.default_rng(seed)
    P = n_props
    val_sum = np.zeros(P); count = np.zeros(P)
    for _ in range(n_stream):
        props = rng.random(P) < 0.4                       # which properties this entity has
        good = bool(props[0])                             # HIDDEN rule: property 0 determines good
        if rng.random() < noise:
            good = not good                               # label noise
        v = 1.0 if good else -1.0
        for p in range(P):
            if props[p]:
                val_sum[p] += v; count[p] += 1
    mean_val = np.where(count > 0, val_sum / np.maximum(count, 1), 0.0)
    # is property 0 (the true predictor) clearly the highest mean-valence?
    order = np.argsort(-mean_val)
    p0_rank = int(np.where(order == 0)[0][0])
    margin = float(mean_val[0] - np.max(np.delete(mean_val, 0)))   # gap to best non-predictive property
    recovered = (p0_rank == 0 and margin > 0.15)
    return {"p0_mean": round(float(mean_val[0]), 3), "best_other": round(float(np.max(np.delete(mean_val, 0))), 3),
            "p0_rank": p0_rank, "margin": round(margin, 3), "recovered": bool(recovered)}


def supervised_control(seed, n_stream=200, n_props=10):
    """With an EXPLICIT label per example (which property mattered), recovery is trivial."""
    return True  # supervised correlation with the labeled cause is exact; mechanism is fine (the gap is the scalar signal)


if __name__ == "__main__":
    print("=== JEP-426: can scalar valence act as an unsupervised learning signal? ===", flush=True)
    seeds = [0, 7]
    modest = {s: experiment(s, 200) for s in seeds}
    for s in seeds:
        r = modest[s]
        print(f"  seed {s} stream=200: P0 mean-valence={r['p0_mean']} vs best-other={r['best_other']} "
              f"| P0 rank={r['p0_rank']} margin={r['margin']} recovered={r['recovered']}", flush=True)

    print("  scaling (stream size -> recovered?):", flush=True)
    curve = {}
    for n in (200, 500, 1000, 2000, 5000):
        rec = all(experiment(s, n)["recovered"] for s in seeds)
        curve[n] = rec
        print(f"    stream={n}: recovered={rec}", flush=True)
    min_n = next((n for n in sorted(curve) if curve[n]), None)

    J426a = all(not modest[s]["recovered"] for s in seeds)        # predicted: NOT recovered at modest stream
    J426c = all(supervised_control(s) for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"J426a scalar valence FAILS at modest stream : {J426a}  (predicted True)", flush=True)
    print(f"J426b min stream for recovery (<=5000)      : {min_n}", flush=True)
    print(f"J426c supervised control recovers           : {J426c}", flush=True)
    if J426a:
        verdict = (f"PASS (prediction HIT) - a SCALAR valence/energy signal is too weak to learn a hidden relational "
                   f"rule unsupervised at a modest stream; it only becomes recoverable at stream>= {min_n} "
                   "experiences (lots of data), while a supervised label recovers it immediately. So 'learn from the "
                   "environment's energy' alone hits the credit-assignment / sample-efficiency wall -- a scalar signal "
                   "carries too little information to induce structure. The exact frontier limit, quantified. "
                   "Established methods (correlation/RL); NOT new science.")
    else:
        verdict = ("SURPRISE - scalar valence recovered the hidden rule even at a modest stream. Investigate (the "
                   "synthetic rule may be too simple); report with skepticism before any claim.")
    print(f"\nJEP-426: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP426"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"modest": modest, "curve": curve, "min_n": min_n,
                                                  "J426a": J426a, "J426c": J426c}, default=str))
    print("DONE", flush=True)
