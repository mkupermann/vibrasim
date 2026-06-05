"""conversation — talk to the substrate human-to-human; the durable memory GROWS as it learns during the talk.

Each line you say is either a STATEMENT (it learns the facts -> the durable memory grows -> it acknowledges what is
new) or a QUESTION (it answers from everything it knows so far, including what you just taught it and what it learned
in earlier sessions). Built only on substrate primitives (learn_sentence + BrainQuery over the durable VSA store):
no transformer, no pretrained model.
"""
import os
import re

QUESTION_STARTS = ("is ", "are ", "can ", "does ", "do ", "what ", "why ", "who ", "how ", "where ", "which ")


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

    def say(self, text):
        text = text.strip()
        if not text:
            return ""
        if self.is_question(text):
            from world.brain_query import BrainQuery
            ans = BrainQuery(self.sm, seed=self.seed).ask(text)
            if ans is None:
                return "I don't know that yet — teach me and ask again."
            if isinstance(ans, bool):
                return "Yes." if ans else "No."
            if isinstance(ans, list):
                return (", ".join(ans) if ans else "Nothing I know of") + "."
            return str(ans)
        # STATEMENT -> learn; report how the memory grew
        before = len(self.sm.facts)
        for sent in re.split(r"(?<=[.!])\s+", text if text.endswith(('.', '!')) else text + "."):
            sent = sent.strip()
            if sent:
                self.sm.learn_sentence(sent, self.eng)
        grew = len(self.sm.facts) - before
        return (f"Got it — I learned {grew} new fact{'s' if grew != 1 else ''} (I now know "
                f"{len(self.sm.facts)} facts)." if grew else "Noted (nothing new to me there).")

    def save(self):
        if self.sm.has_resolvable_corrections():
            self.sm = self.sm.compact()
        self.sm.save(self.brain_dir)

    @property
    def n_facts(self):
        return len(self.sm.facts)
