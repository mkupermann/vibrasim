"""BET-118 — sparse distributed representations to reduce sequence interference."""
import json
from pathlib import Path
import numpy as np
from world.energy import EnergyNet

L = 4

def sparse_pat(N, a, rng):
    p = -np.ones(N); on = rng.random(N) < a; p[on] = 1.0; return p

def run(npm, S, a=0.15, sparse=True, shuffle_T=False, seed=0):
    net = EnergyNet(n_per_module=npm, n_modules=2, p_in=0.5, p_cross=0.04,
                    beta=1.5, seed=seed)
    N = net.N; rng = np.random.default_rng(7)
    mu = (2*a - 1) if sparse else 0.0
    seqs = []
    for s in range(S):
        seqs.append([sparse_pat(N, a, rng) if sparse else rng.choice([-1.,1.],N)
                     for _ in range(L)])
    # centered covariance learning for W (attractors) and T (transitions)
    for sq in seqs:
        for p in sq:
            net.W += 0.02*np.outer(p-mu, p-mu)*net.M
        for t in range(L-1):
            net.T += 0.06*np.outer(sq[t+1]-mu, sq[t]-mu)*net.M
    np.fill_diagonal(net.W,0); net.W=0.5*(net.W+net.W.T); np.fill_diagonal(net.T,0)
    if shuffle_T:
        net.T = rng.permutation(net.T.flatten()).reshape(net.T.shape)
    # recall: predict via T (centered), threshold back to sparse, light clean-up
    thr = 0.0
    mn = 1.0
    for sq in seqs:
        state = sq[0].copy(); rec=[state.copy()]
        for _ in range(L-1):
            field = (net.T*net.M)@(state-mu)
            nxt = np.where(field > thr, 1.0, -1.0)
            # one clean-up half-step toward nearest attractor
            f2 = (net.W*net.M)@(nxt-mu)
            nxt = np.where(f2 > thr, 1.0, -1.0)
            state = nxt; rec.append(state.copy())
        ov=[float(np.mean(np.sign(r)==np.sign(p))) for r,p in zip(rec,sq)]
        mn=min(mn,min(ov))
    return mn

if __name__=="__main__":
    print("=== BET-118: sparse distributed representations ===", flush=True)
    s3=run(150,3,sparse=True); s5=run(150,5,sparse=True)
    ctrl=run(150,3,sparse=True,shuffle_T=True)
    print(f"sparse S=3 @N300: {s3:.3f}", flush=True)
    print(f"sparse S=5 @N300: {s5:.3f}", flush=True)
    print(f"sparse control (shuffled T): {ctrl:.3f}", flush=True)
    T118a=s3>=0.90; T118b=s5>=0.85; T118c=ctrl<0.70
    passed=T118a and T118b and T118c
    print("\n--- VERDICT ---", flush=True)
    print(f"T118a S=3 (>=0.90): {T118a}", flush=True)
    print(f"T118b S=5 (>=0.85): {T118b}", flush=True)
    print(f"T118c control (<0.70): {T118c}", flush=True)
    print(f"\nBET-118: {'PASS (sparse breaks the wall)' if passed else 'NULL'}", flush=True)
    out=Path.home()/'.eqmod'/'bet'/'BET-118'; out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps({"s3":s3,"s5":s5,"ctrl":ctrl,"passed":passed},indent=2))
    print("DONE", flush=True)
