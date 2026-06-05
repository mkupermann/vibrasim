"""JEP-253 — the full LEARN->UNDERSTAND->COMMUNICATE loop THROUGH the substrate (English answers).

Read prose (LEARN) -> store in the EnergyNet -> answer by SUBSTRATE reasoning (UNDERSTAND) -> render in ENGLISH with
the engine's OWN template (COMMUNICATE), and check the English matches the symbolic e.explain() string-for-string.
Established (content-addressable reasoning + template realization), named.

Pre-registered bars in docs/amendments/jep253_three_verb_loop_substrate.md.
"""
import json
from pathlib import Path
import numpy as np

from world.energy import EnergyNet
from world.understanding import UnderstandingEngine
from tools.run_jep232_relation_store import KEY, VAL, N

PASSAGE = ("A poodle is a dog. A dog is a canine. A canine is a mammal. A mammal is an animal. "
           "An animal is an organism. A cat is a feline. A feline is a mammal.")
QUESTIONS = [
    "is a poodle an animal?", "is a poodle an organism?", "is a poodle a mammal?",
    "is a cat an animal?", "is a poodle a cat?", "is a cat a dog?",
    "is a dog an organism?", "is a feline a mammal?",
]


def build_substrate(e, seed):
    edges = [(c, p) for c, ps in e.parents.items() for p in ps]
    concepts = sorted({x for ed in edges for x in ed})
    code = {c: np.random.default_rng(hash((seed, c)) % (2**32)).choice([-1.0, 1.0], KEY) for c in concepts}
    net = EnergyNet(n_per_module=N, n_modules=1, seed=seed)
    pats = [np.concatenate([code[c], code[p]]) for c, p in edges]
    for _ in range(140):
        net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=12)
    e_cut = 0.7 * float(np.median([net.energy(p) for p in pats])) if pats else -1
    return net, code, concepts, e_cut


def substrate_chain(net, x, code, concepts, e_cut, seed, max_depth=10):
    """Ordered is-a chain [x, p1, ..., root-or-target] via energy-gated retrieval."""
    path, seen, cur = [x], {x}, x
    for d in range(max_depth):
        net.state = np.random.default_rng(seed + d).choice([-1.0, 1.0], N)
        s = net.relax(np.arange(KEY), code[cur], steps=40)
        if net.energy(s) > e_cut:
            break
        val = np.sign(s[KEY:KEY + VAL])
        nxt = max(concepts, key=lambda c: float(val @ code[c]))
        if nxt in seen:
            break
        path.append(nxt); seen.add(nxt); cur = nxt
    return path


def substrate_explain(e, question, net, code, concepts, e_cut, seed):
    """Mirror e.explain() but use the SUBSTRATE chain for the verdict + steps."""
    q = question.strip().rstrip("?").lower()
    sc = e._parse_isa_q(q)
    if not sc:
        return "I cannot parse that question."
    x, c = e._norm_phrase(sc[0]), e._norm_phrase(sc[1])
    if x not in concepts or c not in concepts:
        return f"I don't know whether {e._art(x)} is {e._art(c)}."
    path = substrate_chain(net, x, code, concepts, e_cut, seed)
    disp = lambda w: w.replace("_", " ")
    if c in path[1:]:                                  # substrate reaches c -> Yes, with the chain up to c
        sub = path[: path.index(c) + 1]
        steps = ", ".join(f"{e._art(disp(sub[i]))} is {e._art(disp(sub[i+1]))}" for i in range(len(sub) - 1))
        steps = steps[0].upper() + steps[1:] if steps else steps
        return f"Yes. {steps}."
    rest = f"{e._art(x)} is not {e._art(c)} as far as I know."
    return "No. " + rest[0].upper() + rest[1:]


def run_seed(seed):
    e = UnderstandingEngine(seed=seed); e.read(PASSAGE)
    net, code, concepts, e_cut = build_substrate(e, seed)
    match = verdict_ok = wellformed = 0
    for q in QUESTIONS:
        sym = e.explain(q)
        sub = substrate_explain(e, q, net, code, concepts, e_cut, seed)
        match += (sym == sub)
        verdict_ok += (sym.startswith("Yes") == sub.startswith("Yes")) and (sym.startswith("No") == sub.startswith("No"))
        wellformed += (sub[0].isupper() and sub.endswith(".") and "  " not in sub and " a a" not in sub.lower())
    n = len(QUESTIONS)
    # J253d: a depth-3 question answered end-to-end through the substrate
    deep = substrate_explain(e, "is a poodle an organism?", net, code, concepts, e_cut, seed)
    return {"match": round(match / n, 3), "verdict": round(verdict_ok / n, 3),
            "wellformed": round(wellformed / n, 3), "deep_answer": deep,
            "deep_ok": deep.startswith("Yes") and "organism" in deep}


if __name__ == "__main__":
    print("=== JEP-253: LEARN->UNDERSTAND->COMMUNICATE loop through the substrate ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: string-match={r['match']} verdict-match={r['verdict']} wellformed={r['wellformed']} "
              f"| deep: \"{r['deep_answer']}\" ok={r['deep_ok']}", flush=True)

    J253a = all(R[s]['match'] >= 0.90 for s in seeds)
    J253b = all(R[s]['verdict'] == 1.0 for s in seeds)
    J253c = all(R[s]['wellformed'] == 1.0 for s in seeds)
    J253d = all(R[s]['deep_ok'] for s in seeds)
    passed = J253a and J253b

    print("\n--- VERDICT ---", flush=True)
    print(f"J253a substrate English matches symbolic (>=.90): {J253a}", flush=True)
    print(f"J253b verdicts all correct                      : {J253b}", flush=True)
    print(f"J253c English well-formed                       : {J253c}", flush=True)
    print(f"J253d depth-3 answered end-to-end               : {J253d}", flush=True)
    verdict = ("PASS - the full LEARN->UNDERSTAND->COMMUNICATE loop runs through the substrate: read prose, store, "
               "reason, answer in English matching the symbolic engine") if passed else "NULL/partial"
    print(f"\nJEP-253: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP253"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J253a": J253a, "J253b": J253b,
         "J253c": J253c, "J253d": J253d, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
