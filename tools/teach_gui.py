"""teach_gui — the interactive TEACHING tool (per Michael's steer: 'if the substrate is not sure it asks me via GUI,
I answer correct / not correct; later, sentences').

Run:  PYTHONPATH=. .venv/Scripts/python.exe tools/teach_gui.py

The engine shows you a WRITTEN LETTER it perceived, tells you its guess + how SURE it is, and:
  - if it is CONFIDENT, it just states its answer (and learns nothing unless you correct it);
  - if it is UNSURE, it ASKS YOU. You click [Correct] or [Not correct].
    On 'Not correct' a small box appears -> type the right letter (later: a full sentence).
Every answer you give teaches it (updates the letter's prototype), so it slowly grounds the alphabet from YOU.

The cross-modal hook is built in: the same symbol store accepts an audio modality later, so 'hear A' binds to the
same 'A' as 'write A'. No transformer, no pretrained model -- it learns only from what you teach it.

This module is import-safe (no Tk window is created on import); the GUI launches only under __main__.
"""
import os
import sys
import string
import numpy as np

# self-bootstrap: add the repo root to sys.path so this runs DIRECTLY (no PYTHONPATH needed) --
#   .venv\Scripts\python.exe tools\teach_gui.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world.active_learner import ActiveLearner

SIZE = 28
LETTERS = string.ascii_uppercase


def answer_question(sm, q):
    """Answer a natural question against the durable store (testable without Tk). Returns a display string."""
    if sm is None:
        return "(no durable brain — teach me some facts by sentence first)"
    from world.brain_query import BrainQuery
    ans = BrainQuery(sm).ask(q)
    if ans is None:
        return "I can't answer that yet. Try 'is a poodle an animal?', 'can a penguin fly?', 'what causes cancer?'."
    return str(ans)


def _norm_glyph(a):
    """Scale+translation normalize: crop to the ink bounding box and resize to SIZExSIZE. Makes a small 'D' and a
    large 'D' land on the same feature, so corrections STICK and round/stem letters (D,O,B,P) stop colliding by size.
    (The earlier _center only translated -> a small letter still collided with a large different letter.)"""
    from PIL import Image
    ys, xs = np.nonzero(a > 0.3)
    if len(xs) == 0:
        return a
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = a[y0:y1, x0:x1]
    im = Image.fromarray((np.clip(crop, 0, 1) * 255).astype(np.uint8)).resize((SIZE, SIZE), Image.BILINEAR)
    return np.asarray(im, dtype=np.float64) / 255.0


def render_letter(ch, rng):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", int(rng.integers(18, 24)))
    except Exception:
        font = ImageFont.load_default()
    d.text((int(rng.integers(3, 7)), int(rng.integers(2, 5))), ch, fill=255, font=font)
    a = _norm_glyph(np.asarray(img, dtype=np.float64) / 255.0)   # scale-invariant feature
    a += rng.normal(0, 0.06, a.shape)
    return np.clip(a, 0, 1)


class TeachApp:
    """Tkinter teaching loop. Kept in a class so the experiment can import this module without opening a window."""
    def __init__(self, learner=None, seed=0, brain_dir=None):
        import tkinter as tk
        self.tk = tk
        # DURABLE memory (JEP-295): persist what Michael teaches to a folder so it survives close+reopen and GROWS
        # across sessions. If a learner is injected (the experiment), stay in-memory and don't touch disk.
        self.sm = None
        if learner is not None:
            self.al = learner
        else:
            from world.substrate_memory import SubstrateMemory
            self.brain_dir = brain_dir or os.path.join(os.path.expanduser("~"), ".eqmod", "brain", "teach_gui")
            if os.path.exists(os.path.join(self.brain_dir, "meta.json")):
                self.sm = SubstrateMemory.load(self.brain_dir)
                if self.sm.sentences:                  # rebuild the reasoning engine from durable taught prose
                    self.eng = self.sm.rebuild_engine(seed=0)
            else:
                self.sm = SubstrateMemory(tau=0.12)
            self.al = self.sm.learner
        self.rng = np.random.default_rng(seed)
        self.cur_x = None
        self.cur_truth = None
        self.root = tk.Tk()
        self.root.title("Teach the substrate — letters")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.canvas = tk.Canvas(self.root, width=SIZE * 8, height=SIZE * 8, bg="black")
        self.canvas.pack(padx=10, pady=10)
        self.msg = tk.Label(self.root, text="", font=("Arial", 14), wraplength=SIZE * 8)
        self.msg.pack()
        taught = sum(len(v) for v in self.al.protos.values())
        self.mem_lbl = tk.Label(self.root, text=self._mem_text(taught), font=("Arial", 10), fg="#0a7")
        self.mem_lbl.pack()
        self.btns = tk.Frame(self.root); self.btns.pack(pady=8)
        self.next_btn = tk.Button(self.root, text="Show me a letter", command=self.next_item)
        self.next_btn.pack(pady=4)
        # HEAR a sound (per Michael: hear 'A' <-> write 'A'). Record yourself (Windows Voice Recorder -> .wav),
        # then load it here and say which letter -> it grounds the SOUND to the same symbol as the written letter.
        self.sound_btn = tk.Button(self.root, text="I recorded a sound (load .wav)", command=self.load_sound)
        self.sound_btn.pack(pady=2)
        # ASK THE BRAIN (JEP-324): after teaching facts by sentence, ask questions in the same window.
        ask_frame = tk.Frame(self.root); ask_frame.pack(pady=4, fill="x", padx=10)
        tk.Label(ask_frame, text="Ask:").pack(side="left")
        self.ask_entry = tk.Entry(ask_frame, width=34); self.ask_entry.pack(side="left", padx=4)
        tk.Button(ask_frame, text="Ask the brain", command=self.ask_brain).pack(side="left")
        self.ask_entry.bind("<Return>", lambda e: self.ask_brain())
        self.ask_lbl = tk.Label(self.root, text="", font=("Arial", 12), fg="#06c", wraplength=SIZE * 8)
        self.ask_lbl.pack()
        self.next_item()

    def ask_brain(self):
        q = self.ask_entry.get().strip()
        if q:
            self.ask_lbl.config(text=f"Q: {q}\nA: {answer_question(self.sm, q)}")

    def _mem_text(self, n):
        where = "in memory only" if self.sm is None else "saved to disk — survives restart & grows"
        return f"Memory: {n} examples learned · {where}"

    def _save(self):
        """Persist the taught memory so it survives the program closing (JEP-295)."""
        if self.sm is not None:
            self.sm.save(self.brain_dir)
        taught = sum(len(v) for v in self.al.protos.values())
        if hasattr(self, "mem_lbl"):
            self.mem_lbl.config(text=self._mem_text(taught))

    def _on_close(self):
        # compact on close so corrections are PHYSICALLY applied to the durable brain (JEP-335/336), not left to
        # ~95%-reliable per-query override. Only rebuilds when there's something to resolve.
        if self.sm is not None and self.sm.has_resolvable_corrections():
            self.sm = self.sm.compact()
            self.al = self.sm.learner
        self._save()
        self.root.destroy()

    def load_sound(self):
        from tkinter import filedialog
        from world.audio_features import wav_to_feature
        path = filedialog.askopenfilename(title="Pick a .wav you recorded", filetypes=[("WAV audio", "*.wav")])
        if not path:
            return
        feat = wav_to_feature(path)
        guess, conf = self.al.guess("sound", feat)
        if guess is not None and conf >= self.al.tau:
            self.msg.config(text=f"I think I HEARD '{guess}' (confidence {conf:.0%}). Type the letter if I'm wrong.")
        else:
            self.msg.config(text="I HEARD a new sound — which letter is it?")
        for w in self.btns.winfo_children():
            w.destroy()
        ent = self.tk.Entry(self.btns, width=8); ent.pack(side="left", padx=4); ent.focus()
        def submit():
            ch = ent.get().strip().upper()[:1]
            if ch:
                self.al.teach("sound", ch, feat)               # ground the SOUND to the symbol (same 'A' as written)
                self._save()                                   # durable: survives restart (JEP-295)
                self.msg.config(text=f"Thank you — I now link that SOUND to '{ch}' (and to the written '{ch}').")
            for w in self.btns.winfo_children():
                w.destroy()
        self.tk.Button(self.btns, text="Teach (sound)", command=submit).pack(side="left", padx=4)
        ent.bind("<Return>", lambda e: submit())

    def _draw(self, a):
        self.canvas.delete("all")
        for i in range(SIZE):
            for j in range(SIZE):
                v = int(a[i, j] * 255)
                if v > 20:
                    self.canvas.create_rectangle(j * 8, i * 8, j * 8 + 8, i * 8 + 8, fill=f"#{v:02x}{v:02x}{v:02x}", width=0)

    def next_item(self):
        for w in self.btns.winfo_children():
            w.destroy()
        self.cur_truth = LETTERS[int(self.rng.integers(26))]
        self.cur_x = render_letter(self.cur_truth, self.rng)
        self._draw(self.cur_x)
        sym, conf = self.al.guess("write", self.cur_x.ravel())
        if sym is None:
            self.msg.config(text="I have never seen a letter yet. What is this?")
            self._ask_truth()
        else:
            # ALWAYS offer correction -- even when 'confident'. A confidently-WRONG guess must be fixable,
            # otherwise the tool can't be taught out of an early mistake (Michael's D-called-P bug).
            sure = "UNSURE — is this" if conf < self.al.tau else "fairly sure this is"
            self.msg.config(text=f"I'm {sure} the letter '{sym}'  (confidence {conf:.0%}).  Am I right?")
            self.tk.Button(self.btns, text="Yes, correct", command=lambda: self._feedback(sym, True)).pack(side="left", padx=6)
            self.tk.Button(self.btns, text="No — let me correct it", command=lambda: self._ask_truth(sym)).pack(side="left", padx=6)

    def _ask_truth(self, guessed=None):
        for w in self.btns.winfo_children():
            w.destroy()
        self.tk.Label(self.btns, text="Type the correct letter, OR a sentence ('This is an A. An A is a letter.'):").pack(side="left")
        ent = self.tk.Entry(self.btns, width=40); ent.pack(side="left", padx=4); ent.focus()
        def submit():
            ans = ent.get().strip()
            if ans:
                # SENTENCE answer (Michael's "later, sentences"): name the percept + teach its facts in one go.
                if " is " in ans.lower() or len(ans.split()) > 1:
                    name = self._teach_sentence(ans)
                    self.msg.config(text=f"Thank you — learned this as '{name}', and noted what you told me.")
                else:                                          # a single letter/symbol
                    self.al.teach("write", ans.upper()[:1], self.cur_x.ravel())
                    self.msg.config(text=f"Thank you — learned this as '{ans.upper()[:1]}'.")
                self._save()                                   # durable: survives restart (JEP-295)
            self.next_item()
        self.tk.Button(self.btns, text="Teach", command=submit).pack(side="left", padx=4)
        ent.bind("<Return>", lambda e: submit())

    def _teach_sentence(self, sentence):
        """Michael answers with a sentence -> ground the percept from its first clause AND read its facts into the
        engine (the JEP-291 mechanism). Lazily attaches an UnderstandingEngine the first time a sentence is used."""
        import re
        if not hasattr(self, "eng"):
            from world.understanding import UnderstandingEngine
            self.eng = UnderstandingEngine(seed=0)
        s = sentence.strip()
        m = re.match(r"(?:this|it|that)\s+is\s+(?:an?\s+|the\s+)?([a-z][a-z0-9\- ]*?)\s*[.,]", s.lower() + ".")
        if not m:
            m = re.match(r"^(?:an?\s+|the\s+)?([a-z][a-z0-9\- ]*?)\b", s.lower())
        name = self.eng._norm(m.group(1).split()[-1]) if m else s.split()[0].lower()
        self.al.teach("write", name, self.cur_x.ravel())       # ground the percept to the named symbol
        if self.sm is not None:
            self.sm.learn_sentence(sentence, self.eng)         # DURABLE: record prose + bridge facts to substrate
        else:
            self.eng.read(sentence)                            # learn the sentence's facts (in-memory only)
        return name

    def _feedback(self, guessed, correct):
        self.al.confirm("write", self.cur_x.ravel(), guessed, correct)
        self._save()                                           # durable: survives restart (JEP-295)
        self.msg.config(text=f"Thanks — confirmed '{guessed}'.")
        self.next_item()

    def run(self):
        self.root.mainloop()


def main():
    print("Launching the teaching GUI… (close the window to stop)")
    TeachApp(seed=0).run()


if __name__ == "__main__":
    main()
