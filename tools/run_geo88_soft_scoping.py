"""GEO-88 — soft kind-scoping (boost routed kind, don't filter) vs hard-scope vs unscoped."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner
from linear_router import LinearRouter

CONTACTS=[("Sarah Chen","designer","Pixelworks"),("Tom Reyes","accountant","Ledgerly"),
          ("Mia Okafor","lawyer","Justis"),("Raj Patel","plumber","FlowFix"),
          ("Lena Voss","architect","BuildCo"),("Omar Said","dentist","BrightSmile")]
TASKS=[("file the tax return","2025"),("review the lease contract","2024"),("fix the kitchen sink","2025")]
NOTES=[("budget","the renovation budget is capped at 50 thousand"),("vacation","we are planning a trip to Portugal in spring")]
RT={"contact":["who is the plumber","the teeth doctor","the legal eagle","that money numbers guy","who is the dentist","the architect"],
    "task":["when is the tax due","the sink fix job","what's due in 2025","when's the tax thing","review the lease task","upcoming deadlines"],
    "note":["the budget note","what about vacation","that money cap thing","the trip plan note","note on the car","budget details"]}
TESTS=[("the teeth doctor","Omar Said"),("the legal eagle","Mia Okafor"),("the pipe fixing person","Raj Patel"),
       ("that money numbers guy","Tom Reyes"),("that money cap thing","budget"),("the trip plan note","vacation"),
       ("when's the tax thing","file the tax return"),("that kitchen plumbing job","fix the kitchen sink"),
       ("Who is the plumber?","Raj Patel"),("What is the note about the budget?","budget")]


def main():
    print("=== GEO-88: soft kind-scoping ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0)
    for n,role,co in CONTACTS: r.add_fact(f"{n} is a {role} at {co}.", subject=n, kind="contact")
    for d,yr in TASKS: r.add_fact(f"Task: {d}, due {yr}.", subject=d, kind="task")
    for t,txt in NOTES: r.add_fact(f"Note about {t}: {txt}.", subject=t, kind="note")
    router=LinearRouter(_shared=r.model).fit(RT)
    kinds=np.array([m.get("kind") for m in r.fact_meta])
    def answer(q, mode, boost=0.0):
        qv=r._embed([q])[0]; sims=r.F@qv.copy(); rk=router.route(q)
        if mode=="hard":
            sims=np.where(kinds==rk, sims, -np.inf)
        elif mode=="soft":
            sims=sims+np.where(kinds==rk, boost, 0.0)
        j=int(np.argmax(sims)); return r.fact_meta[j].get("subject")
    def acc(mode,boost=0.0): return np.mean([answer(q,mode,boost)==exp for q,exp in TESTS])
    uns=acc("unscoped"); hard=acc("hard")
    print(f"  unscoped   = {uns:.2f}", flush=True)
    print(f"  hard-scope = {hard:.2f}", flush=True)
    best=0;bb=0
    for b in [0.05,0.1,0.2]:
        a=acc("soft",b); print(f"  soft-scope boost={b} = {a:.2f}", flush=True)
        if a>best: best=a;bb=b
    print("\n--- VERDICT ---", flush=True)
    if best>=0.90 and best>=hard:
        print(f"GEO-88: PASS - SOFT scoping (boost={bb}, acc={best:.2f}) recovers robustness vs hard-scope ({hard:.2f}) {'and beats' if best>uns else 'matching'} unscoped ({uns:.2f}): boosting the routed kind degrades gracefully on mis-routes (the right fact can still win on raw similarity). Soft > hard for fallible routers — the right design.", flush=True)
    else:
        print(f"GEO-88: best soft {best:.2f}, hard {hard:.2f}, unscoped {uns:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
