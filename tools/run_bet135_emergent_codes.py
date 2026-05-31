"""BET-135 — emergent (locally-learned) symbol codes vs the modular wall."""
import json
from pathlib import Path
import numpy as np

V, D = 12, 64
EPOCHS = 400
ETA_W, ETA_E = 0.05, 0.05

def setup(seed):
    rng = np.random.default_rng(seed)
    E = rng.normal(0, 1/np.sqrt(D), (V, D))
    O = rng.normal(0, 1/np.sqrt(D), (V, D))
    pos1 = rng.choice([-1.0, 1.0], D); pos2 = rng.choice([-1.0, 1.0], D)
    return rng, E, O, pos1, pos2

def context(E, a, b, pos1, pos2):
    c = pos1 * E[a] + pos2 * E[b]
    n = np.linalg.norm(c); return c / n if n > 0 else c

def train(seed=0, learn_codes=True):
    rng, E, O, pos1, pos2 = setup(seed)
    bigrams = [(a, b) for a in range(V) for b in range(V) if a != b]
    rng.shuffle(bigrams); te = bigrams[:44]; tr = bigrams[44:]
    W = np.zeros((D, D))
    def acc():
        ok = 0
        for (a, b) in te:
            c = context(E, a, b, pos1, pos2); pred = W @ c
            k = int(np.argmax(O @ pred))            # cleanup over output codebook
            if k == (a + b) % V: ok += 1
        return ok / len(te)
    for ep in range(EPOCHS):
        order = list(tr); rng.shuffle(order)
        for (a, b) in order:
            c = context(E, a, b, pos1, pos2)
            pred = W @ c
            err = O[(a + b) % V] - pred            # local target error
            back = W.T @ err                        # one linear step to the embedding
            W += ETA_W * np.outer(err, c)
            if learn_codes:
                E[a] += ETA_E * (pos1 * back)
                E[b] += ETA_E * (pos2 * back)
    return acc()

if __name__ == "__main__":
    print("=== BET-135: emergent codes vs the modular wall ===", flush=True)
    learn = float(np.mean([train(s, learn_codes=True) for s in range(3)]))
    frozen = float(np.mean([train(s, learn_codes=False) for s in range(3)]))
    print(f"  learnable-code held-out acc : {learn:.3f}", flush=True)
    print(f"  frozen-random (readout only): {frozen:.3f}", flush=True)
    T135a = learn >= 0.85; T135b = frozen < 0.30; T135c = (learn - frozen) >= 0.50
    passed = T135a and T135b and T135c
    print("\n--- VERDICT ---", flush=True)
    print(f"T135a emergent breaks wall (>=0.85): {T135a} ({learn:.3f})", flush=True)
    print(f"T135b established fails (<0.30)    : {T135b} ({frozen:.3f})", flush=True)
    print(f"T135c gap (>=0.50)                : {T135c} ({learn-frozen:.3f})", flush=True)
    if passed:
        msg = "PASS - emergent local-rule representations break a wall fixed random codes cannot"
    elif frozen < 0.30 and learn < 0.85:
        msg = "NULL - even learnable codes can't make ADDITIVE composition do modular arithmetic: the limit is the OPERATOR (-> circular-convolution binding)"
    else:
        msg = "NULL/partial"
    print(f"\nBET-135: {msg}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-135'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps({"learn":learn,"frozen":frozen,"passed":passed}, indent=2))
    print("DONE", flush=True)
