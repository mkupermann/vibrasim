"""BET-125 — systematic generalization over VSA-composed substrate codes."""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle
from world.reservoir import SubstrateReservoir

D = 1024
M = 10

def build(seed=0, shuffle_labels=False, binding=True):
    rng = np.random.default_rng(seed)
    hv = [rand_hv(D, rng) for _ in range(M)]
    val = rng.normal(0, 1, M)
    role_l = rand_hv(D, rng); role_r = rand_hv(D, rng)
    pairs = [(i, j) for i in range(M) for j in range(M) if i != j]
    codes, labels = [], []
    for (i, j) in pairs:
        if binding:
            c = bundle([bind(role_l, hv[i]), bind(role_r, hv[j])])
        else:
            c = bundle([hv[i], hv[j]])               # no roles: code(i,j)==code(j,i)
        codes.append(c.astype(float))
        labels.append(1.0 if val[i] > val[j] else -1.0)
    codes = np.array(codes); labels = np.array(labels)
    if shuffle_labels:
        labels = labels[rng.permutation(len(labels))]
    idx = rng.permutation(len(pairs))
    tr, te = idx[:54], idx[54:]                       # 60% / 40% held-out combinations
    return codes, labels, tr, te

def run(reservoir, **kw):
    codes, labels, tr, te = build(**kw)
    if reservoir:
        net = SubstrateReservoir(D, 1, D=900, spectral=1.4, seed=2, ridge=1e-1)
    else:
        net = SubstrateReservoir(D, 1, D=D, seed=2, ridge=1e-2)
        net.features = lambda x: np.asarray(x, float)
        net.P = np.eye(D) / 1e-2; net.Wout = np.zeros((1, D)); net.D = D
    for i in tr:                                      # ONLINE, one pair at a time
        net.learn_online(codes[i], [labels[i]])
    pred = np.array([np.sign(net.predict(codes[i])[0]) for i in te])
    return float(np.mean(pred == labels[te]))

if __name__ == "__main__":
    print("=== BET-125: systematic generalization over composed codes ===", flush=True)
    res = run(reservoir=True)
    lin = run(reservoir=False)
    nobind = run(reservoir=True, binding=False)
    shuf = run(reservoir=True, shuffle_labels=True)
    best = max(res, lin)
    print(f"  reservoir   held-out acc : {res:.3f}", flush=True)
    print(f"  linear-VSA  held-out acc : {lin:.3f}", flush=True)
    print(f"  no-binding  control      : {nobind:.3f}", flush=True)
    print(f"  shuffled-lbl control     : {shuf:.3f}", flush=True)
    T125a = best >= 0.85; T125b = nobind < 0.65; T125c = shuf < 0.65
    passed = T125a and T125b and T125c
    print("\n--- VERDICT ---", flush=True)
    print(f"T125a systematic gen (best>=0.85)   : {T125a}", flush=True)
    print(f"T125b composition carries (<0.65)   : {T125b}", flush=True)
    print(f"T125c relation learned (shuf<0.65)  : {T125c}", flush=True)
    print(f"\nBET-125: {'PASS - systematic generalization over novel symbol combinations' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-125'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(
        {"res":res,"lin":lin,"nobind":nobind,"shuf":shuf,"passed":passed}, indent=2))
    print("DONE", flush=True)
