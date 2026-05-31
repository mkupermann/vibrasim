"""BET-133 — two-word compositional next-word generalization to novel bigrams."""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle_analog, CleanupMemory
from world.reservoir import SubstrateReservoir

D = 512
V = 12

def setup(seed):
    rng = np.random.default_rng(seed)
    word = [rand_hv(D, rng) for _ in range(V)]
    pos1 = rand_hv(D, rng); pos2 = rand_hv(D, rng)
    cleanup = CleanupMemory()
    for k in range(V):
        cleanup.add(f"w{k:02d}", word[k])
    return rng, word, pos1, pos2, cleanup

def ctx(a, b, word, pos1, pos2, mask_pos2=False):
    parts = [bind(pos1, word[a])]
    if not mask_pos2:
        parts.append(bind(pos2, word[b]))
    c = bundle_analog(parts); return c / np.linalg.norm(c)

def run(seed=0, random_target=False, mask_pos2=False, checkpoints=(0.25, 1.0)):
    rng, word, pos1, pos2, cleanup = setup(seed)
    bigrams = [(a, b) for a in range(V) for b in range(V) if a != b]   # 132 contexts
    rng.shuffle(bigrams)
    te = bigrams[:44]; tr = bigrams[44:]                              # held-out novel bigrams
    rand_tgt = {p: int(rng.integers(V)) for p in bigrams}
    def target(a, b):
        return rand_tgt[(a, b)] if random_target else (a + b) % V
    net = SubstrateReservoir(D, D, D=D, seed=seed, ridge=1e-2)
    net.features = lambda x: np.asarray(x, float)
    net.P = np.eye(D) / 1e-2; net.Wout = np.zeros((D, D)); net.D = D

    def acc():
        ok = 0
        for (a, b) in te:
            c = ctx(a, b, word, pos1, pos2, mask_pos2)
            name, _ = cleanup.cleanup(net.predict(c))
            if int(name[1:]) == target(a, b): ok += 1
        return ok / len(te)

    accs = {}; cps = sorted(set(int(round(f*len(tr))) for f in checkpoints))
    for i, (a, b) in enumerate(tr, 1):
        c = ctx(a, b, word, pos1, pos2, mask_pos2)
        net.learn_online(c, word[target(a, b)])
        if i in cps: accs[i] = acc()
    return accs

if __name__ == "__main__":
    print("=== BET-133: two-word compositional next-word (novel bigrams) ===", flush=True)
    accs = run(); k = sorted(accs); early, full = accs[k[0]], accs[k[-1]]
    rnd = run(random_target=True); rnd_full = rnd[sorted(rnd)[-1]]
    one = run(mask_pos2=True); one_full = one[sorted(one)[-1]]
    print(f"  held-out acc @25% / @100% : {early:.3f} / {full:.3f}", flush=True)
    print(f"  no-rule (random) control  : {rnd_full:.3f}", flush=True)
    print(f"  single-word (POS2 masked) : {one_full:.3f}", flush=True)
    T133a = full >= 0.85; T133b = (full-early) >= 0.15; T133c = rnd_full < 0.30; T133d = one_full < 0.45
    passed = T133a and T133b and T133c and T133d
    print("\n--- VERDICT ---", flush=True)
    print(f"T133a held-out >=0.85    : {T133a} ({full:.3f})", flush=True)
    print(f"T133b online gain >=0.15 : {T133b} ({full-early:.3f})", flush=True)
    print(f"T133c no-rule <0.30      : {T133c} ({rnd_full:.3f})", flush=True)
    print(f"T133d needs both <0.45   : {T133d} ({one_full:.3f})", flush=True)
    print(f"\nBET-133: {'PASS - two-word compositional generalization to unseen bigrams, online, no transformer' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-133'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(
        {"early":early,"full":full,"random":rnd_full,"single":one_full,"passed":passed}, indent=2))
    print("DONE", flush=True)
