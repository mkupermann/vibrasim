"""
GroundedQA — a usable grounded question-answering assistant on the PC (EQMOD-3 capstone, GEO-34).

Combines the geometric reasoning layer (tools/geometric_reasoner.py: retrieval + focus-term answerability
verification) with an OPTIONAL small instruct LLM as the generator. The result is a QA assistant that:
  * answers from an explicit, UPDATABLE store (edit one entry, no retraining)  -- GEO-30
  * FOLLOWS the store over the LLM's parametric prior                          -- GEO-34(a)
  * ABSTAINS ("I don't know") on unanswerable questions instead of confabulating -- GEO-33 / GEO-34(b)

Generation is OPTIONAL: without a generator it returns the retrieved fact text (extractive); with one it
produces a fluent answer grounded ONLY in the retrieved fact. RAG is an established method; the contribution
is the verified-retrieval + abstention grounding around it. Generator fluency is bounded by the chosen model.

Deps: sentence-transformers + numpy (always); transformers + torch + a small instruct model (only if
generate=True). Default model Qwen2.5-0.5B-Instruct runs on CPU (~0.5s/answer).
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from geometric_reasoner import GeometricReasoner


class GroundedQA:
    def __init__(self, generate: bool = False, gen_model: str = "Qwen/Qwen2.5-0.5B-Instruct",
                 abstain_tau: float = 0.40, focus_tau: float = 0.6):
        self.r = GeometricReasoner(abstain_tau=abstain_tau)
        self.focus_tau = focus_tau               # focus-existence threshold (GEO-33)
        self._focus_values = []                  # structured values the focus is checked against
        self._focus_emb = None
        self.gen = None
        if generate:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self._tok = AutoTokenizer.from_pretrained(gen_model)
            self._mdl = AutoModelForCausalLM.from_pretrained(gen_model)
            self.gen = True

    # ---- build the store -------------------------------------------------
    def add_fact(self, text: str, focus_value: str | None = None, **meta):
        """Add a fact. focus_value (e.g. the role/type this fact is ABOUT) feeds answerability checks."""
        self.r.add_fact(text, **meta)
        if focus_value is not None:
            self._focus_values.append(focus_value)
            self._focus_emb = None

    # ---- answerability: does the question's focus exist in the store? (GEO-33)
    def _focus_exists(self, focus: str) -> bool:
        if not self._focus_values:
            return True                          # no focus index -> rely on retrieval threshold only
        if self._focus_emb is None:
            self._focus_emb = np.asarray(self.r.model.encode(self._focus_values, normalize_embeddings=True))
        v = self.r.model.encode([focus], normalize_embeddings=True)[0]
        return float(np.max(self._focus_emb @ v)) >= self.focus_tau

    def _llm(self, prompt: str, n: int = 24) -> str:
        enc = self._tok.apply_chat_template([{"role": "user", "content": prompt}],
                                            add_generation_prompt=True, return_tensors="pt", return_dict=True)
        out = self._mdl.generate(enc["input_ids"], attention_mask=enc.get("attention_mask"),
                                 max_new_tokens=n, do_sample=False, pad_token_id=self._tok.eos_token_id)
        return self._tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()

    # ---- answer ----------------------------------------------------------
    def answer(self, question: str, focus: str | None = None) -> dict:
        """Answer grounded in the store, or abstain. `focus` (the thing asked about) enables the GEO-33
        answerability check that catches in-domain-but-unanswerable questions."""
        if focus is not None and not self._focus_exists(focus):
            return {"answer": "I don't know.", "grounded": False, "reason": "focus not in store"}
        j, sim = self.r.retrieve(question)
        if j is None:
            return {"answer": "I don't know.", "grounded": False, "reason": "no relevant fact", "sim": sim}
        fact = self.r.fact_texts[j]
        if self.gen:
            # Strong context-forcing prompt (GEO-34): small models are prompt-sensitive and will otherwise
            # revert to their parametric prior, ignoring the (possibly updated) store.
            ans = self._llm(f"Context: {fact}\nUsing ONLY the context above and IGNORING any prior "
                            f"knowledge, answer this question concisely: {question}")
        else:
            ans = fact                            # extractive fallback
        return {"answer": ans, "grounded": True, "fact": fact, "sim": sim}


def _demo():
    print("=== GroundedQA self-test ===", flush=True)
    use_gen = "--gen" in sys.argv
    qa = GroundedQA(generate=use_gen)
    # counterfactual store (contradicts world knowledge) + a focus index of which capitals exist
    facts = [("France", "Lyon"), ("Japan", "Osaka"), ("Brazil", "Rio")]
    for country, city in facts:
        qa.add_fact(f"The capital of {country} is {city}.", focus_value=country, subject=country, object=city)

    a = qa.answer("What is the capital of France?", focus="France")
    print(f"  grounded (counterfactual): {a['answer']!r}  grounded={a['grounded']}", flush=True)
    u = qa.answer("What is the capital of Atlantis?", focus="Atlantis")
    print(f"  unanswerable: {u['answer']!r}  grounded={u['grounded']} ({u.get('reason')})", flush=True)

    ok = a["grounded"] and (("Lyon" in a["answer"]) or (not use_gen and "Lyon" in a["answer"])) and not u["grounded"]
    print(f"\n  SELF-TEST: {'PASS' if ok else 'CHECK'} (run with --gen to exercise the LLM generator)", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    _demo()
