"""GEO-46 — cross-lingual grounded retrieval: German queries -> English facts via a multilingual model."""
import numpy as np
from sentence_transformers import SentenceTransformer

PAIRS=[("France","Paris","dem Eiffelturm"),("Japan","Tokyo","Sushi und dem Berg Fuji"),
       ("Egypt","Cairo","den Pyramiden und dem Nil"),("Italy","Rome","dem Kolosseum und Pasta"),
       ("Spain","Madrid","Flamenco und Paella"),("China","Beijing","der Großen Mauer"),
       ("Russia","Moscow","Sibirien als größtes Land"),("Greece","Athens","der Wiege der Demokratie"),
       ("Canada","Ottawa","dem Ahornblatt nördlich der USA"),("Brazil","Brasilia","dem Amazonas-Regenwald"),
       ("Germany","Berlin","Bier, Brezeln und dem Schwarzwald"),("India","Delhi","Currys und dem Taj Mahal")]


def main():
    print("=== GEO-46: cross-lingual retrieval (DE query -> EN fact) ===", flush=True)
    facts=[f"The capital of {c} is {city}." for c,city,_ in PAIRS]
    ques =[f"Welche Stadt ist die Hauptstadt des Landes mit {d}?" for _,_,d in PAIRS]  # German, no shared token
    n=len(PAIRS)
    def acc(model):
        m=SentenceTransformer(model)
        F=np.array(m.encode(facts,normalize_embeddings=True))
        Q=np.array(m.encode(ques,normalize_embeddings=True))
        return np.mean(np.argmax(Q@F.T,1)==np.arange(n))
    multi=acc("paraphrase-multilingual-MiniLM-L12-v2")
    mono=acc("all-MiniLM-L6-v2")
    print(f"  multilingual model  DE->EN hits@1 = {multi:.2f}", flush=True)
    print(f"  English-only model  DE->EN hits@1 = {mono:.2f}  (chance {1/n:.2f})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if multi>=0.7 and multi>=mono+0.2:
        print(f"GEO-46: PASS - cross-lingual grounded retrieval works: German questions retrieve the correct English facts ({multi:.2f}) via a multilingual shared space, where the English-only model is weaker ({mono:.2f}). Directly useful for a German-speaking user.", flush=True)
    else:
        print(f"GEO-46: PARTIAL/NULL - multi {multi:.2f}, mono {mono:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
