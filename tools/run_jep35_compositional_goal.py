"""JEP-35 - compositional abstract goals: set logic (AND/OR/NOT) + relatedness over IS-A, then plan.
Composes symbolic operators + concept reasoner + world-model planner."""
import numpy as np
from collections import deque
from tools.concept_reasoner import ConceptReasoner

rng = np.random.default_rng(35)
TAX = {
    "living_thing": ["animal", "plant"], "animal": ["mammal", "bird"],
    "mammal": ["carnivore", "primate"], "carnivore": ["cat", "dog", "wolf"],
    "primate": ["human", "chimp"], "bird": ["eagle", "sparrow", "owl"],
    "plant": ["tree", "flower"], "tree": ["oak", "pine", "maple"], "flower": ["rose", "tulip", "daisy"],
}
LEAVES = ["cat", "dog", "wolf", "human", "chimp", "eagle", "sparrow", "owl", "oak", "pine", "maple", "rose", "tulip", "daisy"]
M = 10


def gen_looped(M, extra=30):
    adj = {(x, y): set() for x in range(M) for y in range(M)}
    seen = {(0, 0)}; st = [(0, 0)]
    while st:
        x, y = st[-1]
        nb = [(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
              if 0 <= x + dx < M and 0 <= y + dy < M and (x + dx, y + dy) not in seen]
        if nb:
            n = nb[rng.integers(len(nb))]; adj[(x, y)].add(n); adj[n].add((x, y)); seen.add(n); st.append(n)
        else:
            st.pop()
    cells = [(x, y) for x in range(M) for y in range(M)]; added = 0
    while added < extra:
        c = cells[rng.integers(len(cells))]; x, y = c
        opts = [(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                if 0 <= x + dx < M and 0 <= y + dy < M and (x + dx, y + dy) not in adj[c]]
        if opts:
            n = opts[rng.integers(len(opts))]; adj[c].add(n); adj[n].add(c); added += 1
    return adj


ADJ = gen_looped(M); CELLS = [(x, y) for x in range(M) for y in range(M)]
ID = {c: i for i, c in enumerate(CELLS)}; S = len(CELLS); gamma = 0.97


def sr_td(steps=2_000_000, alpha=0.02):
    Mt = np.zeros((S, S), np.float32); I = np.eye(S, dtype=np.float32); c = CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs = list(ADJ[c]); nb = nbs[rng.integers(len(nbs))]
        Mt[ID[c]] += alpha * (I[ID[c]] + gamma * Mt[ID[nb]] - Mt[ID[c]]); c = nb
    return Mt


def descendants(cr, name):
    root = cr.ID.get(name)
    if root is None:
        return set()
    children = {p: [] for p in range(cr.N)}
    for c, p in cr.parent.items():
        children[p].append(c)
    out = set(); q = deque([root])
    while q:
        n = q.popleft()
        for c in children[n]:
            out.add(cr.nodes[c]); q.append(c)
    return out


def main():
    print("=== JEP-35: compositional abstract goals (set logic + relatedness over IS-A) ===", flush=True)
    cr = ConceptReasoner(TAX); cr.fit(hyp_dim=10, iters=4000)
    Mt = sr_td()
    leafset = set(LEAVES)

    # goal types: each returns (predicate name, grounded set via reasoner, TRUE set via ground truth)
    def ground_and_truth(kind):
        if kind == "AND_NOT":  # mammal AND NOT carnivore -> primates
            grounded = [e for e in LEAVES if cr.is_a(e, "mammal") and not cr.is_a(e, "carnivore")]
            truth = (descendants(cr, "mammal") & leafset) - (descendants(cr, "carnivore") & leafset)
            return "mammal AND NOT carnivore", grounded, truth
        if kind == "OR":  # carnivore OR bird
            grounded = [e for e in LEAVES if cr.is_a(e, "carnivore") or cr.is_a(e, "bird")]
            truth = (descendants(cr, "carnivore") | descendants(cr, "bird")) & leafset
            return "carnivore OR bird", grounded, truth
        if kind == "NOT":  # NOT animal -> plants
            grounded = [e for e in LEAVES if not cr.is_a(e, "animal")]
            truth = leafset - (descendants(cr, "animal") & leafset)
            return "NOT animal", grounded, truth
        if kind == "RELATED":  # most related LEAF to a query entity (Euclidean nearest among placed entities)
            q = LEAVES[rng.integers(len(LEAVES))]
            near = [e for e in cr.nearest(q, k=cr.N) if e in leafset and e != q][0]
            qp = cr.parent.get(cr.ID[q]); sibs = {cr.nodes[c] for c in range(cr.N) if cr.parent.get(c) == qp and c != cr.ID[q]} & leafset
            return f"most related to {q}", [near], sibs if sibs else {near}

    kinds = ["AND_NOT", "OR", "NOT", "RELATED"]
    per = {k: [0, 0] for k in kinds}
    reached = rand = trials = 0
    for _ in range(160):
        cells = list(CELLS); rng.shuffle(cells)
        ent_cell = {LEAVES[i]: cells[i] for i in range(len(LEAVES))}
        kind = kinds[rng.integers(len(kinds))]
        desc, grounded, truth = ground_and_truth(kind)
        grounded = [e for e in grounded if e in ent_cell]  # only placed leaf entities are navigable
        if not grounded or not truth:
            continue
        trials += 1; per[kind][1] += 1
        start = CELLS[rng.integers(S)]
        target = max(grounded, key=lambda e: Mt[ID[start], ID[ent_cell[e]]])
        g = ent_cell[target]; c = start
        for _ in range(6 * S):
            nbs = list(ADJ[c]); c = max(nbs, key=lambda nb: Mt[ID[nb], ID[g]])
            if c == g:
                break
        arrived = next((e for e, cell in ent_cell.items() if cell == c), None)
        ok = int(arrived in truth); reached += ok; per[kind][0] += ok
        rand += int(LEAVES[rng.integers(len(LEAVES))] in truth)
    print(f"  trials={trials}", flush=True)
    print(f"  reached a goal-SATISFYING entity = {reached / trials:.3f}", flush=True)
    print(f"  random-entity baseline           = {rand / trials:.3f}", flush=True)
    print("  by goal type (accuracy / n):", flush=True)
    for k in kinds:
        if per[k][1]:
            print(f"    {k}: {per[k][0] / per[k][1]:.2f}  ({per[k][1]})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    acc = reached / trials
    if acc >= 0.85 and acc >= rand / trials + 0.3:
        print(f"JEP-35: PASS - the agent handles COMPOSITIONAL conceptual goals: set logic (AND/OR/NOT) + relatedness", flush=True)
        print(f"over IS-A ground the goal, the world-model navigates - reaching a goal-satisfying entity {acc:.2f} of the", flush=True)
        print(f"time (random {rand / trials:.2f}). Symbolic operators + concept geometry + planning compose. A richer", flush=True)
        print(f"step toward understanding-informed behaviour than single-category goals (JEP-34). Established, named.", flush=True)
    else:
        print(f"JEP-35: PARTIAL/NULL - reached {acc:.2f}, random {rand / trials:.2f}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
