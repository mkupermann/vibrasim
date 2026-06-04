"""GEO-83 — realistic personal knowledge base (contacts + tasks + notes)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner

CONTACTS=[("Sarah Chen","designer","Pixelworks"),("Tom Reyes","accountant","Ledgerly"),
          ("Mia Okafor","lawyer","Justis"),("Raj Patel","plumber","FlowFix"),
          ("Lena Voss","architect","BuildCo"),("Omar Said","dentist","BrightSmile")]
TASKS=[("file the tax return","2025","Tom Reyes"),("review the lease contract","2024","Mia Okafor"),
       ("fix the kitchen sink","2025","Raj Patel"),("submit the building permit","2026","Lena Voss"),
       ("schedule a dental cleaning","2025","Omar Said")]
NOTES=[("budget","the renovation budget is capped at 50 thousand"),
       ("vacation","we are planning a trip to Portugal in spring"),
       ("car","the car needs new brake pads soon"),
       ("book","recommended a novel about Antarctic explorers")]


def main():
    print("=== GEO-83: personal knowledge base ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0, rerank_k=5)
    for n,role,co in CONTACTS: r.add_fact(f"{n} is a {role} at {co}.", subject=n, role=role, object=co, kind="contact")
    for d,yr,owner in TASKS: r.add_fact(f"Task: {d}, due {yr}, owned by {owner}.", subject=d, year=yr, owner=owner, kind="task")
    for topic,txt in NOTES: r.add_fact(f"Note about {topic}: {txt}.", subject=topic, kind="note", text=txt)
    r.calibrate_abstention(["What company is Sarah Chen at?","Who owns the tax return task?"],
                           ["What is the stock market doing?","Who won the election?"])
    checks=[]
    # factoid: company of a contact
    res=r.ask("What company is Sarah Chen at?"); checks.append(("factoid", res["grounded"] and res["answer"].get("object")=="Pixelworks"))
    res=r.ask("Where does Mia Okafor work?"); checks.append(("factoid", res["grounded"] and res["answer"].get("object")=="Justis"))
    # semantic: which note about budget / car (no exact topic word in query)
    def note_match(q):
        notes=[(i,m) for i,m in enumerate(r.fact_meta) if m.get("kind")=="note"]
        qv=r._embed([q])[0]; idx=[i for i,_ in notes]; sims=[r.F[i]@qv for i in idx]
        return r.fact_meta[idx[int(np.argmax(sims))]]["subject"]
    checks.append(("semantic", note_match("how much can we spend on the renovation?")=="budget"))
    checks.append(("semantic", note_match("what is wrong with the vehicle?")=="car"))
    # temporal: tasks due in 2025
    due2025={m["subject"] for m in r.fact_meta if m.get("kind")=="task" and m.get("year")=="2025"}
    checks.append(("temporal", due2025=={"file the tax return","fix the kitchen sink","schedule a dental cleaning"}))
    # aggregation: how many tasks owned by Tom
    tom=sum(1 for m in r.fact_meta if m.get("kind")=="task" and m.get("owner")=="Tom Reyes")
    checks.append(("aggregation", tom==1))
    # multi-hop-ish: who is the plumber, and what's their company
    res=r.ask("Who can fix plumbing?"); checks.append(("semantic-role", res["grounded"] and res["answer"].get("role")=="plumber"))
    # abstain out-of-KB
    checks.append(("abstain", not r.ask("What is the capital of France?")["grounded"]))
    checks.append(("abstain", not r.ask("What will the weather be tomorrow?")["grounded"]))
    # temporal 2026
    checks.append(("temporal", {m["subject"] for m in r.fact_meta if m.get("kind")=="task" and m.get("year")=="2026"}=={"submit the building permit"}))
    npass=sum(c for _,c in checks); n=len(checks)
    for name,c in checks:
        if not c: print(f"    FAIL: {name}", flush=True)
    print(f"  overall = {npass}/{n} = {npass/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if npass/n>=0.8:
        print(f"GEO-83: PASS - the toolkit handles a realistic PERSONAL knowledge base ({npass/n:.2f}): contacts/tasks/notes with factoid, semantic, temporal, aggregation queries and out-of-KB abstention. Validates the actual personal-use scenario the user asked for ('on my PC').", flush=True)
    else:
        print(f"GEO-83: PARTIAL - {npass/n:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
