"""JEP-36 - sequential abstract goals: 'visit a <catA> THEN a <catB>'. Temporal composition of grounded subgoals."""
import numpy as np
from collections import deque
from tools.concept_reasoner import ConceptReasoner

rng = np.random.default_rng(36)
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
    children = {p: [] for p in range(cr.N)}
    for c, p in cr.parent.items():
        children[p].append(c)
    out = set(); q = deque([cr.ID[name]])
    while q:
        n = q.popleft()
        for c in children[n]:
            out.add(cr.nodes[c]); q.append(c)
    return out


def navigate_to(Mt, start, g):
    c = start
    for _ in range(6 * S):
        nbs = list(ADJ[c]); c = max(nbs, key=lambda nb: Mt[ID[nb], ID[g]])
        if c == g:
            return c
    return c


def main():
    print("=== JEP-36: sequential abstract goals ('visit a <A> THEN a <B>') ===", flush=True)
    cr = ConceptReasoner(TAX); cr.fit(hyp_dim=10, iters=4000)
    Mt = sr_td()
    cats = ["carnivore", "primate", "bird", "tree", "flower"]
    leafset = set(LEAVES)
    correct_seq = 0; trials = 0
    for _ in range(150):
        cells = list(CELLS); rng.shuffle(cells)
        ent_cell = {LEAVES[i]: cells[i] for i in range(len(LEAVES))}
        a, b = rng.choice(cats, 2, replace=False)
        gA = [e for e in LEAVES if cr.is_a(e, a)]
        gB = [e for e in LEAVES if cr.is_a(e, b)]
        if not gA or not gB:
            continue
        trials += 1
        start = CELLS[rng.integers(S)]
        # leg 1: nearest A-entity from start
        tA = max(gA, key=lambda e: Mt[ID[start], ID[ent_cell[e]]])
        pos1 = navigate_to(Mt, start, ent_cell[tA])
        e1 = next((e for e, cell in ent_cell.items() if cell == pos1), None)
        # leg 2: nearest B-entity from where we ended
        tB = max(gB, key=lambda e: Mt[ID[pos1], ID[ent_cell[e]]])
        pos2 = navigate_to(Mt, pos1, ent_cell[tB])
        e2 = next((e for e, cell in ent_cell.items() if cell == pos2), None)
        trueA = descendants(cr, a) & leafset; trueB = descendants(cr, b) & leafset
        correct_seq += int(e1 in trueA and e2 in trueB)
    acc = correct_seq / trials
    print(f"  trials={trials}", flush=True)
    print(f"  visited A THEN B correctly (in order) = {acc:.3f}", flush=True)
    print(f"  (chance of a random 2-entity sequence matching both categories ~ {((3/14)**2):.3f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc >= 0.85:
        print(f"JEP-36: PASS - the agent executes SEQUENTIAL conceptual tasks: 'visit a <A> THEN a <B>' grounded via", flush=True)
        print(f"IS-A and navigated in ORDER, reaching the right category at each step {acc:.2f} of the time (random", flush=True)
        print(f"~0.05). Temporal composition of grounded subgoals - a step beyond logical composition (JEP-35) toward", flush=True)
        print(f"multi-step task understanding. Established methods (SR/TD, Poincare, sequential planning), named.", flush=True)
    else:
        print(f"JEP-36: PARTIAL/NULL - sequential accuracy {acc:.2f}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
