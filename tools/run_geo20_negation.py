"""GEO-20 — edge test: negation & comparison, where embedding geometry is expected to break."""
import numpy as np
from sentence_transformers import SentenceTransformer

DATA=[("Paris","France","Europe"),("Berlin","Germany","Europe"),("Rome","Italy","Europe"),
      ("Madrid","Spain","Europe"),("Tokyo","Japan","Asia"),("Beijing","China","Asia"),
      ("Delhi","India","Asia"),("Cairo","Egypt","Africa"),("Lagos","Nigeria","Africa"),
      ("Nairobi","Kenya","Africa"),("Lima","Peru","SouthAmerica"),("Bogota","Colombia","SouthAmerica")]
POP=[("Tokyo",37),("Delhi",32),("Beijing",21),("Lagos",15),("Cairo",21),("Lima",11),("Paris",11),("Bogota",11)]


def f1(pred,true):
    p=set(pred); t=set(true)
    if not p and not t: return 1.0
    tp=len(p&t); 
    prec=tp/len(p) if p else 0; rec=tp/len(t) if t else 0
    return 0.0 if prec+rec==0 else 2*prec*rec/(prec+rec)


def main():
    print("=== GEO-20: negation & comparison edge test ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    cities=[d[0] for d in DATA]; conts=[d[2] for d in DATA]
    CE=np.array(m.encode(cities,normalize_embeddings=True))
    # (A) negation: "cities NOT in Europe"
    true_non_eu=[cities[i] for i in range(len(DATA)) if conts[i]!="Europe"]
    qv=m.encode(["Which cities are not in Europe?"],normalize_embeddings=True)[0]
    sims=CE@qv
    # pure-geometry interpretation: top-k most similar to the (negated) query
    k=len(true_non_eu)
    pure=[cities[i] for i in np.argsort(-sims)[:k]]
    pure_f1=f1(pure,true_non_eu)
    # symbolic: resolve each city's continent (geometry) then FILTER != Europe
    eu=m.encode(["Europe"],normalize_embeddings=True)[0]
    # resolve continent per city by nearest continent concept
    uc=sorted(set(conts)); UC=np.array(m.encode(uc,normalize_embeddings=True))
    sym=[cities[i] for i in range(len(DATA)) if uc[int(np.argmax(CE[i]@UC.T))]!="Europe"]
    sym_f1=f1(sym,true_non_eu)
    # (B) comparison
    popd=dict(POP); names=[p[0] for p in POP]
    NE=np.array(m.encode(names,normalize_embeddings=True))
    pairs=[(names[i],names[j]) for i in range(len(names)) for j in range(i+1,len(names))]
    corr=0
    for a,b in pairs:
        q=m.encode([f"Which has the larger population, {a} or {b}?"],normalize_embeddings=True)[0]
        # pure geometry: which name embedding is closer to the question
        sa=q@NE[names.index(a)]; sb=q@NE[names.index(b)]
        pick=a if sa>=sb else b
        truth=a if popd[a]>popd[b] else b
        corr+= int(pick==truth)
    comp=corr/len(pairs)
    print(f"  (A) negation 'not in Europe' pure-geometry F1 = {pure_f1:.2f}", flush=True)
    print(f"      negation via symbolic continent-filter  F1 = {sym_f1:.2f}", flush=True)
    print(f"  (B) comparison larger-population pure-geom  acc = {comp:.2f}  (chance 0.50)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if (pure_f1<0.6 or comp<0.65) and sym_f1>=0.9:
        print("GEO-20: PASS-as-designed - geometry alone is WEAK on negation/comparison (the expected edge); the symbolic layer fixes negation. Confirms: geometry retrieves, symbols negate/compare/aggregate.", flush=True)
    else:
        print(f"GEO-20: surprising - pure-neg {pure_f1:.2f}, comp {comp:.2f}, symbolic-neg {sym_f1:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
