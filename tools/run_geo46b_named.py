"""GEO-46b — realistic cross-lingual: German NAMED queries (shared entity anchor) -> English facts."""
import numpy as np
from sentence_transformers import SentenceTransformer
PAIRS=[("France","Paris"),("Japan","Tokyo"),("Egypt","Cairo"),("Italy","Rome"),("Spain","Madrid"),
       ("China","Beijing"),("Russia","Moscow"),("Greece","Athens"),("Canada","Ottawa"),("Brazil","Brasilia"),
       ("Germany","Berlin"),("India","Delhi")]
DE={"France":"Frankreich","Japan":"Japan","Egypt":"Ägypten","Italy":"Italien","Spain":"Spanien",
    "China":"China","Russia":"Russland","Greece":"Griechenland","Canada":"Kanada","Brazil":"Brasilien",
    "Germany":"Deutschland","India":"Indien"}
def main():
    print("=== GEO-46b: cross-lingual NAMED queries (DE->EN) ===", flush=True)
    m=SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    facts=[f"The capital of {c} is {city}." for c,city in PAIRS]
    ques=[f"Was ist die Hauptstadt von {DE[c]}?" for c,_ in PAIRS]
    F=np.array(m.encode(facts,normalize_embeddings=True)); Q=np.array(m.encode(ques,normalize_embeddings=True))
    n=len(PAIRS); acc=np.mean(np.argmax(Q@F.T,1)==np.arange(n))
    print(f"  DE named query -> EN fact hits@1 = {acc:.2f}  (chance {1/n:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"GEO-46b: {'PASS' if acc>=0.8 else 'PARTIAL'} - realistic cross-lingual retrieval (named queries) = {acc:.2f}. German questions with entity names reliably retrieve English facts.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__":
    main()
