"""JEP-315 — repair noise robustness (fixes JEP-313). Levers: wider vectors (D) and redundant copies. No transformer.
Pre-registered bars in docs/amendments/jep315_noise_fix.md.
"""
import json
from pathlib import Path
import numpy as np
from world.substrate_memory import SubstrateMemory, atom_vector
from world.vsa import bind, rand_hv


def width_recall(Dw, seed, fs, nfacts=100):
    rng = np.random.default_rng(seed)
    mem = SubstrateMemory(D=Dw, tau=0.12, directed=True)
    facts = [(f"e{i}", "rel", f"v{i}") for i in range(nfacts)]
    for (e, r, o) in facts:
        mem.add_fact(e, r, o)
    VM, names = mem._value_matrix()
    out = {}
    for f in fs:
        frng = np.random.default_rng(seed + int(f * 1000))
        ok = 0
        for (e, r, o) in facts:
            key = bind(atom_vector(e, Dw), atom_vector(r, Dw)).copy()
            nf = int(f * Dw)
            if nf:
                key[frng.choice(Dw, nf, replace=False)] *= -1
            best, bi = -1e9, None
            for m in mem._route(e, r):
                rv = np.roll(mem._mem(m) * key, -1)
                sc = rv @ VM.T / Dw
                j = int(np.argmax(sc))
                if sc[j] > best:
                    best, bi = sc[j], names[j]
            ok += (bi == o)
        out[f] = round(ok / nfacts, 3)
    return out


def redundant_recall(seed, fs, R=5, Dw=4096, nfacts=100):
    """Store each fact in R copies (independent copy-modifier vectors); average retrievals over copies."""
    rng = np.random.default_rng(seed)
    copy_vec = [rand_hv(Dw, rng) for _ in range(R)]
    ents = [f"e{i}" for i in range(nfacts)]; vals = [f"v{i}" for i in range(nfacts)]
    role = atom_vector("rel", Dw)
    accum = np.zeros(Dw)
    for i in range(nfacts):
        ekey = bind(atom_vector(ents[i], Dw), role)
        for k in range(R):
            accum = accum + bind(bind(ekey, copy_vec[k]), np.roll(atom_vector(vals[i], Dw), 1))
    mem = np.sign(accum); mem[mem == 0] = 1.0
    VM = np.stack([atom_vector(v, Dw) for v in vals]); names = vals
    out = {}
    for f in fs:
        frng = np.random.default_rng(seed + int(f * 1000))
        ok = 0
        for i in range(nfacts):
            ek = bind(atom_vector(ents[i], Dw), role).copy()
            nf = int(f * Dw)
            if nf:
                ek[frng.choice(Dw, nf, replace=False)] *= -1
            acc = np.zeros(Dw)
            for k in range(R):
                acc = acc + np.roll(mem * bind(ek, copy_vec[k]), -1)
            sc = (acc / R) @ VM.T / Dw
            ok += (names[int(np.argmax(sc))] == vals[i])
        out[f] = round(ok / nfacts, 3)
    return out


if __name__ == "__main__":
    print("=== JEP-315: repair noise robustness ===", flush=True)
    seeds = [0, 7]; fs = [0.05, 0.10, 0.15, 0.20, 0.30]
    width = {D: {s: width_recall(D, s, fs) for s in seeds} for D in [4096, 8192, 16384]}
    for D in [4096, 8192, 16384]:
        for s in seeds:
            print(f"  width D={D} seed {s}: {width[D][s]}", flush=True)
    redun = {s: redundant_recall(s, fs, R=5) for s in seeds}
    for s in seeds:
        print(f"  redundant R=5 D=4096 seed {s}: {redun[s]}", flush=True)

    J315a = all(width[8192][s][0.10] >= 0.90 for s in seeds) and all(width[16384][s][0.10] >= 0.90 for s in seeds)
    J315b = all(redun[s][0.10] >= 0.90 for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"J315a wider vectors recover recall>=.90 @f=0.10 (D=8192 & 16384): {J315a}", flush=True)
    print(f"J315b redundancy (R=5) recovers recall>=.90 @f=0.10            : {J315b}", flush=True)
    base = {s: width[4096][s][0.10] for s in seeds}
    print(f"  baseline D=4096 @f=0.10: {base}", flush=True)
    passed = J315a            # width is the primary fix; redundancy is exploratory (predicted may fail)
    verdict = ("PASS - wider vectors restore noise tolerance (D is the lever); redundancy result reported") if passed \
        else "NULL/partial"
    print(f"\nJEP-315: {verdict} (J315a={J315a}, J315b={J315b})", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP315"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({
        "width": {str(D): {str(s): {str(k): v for k, v in width[D][s].items()} for s in seeds} for D in width},
        "redun": {str(s): {str(k): v for k, v in redun[s].items()} for s in seeds},
        "J315a": J315a, "J315b": J315b, "passed": passed}, default=str))
    print("DONE", flush=True)
