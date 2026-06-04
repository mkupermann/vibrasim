"""UnifiedReasoner — auto-dispatching agent: symbolic route -> geometric resolve -> symbolic operate (GEO-49).
Capstone assembly of the EQMOD-3 architecture. Self-contained: extracts the query's entity by matching stored
subjects, routes intent by keywords, dispatches to the right operator. CPU, sentence-transformers + numpy."""
from __future__ import annotations
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from geometric_reasoner import GeometricReasoner


class UnifiedReasoner:
    def __init__(self, **kw):
        self.r = GeometricReasoner(**kw)
        self.people = {}          # person -> {team}
        self.team_city = {}       # team -> city
        self.time_facts = []      # {subject, year, value}

    # ---- build ----
    def add_person(self, name, team):
        self.people[name] = {"team": team}
        self.r.add_fact(f"{name} is on the {team} team.", subject=name, object=team, kind="person")

    def add_team_city(self, team, city):
        self.team_city[team] = city
        self.r.add_fact(f"The {team} team is based in {city}.", subject=team, object=city, kind="team")

    def add_time_fact(self, subject, year, value):
        self.time_facts.append({"subject": subject, "year": year, "value": value})
        self.r.add_fact(f"From {year}, {subject} was on the {value} team.", subject=subject, year=year, object=value, kind="time")

    # ---- helpers ----
    def _entity(self, q):
        """Extract the query's person by matching capitalized tokens to stored people (fuzzy, GEO-44)."""
        names = list(self.people)
        for tok in re.findall(r"[A-Z][a-z]+", q):
            if tok in names:
                return tok
        cands = re.findall(r"[A-Z][a-z]+", q)
        return self.r.resolve_entity(cands[0], candidates=names) if cands and names else None

    def _city_of(self, person):
        return self.team_city.get(self.people.get(person, {}).get("team"))

    # ---- symbolic intent router (GEO-48b) ----
    @staticmethod
    def route(q):
        ql = q.lower()
        if re.search(r"\b(how many|count|number of|headcount)\b", ql): return "COUNT"
        if re.search(r"\bin (19|20)\d\d\b", ql): return "TEMPORAL"
        if re.search(r"\b(same .* as|who else|teammates|works? with|share[sd]?)\b", ql): return "JOIN"
        return "FACTOID"

    # ---- dispatch (route -> resolve -> operate) ----
    def answer(self, q):
        intent = self.route(q)
        if intent == "COUNT":
            city = next((c for c in set(self.team_city.values()) if c.lower() in q.lower()), None)
            n = sum(1 for p in self.people if self._city_of(p) == city) if city else 0
            return {"intent": intent, "answer": n}
        if intent == "TEMPORAL":
            yr = int(re.search(r"(19|20)\d\d", q).group())
            subj = self._entity(q)
            valid = [t for t in self.time_facts if t["subject"] == subj and t["year"] <= yr]
            return {"intent": intent, "answer": max(valid, key=lambda x: x["year"])["value"] if valid else None}
        if intent == "JOIN":
            subj = self._entity(q)
            myteam = self.people.get(subj, {}).get("team")
            peers = {p for p in self.people if p != subj and self.people[p]["team"] == myteam}
            return {"intent": intent, "answer": peers}
        # FACTOID: city (chain) or team (direct)
        subj = self._entity(q)
        if subj and re.search(r"\b(city|live|based|located)\b", q.lower()):
            return {"intent": intent, "answer": self._city_of(subj)}
        return {"intent": intent, "answer": self.people.get(subj, {}).get("team")}


if __name__ == "__main__":
    print("UnifiedReasoner — see tools/run_geo49_unified.py for the end-to-end test.")
