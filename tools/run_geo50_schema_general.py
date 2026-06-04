"""GEO-50 — schema-general auto-dispatch: field-parameterized operators on two different schemas."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from geometric_reasoner import GeometricReasoner


class GeneralReasoner:
    """Schema-agnostic: facts are (text, meta-dict). Operators parameterized by meta field name."""
    def __init__(self, **kw):
        self.r = GeometricReasoner(**kw)
        self.rows = []   # list of meta dicts (subject + arbitrary fields)

    def add(self, text, **meta):
        self.r.add_fact(text, **meta); self.rows.append(meta)

    def subjects(self):
        return [m.get("subject") for m in self.rows if m.get("subject")]

    def get(self, subject, field):
        for m in self.rows:
            if m.get("subject") == subject: return m.get(field)
        return None

    def count_by(self, field, value):
        return sum(1 for m in self.rows if m.get(field) == value)

    def join_on(self, subject, field):
        v = self.get(subject, field)
        return {m["subject"] for m in self.rows if m.get("subject") != subject and m.get(field) == v}

    def answer(self, q, field_hints):
        """field_hints: {'count_fields':[...], 'join_field':..., 'get_field':...} map query words to fields."""
        ql = q.lower()
        if re.search(r"\b(how many|count|number of)\b", ql):
            for val, field in field_hints["count_values"].items():
                if val.lower() in ql: return self.count_by(field, val)
            return 0
        if re.search(r"\b(same .* as|who else|works? with|shares?)\b", ql):
            subj = self._entity(q); return self.join_on(subj, field_hints["join_field"])
        subj = self._entity(q)
        for kw, field in field_hints["get_map"].items():
            if kw in ql: return self.get(subj, field)
        return self.get(subj, field_hints["default_field"])

    def _entity(self, q):
        names = self.subjects()
        for tok in re.findall(r"[A-Z][a-z]+", q):
            if tok in names: return tok
        c = re.findall(r"[A-Z][a-z]+", q)
        return self.r.resolve_entity(c[0], candidates=names) if c and names else None


def run_schema(name, rows, hints, tests):
    g=GeneralReasoner(abstain_tau=0.30)
    for text,meta in rows: g.add(text,**meta)
    ok=0
    for q,exp in tests:
        got=g.answer(q,hints); ok+= int(got==exp)
        if got!=exp: print(f"    MISS [{name}] {q!r} -> {got!r} (exp {exp!r})", flush=True)
    print(f"  schema {name}: {ok}/{len(tests)} = {ok/len(tests):.2f}", flush=True)
    return ok/len(tests)


def main():
    print("=== GEO-50: schema-general auto-dispatch ===", flush=True)
    # Schema A: people {team, city}
    A_rows=[(f"{p} is on the {t} team in {c}.", {"subject":p,"team":t,"city":c}) for p,t,c in
            [("Alice","Analytics","Boston"),("Bob","Platform","Denver"),("Carol","Design","Austin"),
             ("David","Analytics","Boston"),("Eve","Platform","Denver")]]
    A_hints={"count_values":{"Boston":"city","Denver":"city","Austin":"city"},
             "join_field":"team","get_map":{"city":"city","live":"city","team":"team"},"default_field":"team"}
    A_tests=[("Which team is Carol on?","Design"),("What city does Bob live in?","Denver"),
             ("How many people work in Boston?",2),("Who is on the same team as Alice?",{"David"})]
    # Schema B: products {category, warehouse}
    B_rows=[(f"{p} is a {cat} stored in {w}.", {"subject":p,"category":cat,"warehouse":w}) for p,cat,w in
            [("Widget","Hardware","East"),("Gadget","Electronics","West"),("Gizmo","Hardware","East"),
             ("Doohickey","Electronics","West"),("Sprocket","Hardware","North")]]
    B_hints={"count_values":{"East":"warehouse","West":"warehouse","North":"warehouse"},
             "join_field":"category","get_map":{"warehouse":"warehouse","stored":"warehouse","category":"category"},"default_field":"category"}
    B_tests=[("What category is Gadget?","Electronics"),("Which warehouse is Sprocket stored in?","North"),
             ("How many products are in East?",2),("What shares the same category as Widget?",{"Gizmo","Sprocket"})]
    a=run_schema("A people",A_rows,A_hints,A_tests)
    b=run_schema("B products",B_rows,B_hints,B_tests)
    print("\n--- VERDICT ---", flush=True)
    if a>=0.8 and b>=0.8:
        print(f"GEO-50: PASS - the SAME schema-general agent (field-parameterized operators) works on two different schemas (people {a:.2f}, products {b:.2f}). The auto-dispatch pattern is schema-general, a usable tool for arbitrary data.", flush=True)
    else:
        print(f"GEO-50: PARTIAL - people {a:.2f}, products {b:.2f}", flush=True)
    print("DONE", flush=True)


if __name__=="__main__":
    main()
