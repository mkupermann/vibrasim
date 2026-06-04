"""JEP-42 - order embeddings (Vendrov et al. 2016): does a DIFFERENT is-a method break the ~0.78 ceiling
(JEP-40/41) on real WordNet? Partial-order embedding, not distance/cone."""
import numpy as np, torch
from nltk.corpus import wordnet as wn


def build_tax(root):
    r = wn.synset(root); seen = set()

    def cl(s):
        seen.add(s)
        for h in s.hyponyms():
            if h not in seen:
                cl(h)
    cl(r); tax = {}
    for s in seen:
        for c in s.hyponyms():
            if c in seen:
                tax.setdefault(s.name(), []).append(c.name())
    return tax


TAX = build_tax("carnivore.n.01")
nodes = set()
for p, cs in TAX.items():
    nodes.add(p); nodes.update(cs)
nodes = sorted(nodes); ID = {n: i for i, n in enumerate(nodes)}; N = len(nodes); parent = {}
for p, cs in TAX.items():
    for c in cs:
        parent[ID[c]] = ID[p]


def anc(v):
    a = []; p = parent.get(v)
    while p is not None:
        a.append(p); p = parent.get(p)
    return a


ALL = [(u, v) for v in range(N) for u in anc(v)]  # (ancestor u, descendant v) -> v is_a u
ANCS = set(ALL)
rng = np.random.default_rng(0); idx = rng.permutation(len(ALL)); cut = int(0.3 * len(ALL))
HO = set(ALL[i] for i in idx[:cut]); TR = [ALL[i] for i in idx[cut:]]
D = 50; torch.manual_seed(0)


def energy(child, ancv, X):
    # E(child is_a ancestor): want coords[child] >= coords[ancestor] (child dominates) -> penalty ||relu(anc-child)||^2
    return torch.relu(X[ancv] - X[child]).pow(2).sum(-1)


def main():
    print(f"=== JEP-42: order embeddings for IS-A (WordNet carnivore N={N}) ===", flush=True)
    X = torch.rand(N, D) * 0.1; X.requires_grad_(True)
    opt = torch.optim.Adam([X], lr=0.05)
    trc = torch.tensor([p[1] for p in TR]); tra = torch.tensor([p[0] for p in TR])  # child=v, ancestor=u
    margin = 1.0
    for it in range(6000):
        opt.zero_grad()
        ep = energy(trc, tra, X).mean()  # positives -> 0
        nc = torch.randint(0, N, (len(TR),)); na = torch.randint(0, N, (len(TR),))
        en = torch.relu(margin - energy(nc, na, X)).mean()  # negatives -> >= margin
        loss = ep + en
        loss.backward(); opt.step()
        with torch.no_grad():
            X.clamp_(min=0.0)  # non-negative orthant
    with torch.no_grad():
        # calibrate threshold on TRAIN positives vs random negatives
        pe = energy(torch.tensor([p[1] for p in TR]), torch.tensor([p[0] for p in TR]), X).numpy()
        negc = rng.integers(0, N, len(TR)); nega = rng.integers(0, N, len(TR))
        ne = energy(torch.tensor(negc), torch.tensor(nega), X).numpy()
        # threshold = midpoint that best separates (simple: value maximizing balanced acc on train)
        cands = np.percentile(np.concatenate([pe, ne]), np.linspace(1, 99, 99))
        best_t = max(cands, key=lambda t: (np.mean(pe <= t) + np.mean(ne > t)) / 2)

        def isa_pair(child, ancv):
            return float(energy(torch.tensor([child]), torch.tensor([ancv]), X)) <= best_t
        tp = np.mean([isa_pair(v, u) for (u, v) in HO])  # held-out v is_a u
        neg = []
        while len(neg) < len(HO):
            a, b = int(rng.integers(N)), int(rng.integers(N))
            if a != b and (a, b) not in ANCS:
                neg.append((a, b))
        tn = np.mean([not isa_pair(b, a) for (a, b) in neg])  # a,b non-ancestor: is b is_a a? should be False
        acc = (tp + tn) / 2
    print(f"  held-out IS-A: TPR={tp:.3f} TNR={tn:.3f} balanced-acc={acc:.3f}  (Poincare ceiling ~0.78)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc >= 0.88:
        print(f"JEP-42: PASS - order embeddings BREAK the ~0.78 ceiling: held-out balanced IS-A {acc:.2f} on 366", flush=True)
        print(f"WordNet concepts (TPR {tp:.2f}, TNR {tn:.2f}). The ceiling WAS the Poincare method; a partial-order", flush=True)
        print(f"embedding (Vendrov 2016) - designed for transitive entailment - handles deep real hierarchies far", flush=True)
        print(f"better. The method, not the data, was the limit. Established (Vendrov 2016), named as such.", flush=True)
    elif acc >= 0.80:
        print(f"JEP-42: PARTIAL - order embeddings {acc:.2f} > Poincare ceiling 0.78 but not >=0.88: a different", flush=True)
        print(f"method helps somewhat; the limit is partly method, partly the noisy/multi-parent real taxonomy.", flush=True)
    else:
        print(f"JEP-42: NULL - order embeddings {acc:.2f} ~ Poincare ceiling: the ~0.78 limit is NOT just the", flush=True)
        print(f"Poincare method - it persists across methods, so it is the DATA (deep, noisy real WordNet at this", flush=True)
        print(f"budget), not the embedding geometry. Deeper honest limit.", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
