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
import string
import numpy as np

from world.active_learner import ActiveLearner

SIZE = 28
LETTERS = string.ascii_uppercase


def _center(a):
    ys, xs = np.nonzero(a > 0.3)
    if len(xs) == 0:
        return a
    sy, sx = int(round(SIZE / 2 - ys.mean())), int(round(SIZE / 2 - xs.mean()))
    return np.roll(np.roll(a, sy, axis=0), sx, axis=1)


def render_letter(ch, rng):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", int(rng.integers(18, 24)))
    except Exception:
        font = ImageFont.load_default()
    d.text((int(rng.integers(3, 7)), int(rng.integers(2, 5))), ch, fill=255, font=font)
    a = _center(np.asarray(img, dtype=np.float64) / 255.0)
    a += rng.normal(0, 0.06, a.shape)
    return np.clip(a, 0, 1)


class TeachApp:
    """Tkinter teaching loop. Kept in a class so the experiment can import this module without opening a window."""
    def __init__(self, learner=None, seed=0):
        import tkinter as tk
        self.tk = tk
        self.al = learner or ActiveLearner(tau=0.12)
        self.rng = np.random.default_rng(seed)
        self.cur_x = None
        self.cur_truth = None
        self.root = tk.Tk()
        self.root.title("Teach the substrate — letters")
        self.canvas = tk.Canvas(self.root, width=SIZE * 8, height=SIZE * 8, bg="black")
        self.canvas.pack(padx=10, pady=10)
        self.msg = tk.Label(self.root, text="", font=("Arial", 14), wraplength=SIZE * 8)
        self.msg.pack()
        self.btns = tk.Frame(self.root); self.btns.pack(pady=8)
        self.next_btn = tk.Button(self.root, text="Show me a letter", command=self.next_item)
        self.next_btn.pack(pady=4)
        self.next_item()

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
        elif conf < self.al.tau:
            self.msg.config(text=f"I'm UNSURE — is this the letter '{sym}'?  (confidence {conf:.0%})")
            self.tk.Button(self.btns, text="Correct", command=lambda: self._feedback(sym, True)).pack(side="left", padx=6)
            self.tk.Button(self.btns, text="Not correct", command=lambda: self._ask_truth(sym)).pack(side="left", padx=6)
        else:
            self.msg.config(text=f"I'm confident this is '{sym}' (confidence {conf:.0%}).  [click 'Show me a letter']")

    def _ask_truth(self, guessed=None):
        for w in self.btns.winfo_children():
            w.destroy()
        self.tk.Label(self.btns, text="Type the correct letter (or a sentence later):").pack(side="left")
        ent = self.tk.Entry(self.btns, width=12); ent.pack(side="left", padx=4); ent.focus()
        def submit():
            ans = ent.get().strip().upper()[:1]
            if ans:
                self.al.teach("write", ans, self.cur_x.ravel())
                self.msg.config(text=f"Thank you — learned this as '{ans}'.")
            self.next_item()
        self.tk.Button(self.btns, text="Teach", command=submit).pack(side="left", padx=4)
        ent.bind("<Return>", lambda e: submit())

    def _feedback(self, guessed, correct):
        self.al.confirm("write", self.cur_x.ravel(), guessed, correct)
        self.msg.config(text=f"Thanks — confirmed '{guessed}'.")
        self.next_item()

    def run(self):
        self.root.mainloop()


def main():
    print("Launching the teaching GUI… (close the window to stop)")
    TeachApp(seed=0).run()


if __name__ == "__main__":
    main()
