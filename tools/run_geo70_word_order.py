"""GEO-70 — transformer vs static on word-order-sensitive (compositional) matching."""
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# facts where word order / role determines meaning; queries share words with their CORRECT fact's relation
PAIRS=[
 ("Canada is north of the United States.","Which country is north of the United States?","Canada"),
 ("The United States is north of Mexico.","Which country is north of Mexico?","United States"),
 ("Alice is the teacher of Bob.","Who is the teacher of Bob?","Alice"),
 ("Bob is the student of Alice.","Who is the student of Alice?","Bob"),
 ("The cat chased the dog.","What did the cat chase?","dog"),
 ("The dog chased the cat.","What did the dog chase?","cat"),
 ("Paris is the capital of France.","What is the capital of France?","Paris"),
 ("France is a country whose capital is Paris.","Which country has Paris as its capital?","France"),
]


def main():
    print("=== GEO-70: word-order / compositional matching ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    facts=[f for f,_,_ in PAIRS]; qs=[q for _,q,_ in PAIRS]; n=len(PAIRS)
    F=np.array(m.encode(facts,normalize_embeddings=True)); Q=np.array(m.encode(qs,normalize_embeddings=True))
    ctx=np.mean(np.argmax(Q@F.T,1)==np.arange(n))
    # static mean-pooled (order-blind)
    tok=m.tokenizer; emb=m[0].auto_model.embeddings.word_embeddings
    def stat_embed(texts):
        out=[]
        for t in texts:
            ids=tok(t,return_tensors="pt",truncation=True)["input_ids"][0]
            with torch.no_grad(): v=emb(ids).mean(0).numpy()
            out.append(v/(np.linalg.norm(v)+1e-9))
        return np.array(out)
    Fs=stat_embed(facts); Qs=stat_embed(qs)
    stat=np.mean(np.argmax(Qs@Fs.T,1)==np.arange(n))
    print(f"  contextual (transformer) hits@1 = {ctx:.2f}", flush=True)
    print(f"  static (order-blind)     hits@1 = {stat:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ctx>=0.7 and ctx-stat>=0.2:
        print(f"GEO-70: PASS-as-designed - the TRANSFORMER genuinely beats static on WORD-ORDER/compositional matching ({ctx:.2f} vs {stat:.2f}). Static mean-pooling is order-blind and fails when word order changes meaning; the transformer's irreducible contribution is COMPOSITIONAL/SYNTACTIC encoding (beyond distributional keyword matching).", flush=True)
    else:
        print(f"GEO-70: see cells - contextual {ctx:.2f}, static {stat:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
