"""JEP-1 — toy JEPA: predict masked element's representation from context; learn world structure."""
import numpy as np

rng=np.random.default_rng(0)
N=8; D=64
# fixed random target-encoder: cell (x,y) -> embedding (frozen "representation")
W1=rng.normal(0,1,(2,128)); W2=rng.normal(0,1,(128,D))
def enc(xy):
    h=np.tanh(np.array(xy,dtype=float)@W1); e=np.tanh(h@W2); return e/ (np.linalg.norm(e)+1e-9)
CELLS={(x,y):enc((x/N,y/N)) for x in range(N) for y in range(N)}
EMB=np.array(list(CELLS.values())); KEYS=list(CELLS.keys())
DIRS={0:(1,0),1:(-1,0),2:(0,1),3:(0,-1)}


def neighbour(x,y,d):
    dx,dy=DIRS[d]; nx,ny=x+dx,y+dy
    return (nx,ny) if (nx,ny) in CELLS else None


def make_data(cells):
    X=[];Y=[]
    for (x,y) in cells:
        for d in DIRS:
            n=neighbour(x,y,d)
            if n is None: continue
            ctx=np.concatenate([CELLS[(x,y)], np.eye(4)[d]])
            X.append(ctx); Y.append(CELLS[n])
    return np.array(X),np.array(Y)


def main():
    print("=== JEP-1: toy JEPA ===", flush=True)
    allc=list(CELLS); rng.shuffle(allc); tr=allc[:48]; te=allc[48:]
    Xtr,Ytr=make_data(tr); Xte,Yte=make_data(te)
    # JEPA predictor: 2-layer MLP context-emb -> target-emb (predict in representation space)
    Din=D+4; H=128; W_a=rng.normal(0,.1,(Din,H)); W_b=rng.normal(0,.1,(H,D)); lr=0.05
    for ep in range(400):
        Hh=np.tanh(Xtr@W_a); P=Hh@W_b
        P=P/(np.linalg.norm(P,axis=1,keepdims=True)+1e-9)
        g=(P-Ytr)/len(Xtr)
        W_b-=lr*Hh.T@g; W_a-=lr*Xtr.T@((g@W_b.T)*(1-Hh**2))
    def hits(Xset,Yset,cellset_keys):
        Hh=np.tanh(Xset@W_a); P=Hh@W_b; P/=np.linalg.norm(P,axis=1,keepdims=True)+1e-9
        ok=0
        for i in range(len(P)):
            j=int(np.argmax(P[i]@EMB.T)); ok+= int(np.allclose(EMB[j],Yset[i]))
        return ok/len(P)
    jepa_te=hits(Xte,Yte,te)
    # baselines on held-out: COPY (context cell emb), MEAN
    copy_ok=0
    for i in range(len(Xte)):
        ctx_emb=Xte[i][:D]; j=int(np.argmax(ctx_emb@EMB.T))  # nearest to context = itself (wrong, it's the source)
        copy_ok+= int(np.allclose(EMB[j],Yte[i]))
    mean=EMB.mean(0); mean/=np.linalg.norm(mean)+1e-9
    jm=int(np.argmax(mean@EMB.T)); mean_ok=np.mean([np.allclose(EMB[jm],Yte[i]) for i in range(len(Yte))])
    print(f"  JEPA held-out hits@1 = {jepa_te:.2f}", flush=True)
    print(f"  COPY baseline        = {copy_ok/len(Xte):.2f}", flush=True)
    print(f"  MEAN baseline        = {mean_ok:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if jepa_te>=0.7 and jepa_te>=copy_ok/len(Xte)+0.3:
        print(f"JEP-1: PASS - the toy JEPA learns the world's transition structure in REPRESENTATION space ({jepa_te:.2f}) and generalizes to HELD-OUT cells, far above baselines. Demonstrates LeCun's JEPA principle (predict the masked representation, not raw input) at PC scale. Established method, working demo.", flush=True)
    else:
        print(f"JEP-1: PARTIAL/NULL - JEPA {jepa_te:.2f}, copy {copy_ok/len(Xte):.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
