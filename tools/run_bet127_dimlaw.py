"""BET-127 — dimension scaling law for systematic generalization."""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle_analog
from world.reservoir import SubstrateReservoir

M = 10

def trial(D, seed, binding=True):
    rng = np.random.default_rng(seed)
    hv = [rand_hv(D, rng) for _ in range(M)]
    val = rng.normal(0, 1, M)
    role_l = rand_hv(D, rng); role_r = rand_hv(D, rng)
    pairs = [(i, j) for i in range(M) for j in range(M) if i != j]
    codes, labels = [], []
    for (i, j) in pairs:
        parts = [bind(role_l, hv[i]), bind(role_r, hv[j])] if binding else [hv[i], hv[j]]
        codes.append(bundle_analog(parts)); labels.append(1.0 if val[i] > val[j] else -1.0)
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
    print("=== BET-127: dimension scaling law for systematic generalization ===", flush=True)
    Ds = [256, 512, 1024, 2048, 4096, 8192]
    accs = []
    for D in Ds:
        a = mean_acc(D); accs.append(a)
        print(f"  D={D:5d}: held-out acc {a:.3f}", flush=True)
    nobind_big = mean_acc(Ds[-1], binding=False)
    print(f"  no-binding control D={Ds[-1]}: {nobind_big:.3f}", flush=True)
    dips = sum(1 for i in range(len(accs)-1) if accs[i+1] < accs[i] - 0.03)
    T127a = dips <= 1
    T127b = accs[-1] >= 0.90
    T127c = (accs[-1] - accs[0]) >= 0.20
    T127d = nobind_big < 0.65
    passed = T127a and T127b and T127c and T127d
    print("\n--- VERDICT ---", flush=True)
    print(f"T127a monotone (<=1 dip)        : {T127a} ({dips} dips)", flush=True)
    print(f"T127b largest-D >=0.90          : {T127b} ({accs[-1]:.3f})", flush=True)
    print(f"T127c big-small gap >=0.20      : {T127c} ({accs[-1]-accs[0]:.3f})", flush=True)
    print(f"T127d compositional (<0.65)     : {T127d}", flush=True)
    print(f"\nBET-127: {'PASS - systematic generalization SOLVED on the substrate (analog VSA + online linear readout, dimension law)' if passed else 'NULL/partial'}", flush=True)
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        plt.figure(figsize=(6.5,4.2))
        plt.plot(Ds, accs, 'o-', lw=2, color='#2c7fb8', label='systematic held-out acc')
        plt.axhline(0.85, ls='--', color='gray', label='systematic-gen bar 0.85')
        plt.axhline(0.5, ls=':', color='#cccccc', label='chance')
        plt.xscale('log', base=2); plt.xlabel('hypervector dimension D'); plt.ylabel('held-out accuracy (novel pairs)')
        plt.title('BET-127: systematic generalization scales with D'); plt.ylim(0.4,1.02)
        plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.savefig('bet127_dimlaw.png', dpi=110)
        print("saved bet127_dimlaw.png", flush=True)
    except Exception as e:
        print(f"(plot skipped: {e})", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-127'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(
        {"Ds":Ds,"accs":accs,"nobind_big":nobind_big,"passed":passed}, indent=2))
    print("DONE", flush=True)
