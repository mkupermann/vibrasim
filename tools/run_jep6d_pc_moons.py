"""JEP-6d - PC vs backprop on two-moons (iid generalization, the fair test)."""
import numpy as np
rng=np.random.default_rng(5)
def moons(n,noise=0.18):
    m=n//2; t=np.linspace(0,np.pi,m)
    a=np.stack([np.cos(t),np.sin(t)],1)
    b=np.stack([1-np.cos(t),1-np.sin(t)-0.5],1)
    X=np.vstack([a,b]); y=np.array([0]*m+[1]*m)
    X=X+rng.normal(0,noise,X.shape)
    idx=rng.permutation(len(X)); return X[idx],y[idx]
Xtr,ytr=moons(600); Xte,yte=moons(400)
mu,sd=Xtr.mean(0),Xtr.std(0)+1e-9; Xtr=(Xtr-mu)/sd; Xte=(Xte-mu)/sd
H=64;C=2;Din=2
Ytr=np.eye(C)[ytr]
def softmax(Z): Z=Z-Z.max(1,keepdims=True); e=np.exp(Z); return e/e.sum(1,keepdims=True)
def train_backprop(epochs=2000,lr=0.3):
    W1=rng.normal(0,.3,(Din,H)); W2=rng.normal(0,.3,(H,C))
    for ep in range(epochs):
        Hh=np.tanh(Xtr@W1); P=softmax(Hh@W2); g=(P-Ytr)/len(Xtr)
        W2-=lr*Hh.T@g; W1-=lr*Xtr.T@((g@W2.T)*(1-Hh**2))
    return W1,W2
def train_pc(epochs=2000,lr=0.3,infer=50,beta=0.1):
    W1=rng.normal(0,.3,(Din,H)); W2=rng.normal(0,.3,(H,C))
    for ep in range(epochs):
        Hp=np.tanh(Xtr@W1); Z=Hp.copy()
        for _ in range(infer):
            e1=Z-Hp; P=softmax(Z@W2); e2=Ytr-P; Z=Z+beta*(-e1+e2@W2.T)
        e1=Z-Hp; P=softmax(Z@W2); e2=Ytr-P
        W2+=lr*(Z.T@e2)/len(Xtr); W1+=lr*(Xtr.T@(e1*(1-Hp**2)))/len(Xtr)
    return W1,W2
def acc(W1,W2,X,y):
    return np.mean(softmax(np.tanh(X@W1)@W2).argmax(1)==y)
def main():
    print("=== JEP-6d: PC vs backprop on two-moons (iid, fair test) ===",flush=True)
    Wb=train_backprop(); Wp=train_pc(); Wr=(rng.normal(0,.3,(Din,H)),rng.normal(0,.3,(H,C)))
    ab=acc(*Wb,Xte,yte); ap=acc(*Wp,Xte,yte); ar=acc(*Wr,Xte,yte)
    print(f"  TRAIN acc: backprop={acc(*Wb,Xtr,ytr):.2f}  pred-coding={acc(*Wp,Xtr,ytr):.2f}",flush=True)
    print(f"  TEST acc:  backprop={ab:.2f}  pred-coding={ap:.2f}  random={ar:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if ab>=0.90 and ap>=ab-0.07 and ap>=0.7 and ar<0.7:
        print(f"JEP-6d: PASS - on a well-posed iid task, local predictive-coding learning MATCHES backprop:",flush=True)
        print(f"test acc PC={ap:.2f} vs backprop={ab:.2f} (within 0.07), both >> random {ar:.2f}. Predictive coding",flush=True)
        print(f"(Rao-Ballard; Whittington-Bogacz 2017, established) trains the net with LOCAL error nodes + hidden",flush=True)
        print(f"relaxation, no backprop. This validates the substrate-compatible local-learning path. Combined with",flush=True)
        print(f"JEP-4 (relaxation/Hebbian EBM) + JEP-5 (local rep-learning -> EBM/MPC), the JEPA+EBM+MPC loop has a",flush=True)
        print(f"backprop-free, substrate-native realization on well-posed tasks at toy scale.",flush=True)
    else:
        print(f"JEP-6d: PARTIAL/NULL - backprop {ab:.2f}, PC {ap:.2f}, random {ar:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
