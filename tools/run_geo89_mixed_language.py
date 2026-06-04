"""GEO-89 — mixed-language (German+English) KB and queries via multilingual model."""
import numpy as np
from sentence_transformers import SentenceTransformer

# mixed facts: (fact_text, subject)
FACTS=[("Der Zahnarzt heißt Omar und arbeitet in der Stadtmitte.","zahnarzt"),
       ("Die Steuererklärung ist bis 2025 fällig.","steuer"),
       ("Das Budget für die Renovierung ist auf 50 Tausend begrenzt.","budget"),
       ("Maria ist Anwältin bei der Kanzlei Justis.","maria"),
       ("Der Urlaub ist eine Reise nach Portugal im Frühling.","urlaub"),
       ("Raj ist Klempner und repariert die Küchenspüle.","raj"),
       ("Sarah is a designer at Pixelworks.","sarah"),
       ("The lease contract review is due in 2024.","lease"),
       ("Tom is an accountant at Ledgerly.","tom"),
       ("The car needs new brake pads soon.","car"),
       ("Lena is an architect working on a building permit.","lena"),
       ("The note about books recommends an Antarctic novel.","books")]
QUERIES=[("Wer ist der Zahnarzt?","zahnarzt"),("Wann ist die Steuererklärung fällig?","steuer"),
         ("Wie hoch ist das Budget?","budget"),("Who is the lawyer?","maria"),
         ("Wohin geht die Reise?","urlaub"),("Who fixes the kitchen sink?","raj"),
         ("Who is the designer?","sarah"),("Wann ist der Mietvertrag fällig?","lease"),
         ("Wer macht die Buchhaltung?","tom"),("What does the car need?","car")]


def acc(model):
    m=SentenceTransformer(model)
    F=np.array(m.encode([f for f,_ in FACTS],normalize_embeddings=True))
    subs=[s for _,s in FACTS]
    Q=np.array(m.encode([q for q,_ in QUERIES],normalize_embeddings=True))
    hits=0
    for i,(q,exp) in enumerate(QUERIES):
        j=int(np.argmax(Q[i]@F.T)); hits+= int(subs[j]==exp)
    return hits/len(QUERIES)


def main():
    print("=== GEO-89: mixed-language KB ===", flush=True)
    multi=acc("paraphrase-multilingual-MiniLM-L12-v2")
    mono=acc("all-MiniLM-L6-v2")
    print(f"  multilingual model hits@1 = {multi:.2f}", flush=True)
    print(f"  English-only model hits@1 = {mono:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if multi>=0.8:
        print(f"GEO-89: PASS - the multilingual model handles a MIXED German+English KB with cross-language queries ({multi:.2f}, vs English-only {mono:.2f}): German queries find German AND English facts and vice versa. The bilingual personal-use scenario works.", flush=True)
    else:
        print(f"GEO-89: PARTIAL - multi {multi:.2f}, mono {mono:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
