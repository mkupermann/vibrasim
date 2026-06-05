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

    def say(self, text):
        text = text.strip()
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
                self.sm.learn_sentence(sent, self.eng)
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
