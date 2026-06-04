"""GEO-93 — fine-tuning with substantial data (validate the GEO-92 'hundreds+ helps' claim)."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# systematic vocab gap: colloquial query template vs formal fact template, over many roles/items
ROLES=["plumber","dentist","lawyer","accountant","architect","designer","electrician","painter","gardener",
       "mechanic","teacher","nurse","chef","tailor","barber","optician","vet","locksmith","roofer","welder",
       "baker","butcher","florist","jeweler","cobbler","mason","carpenter","glazier","plasterer","surveyor",
       "auditor","notary","broker","banker","actuary","analyst","consultant","trader","clerk","cashier"]
COLLOQ={"plumber":"the pipe fixing person","dentist":"the teeth person","lawyer":"the legal eagle",
        "accountant":"the money numbers guy","architect":"the building designer","designer":"the graphics person",
        "electrician":"the wiring guy","painter":"the wall colour person","gardener":"the plant person",
        "mechanic":"the car fixing guy"}


def colloq(role): return COLLOQ.get(role, f"the {role} expert person who does {role} work")
def formal(role,name): return f"{name} is a fully licensed and certified {role} providing professional services."


def hits(m, test, facts):
    Q=np.array(m.encode([q for q,_ in test],normalize_embeddings=True)); F=np.array(m.encode(facts,normalize_embeddings=True))
    return np.mean([int(facts[int(np.argmax(Q[i]@F.T))]==f) for i,(q,f) in enumerate(test)])


def main():
    print("=== GEO-93: fine-tuning with substantial data ===", flush=True)
    rng=np.random.default_rng(1)
    names=[f"Person{i}" for i in range(len(ROLES))]
    pairs=[(colloq(r), formal(r,n)) for r,n in zip(ROLES,names)]
    # expand with paraphrase variants to ~120
    extra=[]
    for r,n in zip(ROLES,names):
        extra.append((f"who can do {r} work", formal(r,n)))
        extra.append((f"i need someone for {r} stuff", formal(r,n)))
    allp=pairs+extra
    rng.shuffle(allp)
    ents=list(range(len(allp))); split=int(len(allp)*0.83); tr=allp[:split]; te=allp[split:]
    facts=[f for _,f in te]  # retrieve among test facts
    m=SentenceTransformer("all-MiniLM-L6-v2")
    frozen=hits(m,te,facts)
    loader=DataLoader([InputExample(texts=[q,f]) for q,f in tr], shuffle=True, batch_size=16)
    loss=losses.MultipleNegativesRankingLoss(m)
    m.fit(train_objectives=[(loader,loss)], epochs=4, warmup_steps=5, show_progress_bar=False)
    tuned=hits(m,te,facts)
    print(f"  train pairs={len(tr)}, test pairs={len(te)}", flush=True)
    print(f"  frozen     held-out hits@1 = {frozen:.2f}", flush=True)
    print(f"  fine-tuned held-out hits@1 = {tuned:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if tuned>=frozen+0.1:
        print(f"GEO-93: PASS - fine-tuning DOES help with substantial data ({frozen:.2f}->{tuned:.2f}, {len(tr)} pairs): validates the GEO-92 claim. The retrieval bottleneck IS improvable by fine-tuning IF you have ~100+ labelled query-fact pairs. A real improvement lever for users with domain data.", flush=True)
    elif tuned>=frozen-0.05:
        print(f"GEO-93: NULL - even {len(tr)} pairs don't help ({tuned:.2f} vs {frozen:.2f}); REFUTES my GEO-92 'hundreds help' claim for THIS task (frozen already strong / gap not learnable). Honest self-correction.", flush=True)
    else:
        print(f"GEO-93: NULL - hurts ({tuned:.2f}<{frozen:.2f})", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
