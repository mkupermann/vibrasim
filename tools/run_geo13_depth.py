"""GEO-13 — composition DEPTH: train on parent only, infer k-th ancestor by composing k*r_parent for
k=1..5 (grandparent..great-great-great). Measures how deep learned-structure compositional reasoning holds.
CPU."""
import numpy as np
D = 24


def chain(n_chains=6, length=12):
    """n_chains separate linear ancestry chains; each node has a unique id and one parent."""
    parent = {}; nodes = []; nid = 0
    for _ in range(n_chains):
        prev = None
        for d in range(length):
            nodes.append(nid)
            if prev is not None:
                parent[nid] = prev      # nid's parent is prev (prev is one generation older)
            prev = nid; nid += 1
    nE = nid
    edges = [(c, p) for c, p in parent.items()]   # child -> parent
    def anc(c, k):
        x = c
        for _ in range(k):
            if x in parent: x = parent[x]
            else: return None
        return x
    return nE, edges, parent, anc


def train(edges, nE, epochs=7000, lr=0.05, margin=1.0, seed=1):
    r = np.random.default_rng(seed); E = r.normal(0,.3,(nE,D)); rp = r.normal(0,.3,D); ed=np.array(edges)
    for ep in range(epochs):
        E /= np.linalg.norm(E,axis=1,keepdims=True)+1e-9
        neg=ed.copy(); neg[:,1]=r.integers(0,nE,len(ed))
        for (h,t),(hn,tn) in zip(ed,neg):
            dp=E[h]+rp-E[t]; dn=E[hn]+rp-E[tn]; sp=np.linalg.norm(dp); sn=np.linalg.norm(dn)
            if margin+sp-sn>0:
                gp=dp/(sp+1e-9); gn=dn/(sn+1e-9); E[h]-=lr*gp; E[t]+=lr*gp; rp-=lr*gp; E[hn]+=lr*gn; E[tn]-=lr*gn; rp+=lr*gn
    return E, rp


def h1(E,q,t): return int(np.argmin(np.linalg.norm(E-q,axis=1))==t)


if __name__ == "__main__":
    print("=== GEO-13: composition DEPTH (k-th ancestor via k*r_parent) ===", flush=True)
    nE, edges, parent, anc = chain(); E, rp = train(edges, nE)
    for k in [1,2,3,4,5]:
        pairs = [(c, anc(c,k)) for c in range(nE) if anc(c,k) is not None]
        if not pairs: continue
        acc = np.mean([h1(E, E[c]+k*rp, a) for c,a in pairs])
        print(f"  {k}-step ancestor via {k}*r_parent: hits@1 = {acc:.2f}  (n={len(pairs)})", flush=True)
    print("\n  (trained on parent edges only; deeper k = more composition)", flush=True)
    print("DONE", flush=True)
