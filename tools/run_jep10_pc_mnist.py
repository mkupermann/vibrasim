"""JEP-10 - predictive coding vs backprop on full MNIST (16-thread BLAS)."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"]:
    os.environ[v]="16"
import numpy as np, time
rng=np.random.default_rng(10)
d=np.load("data/mnist.npz")
Xtr=d["x_train"].reshape(60000,784).astype(np.float32)/255.0
Xte=d["x_test"].reshape(10000,784).astype(np.float32)/255.0
ytr=d["y_train"].astype(int); yte=d["y_test"].astype(int)
Ytr=np.zeros((60000,10),np.float32); Ytr[np.arange(60000),ytr]=1
Din,H,C=784,1024,10
def softmax(Z): Z=Z-Z.max(1,keepdims=True); e=np.exp(Z); return e/e.sum(1,keepdims=True)
def acc(W1,W2,X,y):
    out=np.empty(len(X),int)
    for i in range(0,len(X),2000):
        out[i:i+2000]=softmax(np.tanh(X[i:i+2000]@W1)@W2).argmax(1)
    return float(np.mean(out==y))
def train_backprop(epochs=15,bs=200,lr=0.5):
    W1=(rng.standard_normal((Din,H))*0.05).astype(np.float32); W2=(rng.standard_normal((H,C))*0.05).astype(np.float32)
    n=len(Xtr)
    for ep in range(epochs):
        idx=rng.permutation(n)
        for b in range(0,n,bs):
            j=idx[b:b+bs]; X=Xtr[j]; Y=Ytr[j]
            Hh=np.tanh(X@W1); P=softmax(Hh@W2); g=(P-Y)/len(X)
            W2-=lr*Hh.T@g; W1-=lr*X.T@((g@W2.T)*(1-Hh**2))
    return W1,W2
def train_pc(epochs=15,bs=200,lr=0.5,infer=20,beta=0.1):
    W1=(rng.standard_normal((Din,H))*0.05).astype(np.float32); W2=(rng.standard_normal((H,C))*0.05).astype(np.float32)
    n=len(Xtr)
    for ep in range(epochs):
        idx=rng.permutation(n)
        for b in range(0,n,bs):
            j=idx[b:b+bs]; X=Xtr[j]; Y=Ytr[j]
            Hp=np.tanh(X@W1); Z=Hp.copy()
            for _ in range(infer):
                e1=Z-Hp; P=softmax(Z@W2); e2=Y-P; Z=Z+beta*(-e1+e2@W2.T)
            e1=Z-Hp; P=softmax(Z@W2); e2=Y-P
            W2+=lr*(Z.T@e2)/len(X); W1+=lr*(X.T@(e1*(1-Hp**2)))/len(X)
    return W1,W2
def main():
    print(f"=== JEP-10: PC vs backprop on MNIST (60k, net 784-{H}-10, 16 threads) ===",flush=True)
    t0=time.time(); Wb=train_backprop(); tb=time.time()-t0
    ab=acc(*Wb,Xte,yte); print(f"  backprop:       test acc={ab:.4f}  ({tb:.0f}s)",flush=True)
    t0=time.time(); Wp=train_pc(); tp=time.time()-t0
    ap=acc(*Wp,Xte,yte); print(f"  pred-coding:    test acc={ap:.4f}  ({tp:.0f}s)",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if ab>=0.95 and ap>=ab-0.03 and ap>=0.5:
        print(f"JEP-10: PASS - substrate-compatible LOCAL learning (predictive coding, no backprop) SCALES to real",flush=True)
        print(f"data: MNIST test acc PC={ap:.4f} matches backprop={ab:.4f} (within 0.03), both >> chance. The local-",flush=True)
        print(f"learning path is not a toy-only result - it holds at 60k x 784 with a 1024-wide net. Predictive",flush=True)
        print(f"coding (Whittington-Bogacz 2017) established, named as such. Trained on 16 CPU threads (no GPU",flush=True)
        print(f"training path on this AMD/Win/Py3.13 machine); GPU used for inference in JEP-10b.",flush=True)
    else:
        print(f"JEP-10: PARTIAL/NULL - backprop {ab:.4f}, PC {ap:.4f}",flush=True)
    # save the PC model for GPU-inference demo (JEP-10b)
    np.savez("data/jep10_pc_model.npz",W1=Wp[0],W2=Wp[1]); print("  saved PC model -> data/jep10_pc_model.npz",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
