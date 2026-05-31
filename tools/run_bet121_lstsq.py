"""BET-121 — least-squares order-2 sequence memory: break the sequence wall."""
import json
from pathlib import Path
import numpy as np
from world.energy import SequencePredictor

def code(alphabet, dim, seed=1):
    rng=np.random.default_rng(seed); return {c:rng.choice([-1.,1.],dim) for c in alphabet}

def replay_text(text, dim=200):
    al=sorted(set(text)); cb=code(al,dim)
    sp=SequencePredictor(dim, lam=0.05); sp.add_sequence([cb[c] for c in text]); sp.fit()
    rec=sp.recall(cb[text[0]], len(text))
    dec=lambda st: max(al, key=lambda c: np.mean(np.sign(st)==np.sign(cb[c])))
    return text[0]+''.join(dec(r) for r in rec[1:])

def multiseq(dim, S, L, seed=0, shuffle=False):
    rng=np.random.default_rng(7)
    seqs=[[rng.choice([-1.,1.],dim) for _ in range(L)] for _ in range(S)]
    sp=SequencePredictor(dim, lam=0.05)
    for sq in seqs: sp.add_sequence(sq)
    sp.fit()
    if shuffle:
        r=np.random.default_rng(9); sp.T2=r.permutation(sp.T2.flatten()).reshape(sp.T2.shape)
    mn=1.0
    for sq in seqs:
        rec=sp.recall(sq[0], L)
        mn=min(mn, min(float(np.mean(np.sign(r)==np.sign(p))) for r,p in zip(rec,sq)))
    return mn

if __name__=="__main__":
    print("=== BET-121: least-squares order-2 sequence memory ===", flush=True)
    h=replay_text("HELLO"); m=replay_text("MISSISSIPPI")
    print(f"  HELLO       -> {h}   {'OK' if h=='HELLO' else 'X'}", flush=True)
    print(f"  MISSISSIPPI -> {m}   {'OK' if m=='MISSISSIPPI' else 'X'}", flush=True)
    s12=multiseq(300,12,4); s20=multiseq(400,20,5); ctrl=multiseq(300,12,4,shuffle=True)
    print(f"  S=12 L=4 @N300 min overlap {s12:.3f}", flush=True)
    print(f"  S=20 L=5 @N400 min overlap {s20:.3f}", flush=True)
    print(f"  control (shuffled T2)      {ctrl:.3f}", flush=True)
    T121a=(h=="HELLO" and m=="MISSISSIPPI"); T121b=s12>=0.999; T121c=s20>=0.95; T121d=ctrl<0.70
    passed=T121a and T121b and T121c and T121d
    print("\n--- VERDICT ---", flush=True)
    print(f"T121a repeats exact     : {T121a}", flush=True)
    print(f"T121b S=12 exact        : {T121b}", flush=True)
    print(f"T121c S=20 (>=0.95)     : {T121c}", flush=True)
    print(f"T121d control fails     : {T121d}", flush=True)
    print(f"\nBET-121: {'PASS - sequence wall BROKEN (no transformer)' if passed else 'NULL'}", flush=True)
    out=Path.home()/'.eqmod'/'bet'/'BET-121'; out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps({"HELLO":h,"MISSISSIPPI":m,"s12":s12,"s20":s20,"ctrl":ctrl,"passed":passed},indent=2))
    print("DONE", flush=True)
