"""Mixed-curvature concept reasoner (EQMOD-4 JEP-28): Euclidean relatedness + hyperbolic IS-A.
No pretrained models, no transformer - just geometry fit from a taxonomy graph."""
import numpy as np, torch
from collections import deque


def _poin_dc(a, b):
    diff = ((a - b) ** 2).sum(-1); na = (a ** 2).sum(-1); nb = (b ** 2).sum(-1)
    return torch.acosh(torch.clamp(1 + 2 * diff / ((1 - na) * (1 - nb) + 1e-9), min=1 + 1e-7))


def _euc_dc(a, b):
    return ((a - b) ** 2).sum(-1).clamp(min=1e-9).sqrt()


class ConceptReasoner:
    """Dual embedding from a taxonomy (parent->children dict): Euclidean for relatedness,
    hyperbolic (Poincare) for IS-A generality. Methods: relatedness, is_a, nearest, more_general."""

    def __init__(self, tax, seed=0):
        torch.manual_seed(seed); self.rng = np.random.default_rng(seed)
        nodes = set()
        for p, cs in tax.items():
            nodes.add(p); nodes.update(cs)
        self.nodes = sorted(nodes); self.ID = {n: i for i, n in enumerate(self.nodes)}; self.N = len(self.nodes)
        self.adj = {i: set() for i in range(self.N)}; self.parent = {}
        for p, cs in tax.items():
            for c in cs:
                self.adj[self.ID[p]].add(self.ID[c]); self.adj[self.ID[c]].add(self.ID[p]); self.parent[self.ID[c]] = self.ID[p]
        self.GD = self._graphdist()

    def _graphdist(self):
        N = self.N; D = np.zeros((N, N))
        for s in range(N):
            d = {s: 0}; q = deque([s])
            while q:
                c = q.popleft()
                for nb in self.adj[c]:
                    if nb not in d:
                        d[nb] = d[c] + 1; q.append(nb)
            for j in range(N):
                D[s, j] = d.get(j, N)
        return D

    def _ancestors(self, v):
        a = []; p = self.parent.get(v)
        while p is not None:
            a.append(p); p = self.parent.get(p)
        return a

    def fit(self, euc_dim=4, hyp_dim=2, iters=3000, holdout_pairs=None):
        N = self.N; iu = np.triu_indices(N, 1); gd = torch.tensor(self.GD[iu], dtype=torch.float32)
        I = torch.tensor(iu[0]); J = torch.tensor(iu[1])
        Xe = torch.randn(N, euc_dim) * 0.1; Xe.requires_grad_(True); s = torch.tensor(1.0, requires_grad=True)
        opt = torch.optim.Adam([Xe, s], lr=0.02)
        for _ in range(iters):
            opt.zero_grad(); (((_euc_dc(Xe[I], Xe[J]) - s * gd) ** 2).mean()).backward(); opt.step()
        self.Xe = Xe.detach()
        POS = []
        for v in range(N):
            for u in self._ancestors(v):
                if holdout_pairs is not None and (u, v) in holdout_pairs:
                    continue
                POS.append((u, v)); POS.append((v, u))
        POS = torch.tensor(POS); Xh = torch.randn(N, hyp_dim) * 0.001
        for _ in range(iters + 1000):
            Xh.requires_grad_(True); u = POS[:, 0]; v = POS[:, 1]; negs = torch.randint(0, N, (len(POS), 15))
            du = _poin_dc(Xh[u], Xh[v]); dn = _poin_dc(Xh[u].unsqueeze(1).expand(-1, 15, -1), Xh[negs])
            torch.nn.functional.cross_entropy(torch.cat([(-du).unsqueeze(1), -dn], 1), torch.zeros(len(POS), dtype=torch.long)).backward()
            with torch.no_grad():
                g = Xh.grad; sc = ((1 - (Xh ** 2).sum(1, keepdim=True)).clamp(min=1e-4) ** 2) / 4.0
                Xh = Xh - 0.3 * sc * g; nrm = Xh.norm(dim=1, keepdim=True); Xh = torch.where(nrm >= 0.999, Xh / nrm * 0.999, Xh)
            Xh = Xh.detach()
        self.Xh = Xh; self.hnorm = (Xh ** 2).sum(1).numpy()
        return self

    def relatedness(self, a, b):
        i, j = self.ID[a], self.ID[b]; return float(-_euc_dc(self.Xe[i:i + 1], self.Xe[j:j + 1]))

    def more_general(self, a, b):
        i, j = self.ID[a], self.ID[b]; return a if self.hnorm[i] < self.hnorm[j] else b

    def is_a(self, a, b):
        i, j = self.ID[a], self.ID[b]; return bool(self.hnorm[j] < self.hnorm[i])

    def nearest(self, a, k=5):
        i = self.ID[a]
        d = [(float(_euc_dc(self.Xe[i:i + 1], self.Xe[m:m + 1])), self.nodes[m]) for m in range(self.N) if m != i]
        return [n for _, n in sorted(d)[:k]]
