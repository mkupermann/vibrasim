"""JEP-6 - predictive coding (local, no backprop) vs backprop for the JEPA next-state predictor."""
import numpy as np
rng=np.random.default_rng(2)
N=8; D=32; H=96
# smooth encoder: random Fourier features of (x/N,y/N) -> neighbours close
Wf=rng.normal(0,3.0,(2,D)); bf=rng.uniform(0,2*np.pi,D)
def enc(x,y):
    e=np.cos(np.array([x/N,y/N])@Wf+bf); return e/(np.linalg.norm(e)+1e-9)
KEYS=[(x,y) for x in range(N) for y in range(N)]
EMB=np.array([enc(*k) for k in KEYS])
DIRS={0:(1,0),1:(-1,0),2:(0,1),3:(0,-1)}
def step(x,y,a):
    dx,dy=DIRS[a]; return min(max(x+dx,0),N-1),min(max(y+dy,0),N-1)
def nearest(v): return KEYS[int(np.argmax(v@EMB.T))]

# build dataset; hold out 20% of cells as test contexts
cells=KEYS[:]; rng.shuffle(cells); test=set(cells[:13]); train=[c for c in cells if c not in test]
def make(ctx_cells):
    X=[];Y=[];meta=[]
    for (x,y) in ctx_cells:
        for a in range(4):
            nx,ny=step(x,y,a)
            X.append(np.concatenate([enc(x,y),np.eye(4)[a]])); Y.append(enc(nx,ny)); meta.append((nx,ny))
    return np.array(X),np.array(Y),meta
Xtr,Ytr,_=make(train); Xte,Yte,Mte=make(sorted(test))
Din=D+4


def evaluate(W1,W2,X,M):
    P=np.tanh(X@W1)@W2; P/=np.linalg.norm(P,axis=1,keepdims=True)+1e-9
    hits=np.mean([nearest(P[i])==M[i] for i in range(len(M))])
    mse=float(np.mean((P-make.__self__ if False else (P- (lambda:0)()) )**2)) if False else 0.0
    return hits


def train_backprop(epochs=400,lr=0.2):
    W1=rng.normal(0,.1,(Din,H)); W2=rng.normal(0,.1,(H,D))
    for ep in range(epochs):
        Hh=np.tanh(Xtr@W1); P=Hh@W2; Pn=P/(np.linalg.norm(P,axis=1,keepdims=True)+1e-9)
        g=(Pn-Ytr)/len(Xtr); W2-=lr*Hh.T@g; W1-=lr*Xtr.T@((g@W2.T)*(1-Hh**2))
    return W1,W2


def train_pc(epochs=400,lr=0.2,infer=20,beta=0.1):
    # predictive coding: hidden free-nodes relax to minimize prediction errors; LOCAL weight updates
    W1=rng.normal(0,.1,(Din,H)); W2=rng.normal(0,.1,(H,D))
    for ep in range(epochs):
        Hp=np.tanh(Xtr@W1)        # top-down prediction of hidden
        Z=Hp.copy()               # free hidden activity, init at prediction
        for _ in range(infer):    # relax Z to reduce errors (inference)
            e1=Z-Hp                # hidden prediction error (local)
            O=Z@W2; e2=Ytr-O       # output error (target clamped) (local)
            Z=Z+beta*(-e1+e2@W2.T) # gradient of energy wrt Z
        e1=Z-Hp; O=Z@W2; e2=Ytr-O
        # LOCAL learning: error x presynaptic activity (no backprop through layers)
        W2+=lr*(Z.T@e2)/len(Xtr)
        W1+=lr*(Xtr.T@(e1*(1-Hp**2)))/len(Xtr)
    return W1,W2


def hits(W1,W2,X,M):
    P=np.tanh(X@W1)@W2; P/=np.linalg.norm(P,axis=1,keepdims=True)+1e-9
    return np.mean([nearest(P[i])==M[i] for i in range(len(M))])


def main():
    print("=== JEP-6: predictive coding (local) vs backprop for JEPA predictor ===",flush=True)
    Wb=train_backprop(); Wp=train_pc()
    Wr=(rng.normal(0,.1,(Din,H)),rng.normal(0,.1,(H,D)))
    hb=hits(*Wb,Xte,Mte); hp=hits(*Wp,Xte,Mte); hr=hits(*Wr,Xte,Mte)
    print(f"  held-out next-cell hits@1:  BACKPROP={hb:.2f}   PRED-CODING={hp:.2f}   RANDOM={hr:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if hp>=hb-0.10 and hp>=0.7 and hp>=hr+0.3 and hb>=hr+0.3:
        print(f"JEP-6: PASS - predictive coding (LOCAL error nodes + hidden relaxation, NO backprop) trains the",flush=True)
        print(f"JEPA next-state predictor to {hp:.2f} hits@1, matching backprop {hb:.2f} (within 0.10) and far above",flush=True)
        print(f"random {hr:.2f}. The substrate-compatible local-learning path to 'predict in representation space'",flush=True)
        print(f"is validated at toy scale. Predictive coding (Rao-Ballard; Whittington-Bogacz 2017) = established,",flush=True)
        print(f"named as such. Completes the substrate-native JEPA loop: local rep-learning (JEP-5) + local",flush=True)
        print(f"predictor (JEP-6) + relaxation/Hebbian EBM inference (JEP-4).",flush=True)
    else:
        print(f"JEP-6: PARTIAL/NULL - PC {hp:.2f} vs backprop {hb:.2f} vs random {hr:.2f}",flush=True)
    print("DONE",flush=True)


if __name__=="__main__":
    main()
