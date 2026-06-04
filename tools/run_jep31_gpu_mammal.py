"""JEP-31 - GPU-accelerated concept reasoner on the FULL mammal WordNet subtree (1170 concepts).
Runs in .venv-dml311 (torch-directml). Self-contained: taxonomy from data/mammal_taxonomy.json."""
import json, time
import numpy as np, torch
from collections import deque
import torch_directml as tdml

dev = tdml.device(0)
print(f"=== JEP-31: GPU concept reasoner on full mammal subtree (device: {tdml.device_name(0)}) ===", flush=True)

TAX = json.load(open("data/mammal_taxonomy.json"))
nodes = set()
for p, cs in TAX.items():
    nodes.add(p); nodes.update(cs)
nodes = sorted(nodes); ID = {n: i for i, n in enumerate(nodes)}; N = len(nodes)
adj = {i: set() for i in range(N)}; parent = {}
for p, cs in TAX.items():
    for c in cs:
        adj[ID[p]].add(ID[c]); adj[ID[c]].add(ID[p]); parent[ID[c]] = ID[p]


def ancestors(v):
    a = []; p = parent.get(v)
    while p is not None:
        a.append(p); p = parent.get(p)
    return a


# graph distances (for Euclidean relatedness target)
def graphdist():
    D = np.zeros((N, N), dtype=np.float32)
    for s in range(N):
        d = {s: 0}; q = deque([s])
        while q:
            c = q.popleft()
            for nb in adj[c]:
                if nb not in d:
                    d[nb] = d[c] + 1; q.append(nb)
        for j in range(N):
            D[s, j] = d.get(j, N)
    return D


print(f"  concepts={N}; computing graph distances...", flush=True)
GD = graphdist()
iu = np.triu_indices(N, 1)
PAIRS = np.stack([iu[0], iu[1]], 1).astype(np.int64)  # ~684k pairs
PAIRD = GD[iu].astype(np.float32)
print(f"  {len(PAIRS)} distance pairs", flush=True)

ANC = [(u, v) for v in range(N) for u in ancestors(v)]
rng = np.random.default_rng(1)
idx = rng.permutation(len(ANC)); cut = int(0.3 * len(ANC))
holdout = set(ANC[i] for i in idx[:cut]); train_anc = [ANC[i] for i in idx[cut:]]
POS = []
for (u, v) in train_anc:
    POS.append((u, v)); POS.append((v, u))
POS = np.array(POS, dtype=np.int64)
print(f"  ancestor pairs: {len(ANC)} ({len(train_anc)} train, {len(holdout)} held out)", flush=True)


def euc_d(a, b):
    return ((a - b) ** 2).sum(-1).clamp(min=1e-9).sqrt()


def poin_d(a, b):
    diff = ((a - b) ** 2).sum(-1); na = (a ** 2).sum(-1); nb = (b ** 2).sum(-1)
    return torch.acosh(torch.clamp(1 + 2 * diff / ((1 - na) * (1 - nb) + 1e-9), min=1 + 1e-7))


def train_euclid(dim=16, iters=4000, bs=40000):
    X = (torch.randn(N, dim) * 0.1).to(dev); X.requires_grad_(True)
    s = torch.tensor(1.0, requires_grad=True, device=dev)
    opt = torch.optim.Adam([X, s], lr=0.01)
    P = torch.tensor(PAIRS, device=dev); T = torch.tensor(PAIRD, device=dev)
    n = len(PAIRS)
    for it in range(iters):
        sel = torch.randint(0, n, (bs,), device=dev)
        i = P[sel, 0]; j = P[sel, 1]
        opt.zero_grad(); loss = ((euc_d(X[i], X[j]) - s * T[sel]) ** 2).mean(); loss.backward(); opt.step()
    return X.detach()


def train_hyper(dim=40, iters=6000, bs=8000):
    X = (torch.randn(N, dim) * 0.001).to(dev)
    P = torch.tensor(POS, device=dev); n = len(POS)
    for it in range(iters):
        sel = torch.randint(0, n, (bs,), device=dev)
        u = P[sel, 0]; v = P[sel, 1]; negs = torch.randint(0, N, (bs, 10), device=dev)
        X.requires_grad_(True)
        du = poin_d(X[u], X[v]); dn = poin_d(X[u].unsqueeze(1).expand(-1, 10, -1), X[negs])
        logits = torch.cat([(-du).unsqueeze(1), -dn], 1)
        loss = torch.nn.functional.cross_entropy(logits, torch.zeros(bs, dtype=torch.long, device=dev))
        loss.backward()
        with torch.no_grad():
            g = X.grad; sc = ((1 - (X ** 2).sum(1, keepdim=True)).clamp(min=1e-4) ** 2) / 4.0
            X = X - 0.3 * sc * g
            nrm = X.norm(dim=1, keepdim=True); X = torch.where(nrm >= 0.999, X / nrm * 0.999, X)
        X = X.detach()
    return X


def main():
    t0 = time.time()
    Xe = train_euclid(); te = time.time() - t0
    print(f"  Euclidean trained ({te:.0f}s)", flush=True)
    t0 = time.time(); Xh = train_hyper(); th = time.time() - t0
    print(f"  hyperbolic trained ({th:.0f}s)", flush=True)
    hn = (Xh ** 2).sum(1).cpu().numpy()
    ok = np.mean([hn[u] < hn[v] for (u, v) in holdout])
    tr = np.mean([hn[u] < hn[v] for (u, v) in train_anc])
    print(f"  trained IS-A direction acc  = {tr:.3f}", flush=True)
    print(f"  HELD-OUT IS-A direction acc = {ok:.3f}  (random 0.5)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok >= 0.85:
        print(f"JEP-31: PASS - GPU-trained concept reasoner SCALES to the FULL {N}-concept mammal WordNet subtree:", flush=True)
        print(f"held-out IS-A direction accuracy {ok:.2f} on real hypernym relations never trained on, trained on the", flush=True)
        print(f"AMD GPU via DirectML ({te:.0f}s Euclid + {th:.0f}s hyperbolic). The reasoning result holds at 16x the", flush=True)
        print(f"toy scale on real data, GPU-accelerated. Nickel-Kiela (2017) established - named as such.", flush=True)
    else:
        print(f"JEP-31: PARTIAL/NULL - held-out IS-A {ok:.2f} (may need more dims/iters at this scale)", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
