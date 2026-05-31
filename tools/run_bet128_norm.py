"""BET-128 — code normalization removes the high-D overfit collapse."""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle_analog
from world.reservoir import SubstrateReservoir

M = 10

def _norm(c):
    n = np.linalg.norm(c)
    return c / n if n > 0 else c

def trial(D, seed, binding=True, normalize=True):
    rng = np.random.default_rng(seed)
    hv = [rand_hv(D, rng) for _ in range(M)]
    val = rng.normal(0, 1, M)
    role_l = rand_hv(D, rng); role_r = rand_hv(D, rng)
    pairs = [(i, j) for i in range(M) for j in range(M) if i != j]
    codes, labels = [], []
    for (i, j) in pairs:
        parts = [bind(role_l, hv[i]), bind(role_r, hv[j])] if binding else [hv[i], hv[j]]
        c = bundle_analog(parts)
        if normalize: c = _norm(c)
        codes.append(c); labels.append(1.0 if val[i] > val[j] else -1.0)
    codes = np.array(codes); labels = np.array(labels)
    idx = rng.permutation(len(pairs)); tr, te = idx[:54], idx[54:]
    net = SubstrateReservoir(D, 1, D=D, seed=seed, ridge=1e-2)
    net.features = lambda x: np.asarray(x, float)
    net.P = np.eye(D) / 1e-2; net.Wout = np.zeros((1, D)); net.D = D
    for i in tr:
        net.learn_online(codes[i], [labels[i]])
    pred = np.array([np.sign(net.predict(codes[i])[0]) for i in te])
    return float(np.mean(pred == labels[te]))

def mean_acc(D, **kw):
    return float(np.mean([trial(D, s, **kw) for s in range(3)]))

if __name__ == "__main__":
    print("=== BET-128: normalized codes vs high-D overfit ===", flush=True)
    Ds = [256, 512, 1024, 2048, 4096, 8192]
    norm_accs = [mean_acc(D, normalize=True) for D in Ds]
    for D, a in zip(Ds, norm_accs):
        print(f"  D={D:5d} normalized: held-out acc {a:.3f}", flush=True)
    nobind_big = mean_acc(Ds[-1], normalize=True, binding=False)
    print(f"  no-binding normalized control D={Ds[-1]}: {nobind_big:.3f}", flush=True)
    dips = sum(1 for i in range(len(norm_accs)-1) if norm_accs[i+1] < norm_accs[i] - 0.03)
    T128a = norm_accs[-1] >= 0.85
    T128b = dips <= 1
    T128c = max(norm_accs) >= 0.88
    T128d = nobind_big < 0.65
    passed = T128a and T128b and T128c and T128d
    print("\n--- VERDICT ---", flush=True)
    print(f"T128a largest-D >=0.85   : {T128a} ({norm_accs[-1]:.3f})", flush=True)
    print(f"T128b stable (<=1 dip)   : {T128b} ({dips} dips)", flush=True)
    print(f"T128c best-D >=0.88      : {T128c} ({max(norm_accs):.3f})", flush=True)
    print(f"T128d compositional<0.65 : {T128d} ({nobind_big:.3f})", flush=True)
    print(f"\nBET-128: {'PASS - systematic symbolic-combination generalization SOLVED & robust on the substrate' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-128'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(
        {"Ds":Ds,"norm_accs":norm_accs,"nobind_big":nobind_big,"passed":passed}, indent=2))
    print("DONE", flush=True)
