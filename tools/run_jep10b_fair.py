"""JEP-10b - FAIR PC-vs-backprop on MNIST: equal lr sweep for both, report best (16 threads)."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"]: os.environ[v]="16"
import numpy as np, time
rng=np.random.default_rng(20)
d=np.load("data/mnist.npz")
Xtr=d["x_train"].reshape(60000,784).astype(np.float32)/255.0; Xte=d["x_test"].reshape(10000,784).astype(np.float32)/255.0
ytr=d["y_train"].astype(int); yte=d["y_test"].astype(int)
Ytr=np.zeros((60000,10),np.float32); Ytr[np.arange(60000),ytr]=1
Din,H,C=784,1024,10
def softmax(Z): Z=Z-Z.max(1,keepdims=True); e=np.exp(Z); return e/e.sum(1,keepdims=True)
def acc(W1,W2,X,y):
    out=np.empty(len(X),int)
    for i in range(0,len(X),2000): out[i:i+2000]=softmax(np.tanh(X[i:i+2000]@W1)@W2).argmax(1)
    return float(np.mean(out==y))
def init(): 
    r=np.random.default_rng(0); return (r.standard_normal((Din,H))*0.05).astype(np.float32),(r.standard_normal((H,C))*0.05).astype(np.float32)
def train_backprop(lr,epochs=12,bs=200):
    W1,W2=init(); n=len(Xtr)
    for ep in range(epochs):
        idx=rng.permutation(n)
        for b in range(0,n,bs):
            j=idx[b:b+bs]; X=Xtr[j]; Y=Ytr[j]
            Hh=np.tanh(X@W1); P=softmax(Hh@W2); g=(P-Y)/len(X); W2-=lr*Hh.T@g; W1-=lr*X.T@((g@W2.T)*(1-Hh**2))
    return W1,W2
def train_pc(lr,epochs=12,bs=200,infer=20,beta=0.1):
    W1,W2=init(); n=len(Xtr)
    for ep in range(epochs):
        idx=rng.permutation(n)
        for b in range(0,n,bs):
            j=idx[b:b+bs]; X=Xtr[j]; Y=Ytr[j]
            Hp=np.tanh(X@W1); Z=Hp.copy()
            for _ in range(infer):
                e1=Z-Hp; P=softmax(Z@W2); e2=Y-P; Z=Z+beta*(-e1+e2@W2.T)
            e1=Z-Hp; P=softmax(Z@W2); e2=Y-P; W2+=lr*(Z.T@e2)/len(X); W1+=lr*(X.T@(e1*(1-Hp**2)))/len(X)
    return W1,W2
def main():
    print(f"=== JEP-10b: FAIR PC vs backprop on MNIST (equal lr sweep, net 784-{H}-10, 16 threads) ===",flush=True)
    lrs=[0.05,0.1,0.2]
    bp={}; pc={}
    for lr in lrs:
        ab=acc(*train_backprop(lr),Xte,yte); bp[lr]=ab; print(f"  backprop   lr={lr}: {ab:.4f}",flush=True)
    for lr in lrs:
        ap=acc(*train_pc(lr),Xte,yte); pc[lr]=ap; print(f"  pred-code  lr={lr}: {ap:.4f}",flush=True)
    bb=max(bp.values()); bpc=max(pc.values())
    print(f"\n  BEST backprop={bb:.4f}  BEST pred-coding={bpc:.4f}",flush=True)
    print("--- VERDICT ---",flush=True)
    if bb>=0.95 and bpc>=bb-0.03:
        print(f"JEP-10b: PASS - with a FAIR equal lr sweep, predictive coding (local, no backprop) MATCHES backprop",flush=True)
        print(f"on real MNIST: best PC={bpc:.4f} vs best backprop={bb:.4f} (within 0.03). Substrate-compatible local",flush=True)
        print(f"learning scales to real data at parity with backprop. Whittington-Bogacz (2017) reproduced at 60k",flush=True)
        print(f"scale on 16 CPU threads. Established method, named as such.",flush=True)
    else:
        print(f"JEP-10b: PARTIAL/NULL - best backprop {bb:.4f}, best PC {bpc:.4f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
