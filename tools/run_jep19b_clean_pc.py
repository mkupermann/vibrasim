"""JEP-19b - clean multi-layer PC vs backprop, MATCHED (MSE+tanh+plain SGD). 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(7)
def act(z): return np.tanh(z)
def dact(z): return 1.0-np.tanh(z)**2
def load(npz):
    d=np.load(npz); Xtr=d["x_train"].reshape(-1,784).astype(np.float32)/255.0
    Xte=d["x_test"].reshape(-1,784).astype(np.float32)/255.0
    ytr=d["y_train"].astype(int); yte=d["y_test"].astype(int)
    Ytr=np.zeros((len(ytr),10),np.float32); Ytr[np.arange(len(ytr)),ytr]=1.0
    return Xtr,Ytr,ytr,Xte,yte
def init(dims):
    return [ (rng.standard_normal((dims[i],dims[i+1]))*(1.0/np.sqrt(dims[i]))).astype(np.float32) for i in range(len(dims)-1) ]
def forward(Ws,X):  # pred = act on hiddens, linear out
    a=X
    for l in range(len(Ws)-1): a=act(a@Ws[l])
    return a@Ws[-1]
def accuracy(Ws,X,y):
    out=np.empty(len(X),int)
    for i in range(0,len(X),4000): out[i:i+4000]=forward(Ws,X[i:i+4000]).argmax(1)
    return float(np.mean(out==y))
def train_backprop(Xtr,Ytr,dims,epochs,lr,bs=128):
    Ws=init(dims); n=len(Xtr); L=len(Ws)
    for ep in range(epochs):
        idx=rng.permutation(n)
        for b in range(0,n,bs):
            j=idx[b:b+bs]; X=Xtr[j]; Y=Ytr[j]
            # forward keeping pre-acts
            zs=[]; a=X; acts=[X]
            for l in range(L-1): z=a@Ws[l]; zs.append(z); a=act(z); acts.append(a)
            out=a@Ws[-1]; 
            g=(out-Y)/len(X)   # MSE grad
            grads=[None]*L; grads[-1]=acts[-1].T@g
            delta=g@Ws[-1].T
            for l in range(L-2,-1,-1):
                delta=delta*dact(zs[l]); grads[l]=acts[l].T@delta; delta=delta@Ws[l].T
            for l in range(L): Ws[l]-=lr*grads[l]
    return Ws
def train_pc(Xtr,Ytr,dims,epochs,lr,bs=128,infer=25,beta=0.1):
    Ws=init(dims); n=len(Xtr); L=len(Ws)
    for ep in range(epochs):
        idx=rng.permutation(n)
        for b in range(0,n,bs):
            j=idx[b:b+bs]; X=Xtr[j]; Y=Ytr[j]; B=len(j)
            # value nodes a[0..L]; a0=X clamped, init others by feedforward
            a=[X]
            for l in range(L-1): a.append(act(a[-1])@Ws[l] if l>0 else a[-1]@Ws[l])
            a.append(a[-1]@Ws[-1] if False else act(a[-1])@Ws[-1])  # placeholder output init
            # recompute output init properly: pred[L] = act(a[L-1])@W[L-1]
            a[L]=act(a[L-1])@Ws[L-1]
            a[L]=Y.copy()  # clamp target
            # helper to compute predictions: pred[l] = (X if l-1==0 else act(a[l-1])) @ W[l-1]
            def pred(l):
                inp = a[l-1] if l-1==0 else act(a[l-1])
                return inp@Ws[l-1]
            for _ in range(infer):
                for l in range(1,L):  # relax hidden nodes 1..L-1
                    e_l=a[l]-pred(l)
                    e_lp1=a[l+1]-pred(l+1)
                    fb=(e_lp1@Ws[l].T)*dact(a[l])
                    a[l]=a[l]+beta*(-e_l+fb)
            # local weight updates: dW[l-1] = inp_{l-1}.T @ e_l
            for l in range(1,L+1):
                e_l=a[l]-pred(l)
                inp = a[l-1] if l-1==0 else act(a[l-1])
                Ws[l-1]+=lr*(inp.T@e_l)/B
    return Ws
def main():
    print("=== JEP-19b: clean PC vs backprop, MATCHED (MSE+tanh+plain SGD) ===",flush=True)
    for name,npz,epochs,lr in [("MNIST","data/mnist.npz",20,0.05),("Fashion-MNIST","data/fashion_mnist.npz",25,0.05)]:
        Xtr,Ytr,ytr,Xte,yte=load(npz)
        print(f"\n  [{name}]",flush=True)
        for hid,lbl in [([512],"1-hidden"),([512,512],"2-hidden")]:
            dims=[784]+hid+[10]
            Wb=train_backprop(Xtr,Ytr,dims,epochs,lr); ab=accuracy(Wb,Xte,yte)
            Wp=train_pc(Xtr,Ytr,dims,epochs,lr); ap=accuracy(Wp,Xte,yte)
            print(f"    {lbl}:  backprop={ab:.4f}   pred-coding={ap:.4f}",flush=True)
    print("\nDONE",flush=True)
if __name__=="__main__":
    main()
