"""GEO-69 — contextual (full transformer) vs static (mean-pooled word embeddings) semantic retrieval."""
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

ITEMS=[("the country famous for the Eiffel Tower","France","Paris"),
       ("the nation known for sushi and Mount Fuji","Japan","Tokyo"),
       ("the land of the pyramids and the Nile","Egypt","Cairo"),
       ("the country home to the Colosseum and pasta","Italy","Rome"),
       ("the nation of flamenco and paella","Spain","Madrid"),
       ("the country of the Great Wall","China","Beijing"),
       ("the largest country, spanning Siberia","Russia","Moscow"),
       ("the birthplace of democracy and the Parthenon","Greece","Athens"),
       ("the maple-leaf country north of the USA","Canada","Ottawa"),
       ("the Amazon rainforest's largest country","Brazil","Brasilia")]


def main():
    print("=== GEO-69: static vs contextual semantic retrieval ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    facts=[f"The capital of {c} is {city}." for _,c,city in ITEMS]
    qs=[f"What is the capital of {d}?" for d,_,_ in ITEMS]; n=len(ITEMS)
    # (a) contextual
    F=np.array(m.encode(facts,normalize_embeddings=True)); Q=np.array(m.encode(qs,normalize_embeddings=True))
    ctx=np.mean(np.argmax(Q@F.T,1)==np.arange(n))
    # (b) static: mean-pool the word-embedding layer (no transformer)
    tok=m.tokenizer; emb_layer=m[0].auto_model.embeddings.word_embeddings  # static token vectors
    def static_embed(texts):
        out=[]
        for t in texts:
            ids=tok(t,return_tensors="pt",truncation=True)["input_ids"][0]
            with torch.no_grad(): v=emb_layer(ids).mean(0).numpy()
            out.append(v/(np.linalg.norm(v)+1e-9))
        return np.array(out)
    Fs=static_embed(facts); Qs=static_embed(qs)
    stat=np.mean(np.argmax(Qs@Fs.T,1)==np.arange(n))
    print(f"  contextual (full transformer) hits@1 = {ctx:.2f}", flush=True)
    print(f"  static (mean-pooled word vecs) hits@1 = {stat:.2f}  (lexical 0.10)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if stat>=0.6:
        print(f"GEO-69: DEFLATION - semantic matching does NOT need the transformer ({stat:.2f} static vs {ctx:.2f} contextual): mean-pooled static word vectors already resolve descriptions. The capability is DISTRIBUTIONAL SEMANTICS (pre-transformer), not an LLM-specific one.", flush=True)
    elif ctx-stat>=0.3:
        print(f"GEO-69: the TRANSFORMER matters - contextual {ctx:.2f} >> static {stat:.2f}. Semantic description-matching genuinely needs contextual encoding, not just static word vectors.", flush=True)
    else:
        print(f"GEO-69: contextual {ctx:.2f}, static {stat:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
