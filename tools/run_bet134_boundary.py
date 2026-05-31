"""BET-134 — which non-separable two-word rules generalize on the substrate."""
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
    val = rng.normal(0, 1, V)
    pos1 = rand_hv(D, rng); pos2 = rand_hv(D, rng)
    cleanup = CleanupMemory()
    for k in range(V):
        cleanup.add(f"w{k:02d}", word[k])
    return rng, word, val, pos1, pos2, cleanup

def ctx(a, b, word, pos1, pos2, mask_pos2=False):
    parts = [bind(pos1, word[a])]
    if not mask_pos2:
        parts.append(bind(pos2, word[b]))
    c = bundle_analog(parts); return c / np.linalg.norm(c)

def run_selection(seed=0, random_target=False, mask_pos2=False, checkpoints=(0.25, 1.0)):
    rng, word, val, pos1, pos2, cleanup = setup(seed)
    bigrams = [(a, b) for a in range(V) for b in range(V) if a != b]
    rng.shuffle(bigrams); te = bigrams[:44]; tr = bigrams[44:]
    rand_tgt = {p: int(rng.integers(V)) for p in bigrams}
    def target(a, b):
        if random_target: return rand_tgt[(a, b)]
        return a if val[a] > val[b] else b               # the LARGER word
    net = SubstrateReservoir(D, D, D=D, seed=seed, ridge=1e-2)
    net.features = lambda x: np.asarray(x, float)
    net.P = np.eye(D)/1e-2; net.Wout = np.zeros((D, D)); net.D = D
    def acc():
        ok = 0
        for (a, b) in te:
            name, _ = cleanup.cleanup(net.predict(ctx(a, b, word, pos1, pos2, mask_pos2)))
            if int(name[1:]) == target(a, b): ok += 1
        return ok/len(te)
    accs = {}; cps = sorted(set(int(round(f*len(tr))) for f in checkpoints))
    for i,(a,b) in enumerate(tr,1):
        net.learn_online(ctx(a,b,word,pos1,pos2,mask_pos2), word[target(a,b)])
        if i in cps: accs[i]=acc()
    return accs

def run_modular_reservoir(seed=0):
    rng, word, val, pos1, pos2, cleanup = setup(seed)
    bigrams = [(a,b) for a in range(V) for b in range(V) if a!=b]
    rng.shuffle(bigrams); te=bigrams[:44]; tr=bigrams[44:]
    net = SubstrateReservoir(D, D, D=2000, spectral=1.4, seed=seed, ridge=1e-1)  # REAL nonlinear reservoir
    def acc():
        ok=0
        for (a,b) in te:
            name,_=cleanup.cleanup(net.predict(ctx(a,b,word,pos1,pos2)))
            if int(name[1:])==(a+b)%V: ok+=1
        return ok/len(te)
    for (a,b) in tr:
        net.learn_online(ctx(a,b,word,pos1,pos2), word[(a+b)%V])
    return acc()

if __name__ == "__main__":
    print("=== BET-134: which non-separable two-word rules generalize ===", flush=True)
    sel = run_selection(); k=sorted(sel); s_early,s_full=sel[k[0]],sel[k[-1]]
    sel_rnd = run_selection(random_target=True); sr=sel_rnd[sorted(sel_rnd)[-1]]
    sel_one = run_selection(mask_pos2=True); so=sel_one[sorted(sel_one)[-1]]
    mod_res = run_modular_reservoir()
    print(f"  selection held-out @25%/@100% : {s_early:.3f} / {s_full:.3f}", flush=True)
    print(f"  selection no-rule control     : {sr:.3f}", flush=True)
    print(f"  selection single-slot         : {so:.3f}", flush=True)
    print(f"  modular WITH reservoir        : {mod_res:.3f}", flush=True)
    T134a=s_full>=0.85; T134b=sr<0.40; T134c=so<0.65; T134d=mod_res<0.40
    passed=T134a and T134b and T134c and T134d
    print("\n--- VERDICT ---", flush=True)
    print(f"T134a structured generalizes (>=0.85): {T134a} ({s_full:.3f})", flush=True)
    print(f"T134b not noise (<0.40)              : {T134b} ({sr:.3f})", flush=True)
    print(f"T134c needs both (<0.65)             : {T134c} ({so:.3f})", flush=True)
    print(f"T134d unstructured unreachable(<0.40): {T134d} ({mod_res:.3f})", flush=True)
    print(f"\nBET-134: {'PASS - boundary mapped: structured non-separable rules generalize, arbitrary non-linear maps over random codes do not' if passed else 'NULL/partial'}", flush=True)
    out=Path.home()/'.eqmod'/'bet'/'BET-134'; out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps(
        {"sel_full":s_full,"sel_early":s_early,"sel_rnd":sr,"sel_one":so,"mod_res":mod_res,"passed":passed},indent=2))
    print("DONE", flush=True)
