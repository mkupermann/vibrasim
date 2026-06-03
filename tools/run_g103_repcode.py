"""G103 — reliable verbatim text via a repetition code (REP=3 majority vote).
Same substrate channel as G102; each message symbol is transmitted 3x and decoded by majority vote of
the 3 readouts. Reports uncoded (REP=1) vs coded (REP=3) CER to confirm the code is the cause.
Bar pre-registered in docs/amendments/g103_repcode.md.
"""
import sys, json, time
from collections import Counter
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
REP = 3
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
        syms.append(byte >> 4)
        syms.append(byte & 0x0F)
    return np.array(syms, dtype=int)


def symbols_to_str(syms):
    out = bytearray()
    for i in range(0, len(syms) - 1, 2):
        out.append((int(syms[i]) << 4) | int(syms[i + 1]))
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
    # calibrate decoder on random single-rep traffic
    rng = np.random.default_rng(10300 + seed)
    calib = rng.integers(0, K, CALIB)
    Xc = np.array([send_symbol(w, c, box, chan_x, s) for s in calib])
    X = np.hstack([Xc, np.ones((len(Xc), 1))])
    W = np.zeros((X.shape[1], K))
    for k in range(K):
        yk = (calib == k).astype(float) - (1.0 / K)
        W[:, k] = np.linalg.solve(X.T @ X + 1.0 * np.eye(X.shape[1]), X.T @ yk)

    def predict(state):
        return int((np.hstack([state, [1.0]]) @ W).argmax())

    msg_syms = str_to_symbols(MESSAGE)
    rep1, repN = [], []
    for s in msg_syms:
        votes = [predict(send_symbol(w, c, box, chan_x, s)) for _ in range(REP)]
        rep1.append(votes[0])                       # uncoded = first repetition
        repN.append(Counter(votes).most_common(1)[0][0])   # majority vote
    rec1 = symbols_to_str(np.array(rep1))
    recN = symbols_to_str(np.array(repN))
    cer1 = 1.0 - sum(1 for i in range(min(len(rec1), len(MESSAGE))) if rec1[i] == MESSAGE[i]) / len(MESSAGE)
    cerN = 1.0 - sum(1 for i in range(min(len(recN), len(MESSAGE))) if recN[i] == MESSAGE[i]) / len(MESSAGE)
    return dict(rec1=rec1, recN=recN, cer1=cer1, cerN=cerN, exactN=(recN == MESSAGE))


if __name__ == "__main__":
    print("=== G103: reliable verbatim text via REP=3 repetition code ===", flush=True)
    print(f"  original : {MESSAGE!r}", flush=True)
    seeds = [42, 7]
    R = {}
    for s in seeds:
        R[s] = run(s)
        print(f"  seed {s}: uncoded CER={R[s]['cer1']:.2f} -> coded CER={R[s]['cerN']:.2f} | coded={R[s]['recN']!r} exact={R[s]['exactN']}", flush=True)
    G103a = all(R[s]['exactN'] for s in seeds)
    G103b = all(R[s]['cerN'] <= R[s]['cer1'] for s in seeds)
    print("\n--- VERDICT ---", flush=True)
    print(f"G103a verbatim (coded CER=0 both seeds): {G103a}", flush=True)
    print(f"G103b code helps (coded CER <= uncoded): {G103b}", flush=True)
    if G103a:
        print("G103: PASS - with a repetition code the substrate transmits text VERBATIM on both seeds (communication in writing, no LLM)", flush=True)
    else:
        print("G103: NULL/PARTIAL - repetition code did not yield verbatim on both seeds", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "G103"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"message": MESSAGE, "rows": {str(s): R[s] for s in seeds},
                                                  "passed": G103a}, indent=2, default=str))
    print("DONE", flush=True)
