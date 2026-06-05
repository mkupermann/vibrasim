"""JEP-313 — noise robustness: query with a bit-flipped key vector; recall vs flip-fraction f."""
import json
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory, atom_vector
from world.vsa import bind

D = 4096


def build(seed, nfacts=100):
    rng = np.random.default_rng(seed)
    mem = SubstrateMemory(D=D, tau=0.12, directed=True)
    facts = [(f"e{i}", "rel", f"v{i}") for i in range(nfacts)]
    for (e, r, o) in facts:
        mem.add_fact(e, r, o)
    return mem, facts, rng


def noisy_recall(mem, facts, f, rng):
    """For each fact, corrupt the key (flip fraction f of its signs), retrieve, check the value."""
    VM, names = mem._value_matrix()
    name_idx = {n: i for i, n in enumerate(names)}
    ok = 0
    for (e, r, o) in facts:
        key = bind(atom_vector(e, D), atom_vector(r, D)).copy()
        nflip = int(f * D)
        if nflip:
            idx = rng.choice(D, nflip, replace=False); key[idx] *= -1
        mods = list(mem._route(e, r))
        best, bi = -1e9, None
        for m in mods:
            rvec = mem._mem(m) * key
            rvec = np.roll(rvec, -1)
            sc = rvec @ VM.T / D
            j = int(np.argmax(sc))
            if sc[j] > best:
                best, bi = sc[j], names[j]
        ok += (bi == o)
    return ok / len(facts)


if __name__ == "__main__":
    seeds = [0, 7]; fs = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]
    curve = {s: {} for s in seeds}
    for s in seeds:
        mem, facts, rng = build(s)
        for f in fs:
            acc = noisy_recall(mem, facts, f, np.random.default_rng(s + int(f * 1000)))
            curve[s][f] = round(float(acc), 3)
            print(f"JEP313 seed {s} flip f={f}: recall={round(float(acc),3)}", flush=True)
    J313a = all(curve[s][0.10] >= 0.90 for s in seeds)
    fstar = {}
    for s in seeds:
        below = [f for f in fs if curve[s][f] < 0.90]
        fstar[s] = below[0] if below else f">{fs[-1]}"
    print(f"JEP-313: {'PASS' if J313a else 'NULL/partial'} | recall>=.90 at f=0.10={J313a} | f*(<.90)={fstar}",
          flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP313"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"curve": {str(s): {str(k): v for k, v in c.items()}
                                                            for s, c in curve.items()},
                                                  "J313a": J313a, "fstar": {str(k): str(v) for k, v in fstar.items()},
                                                  "passed": J313a}, default=str))
    print("DONE", flush=True)
