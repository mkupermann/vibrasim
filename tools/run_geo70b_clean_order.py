"""GEO-70b — clean 2-way word-order test: retrieve between identical-bag facts (order is the only signal)."""
import numpy as np, torch
from sentence_transformers import SentenceTransformer

# each item: (factA, factB with SAME words different order, query, correct=0 for A)
ITEMS=[
 ("The cat chased the dog.","The dog chased the cat.","What did the cat chase?",0),
 ("The cat chased the dog.","The dog chased the cat.","What did the dog chase?",1),
 ("Alice teaches Bob.","Bob teaches Alice.","Who does Alice teach?",0),
 ("Alice teaches Bob.","Bob teaches Alice.","Who does Bob teach?",1),
 ("Canada is north of Mexico.","Mexico is north of Canada.","What is Canada north of?",0),
 ("Canada is north of Mexico.","Mexico is north of Canada.","What is Mexico north of?",1),
 ("John gave Mary a book.","Mary gave John a book.","Who did John give a book to?",0),
 ("John gave Mary a book.","Mary gave John a book.","Who did Mary give a book to?",1),
]


def main():
    print("=== GEO-70b: clean 2-way word-order test ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    tok=m.tokenizer; emb=m[0].auto_model.embeddings.word_embeddings
    def stat(t):
        ids=tok(t,return_tensors="pt",truncation=True)["input_ids"][0]
        with torch.no_grad(): v=emb(ids).mean(0).numpy()
        return v/(np.linalg.norm(v)+1e-9)
    ctx=0; st=0
    for fa,fb,q,correct in ITEMS:
        # contextual
        e=m.encode([fa,fb,q],normalize_embeddings=True)
        pick=0 if e[2]@e[0]>=e[2]@e[1] else 1; ctx+= int(pick==correct)
        # static
        sa,sb,sq=stat(fa),stat(fb),stat(q)
        picks=0 if sq@sa>=sq@sb else 1; st+= int(picks==correct)
    n=len(ITEMS)
    print(f"  contextual (transformer) 2-way acc = {ctx/n:.2f}", flush=True)
    print(f"  static (order-blind)     2-way acc = {st/n:.2f}  (chance 0.50)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ctx/n>=0.7 and ctx/n-st/n>=0.2:
        print(f"GEO-70b: PASS - the transformer genuinely beats static on pure WORD ORDER ({ctx/n:.2f} vs {st/n:.2f}~chance). Static mean-pooling is order-blind (coin-flip between swapped facts); the transformer's IRREDUCIBLE contribution is compositional/syntactic encoding. So the LLM's genuine value over distributional word vectors = handling word order / argument roles.", flush=True)
    else:
        print(f"GEO-70b: contextual {ctx/n:.2f}, static {st/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
