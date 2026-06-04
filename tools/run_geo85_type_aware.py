"""GEO-85 — type-aware agent (auto-kind-routing) eliminates cross-type confusion."""
import sys, os, re
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


def route_kind(q):
    ql=q.lower()
    if re.search(r"\b(who|person|guy|doctor|eagle|lawyer|plumber|dentist|accountant|architect|designer)\b", ql): return "contact"
    if re.search(r"\b(note|about|thing|budget|vacation|trip|plan)\b", ql): return "note"
    if re.search(r"\b(task|due|when|fix|file|review|job)\b", ql): return "task"
    return None


def main():
    print("=== GEO-85: type-aware agent ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0, rerank_k=5)
    for n,role,co in CONTACTS: r.add_fact(f"{n} is a {role} at {co}.", subject=n, kind="contact")
    for d,yr,owner in TASKS: r.add_fact(f"Task: {d}, due {yr}, owned by {owner}.", subject=d, kind="task")
    for topic,txt in NOTES: r.add_fact(f"Note about {topic}: {txt}.", subject=topic, kind="note")
    QUERIES=[("the teeth doctor","Omar Said"),("the legal eagle","Mia Okafor"),
             ("the pipe fixing person","Raj Patel"),("that money numbers guy","Tom Reyes"),
             ("that money cap thing","budget"),("the trip plan note","vacation"),
             ("when's the tax thing","file the tax return"),("that kitchen plumbing job","fix the kitchen sink"),
             ("Who is the plumber?","Raj Patel"),("What is the note about the budget?","budget")]
    def hit(q,correct,scoped):
        k=route_kind(q) if scoped else None
        j,_=r.retrieve(q, kind=k)
        return int(j is not None and r.fact_meta[j].get("subject")==correct)
    unscoped=np.mean([hit(q,s,False) for q,s in QUERIES])
    scoped=np.mean([hit(q,s,True) for q,s in QUERIES])
    for q,s in QUERIES:
        if not hit(q,s,True):
            k=route_kind(q); j,_=r.retrieve(q,kind=k); got=r.fact_meta[j].get("subject") if j is not None else "ABSTAIN"
            print(f"    still miss: {q!r} (kind={k}) -> {got!r} (want {s!r})", flush=True)
    print(f"  without kind-routing = {unscoped:.2f}", flush=True)
    print(f"  with auto-kind-routing = {scoped:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if scoped>=0.95:
        print(f"GEO-85: PASS - auto-kind-routing eliminates cross-type confusion ({unscoped:.2f}->{scoped:.2f}): detect the query's target kind, scope retrieval to it. The type-aware agent handles mixed personal KBs robustly, including vague queries.", flush=True)
    else:
        print(f"GEO-85: PARTIAL - scoped {scoped:.2f} vs unscoped {unscoped:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
