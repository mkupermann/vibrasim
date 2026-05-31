"""BET-120 — order-2 (history-dependent) transitions to break the repeat/interference wall."""
import json
from pathlib import Path
import numpy as np
from world.energy import EnergyNet

def make_net(N, seed=0):
    return EnergyNet(n_per_module=N//2, n_modules=2, p_in=0.5, p_cross=0.04, beta=1.5, seed=seed)

class Order2:
    def __init__(self, net):
        self.net = net; self.N = net.N
        self.T2 = np.zeros((self.N, 2*self.N))
        self.START = np.ones(self.N)  # fixed start-of-sequence context
    def train(self, seq, lr_T=0.06, lr_W=0.02, assoc_epochs=120):
        self.net.train_sequence(seq, lr_T=0.0, lr_W=lr_W, assoc_epochs=assoc_epochs)  # W attractors only
        prev = self.START
        for t in range(len(seq)-1):
            ctx = np.concatenate([seq[t], prev])
            self.T2 += lr_T*np.outer(seq[t+1], ctx)
            prev = seq[t]
    def recall(self, start, length, cleanup=12):
        s = np.sign(start).astype(float); prev = self.START; out=[s.copy()]
        for _ in range(length-1):
            nxt = np.tanh(self.net.beta*(self.T2 @ np.concatenate([s, prev])))
            self.net.state = nxt; self.net.relax(None, None, cleanup)
            prev = s; s = self.net.state.copy(); out.append(s.copy())
        return out

def char_replay(text, N=200):
    rng = np.random.default_rng(1); alpha=sorted(set(text))
    cb={c:rng.choice([-1.,1.],N) for c in alpha}
    o2=Order2(make_net(N)); o2.train([cb[c] for c in text], assoc_epochs=150)
    rec=o2.recall(cb[text[0]], len(text))
    def dec(st): return max(alpha, key=lambda c: np.mean(np.sign(st)==np.sign(cb[c])))
    return ''.join([text[0]]+[dec(r) for r in rec[1:]])

def multiseq(npm,S,L=4,seed=0):
    net=make_net(2*npm,seed); rng=np.random.default_rng(7)
    seqs=[[rng.choice([-1.,1.],net.N) for _ in range(L)] for _ in range(S)]
    o2=Order2(net)
    for sq in seqs: o2.train(sq, assoc_epochs=100)
    mn=1.0
    for sq in seqs:
        rec=o2.recall(sq[0],L)
        mn=min(mn,min(float(np.mean(np.sign(r)==np.sign(p))) for r,p in zip(rec,sq)))
    return mn

if __name__=="__main__":
    print("=== BET-120: order-2 history-dependent transitions ===", flush=True)
    h=char_replay("HELLO"); print(f"  HELLO -> {h}  {'OK' if h=='HELLO' else 'still breaks'}", flush=True)
    m3=multiseq(100,3); m5=multiseq(100,5)
    print(f"  S=3 @N200 min overlap {m3:.3f}", flush=True)
    print(f"  S=5 @N200 min overlap {m5:.3f}", flush=True)
    T120a=(h=="HELLO"); T120b=m3>=0.90; T120c=m5>=0.85
    passed=T120a and T120b and T120c
    print("\n--- VERDICT ---", flush=True)
    print(f"T120a HELLO exact      : {T120a}", flush=True)
    print(f"T120b S=3 (>=0.90)     : {T120b}", flush=True)
    print(f"T120c S=5 (>=0.85)     : {T120c}", flush=True)
    print(f"\nBET-120: {'PASS (higher-order breaks the wall!)' if passed else 'NULL'}", flush=True)
    out=Path.home()/'.eqmod'/'bet'/'BET-120'; out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps({"HELLO":h,"m3":m3,"m5":m5,"passed":passed},indent=2))
    print("DONE", flush=True)
