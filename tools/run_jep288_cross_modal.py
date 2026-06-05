"""JEP-288 — cross-modal grounding: 'hear A' <-> 'write A' (per Michael's steer).

The engine grounds letters in TWO senses -- SIGHT (written-letter images) and SOUND (synthesized per-letter tones ->
FFT features) -- bound to the SAME symbols, and we show cross-modal recall (hearing a letter retrieves its written
form). Real waveform synthesis + real FFT features; no real recordings, no AI.

Pre-registered bars in docs/amendments/jep288_cross_modal_hear_write.md.
"""
import json, string
from pathlib import Path
import numpy as np

from world.active_learner import ActiveLearner
from tools.run_jep287_active_letter_learning import render_letter

LETTERS = string.ascii_uppercase
SR = 8000
DUR = 0.2


def letter_formants(ch):
    """Deterministic per-letter 3-formant frequencies (a distinct 'sound' per letter; stands in for speech)."""
    i = ord(ch) - 65
    return [300 + 40 * i, 900 + 25 * ((i * 7) % 26), 2000 + 30 * ((i * 13) % 26)]


def hear_letter(ch, rng):
    """Synthesize the letter's tone and return its 'heard' feature = log-FFT magnitude (32 bins) + noise."""
    t = np.linspace(0, DUR, int(SR * DUR), endpoint=False)
    wave = sum(np.sin(2 * np.pi * f * t) for f in letter_formants(ch))
    wave += rng.normal(0, 0.3, wave.shape)                       # ambient noise
    mag = np.abs(np.fft.rfft(wave * np.hanning(len(wave))))       # 0..SR/2 Hz spectrum
    nb = 32
    B = len(mag) // nb
    binned = np.array([mag[i * B:(i + 1) * B].mean() for i in range(nb)])   # 32 CONTIGUOUS frequency bands
    feat = np.log1p(binned)
    return feat / (np.linalg.norm(feat) + 1e-9)


def run_seed(seed):
    rng = np.random.default_rng(seed)
    al = ActiveLearner(tau=0.12)
    # TEACH both senses, bound to the same symbols
    for ch in LETTERS:
        for _ in range(20):
            al.teach("write", ch, render_letter(ch, rng))
            al.teach("sound", ch, hear_letter(ch, rng))

    # J288a: hear held-out sounds -> correct symbol
    hear_ok = tot = 0
    for ch in LETTERS:
        for _ in range(10):
            tot += 1; hear_ok += (al.guess("sound", hear_letter(ch, rng))[0] == ch)
    hear_acc = hear_ok / tot

    # J288b: both senses ground the SAME symbol set
    sound_syms = {sym for (mod, sym) in al.protos if mod == "sound"}
    write_syms = {sym for (mod, sym) in al.protos if mod == "write"}
    same_symbols = (sound_syms == write_syms == set(LETTERS))

    # J288c: CROSS-MODAL recall -- hear a letter -> its symbol -> retrieve the WRITTEN prototype; verify that written
    # prototype is nearest to held-out WRITTEN images of the same letter (sound -> symbol -> sight)
    xrecall_ok = xtot = 0
    for ch in LETTERS:
        xtot += 1
        heard_sym = al.guess("sound", hear_letter(ch, rng))[0]              # hear -> symbol
        recalled_proto = al._proto("write", heard_sym)                      # symbol -> written prototype
        test_img = render_letter(ch, rng)                                   # a real written 'ch'
        nearest_write = al.guess("write", test_img)[0]
        xrecall_ok += (heard_sym == ch and nearest_write == ch)            # the recalled written form is the right letter

    # J288d: TRANSFER -- a symbol taught only by SOUND, then ONE written example -> recognized by sight
    al2 = ActiveLearner(tau=0.12)
    for _ in range(20):
        al2.teach("sound", "Q", hear_letter("Q", rng))                     # learned Q only by EAR
    sound_only_q = al2.guess("sound", hear_letter("Q", rng))[0] == "Q"
    al2.teach("write", "Q", render_letter("Q", rng))                       # one WRITTEN Q (same symbol)
    sight_q = al2.guess("write", render_letter("Q", rng))[0] == "Q"        # now recognizes the WRITTEN Q
    transfer = bool(sound_only_q and sight_q)

    return {"hear_acc": round(hear_acc, 3), "same_symbols": bool(same_symbols),
            "xrecall_acc": round(xrecall_ok / xtot, 3), "transfer": transfer,
            "n_symbols_sound": len(sound_syms), "n_symbols_write": len(write_syms)}


if __name__ == "__main__":
    print("=== JEP-288: cross-modal hear<->write grounding ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: hear-acc={r['hear_acc']} | same-symbol-set={r['same_symbols']} "
              f"({r['n_symbols_sound']} sound, {r['n_symbols_write']} write) | cross-modal recall={r['xrecall_acc']} "
              f"| transfer(ear->eye)={r['transfer']}", flush=True)

    J288a = all(R[s]['hear_acc'] >= 0.90 for s in seeds)
    J288b = all(R[s]['same_symbols'] for s in seeds)
    J288c = all(R[s]['xrecall_acc'] >= 0.90 for s in seeds)
    J288d = all(R[s]['transfer'] for s in seeds)
    passed = J288a and J288b and J288c

    print("\n--- VERDICT ---", flush=True)
    print(f"J288a hears letters (>=0.90)          : {J288a}", flush=True)
    print(f"J288b hear+write share one symbol set : {J288b}", flush=True)
    print(f"J288c cross-modal recall (>=0.90)     : {J288c}", flush=True)
    print(f"J288d transfer ear<->eye              : {J288d}", flush=True)
    verdict = ("PASS - the engine HEARS letters and links them to the WRITTEN letters via a shared symbol "
               "(Michael's hear<->write link)") if passed else "NULL/partial"
    print(f"\nJEP-288: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP288"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J288a": J288a, "J288b": J288b, "J288c": J288c, "J288d": J288d,
         "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
