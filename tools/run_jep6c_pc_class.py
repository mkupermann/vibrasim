"""JEP-6c - PC vs backprop, 64-way softmax classification of next-cell (interpolation split)."""
import numpy as np
rng=np.random.default_rng(4)
N=8; D=32; H=128; C=N*N
Wf=rng.normal(0,3.0,(2,D)); bf=rng.uniform(0,2*np.pi,D)
def enc(x,y):
    e=np.cos(np.array([x/N,y/N])@Wf+bf); return e/(np.linalg.norm(e)+1e-9)
KEYS=[(x,y) for x in range(N) for y in range(N)]; IDX={k:i for i,k in enumerate(KEYS)}
DIRS={0:(1,0),1:(-1,0),2:(0,1),3:(0,-1)}
def step(x,y,a):
    dx,dy=DIRS[a]; return min(max(x+dx,0),N-1),min(max(y+dy,0),N-1)
pairs=[((x,y),a) for (x,y) in KEYS for a in range(4)]; rng.shuffle(pairs)
cut=int(0.2*len(pairs)); testidx=set(range(cut))   # already shuffled
def build(want):
    X=[];Yi=[]
    for i,((x,y),a) in enumerate(pairs):
        if (i in testidx)!=want: continue
        nx,ny=step(x,y,a); X.append(np.concatenate([enc(x,y),np.eye(4)[a]])); Yi.append(IDX[(nx,ny)])
    X=np.array(X); Y=np.zeros((len(Yi),C)); Y[np.arange(len(Yi)),Yi]=1; return X,Y,np.array(Yi)
Xtr,Ytr,ytr=build(False); Xte,Yte,yte=build(True); Din=D+4
def softmax(Z): Z=Z-Z.max(1,keepdims=True); e=np.exp(Z); return e/e.sum(1,keepdims=True)
def train_backprop(epochs=600,lr=0.3):
    W1=rng.normal(0,.1,(Din,H)); W2=rng.normal(0,.1,(H,C))
    for ep in range(epochs):
        Hh=np.tanh(Xtr@W1); P=softmax(Hh@W2); g=(P-Ytr)/len(Xtr)
        W2-=lr*Hh.T@g; W1-=lr*Xtr.T@((g@W2.T)*(1-Hh**2))
    return W1,W2
def train_pc(epochs=600,lr=0.3,infer=25,beta=0.1):
    W1=rng.normal(0,.1,(Din,H)); W2=rng.normal(0,.1,(H,C))
    for ep in range(epochs):
        Hp=np.tanh(Xtr@W1); Z=Hp.copy()
        for _ in range(infer):
            e1=Z-Hp; P=softmax(Z@W2); e2=Ytr-P; Z=Z+beta*(-e1+e2@W2.T)
        e1=Z-Hp; P=softmax(Z@W2); e2=Ytr-P
        W2+=lr*(Z.T@e2)/len(Xtr); W1+=lr*(Xtr.T@(e1*(1-Hp**2)))/len(Xtr)
    return W1,W2
def acc(W1,W2,X,y):
    P=softmax(np.tanh(X@W1)@W2); return np.mean(P.argmax(1)==y)
def main():
    print("=== JEP-6c: PC vs backprop, 64-way softmax classification ===",flush=True)
    Wb=train_backprop(); Wp=train_pc(); Wr=(rng.normal(0,.1,(Din,H)),rng.normal(0,.1,(H,C)))
    ab=acc(*Wb,Xte,yte); ap=acc(*Wp,Xte,yte); ar=acc(*Wr,Xte,yte)
    abt=acc(*Wb,Xtr,ytr); apt=acc(*Wp,Xtr,ytr)
    print(f"  TRAIN acc:    backprop={abt:.2f}  pred-coding={apt:.2f}",flush=True)
    print(f"  held-out acc: backprop={ab:.2f}  pred-coding={ap:.2f}  random={ar:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if ab>=0.7 and ap>=0.7 and abs(ap-ab)<=0.10 and ap>=ar+0.3:
        print(f"JEP-6c: PASS - local predictive-coding learning MATCHES a successful backprop predictor: held-out",flush=True)
        print(f"acc PC={ap:.2f} vs backprop={ab:.2f} (|diff|<=0.10), both >=0.70, random {ar:.2f}. The substrate-",flush=True)
        print(f"compatible local-learning path to JEPA's 'predict in representation space' is validated where the",flush=True)
        print(f"task is genuinely learnable. Predictive coding (Rao-Ballard; Whittington-Bogacz 2017) = established,",flush=True)
        print(f"named as such. Full substrate-native loop: JEP-4 (relax/Hebbian EBM) + JEP-5 (local rep-learning) +",flush=True)
        print(f"JEP-6c (local predictor) — backprop-free JEPA+EBM+MPC at toy scale.",flush=True)
    else:
        print(f"JEP-6c: PARTIAL/NULL - backprop {ab:.2f}, PC {ap:.2f}, random {ar:.2f} (train bp {abt:.2f}/pc {apt:.2f})",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
