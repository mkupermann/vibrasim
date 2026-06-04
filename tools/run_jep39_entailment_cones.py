"""JEP-39 - hyperbolic entailment cones (Ganea et al. 2018) for IS-A: does angular containment fix the
sibling residual (JEP-33) that distance-based readouts could not?"""
import numpy as np, torch

TAX = {
    "living_thing": ["animal", "plant"], "animal": ["mammal", "bird"],
    "mammal": ["carnivore", "primate"], "carnivore": ["cat", "dog", "wolf"],
    "primate": ["human", "chimp"], "bird": ["eagle", "sparrow", "owl"],
    "plant": ["tree", "flower"], "tree": ["oak", "pine", "maple"], "flower": ["rose", "tulip", "daisy"],
}
nodes = set()
for p, cs in TAX.items():
    nodes.add(p); nodes.update(cs)
nodes = sorted(nodes); ID = {n: i for i, n in enumerate(nodes)}; N = len(nodes)
parent = {}
for p, cs in TAX.items():
    for c in cs:
        parent[ID[c]] = ID[p]


def ancestors(v):
    a = []; p = parent.get(v)
    while p is not None:
        a.append(p); p = parent.get(p)
    return a


# positives: (ancestor x, descendant y) -> y should be in x's cone
POS = [(u, v) for v in range(N) for u in ancestors(v)]
ANC = set(POS)
EPS = 0.1; K = 0.1
torch.manual_seed(0)


def norm(x):
    return x.norm(dim=-1).clamp(min=EPS, max=1 - 1e-4)


def aperture(x):
    nx = norm(x)
    return torch.asin(torch.clamp(K * (1 - nx ** 2) / nx, max=1 - 1e-6))


def xi(x, y):
    # angle at x between (radial direction through x) and (direction to y); Ganea eq.
    nx = norm(x); ny = norm(y)
    xy = (x * y).sum(-1)
    nxy = (x - y).norm(dim=-1).clamp(min=1e-6)
    num = xy * (1 + nx ** 2) - nx ** 2 * (1 + ny ** 2)
    den = nx * nxy * torch.sqrt(torch.clamp(1 + nx ** 2 * ny ** 2 - 2 * xy, min=1e-9))
    return torch.acos(torch.clamp(num / den, -1 + 1e-6, 1 - 1e-6))


def energy(x, y):  # 0 if y inside x's cone
    return torch.clamp(xi(x, y) - aperture(x), min=0.0)


def main():
    print("=== JEP-39: hyperbolic entailment cones for IS-A (sibling fix) ===", flush=True)
    X = (torch.randn(N, 2) * 0.1)
    with torch.no_grad():
        n = X.norm(dim=1, keepdim=True); X *= (EPS + 0.3) / n.clamp(min=1e-6)
    posX = torch.tensor([p[0] for p in POS]); posY = torch.tensor([p[1] for p in POS])
    for it in range(6000):
        X.requires_grad_(True)
        ep = energy(X[posX], X[posY]).mean()  # minimize: descendants inside ancestor cones
        negx = torch.randint(0, N, (len(POS),)); negy = torch.randint(0, N, (len(POS),))
        en = torch.clamp(0.3 - energy(X[negx], X[negy]), min=0.0).mean()  # push non-pairs OUT (margin)
        loss = ep + en
        loss.backward()
        with torch.no_grad():
            X = X - 0.05 * X.grad
            nn = X.norm(dim=1, keepdim=True)
            X = torch.where(nn < EPS, X * EPS / nn.clamp(min=1e-6), X)
            X = torch.where(nn > 1 - 1e-3, X / nn * (1 - 1e-3), X)
        X = X.detach()
    # is_a(a,b) = a in b's cone => energy(b, a) ~ 0
    with torch.no_grad():
        def isa(a, b):
            return float(energy(X[ID[b]:ID[b] + 1], X[ID[a]:ID[a] + 1])) < 0.05
        sanity = [('cat', 'mammal', True), ('cat', 'animal', True), ('cat', 'carnivore', True),
                  ('cat', 'dog', False), ('dog', 'cat', False), ('eagle', 'sparrow', False),
                  ('oak', 'pine', False), ('rose', 'animal', False), ('oak', 'mammal', False),
                  ('mammal', 'cat', False)]
        wrong = 0; sib_ok = True
        print("  sanity:", flush=True)
        for a, b, exp in sanity:
            r = isa(a, b); tag = 'OK' if r == exp else 'WRONG'; wrong += (r != exp)
            if (a, b) in [('cat', 'dog'), ('dog', 'cat'), ('eagle', 'sparrow'), ('oak', 'pine')] and r:
                sib_ok = False
            print(f"    is_a({a},{b})={r} exp={exp} {tag}", flush=True)
        # classification accuracy
        rng = np.random.default_rng(3); pos = list(ANC); neg = []
        while len(neg) < len(pos):
            a, b = int(rng.integers(N)), int(rng.integers(N))
            if a != b and (a, b) not in ANC:
                neg.append((a, b))
        tp = np.mean([isa(nodes[v], nodes[u]) for (u, v) in pos])   # v is-a u (u ancestor)
        tn = np.mean([not isa(nodes[b], nodes[a]) for (a, b) in neg])
        acc = (tp * len(pos) + tn * len(neg)) / (len(pos) + len(neg))
    print(f"  is-a classification: TPR={tp:.3f} TNR={tn:.3f} acc={acc:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc >= 0.90 and sib_ok and wrong == 0:
        print(f"JEP-39: PASS - hyperbolic ENTAILMENT CONES fix the sibling residual: ALL sanity cases correct incl.", flush=True)
        print(f"siblings (cat/dog, eagle/sparrow rejected) AND cross-branch AND ancestors, classification acc {acc:.2f}.", flush=True)
        print(f"Angular containment (a in b's cone) succeeds where distance/norm features failed (JEP-33) - siblings", flush=True)
        print(f"are angularly OUTSIDE each other's cones. Ganea et al. 2018 established - named as such.", flush=True)
    else:
        print(f"JEP-39: PARTIAL/NULL - acc {acc:.2f}, siblings_ok {sib_ok}, sanity_wrong {wrong}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
