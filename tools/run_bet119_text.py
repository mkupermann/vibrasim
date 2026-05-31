"""BET-119 — the working single-sequence predictor on REAL characters. A short
text is encoded as a sequence of character-patterns; recall replays it. Unique-
character text replays exactly; repeated-character text breaks at the repeat
(the context limit, shown on readable text)."""
import json
from pathlib import Path
import numpy as np
from world.energy import EnergyNet

def char_codebook(alphabet, N, seed=1):
    rng = np.random.default_rng(seed)
    return {c: rng.choice([-1.0, 1.0], N) for c in alphabet}

def decode(state, codebook):
    best, bc = -2, '?'
    for c, code in codebook.items():
        o = float(np.mean(np.sign(state) == np.sign(code)))
        if o > best: best, bc = o, c
    return bc

def replay(text, N=200, seed=0):
    alpha = sorted(set(text))
    cb = char_codebook(alpha, N)
    net = EnergyNet(n_per_module=N//2, n_modules=2, p_in=0.5, p_cross=0.04,
                    beta=1.5, seed=seed)
    seq = [cb[c] for c in text]
    net.train_sequence(seq, lr_T=0.06, lr_W=0.02, assoc_epochs=150)
    state = cb[text[0]].copy(); out = [text[0]]
    for _ in range(len(text)-1):
        state = net.predict_step(state, cleanup_steps=12)
        out.append(decode(state, cb))
    return ''.join(out)

if __name__ == "__main__":
    print("=== BET-119: single-sequence character replay (what works + the limit) ===", flush=True)
    unique = "BRAIN"        # all distinct characters
    repeat = "HELLO"        # 'L' repeated -> ambiguous transition
    ru = replay(unique); rr = replay(repeat)
    print(f"  input  '{unique}'  ->  recalled '{ru}'   {'OK' if ru==unique else 'MISMATCH'}", flush=True)
    print(f"  input  '{repeat}'  ->  recalled '{rr}'   {'OK' if rr==repeat else 'BREAKS at repeat'}", flush=True)
    longer = "GEOMTRICAVS"   # distinct chars, longer
    rl = replay(longer, N=240)
    print(f"  input  '{longer}'  ->  recalled '{rl}'   {'OK' if rl==longer else 'MISMATCH'}", flush=True)

    T119a = (ru == unique) and (rl == longer)     # unique-char text replays exactly
    T119b = (rr != repeat)                         # repeated-char text breaks (the limit)
    passed = T119a and T119b
    print("\n--- VERDICT ---", flush=True)
    print(f"T119a unique-char text exact   : {T119a}", flush=True)
    print(f"T119b repeated-char breaks     : {T119b}  (demonstrates the context limit)", flush=True)
    print(f"\nBET-119: {'PASS' if passed else 'NULL/FAIL'}", flush=True)
    out=Path.home()/'.eqmod'/'bet'/'BET-119'; out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps({"unique":[unique,ru],"repeat":[repeat,rr],"longer":[longer,rl],"passed":passed},indent=2))
    print("DONE", flush=True)
