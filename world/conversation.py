"""conversation — talk to the substrate human-to-human; the durable memory GROWS as it learns during the talk.

Each line you say is either a STATEMENT (it learns the facts -> the durable memory grows -> it acknowledges what is
new) or a QUESTION (it answers from everything it knows so far, including what you just taught it and what it learned
in earlier sessions). Built only on substrate primitives (learn_sentence + BrainQuery over the durable VSA store):
no transformer, no pretrained model.
"""
import os
import re

QUESTION_STARTS = ("is ", "are ", "can ", "does ", "do ", "what ", "why ", "who ", "how ", "where ", "which ",
                   "tell me ", "describe ")          # treat 'tell me about X' / 'describe X' as questions to answer


class Conversation:
    def __init__(self, brain_dir=None, seed: int = 0):
        from world.substrate_memory import SubstrateMemory
        from world.understanding import UnderstandingEngine
        self.seed = seed
        self.brain_dir = brain_dir or os.path.join(os.path.expanduser("~"), ".eqmod", "brain", "talk")
        if os.path.exists(os.path.join(self.brain_dir, "meta.json")):
            self.sm = SubstrateMemory.load(self.brain_dir)
        else:
            self.sm = SubstrateMemory(tau=0.12, directed=True)
        self.eng = self.sm.rebuild_engine(seed=seed) if self.sm.sentences else UnderstandingEngine(seed=seed)

    @staticmethod
    def is_question(text):
        t = text.strip().lower()
        return t.endswith("?") or t.startswith(QUESTION_STARTS)

    def _resolve_pronoun(self, text):
        """Replace a standalone 'it' with the last subject discussed (so 'can it bark?' follows 'a poodle ...')."""
        if getattr(self, "_last_subject", None):
            return re.sub(r"\bit\b", self._last_subject, text)
        return text

    def _track_subject(self, text):
        # remember the last concrete noun mentioned (after a/an/the, or after is/can/does) for pronoun binding
        m = re.search(r"\b(?:a|an|the)\s+([a-z]+)\b", text.lower()) or \
            re.search(r"\b(?:is|can|does|about)\s+([a-z]+)\b", text.lower())
        if m and m.group(1) not in ("it", "kind", "type"):
            self._last_subject = m.group(1)

    _FILLER_RE = re.compile(r"^(so|well|um|uh|hmm|ok|okay|please|hey|and|also|now)\b[,\s]*", re.I)

    def _preprocess(self, text):
        """Strip leading filler/politeness and normalise negated/contracted auxiliaries so messy input still routes."""
        t = text.strip()
        while True:
            m = self._FILLER_RE.match(t)
            if not m or m.end() == 0:
                break
            t = t[m.end():]
        # negated/contracted question auxiliaries -> base form (meaning preserved for yes/no lookups)
        t = re.sub(r"^(isn't|isnt)\b", "is", t, flags=re.I)
        t = re.sub(r"^(aren't|arent)\b", "are", t, flags=re.I)
        t = re.sub(r"^(doesn't|doesnt)\b", "does", t, flags=re.I)
        t = re.sub(r"^(don't|dont)\b", "do", t, flags=re.I)
        t = re.sub(r"^(can't|cant)\b", "can", t, flags=re.I)
        return t.strip()

    def say(self, text):
        text = (text or "").strip()
        if not text:
            return ""
        # "what about X?" follow-up: re-ask the last question template with the new subject
        m = re.match(r"(?:and )?what about (?:a |an |the )?([a-z]+)\??$", text.strip().lower())
        if m and getattr(self, "_last_question", None):
            return self._say_one(re.sub(r"\b" + re.escape(self._last_q_subject) + r"\b",
                                        m.group(1), self._last_question)) if getattr(self, "_last_q_subject", None) \
                else self._say_one(text)
        # a turn may mix teaching and asking across sentences -> process each clause
        clauses = [c.strip() for c in re.split(r"(?<=[.!?])\s+", text) if c.strip()]
        if len(clauses) > 1:
            return " ".join(self._say_one(c) for c in clauses)
        return self._say_one(text)

    def _say_one(self, text):
        text = self._preprocess(text)
        if not text:
            return ""
        if text.lower().rstrip("?.!").strip() in (
                "draw what you know", "show me what you know", "draw what you have learned",
                "show what you know", "draw your knowledge", "what do you know"):
            from world.visualize import draw_knowledge
            p = draw_knowledge(self.sm, title="What I know")
            return (f"Here's a picture of what I know — saved to {p}" if p
                    else "I don't have enough connected knowledge to draw yet — teach me a few facts first.")
        if self.is_question(text):
            from world.brain_query import BrainQuery
            text = self._resolve_pronoun(text)
            self._track_subject(text)
            self._last_question = text
            low_q = text.lower().rstrip("?.! ").strip()
            if low_q in ("what is not clear to you", "what is unclear to you", "what don't you understand",
                         "what dont you understand", "what is not clear", "what is unclear",
                         "what do you not understand", "what are you unsure about"):
                g = self.gaps()
                if not g:
                    return "Everything I've been taught connects so far — nothing is unclear to me yet."
                qs = "; ".join(f"what is {'an' if c[0] in 'aeiou' else 'a'} {c}?" for c in g[:5])
                return f"A few things aren't clear to me yet — {qs}"
            ms = re.search(r"\b(?:is|can|does|do|about)\s+(?:a |an |the )?([a-z]+)\b", text.lower())
            self._last_q_subject = ms.group(1) if ms else None
            ans = BrainQuery(self.sm, seed=self.seed).ask(text)
            if ans is None:
                return "I don't know that yet — teach me and ask again."
            if isinstance(ans, bool):
                return "Yes." if ans else "No."
            if isinstance(ans, list):
                return (", ".join(ans) if ans else "Nothing I know of") + "."
            return str(ans)
        # STATEMENT -> learn; report how the memory grew
        self._track_subject(text)
        before = len(self.sm.facts)
        for sent in re.split(r"(?<=[.!])\s+", text if text.endswith(('.', '!')) else text + "."):
            sent = sent.strip()
            if sent:
                self._learn_one(sent)
        grew = len(self.sm.facts) - before
        base = (f"Got it — I learned {grew} new fact{'s' if grew != 1 else ''} (I now know "
                f"{len(self.sm.facts)} facts)." if grew else "Noted (nothing new to me there).")
        conn = self._connections(getattr(self, "_last_subject", None)) if grew else []
        if conn:
            base += " And that connects: " + "; ".join(conn) + "."
        oq = self._open_ended(text, getattr(self, "_last_subject", None)) if grew else None
        if oq:
            base += " " + oq
        return base

    _NUMW = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
             "nine": 9, "ten": 10, "zero": 0}

    @staticmethod
    def _singular(w):
        if w.endswith("ies") and len(w) > 4:
            return w[:-3] + "y"
        if w.endswith("ses") or w.endswith("xes") or w.endswith("ches") or w.endswith("shes"):
            return w[:-2]
        if w.endswith("s") and not w.endswith("ss"):
            return w[:-1]
        return w

    def _normalize_for_learning(self, s):
        """Rewrite common encyclopedic forms into engine-parseable ones (JEP-348). Returns (sentence, extra_facts)."""
        extra = []
        t = s.strip()
        # 'is a kind/type/sort of' -> 'is a'
        t = re.sub(r"\bis\s+(an?)\s+(?:kind|type|sort)\s+of\b", r"is \1", t, flags=re.I)
        # numeric possession: 'A dog has four/4 legs' -> add (dog, has_<noun>, N)
        m = re.search(r"\b([A-Za-z]+)\s+has\s+(\w+)\s+([a-z]+s)\b", t, flags=re.I)
        if m:
            subj = self._singular(m.group(1).lower())
            cnt = m.group(2).lower()
            num = self._NUMW.get(cnt, cnt if cnt.isdigit() else None)
            if num is not None and subj not in ("a", "an", "the"):
                extra.append((subj, f"has_{m.group(3).lower()}", str(num)))   # full noun -> e.g. has_legs
        # plural is-a: 'Dogs are carnivores' / 'Dogs are domesticated animals' -> 'A dog is a <head noun>'
        m = re.match(r"^([A-Z][a-z]+)s\s+are\s+(?:a\s+)?(.+?)\.?$", t)
        if m and " " not in m.group(1):
            subj = self._singular((m.group(1)).lower())
            obj_head = self._singular(m.group(2).strip().rstrip(".").split()[-1].lower())  # head noun
            art = "an" if obj_head[0] in "aeiou" else "a"
            t = f"A {subj} is {art} {obj_head}."
        return t, extra

    def _learn_one(self, sentence):
        rewritten, extra = self._normalize_for_learning(sentence)
        self.sm.learn_sentence(rewritten, self.eng)
        for (a, r, b) in extra:
            if (a, r, b) not in set(self.sm.facts):
                self.sm.add_fact(a, r, b)

    ROOTS = {"animal", "organism", "thing", "object", "plant", "matter", "substance", "concept", "idea",
             "place", "person", "event", "process", "material"}

    def read_text(self, text):
        """Read a whole document into the durable brain (Michael: 'the substrate reads a new text'). Learns every
        parseable sentence, the memory grows; the same brain accumulates across sessions/days. Returns a summary."""
        before = len(self.sm.facts)
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]
        for s in sents:
            if not self.is_question(s):
                self._learn_one(s)
        grew = len(self.sm.facts) - before
        concepts = len({a for (a, r, b) in self.sm.facts if r == "isa"} |
                       {b for (a, r, b) in self.sm.facts if r == "isa"})
        return {"sentences": len(sents), "facts_learned": grew, "total_facts": len(self.sm.facts),
                "concepts": concepts}

    def gaps(self):
        """What the brain has heard of but cannot place: concepts REFERENCED (is-a / relations) but never DEFINED
        (no is-a parent of their own) and not recognized roots. These are honest knowledge gaps."""
        facts = self.sm.facts
        defined = {a for (a, r, b) in facts if r == "isa"}             # has its own is-a parent -> we know what it is
        referenced = set()
        for (a, r, b) in facts:
            referenced.add(a)
            if r in ("isa", "partof"):
                referenced.add(b)
        return [c for c in sorted(referenced) if c not in defined and c not in self.ROOTS]

    READY_FACTS = 6                                      # "once it is ready" (Michael rule #1): enough connected facts

    def _open_ended(self, text, subject):
        """Open-ended Socratic question back, gated on readiness (Michael rule #1). The brain POSES it (it does not
        creatively answer it -- the JEP-332 wall)."""
        if len(self.sm.facts) < self.READY_FACTS:
            return None
        low = text.lower()
        m = re.search(r"(\w+) causes? (\w+)", low)
        if m:
            return f"Why do you think {m.group(1)} causes {m.group(2)}?"
        m = re.search(r"(\w+) (?:happened |comes )?before (?:the )?(\w+)", low)
        if m:
            return f"And what do you think comes after {m.group(2)}?"
        if subject:
            from world.brain_query import BrainQuery
            bq = BrainQuery(self.sm, seed=self.seed)
            chain = bq._ancestors(subject, "isa")
            top = chain[-1] if chain else subject
            roots = {"animal", "organism", "thing", "object", "plant", "matter"}
            if top not in roots and not [p for (p, _) in self.sm.query_all(top, "isa", bq.gate)]:
                return f"What is {'an' if top[0] in 'aeiou' else 'a'} {top}?"
        return None

    def _connections(self, subject):
        """Make connections (Michael's rule #2): the NEW entailments unlocked for `subject` by linking the new fact
        to what is already known — deductive generation (JEP-331). Returns short English clauses, beyond the direct
        parent."""
        if not subject:
            return []
        from world.brain_query import BrainQuery
        bq = BrainQuery(self.sm, seed=self.seed)
        out = []
        anc = bq._ancestors(subject, "isa")             # [subject, parent, grandparent, ...]
        for a in anc[2:]:                                # skip subject + direct parent -> only multi-hop links
            out.append(f"a {subject} is {'an' if a[0] in 'aeiou' else 'a'} {a}")
        props = []
        for a in anc[1:]:                                # inherited properties (from ancestors, not the subject)
            for (p, _) in self.sm.query_all(a, "hasprop", bq.gate):
                if not self.sm.contains(subject, "not_hasprop", p, bq.gate) and p not in props:
                    props.append(p)
        if props:
            out.append(f"a {subject} can " + ", ".join(props[:3]))
        return out[:4]

    def save(self):
        if self.sm.has_resolvable_corrections():
            self.sm = self.sm.compact()
        self.sm.save(self.brain_dir)

    @property
    def n_facts(self):
        return len(self.sm.facts)
