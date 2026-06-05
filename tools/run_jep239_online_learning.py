"""JEP-239 — does the substrate learn the relational store ONLINE (continual, no catastrophic forgetting)?

Present is-a facts one at a time; after each, a few LOCAL contrastive-Hebbian updates (pure online vs rehearsal);
measure recall over ALL facts seen so far. Characterizes catastrophic forgetting + the rehearsal cure in the
energy-based relational store. Established (continual learning, replay), named.

Pre-registered bars in docs/amendments/jep239_substrate_online_learning.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from tools.run_jep232_relation_store import KEY, VAL, N

NFACTS = 18
INNER = 8          # local update passes per new fact (vs 120 for batch)
REHEARSE = 4       # replayed old facts per step (rehearsal regime)


def codes(n, seed):
    rng = np.random.default_rng(seed)
    return [rng.choice([-1.0, 1.0], KEY) for _ in range(n)]


def pat(c, p, code):
    return np.concatenate([code[c], code[p]])


def recall_over(net, facts, code, seed):
    ok = 0
    for c, p in facts:
        net.state = np.random.default_rng(seed + c).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), code[c], steps=40)
        val = np.sign(s[KEY:KEY + VAL])
        sims = np.array([val @ code[k] for k in range(len(code))])
        sims[c] = -np.inf
        ok += int(np.argmax(sims)) == p
    return ok / len(facts)


def run_regime(seed, rehearse):
    code = codes(NFACTS + 1, seed)
    facts = [(i, i + 1) for i in range(NFACTS)]          # a chain (each child a distinct parent)
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    rng = np.random.default_rng(seed + 999)
    seen = []
    new_immediate = []      # J239a: was the just-added fact recalled right after adding?
    all_curve = []          # recall over all-so-far after each addition
    for (c, p) in facts:
        batch = [pat(c, p, code)]
        if rehearse and seen:
            for j in rng.choice(len(seen), size=min(REHEARSE, len(seen)), replace=False):
                cc, pp = seen[j]; batch.append(pat(cc, pp, code))
        for _ in range(INNER):
            net.train_epoch(batch, cue_frac=0.5, lr=0.02, relax_steps=12)
        seen.append((c, p))
        new_immediate.append(recall_over(net, [(c, p)], code, seed))
        all_curve.append(recall_over(net, seen, code, seed))
    return {"new_immediate": float(np.mean(new_immediate)), "all_curve": all_curve,
            "final_all": all_curve[-1]}


def run_seed(seed):
    pure = run_regime(seed, rehearse=False)
    reh = run_regime(seed, rehearse=True)
    return {"pure": pure, "reh": reh}


if __name__ == "__main__":
    print("=== JEP-239: online/continual learning of the substrate relational store ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        pc = r["pure"]["all_curve"]; rc = r["reh"]["all_curve"]
        print(f"  seed {s}: new-fact immediate recall pure={r['pure']['new_immediate']:.2f} reh={r['reh']['new_immediate']:.2f}",
              flush=True)
        print(f"    pure all-so-far curve: {[round(x,2) for x in pc]}", flush=True)
        print(f"    reh  all-so-far curve: {[round(x,2) for x in rc]}", flush=True)
        print(f"    final all-facts recall: pure={r['pure']['final_all']:.2f}  rehearsal={r['reh']['final_all']:.2f}",
              flush=True)

    J239a = all(R[s]['reh']['new_immediate'] >= 0.9 and R[s]['pure']['new_immediate'] >= 0.9 for s in seeds)
    J239b_forgets = all(min(R[s]['pure']['all_curve']) < 0.7 for s in seeds)
    J239c = all(min(R[s]['reh']['all_curve'][3:]) >= 0.85 for s in seeds)   # after a few facts in
    J239d = all(R[s]['reh']['final_all'] - R[s]['pure']['final_all'] >= 0.15 for s in seeds)
    passed = J239a and J239c and J239d

    print("\n--- VERDICT ---", flush=True)
    print(f"J239a online learns the new fact (>=0.9)      : {J239a}", flush=True)
    print(f"J239b pure online FORGETS (<0.7 somewhere)    : {J239b_forgets}", flush=True)
    print(f"J239c rehearsal MAINTAINS (>=0.85)            : {J239c}", flush=True)
    print(f"J239d rehearsal beats pure online (>=0.15)    : {J239d}", flush=True)
    verdict = ("PASS - the substrate learns the relational store ONLINE with rehearsal; pure online "
               + ("FORGETS" if J239b_forgets else "also holds")) if passed else "NULL/partial"
    print(f"\nJEP-239: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP239"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J239a": J239a, "J239b_forgets": J239b_forgets,
         "J239c": J239c, "J239d": J239d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
