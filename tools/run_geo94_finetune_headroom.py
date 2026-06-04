"""GEO-94 — fine-tune English model on DE->EN pairs (genuine headroom); does it learn cross-lingual retrieval?"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# German query -> English fact pairs (varied everyday facts)
EN_FACTS=["The capital of France is Paris.","The capital of Japan is Tokyo.","The capital of Italy is Rome.",
 "The capital of Spain is Madrid.","The capital of Egypt is Cairo.","The capital of Greece is Athens.",
 "The capital of Poland is Warsaw.","The capital of Norway is Oslo.","The capital of Brazil is Brasilia.",
 "The capital of India is Delhi.","The capital of Kenya is Nairobi.","The capital of Peru is Lima.",
 "The dentist treats teeth.","The plumber fixes pipes.","The lawyer handles legal cases.",
 "The accountant manages finances.","The architect designs buildings.","The doctor treats patients.",
 "The teacher educates students.","The chef cooks food.","The pilot flies planes.","The farmer grows crops.",
 "Water boils at one hundred degrees.","The sun rises in the east.","A week has seven days.",
 "The heart pumps blood.","Bees make honey.","Spiders have eight legs.","The moon orbits the earth.",
 "Light travels faster than sound.","Ice is frozen water.","Plants need sunlight to grow.",
 "The Pacific is the largest ocean.","Mount Everest is the highest mountain.","The Nile is a long river.",
 "Diamonds are very hard.","Gold is a precious metal.","Oxygen is needed for breathing.","Salt dissolves in water.","Fire needs oxygen."]
DE_Q=["Was ist die Hauptstadt von Frankreich?","Was ist die Hauptstadt von Japan?","Was ist die Hauptstadt von Italien?",
 "Was ist die Hauptstadt von Spanien?","Was ist die Hauptstadt von Ägypten?","Was ist die Hauptstadt von Griechenland?",
 "Was ist die Hauptstadt von Polen?","Was ist die Hauptstadt von Norwegen?","Was ist die Hauptstadt von Brasilien?",
 "Was ist die Hauptstadt von Indien?","Was ist die Hauptstadt von Kenia?","Was ist die Hauptstadt von Peru?",
 "Wer behandelt Zähne?","Wer repariert Rohre?","Wer bearbeitet Rechtsfälle?","Wer verwaltet Finanzen?",
 "Wer entwirft Gebäude?","Wer behandelt Patienten?","Wer unterrichtet Schüler?","Wer kocht Essen?",
 "Wer fliegt Flugzeuge?","Wer baut Feldfrüchte an?","Bei welcher Temperatur kocht Wasser?","Wo geht die Sonne auf?",
 "Wie viele Tage hat eine Woche?","Was pumpt das Blut?","Was machen Bienen?","Wie viele Beine haben Spinnen?",
 "Was umkreist die Erde?","Was ist schneller, Licht oder Schall?","Was ist gefrorenes Wasser?","Was brauchen Pflanzen zum Wachsen?",
 "Was ist der größte Ozean?","Was ist der höchste Berg?","Welcher Fluss ist lang?","Was ist sehr hart?",
 "Welches Edelmetall ist wertvoll?","Was braucht man zum Atmen?","Was löst sich in Wasser?","Was braucht Feuer?"]


def hits(m, q, f, facts):
    Q=np.array(m.encode(q,normalize_embeddings=True)); F=np.array(m.encode(facts,normalize_embeddings=True))
    return np.mean([int(facts[int(np.argmax(Q[i]@F.T))]==f[i]) for i in range(len(q))])


def main():
    print("=== GEO-94: fine-tune English model for DE->EN (headroom) ===", flush=True)
    rng=np.random.default_rng(0); idx=rng.permutation(len(EN_FACTS))
    tr=idx[:30]; te=idx[30:]  # train on 30, test on held-out (disjoint facts)
    teq=[DE_Q[i] for i in te]; tef=[EN_FACTS[i] for i in te]; tefacts=tef
    m=SentenceTransformer("all-MiniLM-L6-v2")
    frozen=hits(m, teq, tef, tefacts)
    loader=DataLoader([InputExample(texts=[DE_Q[i],EN_FACTS[i]]) for i in tr], shuffle=True, batch_size=8)
    loss=losses.MultipleNegativesRankingLoss(m)
    m.fit(train_objectives=[(loader,loss)], epochs=8, warmup_steps=3, show_progress_bar=False)
    tuned=hits(m, teq, tef, tefacts)
    print(f"  train pairs={len(tr)}, test pairs={len(te)}", flush=True)
    print(f"  frozen English model  DE->EN held-out = {frozen:.2f}", flush=True)
    print(f"  fine-tuned            DE->EN held-out = {tuned:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if tuned>=frozen+0.15:
        print(f"GEO-94: PASS - fine-tuning TEACHES the English model cross-lingual retrieval ({frozen:.2f}->{tuned:.2f}) where it frozen-fails. So fine-tuning DOES improve retrieval given a real gap with headroom + labelled pairs. Settles the improvability question: FT is a genuine lever (validated here with real headroom). Demonstrated, not just asserted.", flush=True)
    elif tuned>=frozen:
        print(f"GEO-94: PARTIAL - small gain ({frozen:.2f}->{tuned:.2f}); FT helps a bit but 30 pairs / 8 epochs is modest.", flush=True)
    else:
        print(f"GEO-94: NULL - FT hurt ({tuned:.2f}<{frozen:.2f}); overfit/forgot on small data.", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
