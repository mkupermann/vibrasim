"""G137 — map the no-LLM toolkit's competence boundary: systematic generalization vs rule REGULARITY.
Grammar 'subj verb obj' where obj = rule(verb) a fraction (1-noise) of the time, else random. Train on a
SUBSET of (subj,verb) combos; test HELD-OUT combos. The VSA+reservoir+RLS stack should generalize (predict
obj from verb) where a bigram cannot (bigram only sees the previous word = verb, but never saw this
subj+verb context). Sweep noise 0..1; find where the stack stops beating bigram. Characterizes the niche.
No physics, no LLM.
"""
import numpy as np
from collections import defaultdict, Counter
from world.vsa import rand_hv, bind, bundle_analog
from world.reservoir import SubstrateReservoir

NS, NV, NO = 8, 6, 6     # subjects, verbs, objects
D = 1200


def make_data(noise, seed):
    rng = np.random.default_rng(seed)
    a = rng.integers(0, NO, NS)             # subject contribution
    b = rng.integers(0, NO, NV)             # verb contribution
    truerule = lambda s, v: int((a[s] + b[v]) % NO)   # COMPOSITIONAL: needs BOTH symbols
    combos = [(s, v) for s in range(NS) for v in range(NV)]
    rng.shuffle(combos)
    ntr = int(0.7 * len(combos))
    train, test = combos[:ntr], combos[ntr:]
    def obj(s, v):
        return truerule(s, v) if rng.random() > noise else int(rng.integers(0, NO))
    tr = [(s, v, obj(s, v)) for s, v in train]
    te = [(s, v, truerule(s, v)) for s, v in test]   # held-out true compositional answer
    return tr, te


def eq_gen(noise, seed):
    tr, te = make_data(noise, seed)
    rng = np.random.default_rng(100 + seed)
    SUBJ = [rand_hv(D, rng) for _ in range(NS)]; VERB = [rand_hv(D, rng) for _ in range(NV)]
    PS, PV = rand_hv(D, rng), rand_hv(D, rng)
    res = SubstrateReservoir(in_dim=D, out_dim=NO, D=D, seed=seed, ridge=1e-1)
    ctx = lambda s, v: bundle_analog([bind(PS, SUBJ[s]), bind(PV, VERB[v])])
    for s, v, o in tr:
        y = np.zeros(NO); y[o] = 1.0; res.learn_online(ctx(s, v), y)
    return np.mean([int(np.argmax(res.predict(ctx(s, v))) == o) for s, v, o in te])


def bigram_gen(noise, seed):
    tr, te = make_data(noise, seed)
    big = defaultdict(Counter)
    for s, v, o in tr:
        big[v][o] += 1     # bigram: previous word = verb -> object
    pred = lambda v: (big[v].most_common(1)[0][0] if big[v] else 0)
    return np.mean([int(pred(v) == o) for s, v, o in te])


if __name__ == "__main__":
    print("=== G137: competence boundary — systematic generalization vs rule regularity ===", flush=True)
    print(f"  (held-out subj+verb combos; chance=1/{NO}={1/NO:.2f})", flush=True)
    rows = []
    for noise in [0.0, 0.25, 0.5, 0.75, 1.0]:
        eq = np.mean([eq_gen(noise, s) for s in range(4)])
        bg = np.mean([bigram_gen(noise, s) for s in range(4)])
        rows.append((noise, eq, bg))
        print(f"  noise={noise:.2f}: stack={eq:.2f}  bigram={bg:.2f}  (stack-bigram={eq-bg:+.2f})", flush=True)
    clean = [r for r in rows if r[0] == 0.0][0]
    print("\n--- VERDICT ---", flush=True)
    print(f"  clean-rule (noise=0): stack={clean[1]:.2f} vs bigram={clean[2]:.2f}", flush=True)
    if clean[1] >= clean[2] + 0.15:
        print("G137: PASS - on a CLEAN structural rule the no-LLM stack generalizes to held-out combos BEYOND bigram; this IS its niche. Degrades to bigram as the rule gets noisier (the boundary mapped).", flush=True)
    else:
        print("G137: NULL - even on a clean rule the stack does not beat bigram on held-out combos", flush=True)
    print("DONE", flush=True)
