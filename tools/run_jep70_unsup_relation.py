"""JEP-70 - unsupervised relation discovery from unlabeled sequences (offset in a learned co-occurrence embedding)."""
import numpy as np
rng=np.random.default_rng(70)
N=60  # ring of N entities, relation 'next' = i->(i+1)%N
# UNLABELED sequences: random walks that mostly go 'next' (with some noise back-steps)
def gen_seq(L=200000):
    seq=[rng.integers(N)]
    for _ in range(L):
        i=seq[-1]; nxt=(i+1)%N if rng.random()<0.85 else (i-1)%N if rng.random()<0.5 else rng.integers(N)
        seq.append(nxt)
    return seq
seq=gen_seq()
# co-occurrence within window -> PPMI -> SVD embedding (no labels)
W=2; C=np.zeros((N,N))
for t in range(len(seq)):
    for d in range(1,W+1):
        if t+d<len(seq): C[seq[t],seq[t+d]]+=1; C[seq[t+d],seq[t]]+=1
C+=1e-6; P=C/C.sum(); pi=P.sum(1)
PPMI=np.maximum(np.log(P/(pi[:,None]*pi[None,:])+1e-12),0)
U,s,_=np.linalg.svd(PPMI); E=U[:,:16]*np.sqrt(s[:16])
def main():
    print("=== JEP-70: unsupervised relation discovery from unlabeled sequences ===", flush=True)
    # discover 'next' relation as mean offset over a FEW seed pairs (seeds: we know next for a few - minimal supervision)
    seeds=list(rng.choice(N,5,replace=False))
    offset=np.mean([E[(i+1)%N]-E[i] for i in seeds],0)
    # predict next for HELD-OUT entities (not seeds)
    held=[i for i in range(N) if i not in seeds]
    h1=0
    for i in held:
        pred=int(np.argmin(np.linalg.norm(E-(E[i]+offset),axis=1)+(np.arange(N)==i)*1e9))
        h1+=int(pred==(i+1)%N)
    acc=h1/len(held)
    print(f"  discovered-'next' held-out prediction hits@1 = {acc:.3f}  (from 5 seed pairs + UNLABELED sequences)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.7:
        print(f"JEP-70: PASS - the relation is DISCOVERED from UNLABELED sequences: a co-occurrence embedding (SVD of", flush=True)
        print(f"PPMI, no relation labels) places entities so 'next' is a consistent OFFSET; from just 5 seed pairs the", flush=True)
        print(f"offset predicts next for HELD-OUT entities at {acc:.2f}. Structure emerges from SEQUENCE STATISTICS,", flush=True)
        print(f"not labels - the relation is learned, then named by a few seeds (word2vec-style). Reduces the", flush=True)
        print(f"'hand-built structure' critique to near-zero supervision. Established (co-occurrence embeddings), named.", flush=True)
    else:
        print(f"JEP-70: PARTIAL/NULL - discovered-relation held-out hits@1 {acc:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()
