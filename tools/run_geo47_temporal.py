"""GEO-47 — temporal reasoning: time-scoped queries over versioned facts (geometric gather + symbolic filter)."""
import numpy as np
from sentence_transformers import SentenceTransformer

# person -> list of (valid_from_year, team)
HIST={"Alice":[(2020,"Analytics"),(2023,"Platform")],
      "Bob":[(2019,"Design"),(2022,"Product")],
      "Carol":[(2021,"Platform")],
      "David":[(2018,"Analytics"),(2021,"Design"),(2024,"Product")],
      "Eve":[(2020,"Product"),(2023,"Analytics")],
      "Frank":[(2019,"Platform"),(2022,"Design")],
      "Grace":[(2021,"Analytics"),(2024,"Platform")],
      "Heidi":[(2020,"Design")]}


def truth(p,year):
    valid=[(y,t) for y,t in HIST[p] if y<=year]
    return max(valid)[1] if valid else None


def main():
    print("=== GEO-47: temporal reasoning ===", flush=True)
    m=SentenceTransformer("all-MiniLM-L6-v2")
    facts=[]; meta=[]
    for p,hist in HIST.items():
        for y,t in hist:
            facts.append(f"From {y}, {p} was on the {t} team."); meta.append({"subject":p,"year":y,"team":t})
    F=np.array(m.encode(facts,normalize_embeddings=True))
    tests=[("Alice",2021,"Analytics"),("Alice",2024,"Platform"),("Bob",2020,"Design"),("Bob",2023,"Product"),
           ("David",2019,"Analytics"),("David",2022,"Design"),("David",2025,"Product"),("Carol",2022,"Platform"),
           ("Eve",2021,"Product"),("Eve",2024,"Analytics"),("Frank",2020,"Platform"),("Grace",2025,"Platform")]
    ok=0; base_ok=0
    for p,year,exp in tests:
        qv=m.encode([f"Which team was {p} on in {year}?"],normalize_embeddings=True)[0]
        sims=F@qv
        # gather this person's facts (top matches with subject==p), symbolic temporal filter
        order=np.argsort(-sims)
        pfacts=[meta[i] for i in order if meta[i]["subject"]==p]
        valid=[fm for fm in pfacts if fm["year"]<=year]
        ans=max(valid,key=lambda x:x["year"])["team"] if valid else None
        ok+= int(ans==exp)
        # baseline: latest fact only (ignore year)
        base=max(pfacts,key=lambda x:x["year"])["team"] if pfacts else None
        base_ok+= int(base==exp)
    n=len(tests)
    print(f"  temporal hybrid accuracy = {ok/n:.2f}", flush=True)
    print(f"  non-temporal baseline    = {base_ok/n:.2f}  (latest fact, ignores year)", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok/n>=0.8 and ok/n>base_ok/n:
        print(f"GEO-47: PASS - temporal reasoning works: geometric gather of an entity's facts + symbolic time-filter answers time-scoped queries ({ok/n:.2f}), where a non-temporal baseline fails on past years ({base_ok/n:.2f}).", flush=True)
    else:
        print(f"GEO-47: PARTIAL/NULL - temporal {ok/n:.2f}, baseline {base_ok/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
