"""BET-122 — vector-symbolic composition & generalization on the substrate."""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle, CleanupMemory

ROLES = ["SUBJ", "VERB", "OBJ"]

def build(D, vocab_per_role, seed=0):
    rng = np.random.default_rng(seed)
    roles = {r: rand_hv(D, rng) for r in ROLES}
    vocab = {r: {f"{r[0].lower()}{i}": rand_hv(D, rng) for i in range(vocab_per_role)}
             for r in ROLES}
    return rng, roles, vocab

def encode(roles, vocab, s, v, o):
    return bundle([bind(roles["SUBJ"], vocab["SUBJ"][s]),
                   bind(roles["VERB"], vocab["VERB"][v]),
                   bind(roles["OBJ"],  vocab["OBJ"][o])])

def retrieval_acc(D, vpr, n_test=400, seed=0, control=False):
    rng, roles, vocab = build(D, vpr, seed)
    cm = {r: CleanupMemory() for r in ROLES}
    for r in ROLES:
        for name, hv in vocab[r].items():
            cm[r].add(name, hv)
    keys = {r: list(vocab[r]) for r in ROLES}
    correct = tot = 0
    for _ in range(n_test):
        s = keys["SUBJ"][rng.integers(vpr)]
        v = keys["VERB"][rng.integers(vpr)]
        o = keys["OBJ"][rng.integers(vpr)]
        F = encode(roles, vocab, s, v, o)
        for r, true in [("SUBJ", s), ("VERB", v), ("OBJ", o)]:
            key = rand_hv(D, rng) if control else roles[r]
            got, _ = cm[r].cleanup(bind(F, key))
            correct += (got == true); tot += 1
    return correct / tot

if __name__ == "__main__":
    print("=== BET-122: vector-symbolic composition & generalization ===", flush=True)
    # 'seen' vs 'novel' is moot for algebra (no storing of whole sentences) — every
    # query is on a freshly composed sentence, so high accuracy IS generalization to
    # arbitrary (novel) combinations. We measure across many random combinations and
    # a control with the binding structure destroyed.
    a = retrieval_acc(4000, 30)
    novel = retrieval_acc(4000, 30, seed=123)        # different random combos
    big = retrieval_acc(4000, 60)
    ctrl = retrieval_acc(4000, 30, control=True)
    print(f"  role retrieval (vocab 30/role): {a:.3f}", flush=True)
    print(f"  novel combinations            : {novel:.3f}", flush=True)
    print(f"  larger vocab (60/role)        : {big:.3f}", flush=True)
    print(f"  control (no binding)          : {ctrl:.3f}", flush=True)
    T122a = a >= 0.95; T122b = novel >= 0.95; T122c = big >= 0.90; T122d = ctrl < 0.10
    passed = T122a and T122b and T122c and T122d
    print("\n--- VERDICT ---", flush=True)
    print(f"T122a binding (>=0.95)     : {T122a}", flush=True)
    print(f"T122b generalizes (>=0.95) : {T122b}", flush=True)
    print(f"T122c capacity (>=0.90)    : {T122c}", flush=True)
    print(f"T122d control fails (<0.10): {T122d}", flush=True)
    print(f"\nBET-122: {'PASS - compositional generalization on the substrate (no transformer)' if passed else 'NULL'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-122'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps({"acc":a,"novel":novel,"big":big,"ctrl":ctrl,"passed":passed},indent=2))
    print("DONE", flush=True)
