"""JEP-31b - resolve JEP-31: is the 1170-mammal failure under-training? Triple the iterations on GPU."""
import time, numpy as np, torch
import tools.run_jep31_gpu_mammal as J  # reuses taxonomy, data, train fns (module-level setup runs on import)


def main():
    print("\n=== JEP-31b: 3x iterations to test the under-training hypothesis ===", flush=True)
    t0 = time.time(); Xh = J.train_hyper(dim=40, iters=18000, bs=8000); th = time.time() - t0
    hn = (Xh ** 2).sum(1).cpu().numpy()
    ok = np.mean([hn[u] < hn[v] for (u, v) in J.holdout])
    tr = np.mean([hn[u] < hn[v] for (u, v) in J.train_anc])
    print(f"  hyperbolic trained ({th:.0f}s, 18000 iters)", flush=True)
    print(f"  trained IS-A direction acc  = {tr:.3f}  (was 0.575 at 6k iters)", flush=True)
    print(f"  HELD-OUT IS-A direction acc = {ok:.3f}  (was 0.531 at 6k iters)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok >= 0.85:
        print(f"JEP-31b: PASS - 3x iterations RECOVER full-mammal scaling: held-out IS-A {ok:.2f}. JEP-31 was", flush=True)
        print(f"under-training; the reasoner scales to 1170 real concepts with adequate GPU compute.", flush=True)
    elif tr >= 0.8:
        print(f"JEP-31b: PARTIAL - trained acc recovered to {tr:.2f} (under-training confirmed for FIT) but held-out", flush=True)
        print(f"only {ok:.2f}: the embedding now fits training but GENERALIZATION at 1170/depth-12 is harder - a real", flush=True)
        print(f"generalization gap at full scale, not just fitting. Honest finding.", flush=True)
    else:
        print(f"JEP-31b: NULL - even 3x iters give trained {tr:.2f}/held-out {ok:.2f}: not simple under-training -", flush=True)
        print(f"the norm-direction readout / minibatched ranking has a real limit on deep 1170-node hierarchies.", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
