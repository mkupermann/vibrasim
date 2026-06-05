"""JEP-246 — the grounded loop through the substrate: noisy perceptual cue -> clean -> reason multi-hop.

A noisy concept code (perceptual cue) is clamped, the relaxation cleans it while retrieving the parent, then
energy-gated chaining answers multi-hop is_a. Integrates grounding (JEP-178) with the substrate-relational arc.
Established (Hopfield basin cleanup + perceive->symbol->reason loop), named.

Pre-registered bars in docs/amendments/jep246_grounded_substrate_loop.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from tools.run_jep232_relation_store import KEY, VAL, N

CHAIN = ["poodle", "dog", "mammal", "animal", "organism"]      # is-a chain


def setup(seed):
    edges = [(CHAIN[i], CHAIN[i + 1]) for i in range(len(CHAIN) - 1)]
    concepts = CHAIN
    rng = np.random.default_rng(seed)
    code = {c: rng.choice([-1.0, 1.0], KEY) for c in concepts}
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    pats = [np.concatenate([code[c], code[p]]) for c, p in edges]
    for _ in range(140):
        net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    e_cut = 0.7 * float(np.median([net.energy(p) for p in pats]))
    return net, code, concepts, e_cut


def flip(bits, f, rng):
    out = bits.copy()
    out[np.where(rng.random(len(bits)) < f)[0]] *= -1
    return out


def isa_chain(net, start_cue, code, concepts, e_cut, seed, max_depth=8):
    """start_cue is a (possibly noisy) KEY vector; chain energy-gated is-a from it."""
    reach, seen = set(), set()
    cur = start_cue.astype(np.float64)
    cur_name = None
    for d in range(max_depth):
        net.state = np.random.default_rng(seed + d).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), cur, steps=40)
        if net.energy(s) > e_cut:
            break
        val = np.sign(s[KEY:KEY + VAL])
        nxt = max(concepts, key=lambda c: float(val @ code[c]))
        if nxt in seen:
            break
        reach.add(nxt); seen.add(nxt); cur = code[nxt].astype(np.float64)
    return reach


def run_seed(seed):
    net, code, concepts, e_cut = setup(seed)
    rng = np.random.default_rng(seed + 5)
    # battery: is_a(x, y) for x in chain, y a later concept (positive) or earlier/other (negative)
    idx = {c: i for i, c in enumerate(CHAIN)}
    battery = []
    for x in CHAIN[:-1]:
        for y in CHAIN:
            if x != y:
                battery.append((x, y, idx[y] > idx[x]))     # y is an ancestor of x iff later in the chain
    out = {"noise": {}}
    for f in (0.0, 0.1, 0.2, 0.3):
        accs = []
        bitdiffs = []
        for (x, y, truth) in battery:
            cue = flip(code[x], f, rng)
            bitdiffs.append(int((cue != code[x]).sum()))
            ans = y in isa_chain(net, cue, code, concepts, e_cut, seed)
            accs.append(ans == truth)
        out["noise"][f] = {"acc": float(np.mean(accs)), "mean_bitdiff": float(np.mean(bitdiffs))}
    return out


if __name__ == "__main__":
    print("=== JEP-246: grounded loop through the substrate (noisy cue -> clean -> reason) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        n = R[s]["noise"]
        print(f"  seed {s}: acc f=0:{n[0.0]['acc']:.2f} f=.1:{n[0.1]['acc']:.2f} f=.2:{n[0.2]['acc']:.2f} "
              f"f=.3:{n[0.3]['acc']:.2f} | bitdiff@.2={n[0.2]['mean_bitdiff']:.1f}/40", flush=True)

    J246a = all(R[s]["noise"][0.0]['acc'] == 1.00 for s in seeds)
    J246b = all(R[s]["noise"][0.1]['acc'] >= 0.85 for s in seeds)
    J246c = all(R[s]["noise"][0.3]['acc'] < R[s]["noise"][0.0]['acc'] for s in seeds)
    J246d = all(R[s]["noise"][0.2]['mean_bitdiff'] >= 5 for s in seeds)
    passed = J246a and J246b and J246c

    print("\n--- VERDICT ---", flush=True)
    print(f"J246a clean grounded loop = 1.00     : {J246a}", flush=True)
    print(f"J246b robust at f=0.1 (>=0.85)       : {J246b}", flush=True)
    print(f"J246c graceful degradation (f.3<f0)  : {J246c}", flush=True)
    print(f"J246d cue genuinely noisy (>=5 bits) : {J246d}", flush=True)
    verdict = ("PASS - the grounded loop runs through the substrate: a noisy perceptual cue cleans up and reasons "
               "multi-hop, one energy process, tolerating moderate noise") if passed else "NULL/partial"
    print(f"\nJEP-246: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP246"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J246a": J246a, "J246b": J246b,
         "J246c": J246c, "J246d": J246d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
