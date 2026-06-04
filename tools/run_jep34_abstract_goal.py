"""JEP-34 - abstract-goal planning: concept reasoner (IS-A) grounds a conceptual goal, world-model plans to it.
Integrates the two EQMOD-4 threads (JEP-11 SR planning + JEP-28 concept reasoner) into one agent."""
import numpy as np
from collections import deque
from tools.concept_reasoner import ConceptReasoner

rng = np.random.default_rng(34)
TAX = {
    "living_thing": ["animal", "plant"], "animal": ["mammal", "bird"],
    "mammal": ["carnivore", "primate"], "carnivore": ["cat", "dog", "wolf"],
    "primate": ["human", "chimp"], "bird": ["eagle", "sparrow", "owl"],
    "plant": ["tree", "flower"], "tree": ["oak", "pine", "maple"], "flower": ["rose", "tulip", "daisy"],
}
# concrete entities = leaves
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


def main():
    print("=== JEP-34: abstract-goal planning (concept reasoner grounds goal -> world-model navigates) ===", flush=True)
    cr = ConceptReasoner(TAX); cr.fit(hyp_dim=10, iters=4000)
    Mt = sr_td()
    categories = ["carnivore", "mammal", "bird", "plant", "tree", "animal"]
    reached_correct = 0; rand_correct = 0; trials = 0
    for _ in range(120):
        # place each leaf entity at a random distinct free cell
        cells = list(CELLS); rng.shuffle(cells)
        ent_cell = {LEAVES[i]: cells[i] for i in range(len(LEAVES))}
        cat = categories[rng.integers(len(categories))]
        start = CELLS[rng.integers(S)]
        # GROUND the abstract goal via concept reasoner: which entities are-a `cat`?
        grounded = [e for e in LEAVES if cr.is_a(e, cat)]
        if not grounded:
            continue
        trials += 1
        # navigate to the NEAREST grounded entity by SR-value planning
        # pick target = grounded entity whose cell has highest SR value from start (closest)
        target = max(grounded, key=lambda e: Mt[ID[start], ID[ent_cell[e]]])
        g = ent_cell[target]; c = start
        for _ in range(6 * S):
            nbs = list(ADJ[c]); c = max(nbs, key=lambda nb: Mt[ID[nb], ID[g]])
            if c == g:
                break
        arrived = next((e for e, cell in ent_cell.items() if cell == c), None)
        # success = the entity the agent ENDED on truly is-a the category (ground truth)
        true_members = set(LEAVES) & set(_descendants(cr, cat))
        reached_correct += int(arrived in true_members)
        # random baseline: go to a random entity
        rand_target = LEAVES[rng.integers(len(LEAVES))]
        rand_correct += int(rand_target in true_members)
    print(f"  trials={trials}", flush=True)
    print(f"  agent reached a CORRECT-category entity = {reached_correct / trials:.3f}", flush=True)
    print(f"  random-entity baseline                  = {rand_correct / trials:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    acc = reached_correct / trials
    if acc >= 0.85 and acc >= rand_correct / trials + 0.3:
        print(f"JEP-34: PASS - the integrated agent acts on ABSTRACT goals: given a conceptual goal ('reach a", flush=True)
        print(f"<category>'), the concept reasoner GROUNDS it into concrete entities (IS-A) and the world-model SR", flush=True)
        print(f"planner navigates to the nearest one - reaching a truly correct-category entity {acc:.2f} of the time", flush=True)
        print(f"(random {rand_correct / trials:.2f}). Conceptual knowledge + planning compose into understanding-", flush=True)
        print(f"informed behaviour. Integrates JEP-11 (SR planning) + JEP-28 (concept reasoner). Established, named.", flush=True)
    else:
        print(f"JEP-34: PARTIAL/NULL - reached-correct {acc:.2f}, random {rand_correct / trials:.2f}", flush=True)
    print("DONE", flush=True)


def _descendants(cr, name):
    # all entities that are descendants of `name` in the taxonomy (ground truth membership)
    root = cr.ID.get(name)
    if root is None:
        return []
    out = []; q = deque([root]);
    # walk children via adjacency restricted to is-descendant (parent relation)
    children = {p: [] for p in range(cr.N)}
    for c, p in cr.parent.items():
        children[p].append(c)
    while q:
        n = q.popleft()
        for c in children[n]:
            out.append(cr.nodes[c]); q.append(c)
    return out


if __name__ == "__main__":
    main()
