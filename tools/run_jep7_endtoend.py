"""JEP-7 - end-to-end: contrastive-learned encoder + PC-learned predictor + energy-based MPC (all local)."""
import numpy as np
rng=np.random.default_rng(7)
N=8; Du=16; H=96
KEYS=[(x,y) for x in range(N) for y in range(N)]
DIRS={0:(1,0),1:(-1,0),2:(0,1),3:(0,-1)}
def step(x,y,a):
    dx,dy=DIRS[a]; return min(max(x+dx,0),N-1),min(max(y+dy,0),N-1)

def learn_encoder(steps=40000,eta=0.05,margin=1.0):
    E={k:rng.normal(0,0.3,Du) for k in KEYS}
    x,y=rng.integers(0,N),rng.integers(0,N)
    for _ in range(steps):
        a=rng.integers(0,4); nx,ny=step(x,y,a); s,sp=(x,y),(nx,ny)
        if s!=sp:
            d=E[sp]-E[s]; E[s]+=eta*d; E[sp]-=eta*d
        p,q=KEYS[rng.integers(len(KEYS))],KEYS[rng.integers(len(KEYS))]
        if p!=q:
            diff=E[p]-E[q]; dist=np.linalg.norm(diff)+1e-9
            if dist<margin:
                push=eta*(margin-dist)*diff/dist; E[p]+=push; E[q]-=push
        x,y=nx,ny
    M=np.mean([E[k] for k in KEYS],0)
    for k in KEYS: E[k]=E[k]-M
    return E

def make_data(E):
    X=[];Y=[]
    for (x,y) in KEYS:
        for a in range(4):
            nx,ny=step(x,y,a); X.append(np.concatenate([E[(x,y)],np.eye(4)[a]])); Y.append(E[(nx,ny)])
    return np.array(X),np.array(Y)

def train_pc(X,Y,epochs=500,lr=0.2,infer=30,beta=0.1):
    Din=X.shape[1]; Dout=Y.shape[1]
    W1=rng.normal(0,.1,(Din,H)); W2=rng.normal(0,.1,(H,Dout))
    for ep in range(epochs):
        Hp=np.tanh(X@W1); Z=Hp.copy()
        for _ in range(infer):
            e1=Z-Hp; O=Z@W2; e2=Y-O; Z=Z+beta*(-e1+e2@W2.T)
        e1=Z-Hp; O=Z@W2; e2=Y-O
        W2+=lr*(Z.T@e2)/len(X); W1+=lr*(X.T@(e1*(1-Hp**2)))/len(X)
    return W1,W2

def main():
    print("=== JEP-7: end-to-end substrate-native JEPA+EBM+MPC (all local) ===",flush=True)
    E=learn_encoder(); X,Y=make_data(E); W1,W2=train_pc(X,Y)
    W1r,W2r=rng.normal(0,.1,W1.shape),rng.normal(0,.1,W2.shape)
    def predict(W1,W2,emb,a): return np.tanh(np.concatenate([emb,np.eye(4)[a]])@W1)@W2
    # predictor accuracy (decode predicted latent to nearest cell)
    EMB=np.array([E[k] for k in KEYS])
    def nearest(v): return KEYS[int(np.argmin(np.linalg.norm(EMB-v,axis=1)))]
    acc=np.mean([nearest(predict(W1,W2,E[(x,y)],a))==step(x,y,a) for (x,y) in KEYS for a in range(4)])
    print(f"  PC predictor next-cell accuracy = {acc:.2f}",flush=True)
    def mpc(W1,W2,reps=60):
        ok=0
        for _ in range(reps):
            s=KEYS[rng.integers(len(KEYS))]; g=KEYS[rng.integers(len(KEYS))]
            if s==g: ok+=1; continue
            x,y=s
            for _ in range(3*N):
                ba=min(range(4),key=lambda a:np.linalg.norm(predict(W1,W2,E[(x,y)],a)-E[g]))
                x,y=step(x,y,ba)
                if (x,y)==g: ok+=1; break
        return ok/reps
    r_tr=mpc(W1,W2); r_un=mpc(W1r,W2r)
    # random-action baseline
    rok=0
    for _ in range(60):
        s=KEYS[rng.integers(len(KEYS))]; g=KEYS[rng.integers(len(KEYS))]
        if s==g: rok+=1; continue
        x,y=s
        for _ in range(3*N):
            x,y=step(x,y,rng.integers(4))
            if (x,y)==g: rok+=1; break
    r_rand=rok/60
    print(f"  MPC reached (TRAINED PC predictor)   = {r_tr:.2f}",flush=True)
    print(f"  MPC reached (UNTRAINED predictor)    = {r_un:.2f}",flush=True)
    print(f"  random-action baseline               = {r_rand:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if r_tr>=0.7 and r_tr>=r_un+0.3 and r_tr>=r_rand+0.2:
        print(f"JEP-7: PASS - the COMPLETE substrate-native loop plans: encoder (local contrastive) + predictor",flush=True)
        print(f"(predictive coding, local) + energy-based MPC reaches {r_tr:.2f} of goals, vs untrained predictor",flush=True)
        print(f"{r_un:.2f} and random {r_rand:.2f}. A fully backprop-free, locally-learned latent world model supports",flush=True)
        print(f"energy-based planning at toy scale. All components established (contrastive learning, predictive",flush=True)
        print(f"coding, EBM, MPC) - named as such. This is the substrate's principled job in JEPA/EBM/MPC, end to end.",flush=True)
    else:
        print(f"JEP-7: PARTIAL/NULL - trained {r_tr:.2f}, untrained {r_un:.2f}, random {r_rand:.2f}, pred-acc {acc:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()
