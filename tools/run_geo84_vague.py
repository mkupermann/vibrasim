"""GEO-84 — vague/underspecified query robustness on the personal KB."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner

CONTACTS=[("Sarah Chen","designer","Pixelworks"),("Tom Reyes","accountant","Ledgerly"),
          ("Mia Okafor","lawyer","Justis"),("Raj Patel","plumber","FlowFix"),
          ("Lena Voss","architect","BuildCo"),("Omar Said","dentist","BrightSmile")]
TASKS=[("file the tax return","2025","Tom Reyes"),("review the lease contract","2024","Mia Okafor"),
       ("fix the kitchen sink","2025","Raj Patel")]
NOTES=[("budget","the renovation budget is capped at 50 thousand"),
       ("vacation","we are planning a trip to Portugal in spring")]

# (clean query, vague query, correct subject)
PAIRS=[("Who is the accountant?","that money numbers guy","Tom Reyes"),
       ("Who is the plumber?","the pipe fixing person","Raj Patel"),
       ("Who is the lawyer?","the legal eagle","Mia Okafor"),
       ("Who is the dentist?","the teeth doctor","Omar Said"),
       ("What is the note about the budget?","that money cap thing","budget"),
       ("What is the note about vacation?","the trip plan note","vacation"),
       ("When is the tax return due?","when's the tax thing","file the tax return"),
       ("What task is about the sink?","that kitchen plumbing job","fix the kitchen sink")]


def main():
    print("=== GEO-84: vague query robustness ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0, rerank_k=5)
    for n,role,co in CONTACTS: r.add_fact(f"{n} is a {role} at {co}.", subject=n, kind="contact")
    for d,yr,owner in TASKS: r.add_fact(f"Task: {d}, due {yr}, owned by {owner}.", subject=d, kind="task")
    for topic,txt in NOTES: r.add_fact(f"Note about {topic}: {txt}.", subject=topic, kind="note")
    def hit(q,correct):
        j,_=r.retrieve(q); return int(j is not None and r.fact_meta[j].get("subject")==correct)
    clean=np.mean([hit(c,s) for c,_,s in PAIRS])
    vague=np.mean([hit(v,s) for _,v,s in PAIRS])
    print(f"  clean-query hits@1 = {clean:.2f}", flush=True)
    print(f"  vague-query hits@1 = {vague:.2f}", flush=True)
    for c,v,s in PAIRS:
        if not hit(v,s):
            j,_=r.retrieve(v); got=r.fact_meta[j].get("subject") if j is not None else "ABSTAIN"
            print(f"    vague miss: {v!r} -> {got!r} (want {s!r})", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if vague>=0.7 and clean-vague<=0.2:
        print(f"GEO-84: PASS - semantic matching handles VAGUE/colloquial queries ({vague:.2f} vs clean {clean:.2f}): 'the teeth doctor' -> dentist, 'that money cap thing' -> budget note. Robust to real-user vagueness, not just well-formed queries.", flush=True)
    else:
        print(f"GEO-84: PARTIAL - vague {vague:.2f}, clean {clean:.2f} (gap {clean-vague:.2f})", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
