"""G104 — verbatim text by respecting the channel pitch: K=4 (pitch 6 > G97's ~3), no ECC.
Each byte = four 2-bit symbols. Same channel pipeline as G102 (calibrate on random traffic, WIN=4,
per-symbol reset). Predicts clean verbatim recovery on both seeds with no repetition code.
Bar pre-registered in docs/amendments/g104_k4_string.md.
"""
import sys, json, time
from dataclasses import replace
import numpy as np
from pathlib import Path
from world.state import World
from world.physics import tick
from tools.run_bet098 import inject_tight
from tools.run_bet093 import cull_free_vibrations
from tools.run_g43_protocell import cfg as protocfg

SETTLE = 200
K = 4
WIN = 4
NBINS = 24
SPAN = (6.0, 24.0)
CALIB = 240
MESSAGE = "EQMOD SUBSTRATE SPEAKS"


def vib_grid_x(w, box):
    n = w.s_pos.shape[0]
    alive = w.s_alive[:n]
    x = w.s_pos[:n, 0][alive]
    if len(x) == 0:
        return np.zeros(NBINS)
    idx = np.clip((x / box[0] * NBINS).astype(int), 0, NBINS - 1)
    return np.bincount(idx, minlength=NBINS).astype(float)


def str_to_symbols(s):
    syms = []
    for byte in s.encode("ascii"):
        syms += [(byte >> 6) & 3, (byte >> 4) & 3, (byte >> 2) & 3, byte & 3]
    return np.array(syms, dtype=int)


def symbols_to_str(syms):
    out = bytearray()
    for i in range(0, len(syms) - 3, 4):
        b = (int(syms[i]) << 6) | (int(syms[i + 1]) << 4) | (int(syms[i + 2]) << 2) | int(syms[i + 3])
        out.append(b)
    return out.decode("ascii", errors="replace")


def send_symbol(w, c, box, chan_x, s):
    for _ in range(WIN):
        inject_tight(w, c, box, chan_x[int(s)], n=14)
        tick(w, c.dt)
    state = vib_grid_x(w, box)
    cull_free_vibrations(w, keep_frac=0.0)
    return state


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    chan_x = np.linspace(SPAN[0], SPAN[1], K)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    rng = np.random.default_rng(10400 + seed)
    calib = rng.integers(0, K, CALIB)
    Xc = np.array([send_symbol(w, c, box, chan_x, s) for s in calib])
    X = np.hstack([Xc, np.ones((len(Xc), 1))])
    W = np.zeros((X.shape[1], K))
    for k in range(K):
        yk = (calib == k).astype(float) - (1.0 / K)
        W[:, k] = np.linalg.solve(X.T @ X + 1.0 * np.eye(X.shape[1]), X.T @ yk)
    msg_syms = str_to_symbols(MESSAGE)
    pred = np.array([int((np.hstack([send_symbol(w, c, box, chan_x, s), [1.0]]) @ W).argmax()) for s in msg_syms])
    recovered = symbols_to_str(pred)
    sym_acc = float(np.mean(pred == msg_syms))
    cer = 1.0 - sum(1 for i in range(min(len(recovered), len(MESSAGE))) if recovered[i] == MESSAGE[i]) / len(MESSAGE)
    return dict(recovered=recovered, sym_acc=sym_acc, cer=cer, exact=(recovered == MESSAGE))


if __name__ == "__main__":
    print("=== G104: verbatim text at K=4 (respecting G97 pitch), no ECC ===", flush=True)
    print(f"  original : {MESSAGE!r}", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: recovered={R[s]['recovered']!r} | sym-acc={R[s]['sym_acc']:.2f} CER={R[s]['cer']:.2f} exact={R[s]['exact']}", flush=True)
    G104a = all(R[s]['exact'] for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G104a verbatim (CER=0 both seeds, no ECC): {G104a}", flush=True)
    if G104a:
        print("G104: PASS - respecting the channel pitch, the substrate transmits text VERBATIM on both seeds, no error-correcting code (communication in writing, no LLM)", flush=True)
    else:
        print("G104: NULL/PARTIAL - not verbatim on both seeds", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G104"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"message": MESSAGE, "rows": {str(s): R[s] for s in seeds},
                                                  "passed": G104a}, indent=2, default=str))
    print("DONE", flush=True)
