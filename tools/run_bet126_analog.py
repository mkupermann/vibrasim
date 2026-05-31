"""BET-126 — analog superposition restores systematic generalization."""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle, bundle_analog
from world.reservoir import SubstrateReservoir

D = 1024
M = 10

def build(seed=0, shuffle_labels=False, binding=True, analog=True):
    rng = np.random.default_rng(seed)
    hv = [rand_hv(D, rng) for _ in range(M)]
    val = rng.normal(0, 1, M)
    role_l = rand_hv(D, rng); role_r = rand_hv(D, rng)
    sup = bundle_analog if analog else bundle
    pairs = [(i, j) for i in range(M) for j in range(M) if i != j]
    codes, labels = [], []
    for (i, j) in pairs:
        parts = [bind(role_l, hv[i]), bind(role_r, hv[j])] if binding else [hv[i], hv[j]]
        codes.append(sup(parts).astype(float))
        labels.append(1.0 if val[i] > val[j] else -1.0)
    codes = np.array(codes); labels = np.array(labels)
    if shuffle_labels:
        labels = labels[rng.permutation(len(labels))]
    idx = rng.permutation(len(pairs))
    return codes, labels, idx[:54], idx[54:]

def run_linear(**kw):
    codes, labels, tr, te = build(**kw)
    net = SubstrateReservoir(D, 1, D=D, seed=2, ridge=1e-2)
    net.features = lambda x: np.asarray(x, float)
    net.P = np.eye(D) / 1e-2; net.Wout = np.zeros((1, D)); net.D = D
    for i in tr:
        net.learn_online(codes[i], [labels[i]])
    pred = np.array([np.sign(net.predict(codes[i])[0]) for i in te])
    return float(np.mean(pred == labels[te]))

if __name__ == "__main__":
    print("=== BET-126: analog superposition -> systematic generalization ===", flush=True)
    analog = run_linear(analog=True)
    sign_b = run_linear(analog=False)
    nobind = run_linear(analog=True, binding=False)
    shuf   = run_linear(analog=True, shuffle_labels=True)
    print(f"  analog-bundle  held-out acc : {analog:.3f}", flush=True)
    print(f"  sign-bundle    held-out acc : {sign_b:.3f}", flush=True)
    print(f"  no-binding     control      : {nobind:.3f}", flush=True)
    print(f"  shuffled-label control      : {shuf:.3f}", flush=True)
    T126a = analog >= 0.85; T126b = (analog - 0.611) >= 0.15
    T126c = nobind < 0.65;  T126d = shuf < 0.65
    passed = T126a and T126b and T126c and T126d
    print("\n--- VERDICT ---", flush=True)
    print(f"T126a systematic gen (>=0.85)        : {T126a}", flush=True)
    print(f"T126b beats sign-bundle (+>=0.15)    : {T126b}", flush=True)
    print(f"T126c composition carries (<0.65)    : {T126c}", flush=True)
    print(f"T126d relation learned (shuf<0.65)   : {T126d}", flush=True)
    print(f"\nBET-126: {'PASS - first SYSTEMATIC generalization on the substrate (analog VSA + online linear readout)' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-126'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(
        {"analog":analog,"sign":sign_b,"nobind":nobind,"shuf":shuf,"passed":passed}, indent=2))
    print("DONE", flush=True)
