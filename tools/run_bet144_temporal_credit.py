"""BET-144 — deep TEMPORAL credit assignment without BPTT. Leaky-tanh RNN on delayed selective recall with
distractors. Three arms: RESERVOIR (readout-only baseline), RTRL (exact online gradient; Williams-Zipser
1989), E-PROP (eligibility-trace approximation; Bellec 2020 - substrate-native, BTSP-aligned). No BPTT, no
transformer. Established methods, named as such.

Pre-registered bars in docs/amendments/bet_144_temporal_credit_eprop.md.
"""
import json
from pathlib import Path
import numpy as np

K = 4            # vocabulary / classes
H = 24           # hidden size
ALPHA = 0.3      # leak
LR = 0.05        # learning rate (RTRL / e-prop), fixed pre-run
CLIP = 1.0       # grad-norm clip
N_TRAIN = 3000
N_TEST = 400
I = K + 2        # input dim: K-onehot + cue-bit + go-bit


def make_seq(rng, D, distractors):
    """Delayed selective recall. Returns (X: T x I, target_class)."""
    T = D + 2
    X = np.zeros((T, I))
    cue = rng.integers(K)
    X[0, cue] = 1.0; X[0, K] = 1.0            # cue symbol + cue-bit
    for t in range(1, D + 1):
        if distractors:
            X[t, rng.integers(K)] = 1.0       # distractor symbol, cue-bit=0
    X[D + 1, K + 1] = 1.0                      # go-bit
    return X, cue


def softmax(z):
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


def _forward_collect(Win, Wrec, X):
    """Run leaky-tanh RNN, return final hidden state."""
    h = np.zeros(H)
    for t in range(X.shape[0]):
        a = Wrec @ h + Win @ X[t]
        z = np.tanh(a)
        h = (1 - ALPHA) * h + ALPHA * z
    return h


# ---------------- RESERVOIR (readout-only, ridge) -----------------------------------------------
def run_reservoir(rng, D, distractors):
    sr = 0.9
    Wrec = rng.standard_normal((H, H)) / np.sqrt(H)
    ev = np.max(np.abs(np.linalg.eigvals(Wrec)))
    Wrec *= sr / (ev + 1e-9)
    Win = rng.standard_normal((H, I)) * 0.5
    Htr = np.zeros((N_TRAIN, H)); Ytr = np.zeros((N_TRAIN, K))
    for n in range(N_TRAIN):
        X, c = make_seq(rng, D, distractors)
        Htr[n] = _forward_collect(Win, Wrec, X); Ytr[n, c] = 1.0
    # ridge readout (strongest linear readout)
    lam = 1e-2
    Wout = np.linalg.solve(Htr.T @ Htr + lam * np.eye(H), Htr.T @ Ytr).T   # K x H
    correct = 0
    for _ in range(N_TEST):
        X, c = make_seq(rng, D, distractors)
        h = _forward_collect(Win, Wrec, X)
        if int(np.argmax(Wout @ h)) == c:
            correct += 1
    return correct / N_TEST


# ---------------- RTRL (exact online gradient) --------------------------------------------------
def run_rtrl(rng, D, distractors):
    Wrec = rng.standard_normal((H, H)) * (0.4 / np.sqrt(H))
    Win = rng.standard_normal((H, I)) * 0.5
    Wout = np.zeros((K, H))
    for n in range(N_TRAIN):
        X, c = make_seq(rng, D, distractors)
        T = X.shape[0]
        h = np.zeros(H)
        Prec = np.zeros((H, H, H))   # dh_i / dWrec[k,l]
        Pin = np.zeros((H, H, I))    # dh_i / dWin[k,l]
        for t in range(T):
            hp = h
            a = Wrec @ hp + Win @ X[t]
            z = np.tanh(a)
            psi = ALPHA * (1 - z * z)                       # dh/da
            # propagate influence through recurrence: Wrec @ P  (over hidden axis)
            Prec_prop = np.tensordot(Wrec, Prec, axes=([1], [0]))   # H x H x H
            Pin_prop = np.tensordot(Wrec, Pin, axes=([1], [0]))     # H x H x I
            IMM_rec = np.zeros((H, H, H)); idx = np.arange(H)
            IMM_rec[idx, idx, :] = hp                                # IMM[i,i,l]=hp[l]
            IMM_in = np.zeros((H, H, I)); IMM_in[idx, idx, :] = X[t]
            Prec = (1 - ALPHA) * Prec + psi[:, None, None] * (IMM_rec + Prec_prop)
            Pin = (1 - ALPHA) * Pin + psi[:, None, None] * (IMM_in + Pin_prop)
            h = (1 - ALPHA) * hp + ALPHA * z
        # loss at final step
        y = softmax(Wout @ h); err = y.copy(); err[c] -= 1.0
        dLdh = Wout.T @ err                                   # H
        gWrec = np.tensordot(dLdh, Prec, axes=([0], [0]))     # H x H
        gWin = np.tensordot(dLdh, Pin, axes=([0], [0]))       # H x I
        gWout = np.outer(err, h)
        for g in (gWrec, gWin, gWout):
            nrm = np.linalg.norm(g)
            if nrm > CLIP:
                g *= CLIP / nrm
        Wrec -= LR * gWrec; Win -= LR * gWin; Wout -= LR * gWout
    return _eval(Win, Wrec, Wout, rng, D, distractors)


# ---------------- E-PROP (eligibility trace, symmetric) -----------------------------------------
def run_eprop(rng, D, distractors):
    Wrec = rng.standard_normal((H, H)) * (0.4 / np.sqrt(H))
    Win = rng.standard_normal((H, I)) * 0.5
    Wout = np.zeros((K, H))
    for n in range(N_TRAIN):
        X, c = make_seq(rng, D, distractors)
        T = X.shape[0]
        h = np.zeros(H)
        e_rec = np.zeros((H, H))    # eligibility for Wrec[i,j]
        e_in = np.zeros((H, I))     # eligibility for Win[i,l]
        for t in range(T):
            hp = h
            a = Wrec @ hp + Win @ X[t]
            z = np.tanh(a)
            psi = ALPHA * (1 - z * z)
            # symmetric e-prop trace: leaky diagonal recurrence, presynaptic activity
            e_rec = (1 - ALPHA) * e_rec + psi[:, None] * hp[None, :]
            e_in = (1 - ALPHA) * e_in + psi[:, None] * X[t][None, :]
            h = (1 - ALPHA) * hp + ALPHA * z
        y = softmax(Wout @ h); err = y.copy(); err[c] -= 1.0
        L = Wout.T @ err                                      # learning signal (symmetric feedback)
        gWrec = L[:, None] * e_rec
        gWin = L[:, None] * e_in
        gWout = np.outer(err, h)
        for g in (gWrec, gWin, gWout):
            nrm = np.linalg.norm(g)
            if nrm > CLIP:
                g *= CLIP / nrm
        Wrec -= LR * gWrec; Win -= LR * gWin; Wout -= LR * gWout
    return _eval(Win, Wrec, Wout, rng, D, distractors)


def _eval(Win, Wrec, Wout, rng, D, distractors):
    correct = 0
    for _ in range(N_TEST):
        X, c = make_seq(rng, D, distractors)
        h = _forward_collect(Win, Wrec, X)
        if int(np.argmax(Wout @ h)) == c:
            correct += 1
    return correct / N_TEST


if __name__ == "__main__":
    print("=== BET-144: deep temporal credit (reservoir vs RTRL vs e-prop), no BPTT ===", flush=True)
    rng = np.random.default_rng(0)
    print("[sanity D=1, no distractors] (trainers must learn the easy case)", flush=True)
    rtrl_easy = run_rtrl(rng, D=1, distractors=False)
    eprop_easy = run_eprop(rng, D=1, distractors=False)
    print(f"  RTRL easy={rtrl_easy:.3f}  E-PROP easy={eprop_easy:.3f}  (chance {1/K:.2f})", flush=True)

    print("[hard D=8, distractors] (needs temporal credit)", flush=True)
    res_hard = run_reservoir(rng, D=8, distractors=True)
    rtrl_hard = run_rtrl(rng, D=8, distractors=True)
    eprop_hard = run_eprop(rng, D=8, distractors=True)
    print(f"  RESERVOIR={res_hard:.3f}  RTRL={rtrl_hard:.3f}  E-PROP={eprop_hard:.3f}  (chance {1/K:.2f})", flush=True)

    a = (rtrl_easy >= 0.90) and (eprop_easy >= 0.90)
    b = res_hard <= 0.45
    c = rtrl_hard >= 0.80
    d = (eprop_hard >= 0.70) and (eprop_hard >= res_hard + 0.25)
    if a and b and c and d:
        verdict = "PASS - substrate-native eligibility (e-prop) achieves deep temporal credit (delayed selective recall) a reservoir cannot, validated vs exact RTRL, no BPTT"
    elif a and b and c and not d:
        verdict = "PARTIAL - exact RTRL solves it but e-prop eligibility approximation does not; eligibility<->exact gap is the boundary"
    elif not b:
        verdict = "NULL - reservoir already solves the task (too easy, no deep credit needed)"
    elif not c:
        verdict = "NULL - even exact RTRL can't learn it (task/net mis-specified)"
    elif not a:
        verdict = "NULL(impl) - trainers failed the D=1 sanity at fixed hyperparams (not a credit-assignment finding)"
    else:
        verdict = "PARTIAL/mixed"
    print("\n--- VERDICT ---", flush=True)
    print(f"144a sanity (RTRL&eprop>=0.90 D=1) : {a}", flush=True)
    print(f"144b reservoir fails (<=0.45)      : {b}", flush=True)
    print(f"144c RTRL solves (>=0.80)          : {c}", flush=True)
    print(f"144d e-prop suffices (>=0.70,+0.25): {d}", flush=True)
    print(f"\nBET-144: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "BET144"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(dict(
        rtrl_easy=rtrl_easy, eprop_easy=eprop_easy, res_hard=res_hard, rtrl_hard=rtrl_hard,
        eprop_hard=eprop_hard, a=a, b=b, c=c, d=d, verdict=verdict), indent=2, default=str))
    print("DONE", flush=True)
