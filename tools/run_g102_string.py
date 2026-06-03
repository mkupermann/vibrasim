"""G102 — end-to-end string transmission through the substrate (capstone demo).
Encode an ASCII string as nibble-symbols (K=16), transmit each through the one-hot spatial channel with
per-symbol reset, decode from the free-vibration readout (decoder calibrated on random traffic), and
reconstruct the string. No LLM / transformer / embedding — only the substrate channel + linear decode.
Bar pre-registered in docs/amendments/g102_endtoend_string.md.
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
K = 16
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
        syms.append(byte >> 4)        # high nibble
        syms.append(byte & 0x0F)      # low nibble
    return np.array(syms, dtype=int)


def symbols_to_str(syms):
    out = bytearray()
    for i in range(0, len(syms) - 1, 2):
        out.append((int(syms[i]) << 4) | int(syms[i + 1]))
    try:
        return out.decode("ascii", errors="replace")
    except Exception:
        return repr(bytes(out))


def transmit(w, c, box, chan_x, syms):
    states = []
    for s in syms:
        for _ in range(WIN):
            inject_tight(w, c, box, chan_x[int(s)], n=14)
            tick(w, c.dt)
        states.append(vib_grid_x(w, box))
        cull_free_vibrations(w, keep_frac=0.0)
    return np.array(states)


def run(seed):
    c = replace(protocfg(seed), membrane_channel_k=0.0)
    w = World(c)
    box = np.asarray(c.box_size)
    chan_x = np.linspace(SPAN[0], SPAN[1], K)
    for _ in range(SETTLE):
        tick(w, c.dt)
    object.__setattr__(c, 'lambda_gen', 0.0)
    cull_free_vibrations(w, keep_frac=0.0)
    # calibrate on random traffic
    rng = np.random.default_rng(10200 + seed)
    calib_syms = rng.integers(0, K, CALIB)
    Xc = transmit(w, c, box, chan_x, calib_syms)
    X = np.hstack([Xc, np.ones((len(Xc), 1))])
    W = np.zeros((X.shape[1], K))
    for k in range(K):
        yk = (calib_syms == k).astype(float) - (1.0 / K)
        W[:, k] = np.linalg.solve(X.T @ X + 1.0 * np.eye(X.shape[1]), X.T @ yk)
    # transmit the real message
    msg_syms = str_to_symbols(MESSAGE)
    Xm = transmit(w, c, box, chan_x, msg_syms)
    pred = (np.hstack([Xm, np.ones((len(Xm), 1))]) @ W).argmax(axis=1)
    recovered = symbols_to_str(pred)
    sym_acc = float(np.mean(pred == msg_syms))
    # character error rate vs original
    L = min(len(recovered), len(MESSAGE))
    cer = 1.0 - (sum(1 for i in range(L) if recovered[i] == MESSAGE[i]) / len(MESSAGE))
    return dict(recovered=recovered, sym_acc=sym_acc, cer=cer, exact=(recovered == MESSAGE))


if __name__ == "__main__":
    print("=== G102: end-to-end string through the substrate ===", flush=True)
    print(f"  original : {MESSAGE!r}", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: recovered={R[s]['recovered']!r} | sym-acc={R[s]['sym_acc']:.2f} CER={R[s]['cer']:.2f} exact={R[s]['exact']}", flush=True)
    G102a = all(R[s]['exact'] for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G102a verbatim recovery (CER=0 both seeds): {G102a}", flush=True)
    if G102a:
        print("G102: PASS - the substrate transmitted and recovered a text string verbatim (communication in writing, no LLM)", flush=True)
    else:
        print("G102: NULL/PARTIAL - string not recovered verbatim (see CER and garbled output above)", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G102"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"message": MESSAGE,
                                                  "rows": {str(s): R[s] for s in seeds},
                                                  "passed": G102a}, indent=2, default=str))
    print("DONE", flush=True)
