"""GEO-92 — proper contrastive fine-tuning vs frozen for domain retrieval."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from run_geo91_adapter import PAIRS


def hits(m, test_pairs, all_facts):
    Q=np.array(m.encode([q for q,_ in test_pairs],normalize_embeddings=True))
    F=np.array(m.encode(all_facts,normalize_embeddings=True))
    ok=0
    for i,(q,f) in enumerate(test_pairs):
        j=int(np.argmax(Q[i]@F.T)); ok+= int(all_facts[j]==f)
    return ok/len(test_pairs)


def main():
    print("=== GEO-92: proper contrastive fine-tuning ===", flush=True)
    rng=np.random.default_rng(0); n=len(PAIRS); idx=rng.permutation(n); tr=[PAIRS[i] for i in idx[:10]]; te=[PAIRS[i] for i in idx[10:]]
    all_facts=[f for _,f in PAIRS]
    m=SentenceTransformer("all-MiniLM-L6-v2")
    frozen=hits(m, te, all_facts)
    # fine-tune
    train_ex=[InputExample(texts=[q,f]) for q,f in tr]
    loader=DataLoader(train_ex, shuffle=True, batch_size=4)
    loss=losses.MultipleNegativesRankingLoss(m)
    m.fit(train_objectives=[(loader,loss)], epochs=5, warmup_steps=2, show_progress_bar=False)
    tuned=hits(m, te, all_facts)
    print(f"  frozen     held-out hits@1 = {frozen:.2f}", flush=True)
    print(f"  fine-tuned held-out hits@1 = {tuned:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if tuned>=frozen+0.1:
        print(f"GEO-92: PASS - proper contrastive fine-tuning improves retrieval ({frozen:.2f}->{tuned:.2f}). The retrieval bottleneck IS improvable with proper FT (the crude adapter GEO-91 was method-limited). A real improvement lever (needs a few labelled pairs + a short CPU fine-tune).", flush=True)
    elif tuned>=frozen-0.05:
        print(f"GEO-92: NULL - fine-tuning doesn't help ({tuned:.2f} vs {frozen:.2f}): DATA-limited, not method-limited. 10 pairs is too few to improve a pretrained embedder; the frozen model is already strong. Confirms GEO-91 - cheap improvement needs MORE data.", flush=True)
    else:
        print(f"GEO-92: NULL - fine-tuning HURTS ({tuned:.2f} < {frozen:.2f}): overfits/forgets on 10 pairs. Frozen is better; don't fine-tune on tiny data.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
