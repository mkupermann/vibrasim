"""BET-129 — systematic generalization vs number of training compositions."""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle_analog
from world.reservoir import SubstrateReservoir

M = 14
D = 1024
N_HELD = 40

def trial(n_train, seed, shuffle_labels=False):
    rng = np.random.default_rng(seed)
    hv = [rand_hv(D, rng) for _ in range(M)]
    val = rng.normal(0, 1, M)
    role_l = rand_hv(D, rng); role_r = rand_hv(D, rng)
    pairs = [(i, j) for i in range(M) for j in range(M) if i != j]
    codes, labels = [], []
    for (i, j) in pairs:
        c = bundle_analog([bind(role_l, hv[i]), bind(role_r, hv[j])])
        c = c / np.linalg.norm(c)
        codes.append(c); labels.append(1.0 if val[i] > val[j] else -1.0)
    codes = np.array(codes); labels = np.array(labels)
    if shuffle_labels:
        labels = labels[rng.permutation(len(labels))]
    idx = rng.permutation(len(pairs))
    te = idx[:N_HELD]                          # FIXED held-out set (per seed)
    tr = idx[N_HELD:N_HELD + n_train]          # growing training subset
    net = SubstrateReservoir(D, 1, D=D, seed=seed, ridge=1e-2)
    net.features = lambda x: np.asarray(x, float)
    net.P = np.eye(D) / 1e-2; net.Wout = np.zeros((1, D)); net.D = D
    for i in tr:
        net.learn_online(codes[i], [labels[i]])
    pred = np.array([np.sign(net.predict(codes[i])[0]) for i in te])
    return float(np.mean(pred == labels[te]))

def mean_acc(n, **kw):
    return float(np.mean([trial(n, s, **kw) for s in range(3)]))

if __name__ == "__main__":
    print("=== BET-129: held-out acc vs #training compositions (D=1024) ===", flush=True)
    ns = [20, 40, 60, 90, 120, 142]
    accs = [mean_acc(n) for n in ns]
    for n, a in zip(ns, accs):
        print(f"  train={n:4d}: held-out acc {a:.3f}", flush=True)
    shuf_big = mean_acc(ns[-1], shuffle_labels=True)
    print(f"  shuffled-label control (train={ns[-1]}): {shuf_big:.3f}", flush=True)
    dips = sum(1 for i in range(len(accs)-1) if accs[i+1] < accs[i] - 0.03)
    T129a = dips <= 1
    T129b = accs[-1] >= 0.90
    T129c = (accs[-1] - accs[0]) >= 0.15
    T129d = shuf_big < 0.65
    passed = T129a and T129b and T129c and T129d
    print("\n--- VERDICT ---", flush=True)
    print(f"T129a rising (<=1 dip)   : {T129a} ({dips} dips)", flush=True)
    print(f"T129b max>=0.90          : {T129b} ({accs[-1]:.3f})", flush=True)
    print(f"T129c gain>=0.15         : {T129c} ({accs[-1]-accs[0]:.3f})", flush=True)
    print(f"T129d relation (shuf<0.65): {T129d} ({shuf_big:.3f})", flush=True)
    print(f"\nBET-129: {'PASS - systematic generalization scales with compositions seen (curriculum law); high accuracy, online, no transformer' if passed else 'NULL/partial'}", flush=True)
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        plt.figure(figsize=(6.5,4.2))
        plt.plot(ns, accs, 'o-', lw=2, color='#2ca25f', label='systematic held-out acc')
        plt.axhline(0.90, ls='--', color='gray', label='bar 0.90')
        plt.axhline(0.5, ls=':', color='#cccccc', label='chance')
        plt.xlabel('# training compositions seen (online)'); plt.ylabel('held-out acc (fixed novel pairs)')
        plt.title('BET-129: systematic generalization is a curriculum law'); plt.ylim(0.4,1.02)
        plt.legend(); plt.grid(alpha=0.3); plt.tight_layout(); plt.savefig('bet129_curriculum.png', dpi=110)
        print("saved bet129_curriculum.png", flush=True)
    except Exception as e:
        print(f"(plot skipped: {e})", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-129'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps({"ns":ns,"accs":accs,"shuf_big":shuf_big,"passed":passed}, indent=2))
    print("DONE", flush=True)
