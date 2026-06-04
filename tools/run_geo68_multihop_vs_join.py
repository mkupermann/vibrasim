"""GEO-68 — geometric multi-hop vs symbolic DB-join: isolate where multi-hop needs geometry."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner

PEOPLE=[("Alice","Analytics"),("Bob","Platform"),("Carol","Design"),("David","Analytics"),
        ("Eve","Platform"),("Frank","Product")]
TEAM_CITY={"Analytics":"Boston","Platform":"Denver","Design":"Austin","Product":"Seattle"}
# semantic-entry: a description/epithet, no exact name key
EPITHET={"Alice":"the data scientist who joined first","Bob":"the engineer who built the platform"}


def main():
    print("=== GEO-68: geometric multi-hop vs DB-join ===", flush=True)
    r=GeometricReasoner(abstain_tau=0.0)
    person_team=dict(PEOPLE)
    for p,t in PEOPLE:
        r.add_fact(f"{p} is on the {t} team.", subject=p, object=t, kind="person")
    for t,c in TEAM_CITY.items():
        r.add_fact(f"The {t} team is based in {c}.", subject=t, object=c, kind="team")
    # (a) geometric chain
    def geo_chain(query):
        h=r.chain([query,"Where is the {bridge} team based?"])
        return h[-1].get("object") if h else None
    # (b) symbolic DB-join (exact name key)
    def db_join(name):
        t=person_team.get(name); return TEAM_CITY.get(t) if t else None
    # NAMED queries
    geo_named=0; db_named=0
    for p,t in PEOPLE:
        geo_named+= int(geo_chain(f"What team is {p} on?")==TEAM_CITY[t])
        db_named+= int(db_join(p)==TEAM_CITY[t])
    n=len(PEOPLE)
    # SEMANTIC-entry queries (epithet) for the 2 with epithets
    geo_sem=0; db_sem=0
    for p,epi in EPITHET.items():
        geo_sem+= int(geo_chain(f"Which team is {epi} on?")==TEAM_CITY[person_team[p]])
        # db-join needs an exact key; the epithet is not a stored name -> fails
        db_sem+= int(db_join(epi)==TEAM_CITY[person_team[p]])
    ne=len(EPITHET)
    print(f"  NAMED queries:   geometric-chain={geo_named/n:.2f}  DB-join={db_named/n:.2f}", flush=True)
    print(f"  SEMANTIC-entry:  geometric-chain={geo_sem/ne:.2f}  DB-join={db_sem/ne:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if abs(geo_named/n-db_named/n)<0.01 and geo_sem/ne>db_sem/ne:
        print("GEO-68: PASS-as-designed (honest) - on NAMED structured data, geometric multi-hop == DB-join (geometry adds NOTHING for the JOIN; the hops are symbolic lookups). Geometry's genuine multi-hop value is ONLY the SEMANTIC ENTRY (epithet resolution), where DB-join fails (no exact key) and geometric succeeds. 'Geometric composition' on structured data = entity-resolution + database join.", flush=True)
    else:
        print(f"GEO-68: see cells - named geo {geo_named/n:.2f}/db {db_named/n:.2f}, semantic geo {geo_sem/ne:.2f}/db {db_sem/ne:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
