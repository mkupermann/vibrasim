"""JEP-6b - clean PC vs backprop on (cell,action)-pair holdout (interpolation, learnable by both)."""
import numpy as np
rng=np.random.default_rng(3)
N=8; D=32; H=96
Wf=rng.normal(0,3.0,(2,D)); bf=rng.uniform(0,2*np.pi,D)
def enc(x,y):
    e=np.cos(np.array([x/N,y/N])@Wf+bf); return e/(np.linalg.norm(e)+1e-9)
KEYS=[(x,y) for x in range(N) for y in range(N)]
EMB=np.array([enc(*k) for k in KEYS])
DIRS={0:(1,0),1:(-1,0),2:(0,1),3:(0,-1)}
def step(x,y,a):
    dx,dy=DIRS[a]; return min(max(x+dx,0),N-1),min(max(y+dy,0),N-1)
def nearest(v): return KEYS[int(np.argmax(v@EMB.T))]
# all (cell,action) pairs, hold out 20%
pairs=[((x,y),a) for (x,y) in KEYS for a in range(4)]; rng.shuffle(pairs)
ho=set(range(len(pairs))); cut=int(0.2*len(pairs)); testidx=set(list(ho)[:cut])
def build(idxset,want):
    X=[];Y=[];M=[]
    for i,((x,y),a) in enumerate(pairs):
        if (i in testidx)!=want: continue
        nx,ny=step(x,y,a); X.append(np.concatenate([enc(x,y),np.eye(4)[a]])); Y.append(enc(nx,ny)); M.append((nx,ny))
    return np.array(X),np.array(Y),M
Xtr,Ytr,_=build(testidx,False); Xte,Yte,Mte=build(testidx,True); Din=D+4
def train_backprop(epochs=500,lr=0.2):
    W1=rng.normal(0,.1,(Din,H)); W2=rng.normal(0,.1,(H,D))
    for ep in range(epochs):
        Hh=np.tanh(Xtr@W1); P=Hh@W2; Pn=P/(np.linalg.norm(P,axis=1,keepdims=True)+1e-9)
        g=(Pn-Ytr)/len(Xtr); W2-=lr*Hh.T@g; W1-=lr*Xtr.T@((g@W2.T)*(1-Hh**2))
    return W1,W2
def train_pc(epochs=500,lr=0.2,infer=25,beta=0.1):
    W1=rng.normal(0,.1,(Din,H)); W2=rng.normal(0,.1,(H,D))
    for ep in range(epochs):
        Hp=np.tanh(Xtr@W1); Z=Hp.copy()
        for _ in range(infer):
            e1=Z-Hp; O=Z@W2; e2=Ytr-O; Z=Z+beta*(-e1+e2@W2.T)
        e1=Z-Hp; O=Z@W2; e2=Ytr-O
        W2+=lr*(Z.T@e2)/len(Xtr); W1+=lr*(Xtr.T@(e1*(1-Hp**2)))/len(Xtr)
    return W1,W2
def hits(W1,W2,X,M):
    P=np.tanh(X@W1)@W2; P/=np.linalg.norm(P,axis=1,keepdims=True)+1e-9
    return np.mean([nearest(P[i])==M[i] for i in range(len(M))])
def main():
    print("=== JEP-6b: clean PC vs backprop (interpolation split) ===",flush=True)
    Wb=train_backprop(); Wp=train_pc(); Wr=(rng.normal(0,.1,(Din,H)),rng.normal(0,.1,(H,D)))
    hb=hits(*Wb,Xte,Mte); hp=hits(*Wp,Xte,Mte); hr=hits(*Wr,Xte,Mte)
    print(f"  held-out (cell,action) hits@1:  BACKPROP={hb:.2f}  PRED-CODING={hp:.2f}  RANDOM={hr:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if hb>=0.7 and hp>=0.7 and abs(hp-hb)<=0.10 and hp>=hr+0.3:
        print(f"JEP-6b: PASS - local predictive-coding learning matches backprop ({hp:.2f} vs {hb:.2f}, |diff|<=0.10),",flush=True)
        print(f"both >= 0.70 and far above random {hr:.2f}. The substrate-compatible local-learning path to JEPA's",flush=True)
        print(f"'predict in representation space' is validated. Predictive coding (Rao-Ballard; Whittington-Bogacz",flush=True)
        print(f"2017) = established method, named as such. With JEP-4 (relaxation/Hebbian EBM) + JEP-5 (local",flush=True)
        print(f"rep-learning) + JEP-6b (local predictor), the full JEPA+EBM+MPC loop has a substrate-native",flush=True)
        print(f"(backprop-free) realization at toy scale.",flush=True)
    else:
        print(f"JEP-6b: PARTIAL/NULL - PC {hp:.2f} vs backprop {hb:.2f} vs random {hr:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
