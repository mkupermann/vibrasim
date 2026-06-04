"""GEO-67 — minimum viable model for semantic description-retrieval (GEO-25b across model sizes)."""
import numpy as np
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


def acc(model):
    m=SentenceTransformer(model)
    facts=[f"The capital of {c} is {city}." for _,c,city in ITEMS]
    qs=[f"What is the capital of {d}?" for d,_,_ in ITEMS]
    F=np.array(m.encode(facts,normalize_embeddings=True)); Q=np.array(m.encode(qs,normalize_embeddings=True))
    n=len(ITEMS); return np.mean(np.argmax(Q@F.T,1)==np.arange(n))


def main():
    print("=== GEO-67: minimum viable model (semantic retrieval) ===", flush=True)
    for name,size in [("paraphrase-MiniLM-L3-v2","~17M/3-layer"),("all-MiniLM-L6-v2","~22M/6-layer"),("all-mpnet-base-v2","~110M/12-layer")]:
        try:
            a=acc(name); print(f"  {name:28s} ({size:14s}) semantic hits@1 = {a:.2f}", flush=True)
        except Exception as e:
            print(f"  {name}: load failed ({type(e).__name__})", flush=True)
    print("  (lexical baseline on this task: 0.10)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print("GEO-67: characterization — smallest model beating lexical decisively (>=0.6) is the efficiency floor.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
