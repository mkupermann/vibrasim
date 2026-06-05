"""JEP-294 — VSA bundle capacity for instance-distinct facts (the established HRR/Plate measurement, named as such).

Store K facts as one bundle of bind(entity_k * ROLE, value_k); recover each by cleanup(unbind(mem, entity_k*ROLE)).
Measures: (a) does instance-distinct retrieval work at K=8, D=4096; (b) how K* (max facts at >=0.90 recovery)
scales with D; (c) is an untaught entity separable (no hallucination). No transformer, no pretrained model.

Pre-registered bars in docs/amendments/jep294_binding_capacity.md.
"""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, unbind, bundle, sim, CleanupMemory


def build(D, K, seed):
    rng = np.random.default_rng(seed)
    ROLE = rand_hv(D, rng)
    entities = [rand_hv(D, rng) for _ in range(K)]
    values = [rand_hv(D, rng) for _ in range(K)]          # the value vocabulary (= the cleanup dictionary)
    clean = CleanupMemory()
    for i, v in enumerate(values):
        clean.add(f"V{i}", v)
    mem = bundle([bind(bind(entities[k], ROLE), values[k]) for k in range(K)])
    return ROLE, entities, values, clean, mem


def recovery_acc(D, K, seed):
    ROLE, entities, values, clean, mem = build(D, K, seed)
    ok = 0
    for k in range(K):
        got = clean.cleanup(unbind(mem, bind(entities[k], ROLE)))[0]
        ok += (got == f"V{k}")
    return ok / K


def k_star(D, seed, ks):
    """Largest K (scanned) whose recovery >= 0.90."""
    best = 0
    for K in ks:
        if recovery_acc(D, K, seed) >= 0.90:
            best = K
    return best


def no_hallucination_gap(D, K, seed):
    """Taught-entity best-match sim minus an UNtaught-entity best-match sim (want > 0 => separable)."""
    rng = np.random.default_rng(seed + 100)
    ROLE, entities, values, clean, mem = build(D, K, seed)
    taught = np.mean([max(sim(unbind(mem, bind(entities[k], ROLE)), v) for v in values) for k in range(K)])
    untaught = []
    for _ in range(K):
        e = rand_hv(D, rng)
        untaught.append(max(sim(unbind(mem, bind(e, ROLE)), v) for v in values))
    return float(taught - np.mean(untaught)), float(taught), float(np.mean(untaught))


if __name__ == "__main__":
    print("=== JEP-294: VSA bundle capacity for instance-distinct facts ===", flush=True)
    seeds = [0, 7]
    Ks = [2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512]
    Ds = [2048, 4096, 8192]

    # J294a: K=8, D=4096
    a_acc = {s: recovery_acc(4096, 8, s) for s in seeds}
    J294a = all(a_acc[s] >= 0.90 for s in seeds)
    for s in seeds:
        print(f"  J294a seed {s}: recovery@(K=8,D=4096) = {a_acc[s]:.3f}", flush=True)

    # J294b: K* vs D
    kstar = {D: {s: k_star(D, s, Ks) for s in seeds} for D in Ds}
    kstar_mean = {D: float(np.mean([kstar[D][s] for s in seeds])) for D in Ds}
    for D in Ds:
        print(f"  J294b K*(D={D}) = {kstar_mean[D]:.1f}  (seeds {[kstar[D][s] for s in seeds]})", flush=True)
    J294b = kstar_mean[8192] >= 1.5 * max(kstar_mean[2048], 1e-9)

    # J294c: no-hallucination gap at K=8, D=4096
    c = {s: no_hallucination_gap(4096, 8, s) for s in seeds}
    for s in seeds:
        print(f"  J294c seed {s}: taught={c[s][1]:.3f} untaught={c[s][2]:.3f} gap={c[s][0]:+.3f}", flush=True)
    J294c = all(c[s][0] > 0 for s in seeds)

    passed = J294a and J294b and J294c
    print("\n--- VERDICT ---", flush=True)
    print(f"J294a instance-distinct retrieval @K=8,D=4096 (>=0.90): {J294a}", flush=True)
    print(f"J294b capacity scales ~linearly (K*(8192)>=1.5*K*(2048)): {J294b}", flush=True)
    print(f"J294c untaught entity separable (gap>0)                : {J294c}", flush=True)
    verdict = ("PASS - the binding store holds many instance-distinct facts in ONE bundle, capacity scales with "
               "vector size, and untaught queries are separable") if passed else "NULL/partial - see curve"
    print(f"\nJEP-294: {verdict}", flush=True)

    out = Path.home() / ".eqmod" / "bet" / "JEP294"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"a_acc": a_acc, "kstar": kstar, "kstar_mean": kstar_mean, "c_gap": c,
         "J294a": J294a, "J294b": J294b, "J294c": J294c, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
