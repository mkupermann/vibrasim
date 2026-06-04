"""JEP-19c - PC vs backprop on Fashion-MNIST with STANDARDIZED inputs + stable lr (fix divergence). 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(7)
def act(z): return np.tanh(z)
def dact(z): return 1.0-np.tanh(z)**2
d=np.load("data/fashion_mnist.npz")
Xtr=d["x_train"].reshape(-1,784).astype(np.float32)/255.0
Xte=d["x_test"].reshape(-1,784).astype(np.float32)/255.0
mu=Xtr.mean(0,keepdims=True); sd=Xtr.std(0,keepdims=True)+1e-3
Xtr=(Xtr-mu)/sd; Xte=(Xte-mu)/sd   # STANDARDIZE (fix conditioning)
ytr=d["y_train"].astype(int); yte=d["y_test"].astype(int)
Ytr=np.zeros((len(ytr),10),np.float32); Ytr[np.arange(len(ytr)),ytr]=1.0
def init(dims): return [ (rng.standard_normal((dims[i],dims[i+1]))*(1.0/np.sqrt(dims[i]))).astype(np.float32) for i in range(len(dims)-1) ]
def forward(Ws,X):
    a=X
    for l in range(len(Ws)-1): a=act(a@Ws[l])
    return a@Ws[-1]
def accuracy(Ws,X,y):
    out=np.empty(len(X),int)
    for i in range(0,len(X),4000): out[i:i+4000]=forward(Ws,X[i:i+4000]).argmax(1)
    return float(np.mean(out==y))
def train_backprop(dims,epochs,lr,bs=128):
    Ws=init(dims); n=len(Xtr); L=len(Ws)
    for ep in range(epochs):
        idx=rng.permutation(n)
        for b in range(0,n,bs):
            j=idx[b:b+bs]; X=Xtr[j]; Y=Ytr[j]
            zs=[]; a=X; acts=[X]
            for l in range(L-1): z=a@Ws[l]; zs.append(z); a=act(z); acts.append(a)
            out=a@Ws[-1]; g=(out-Y)/len(X); grads=[None]*L; grads[-1]=acts[-1].T@g; delta=g@Ws[-1].T
            for l in range(L-2,-1,-1):
                delta=delta*dact(zs[l]); grads[l]=acts[l].T@delta; delta=delta@Ws[l].T
            for l in range(L): Ws[l]-=lr*grads[l]
    return Ws
def train_pc(dims,epochs,lr,bs=128,infer=20,beta=0.1):
    Ws=init(dims); n=len(Xtr); L=len(Ws)
    for ep in range(epochs):
        idx=rng.permutation(n)
        for b in range(0,n,bs):
            j=idx[b:b+bs]; X=Xtr[j]; Y=Ytr[j]; B=len(j)
            a=[X]
            for l in range(L-1): a.append((X if l==0 else act(a[-1]))@Ws[l])
            a.append(act(a[-1])@Ws[-1]); a[L]=Y.copy()
            def pred(l):
                inp=a[l-1] if l-1==0 else act(a[l-1]); return inp@Ws[l-1]
            for _ in range(infer):
                for l in range(1,L):
                    e_l=a[l]-pred(l); e_lp1=a[l+1]-pred(l+1)
                    a[l]=a[l]+beta*(-e_l+(e_lp1@Ws[l].T)*dact(a[l]))
            for l in range(1,L+1):
                e_l=a[l]-pred(l); inp=a[l-1] if l-1==0 else act(a[l-1]); Ws[l-1]+=lr*(inp.T@e_l)/B
    return Ws
def main():
    print("=== JEP-19c: PC vs backprop on Fashion-MNIST (standardized inputs, lr=0.02) ===",flush=True)
    res={}
    for hid,lbl in [([512],"1-hidden"),([512,512],"2-hidden")]:
        dims=[784]+hid+[10]
        ab=accuracy(train_backprop(dims,25,0.02),Xte,yte)
        ap=accuracy(train_pc(dims,25,0.02),Xte,yte)
        res[lbl]=(ab,ap); print(f"  {lbl}:  backprop={ab:.4f}   pred-coding={ap:.4f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    ok=all(ab>=0.85 and ap>=ab-0.04 for ab,ap in res.values())
    if ok:
        print(f"JEP-19c: PASS - with standardized inputs (fixing JEP-19b's divergence), local PC matches backprop on",flush=True)
        print(f"harder Fashion-MNIST at BOTH depths: 1-hidden {res['1-hidden'][1]:.3f} vs {res['1-hidden'][0]:.3f},",flush=True)
        print(f"2-hidden {res['2-hidden'][1]:.3f} vs {res['2-hidden'][0]:.3f} (within 0.04). Local predictive coding",flush=True)
        print(f"scales with depth AND to harder data. Whittington-Bogacz (2017) established, named as such.",flush=True)
    else:
        print(f"JEP-19c: PARTIAL/NULL - {res}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
