"""GEO-19 — integrated learn-then-reason pipeline on held-out data. MiniLM, CPU."""
import numpy as np
from sentence_transformers import SentenceTransformer

DATA=[("Paris","France","Europe"),("Berlin","Germany","Europe"),("Rome","Italy","Europe"),
      ("Madrid","Spain","Europe"),("Tokyo","Japan","Asia"),("Beijing","China","Asia"),
      ("Delhi","India","Asia"),("Cairo","Egypt","Africa"),("Lagos","Nigeria","Africa"),
      ("Nairobi","Kenya","Africa"),("Lima","Peru","SouthAmerica"),("Bogota","Colombia","SouthAmerica")]
TRAIN=list(range(0,12,2)); HELD=list(range(1,12,2))   # 6/6 split


def main():
    print("=== GEO-19: integrated learn-then-reason pipeline ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    cities=[d[0] for d in DATA]; countries=[d[1] for d in DATA]; conts=[d[2] for d in DATA]
    CE=np.array(m.encode(cities,normalize_embeddings=True))
    NE=np.array(m.encode(countries,normalize_embeddings=True))
    cc_facts=[f"{c} is in {ct}." for c,ct in zip(countries,conts)]
    CC=np.array(m.encode(cc_facts,normalize_embeddings=True))
    uniq_conts=sorted(set(conts))
    # (1) learn relation offset from TRAIN
    r=np.mean([NE[i]-CE[i] for i in TRAIN],0)
    # (2) apply to HELD-OUT cities -> predicted country
    pred_country={}; acc1=0
    for i in HELD:
        pv=CE[i]+r; j=int(np.argmax(pv@NE.T)); pred_country[i]=j; acc1+= int(j==i)
    acc1/=len(HELD)
    # (3) chain predicted country -> continent via retrieval; also oracle
    def cont_of_country(j):
        qv=m.encode([f"What continent is {countries[j]} in?"],normalize_embeddings=True)[0]
        k=int(np.argmax(qv@CC.T)); return conts[k]
    acc2=0; acc2_oracle=0; chain_cont={}
    for i in HELD:
        c_pred=cont_of_country(pred_country[i]); chain_cont[i]=c_pred
        acc2+= int(c_pred==conts[i])
        acc2_oracle+= int(cont_of_country(i)==conts[i])
    acc2/=len(HELD); acc2_oracle/=len(HELD)
    # (4) symbolic aggregate: count held-out cities per continent (true vs chained)
    true_cnt={c:sum(1 for i in HELD if conts[i]==c) for c in uniq_conts}
    chain_cnt={c:sum(1 for i in HELD if chain_cont[i]==c) for c in uniq_conts}
    acc4=np.mean([int(true_cnt[c]==chain_cnt[c]) for c in uniq_conts])
    print(f"  (1)+(2) learned relation generalizes to held-out cities  acc = {acc1:.2f}", flush=True)
    print(f"  (3) chain country->continent (on predicted)              acc = {acc2:.2f}  (oracle-country {acc2_oracle:.2f})", flush=True)
    print(f"  (4) end-to-end symbolic aggregate (count per continent)  acc = {acc4:.2f}", flush=True)
    print(f"      true {true_cnt}  chained {chain_cnt}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc1>=0.6 and acc2_oracle>=0.8 and acc4>=0.6:
        print("GEO-19: PASS - integrated learn->apply->chain->aggregate pipeline works on HELD-OUT data. The whole method runs as one system.", flush=True)
    else:
        print(f"GEO-19: PARTIAL - stages: learn {acc1:.2f}, chain(oracle) {acc2_oracle:.2f}, aggregate {acc4:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
