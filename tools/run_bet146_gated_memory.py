"""BET-146 — does a GATED memory cell (JANET-style forget gate) extend the working-memory horizon past the
ungated wall (BET-145), trained by exact online RTRL (no BPTT)? Confirms BET-145's architectural diagnosis.

Pre-registered bars in docs/amendments/bet_146_gated_memory.md.
"""
import json
from pathlib import Path
import numpy as np
from tools.run_bet144_temporal_credit import make_seq, softmax, K, I

H = 20
LR = 0.05
CLIP = 1.0
N_TRAIN = 2500
N_TEST = 400


def _forward(Wz, Uz, Wf, Uf, bf, Wout, X):
    h = np.zeros(H)
    for t in range(X.shape[0]):
        z = np.tanh(Wz @ X[t] + Uz @ h)
        f = 1.0 / (1.0 + np.exp(-(Wf @ X[t] + Uf @ h + bf)))
        h = f * h + (1 - f) * z
    return Wout @ h, h


def run_gated_rtrl(rng, D, distractors):
    sc = 0.4 / np.sqrt(H)
    Wz = rng.standard_normal((H, I)) * 0.5; Uz = rng.standard_normal((H, H)) * sc
    Wf = rng.standard_normal((H, I)) * 0.5; Uf = rng.standard_normal((H, H)) * sc
    bf = np.ones(H) * 1.0                      # retain-bias init (standard)
    Wout = np.zeros((K, H))
    idx = np.arange(H)
    for n in range(N_TRAIN):
        X, c = make_seq(rng, D, distractors)
        T = X.shape[0]
        h = np.zeros(H)
        # influence tensors dh_i/dparam
        P_Wz = np.zeros((H, H, I)); P_Uz = np.zeros((H, H, H))
        P_Wf = np.zeros((H, H, I)); P_Uf = np.zeros((H, H, H)); P_bf = np.zeros((H, H))
        for t in range(T):
            hp = h
            z = np.tanh(Wz @ X[t] + Uz @ hp)
            f = 1.0 / (1.0 + np.exp(-(Wf @ X[t] + Uf @ hp + bf)))
            dz = (1 - z * z)                      # z'
            dfp = f * (1 - f)                      # sigmoid'
            cf = (hp - z) * dfp                    # coeff on df/dtheta  (H,)
            cz = (1 - f) * dz                      # coeff on dz/dtheta  (H,)
            # recurrent propagation of prior influence through U_z and U_f
            def prop(P):
                return (np.tensordot(Uf, P, axes=([1], [0])),     # Uf @ P
                        np.tensordot(Uz, P, axes=([1], [0])))     # Uz @ P
            for name, P, imm_kind in (("Wz", P_Wz, "z"), ("Uz", P_Uz, "z"),
                                      ("Wf", P_Wf, "f"), ("Uf", P_Uf, "f"), ("bf", P_bf, "f")):
                UfP, UzP = prop(P)
                imm_z = np.zeros_like(P); imm_f = np.zeros_like(P)
                if name == "Wz": imm_z[idx, idx, :] = X[t]
                elif name == "Uz": imm_z[idx, idx, :] = hp
                elif name == "Wf": imm_f[idx, idx, :] = X[t]
                elif name == "Uf": imm_f[idx, idx, :] = hp
                elif name == "bf": imm_f[idx, idx] = 1.0
                # broadcast coeffs over param dims
                shp = (H,) + (1,) * (P.ndim - 1)
                Pn = f.reshape(shp) * P + cf.reshape(shp) * (imm_f + UfP) + cz.reshape(shp) * (imm_z + UzP)
                if name == "Wz": P_Wz = Pn
                elif name == "Uz": P_Uz = Pn
                elif name == "Wf": P_Wf = Pn
                elif name == "Uf": P_Uf = Pn
                elif name == "bf": P_bf = Pn
            h = f * hp + (1 - f) * z
        y = softmax(Wout @ h); err = y.copy(); err[c] -= 1.0
        dLdh = Wout.T @ err
        gWz = np.tensordot(dLdh, P_Wz, axes=([0], [0]))
        gUz = np.tensordot(dLdh, P_Uz, axes=([0], [0]))
        gWf = np.tensordot(dLdh, P_Wf, axes=([0], [0]))
        gUf = np.tensordot(dLdh, P_Uf, axes=([0], [0]))
        gbf = np.tensordot(dLdh, P_bf, axes=([0], [0]))
        gWout = np.outer(err, h)
        for g in (gWz, gUz, gWf, gUf, gbf, gWout):
            nrm = np.linalg.norm(g)
            if nrm > CLIP:
                g *= CLIP / nrm
        Wz -= LR * gWz; Uz -= LR * gUz; Wf -= LR * gWf; Uf -= LR * gUf; bf -= LR * gbf; Wout -= LR * gWout
    # eval
    correct = 0
    for _ in range(N_TEST):
        X, c = make_seq(rng, D, distractors)
        y, _ = _forward(Wz, Uz, Wf, Uf, bf, Wout, X)
        if int(np.argmax(y)) == c:
            correct += 1
    return correct / N_TEST


if __name__ == "__main__":
    print("=== BET-146: GATED cell + exact RTRL (no BPTT) on long-delay selective recall ===", flush=True)
    rng = np.random.default_rng(0)
    easy = run_gated_rtrl(rng, D=1, distractors=False)
    print(f"  sanity D=1: gated-RTRL={easy:.3f}  (chance {1/K:.2f})", flush=True)
    d16 = run_gated_rtrl(rng, D=16, distractors=True)
    print(f"  D=16 + distractors: gated-RTRL={d16:.3f}  (ungated RTRL was 0.290)", flush=True)
    d24 = run_gated_rtrl(rng, D=24, distractors=True)
    print(f"  D=24 + distractors: gated-RTRL={d24:.3f}  (ungated RTRL was 0.258)", flush=True)

    ungated_rtrl_24 = 0.258   # from BET-145
    a = easy >= 0.90
    b = d24 >= 0.80
    c = d24 >= ungated_rtrl_24 + 0.40
    if a and b and c:
        verdict = "PASS - a GATED cell extends the working-memory horizon past the ungated wall, learned online by exact RTRL (no BPTT); BET-145's architectural diagnosis CONFIRMED"
    elif a and d16 >= 0.80 and not b:
        verdict = "PARTIAL - gating extends the horizon (solves D=16) but not fully to D=24 at this size/budget"
    elif not b:
        verdict = "NULL - even a gated cell + exact RTRL can't learn D=24; learnability (not representability) is the wall"
    else:
        verdict = "PARTIAL/mixed"
    print("\n--- VERDICT ---", flush=True)
    print(f"146a sanity (>=0.90 D=1)            : {a}  ({easy:.3f})", flush=True)
    print(f"146b gating extends horizon (D24>=0.80): {b}  ({d24:.3f})", flush=True)
    print(f"146c attributable to gating (+0.40)  : {c}  (gated {d24:.3f} vs ungated {ungated_rtrl_24:.3f})", flush=True)
    print(f"\nBET-146: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "BET146"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(dict(easy=easy, d16=d16, d24=d24, a=a, b=b, c=c,
                                                      verdict=verdict), indent=2, default=str))
    print("DONE", flush=True)
