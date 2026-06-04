"""GEO-91 — learned linear adapter on frozen embeddings for domain retrieval."""
import numpy as np
from sentence_transformers import SentenceTransformer

# query/fact vocabulary gap: colloquial query vs formal fact, same referent
PAIRS=[("the money cap thing","The renovation budget is capped at 50 thousand dollars."),
       ("who fixes pipes","Raj Patel is a licensed plumbing contractor."),
       ("the teeth person","Omar Said is a dental surgeon."),
       ("car brake issue","The vehicle requires replacement of the brake pads."),
       ("tax paperwork deadline","The annual income tax return is due in 2025."),
       ("the lawyer lady","Maria Okafor is an attorney at the Justis firm."),
       ("trip to where","A spring holiday to Portugal is planned."),
       ("building approval task","Submission of the construction permit is pending."),
       ("the design person","Sarah Chen is a graphic designer."),
       ("kitchen water leak","The kitchen sink plumbing needs repair."),
       ("money advisor","Tom Reyes is a certified accountant."),
       ("reading suggestion","A novel about Antarctic exploration was recommended."),
       ("internet bill","The monthly broadband charge is sixty dollars."),
       ("home insurance cost","The property insurance premium is one hundred eighty."),
       ("rent amount","The monthly apartment rent is twelve hundred."),
       ("grocery spend","Monthly food shopping costs four hundred.")]


def main():
    print("=== GEO-91: linear adapter for domain retrieval ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    rng=np.random.default_rng(0)
    Q=np.array(m.encode([q for q,_ in PAIRS],normalize_embeddings=True))
    F=np.array(m.encode([f for _,f in PAIRS],normalize_embeddings=True))
    n=len(PAIRS); idx=rng.permutation(n); tr=idx[:10]; te=idx[10:]
    D=Q.shape[1]
    # frozen retrieval on held-out
    def hits(Qm,Fm,test): return np.mean([int(np.argmax(Qm[i]@Fm[te].T)==list(te).index(i)) for i in test])
    frozen=hits(Q,F,te)
    # learn adapter W (DxD) maximizing matched sim - mismatched, gradient on train pairs
    W=np.eye(D)*1.0; lr=0.05
    for _ in range(300):
        g=np.zeros((D,D))
        for i in tr:
            qi=W@Q[i]; 
            for j in tr:
                fj=W@F[j]; s=qi@fj/(np.linalg.norm(qi)*np.linalg.norm(fj)+1e-9)
                target=1.0 if i==j else 0.0
                # crude gradient: push W toward aligning matched, separating mismatched
                err=(s-target)
                g += err*np.outer(Q[i],F[j])+err*np.outer(F[j],Q[i])
        W-=lr*g/len(tr)
    Qa=(W@Q.T).T; Qa/=np.linalg.norm(Qa,axis=1,keepdims=True)+1e-9
    Fa=(W@F.T).T; Fa/=np.linalg.norm(Fa,axis=1,keepdims=True)+1e-9
    adapted=hits(Qa,Fa,te)
    print(f"  frozen   held-out hits@1 = {frozen:.2f}", flush=True)
    print(f"  adapted  held-out hits@1 = {adapted:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if adapted>=frozen+0.1:
        print(f"GEO-91: PASS - a cheap linear ADAPTER improves domain retrieval ({frozen:.2f}->{adapted:.2f}): training a projection on a few query<->fact pairs aligns the vocabulary gap. The retrieval bottleneck IS improvable cheaply (no full fine-tuning).", flush=True)
    elif adapted>=frozen:
        print(f"GEO-91: NULL/neutral - adapter matches frozen ({adapted:.2f} vs {frozen:.2f}); the frozen space is already near-optimal here, or too few examples. No cheap improvement.", flush=True)
    else:
        print(f"GEO-91: NULL - adapter HURTS ({adapted:.2f} < {frozen:.2f}); overfits on few examples. Frozen is better.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
