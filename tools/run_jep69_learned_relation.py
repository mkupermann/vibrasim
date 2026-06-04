"""JEP-69 - learn a relation from observed pairs (TransE) and generalize to unseen pairs."""
import numpy as np
rng=np.random.default_rng(69)
N=80; Dd=20
# ground-truth relation: a structured map (each entity -> a tail via a hidden linear structure)
true_pos=rng.normal(0,1,(N,Dd))               # latent positions
Rtrue=rng.normal(0,1,Dd)                       # the relation = translation in latent space
# tail = nearest entity to head_pos + Rtrue
def tail_of(i):
    t=true_pos[i]+Rtrue; return int(np.argmin(np.linalg.norm(true_pos-t,axis=1) + (np.arange(N)==i)*1e9))
pairs=[(i,tail_of(i)) for i in range(N)]
rng.shuffle(pairs); cut=int(0.3*len(pairs)); HO=pairs[:cut]; TR=pairs[cut:]
def main():
    print("=== JEP-69: learn a relation from observation (TransE) ===", flush=True)
    E=rng.normal(0,0.1,(N,Dd)); r=rng.normal(0,0.1,Dd); lr=0.05; margin=1.0
    for it in range(4000):
        h,t=TR[rng.integers(len(TR))]; tn=rng.integers(N)
        pos=np.linalg.norm(E[h]+r-E[t]); neg=np.linalg.norm(E[h]+r-E[tn])
        if margin+pos-neg>0:
            gp=(E[h]+r-E[t])/(pos+1e-9); gn=(E[h]+r-E[tn])/(neg+1e-9)
            E[h]-=lr*(gp-gn); r-=lr*(gp-gn); E[t]+=lr*gp; E[tn]-=lr*gn
        E[h]/=max(1,np.linalg.norm(E[h])); E[t]/=max(1,np.linalg.norm(E[t]))
    # held-out tail prediction: rank true tail among all
    h1=h3=0
    for h,t in HO:
        d=np.linalg.norm(E+(E[h]+r),axis=1) if False else np.linalg.norm((E[h]+r)-E,axis=1)
        order=np.argsort(d)
        if order[0]==t: h1+=1
        if t in order[:3]: h3+=1
    print(f"  held-out tail prediction: hits@1={h1/len(HO):.3f}  hits@3={h3/len(HO):.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if h1/len(HO)>=0.7 and h3/len(HO)>=0.9:
        print(f"JEP-69: PASS - the relation is LEARNED from observation and GENERALIZES: held-out tail prediction", flush=True)
        print(f"hits@1 {h1/len(HO):.2f}, hits@3 {h3/len(HO):.2f}. Relational structure need NOT be hand-built - it can", flush=True)
        print(f"be learned from observed pairs (TransE, Bordes 2013) and applied to UNSEEN heads. Reduces the", flush=True)
        print(f"'hand-built structure' critique. HONEST caveat: the SUPERVISION (which pairs hold the relation) is", flush=True)
        print(f"given; UNSUPERVISED relation discovery remains the open gap. Established (TransE), named as such.", flush=True)
    else:
        print(f"JEP-69: PARTIAL/NULL - hits@1 {h1/len(HO):.2f}, hits@3 {h3/len(HO):.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
