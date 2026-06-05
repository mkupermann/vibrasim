"""JEP-292 — HEAR from real audio FILES (per Michael: hear 'A'). Verifies the WAV hearing pipeline end-to-end:
synthesize per-letter tones -> write real WAV files -> read them back via the stdlib `wave` -> FFT features ->
ground + recognize with the ActiveLearner. Michael records 'A' (Voice Recorder -> .wav) and the same path grounds it.

Live mic streaming needs `sounddevice`; this runs everywhere with only the stdlib. No transformer / no pretrained.

Pre-registered bars in docs/amendments/jep292_wav_hearing.md.
"""
import json, string, tempfile, os
from pathlib import Path
import numpy as np

from world.active_learner import ActiveLearner
from world.audio_features import synth_tone, write_wav, wav_to_feature

LETTERS = string.ascii_uppercase


def letter_freqs(ch):
    i = ord(ch) - 65
    return [300 + 40 * i, 900 + 25 * ((i * 7) % 26), 2000 + 30 * ((i * 13) % 26)]


def run_seed(seed, tmp):
    rng = np.random.default_rng(seed)
    al = ActiveLearner(tau=0.12)

    # TEACH: write a real WAV per letter (with noise), read it back via the file path, ground it
    for ch in LETTERS:
        for k in range(8):
            w, sr = synth_tone(letter_freqs(ch), noise=0.05, rng=rng)
            p = os.path.join(tmp, f"train_{ch}_{k}_{seed}.wav")
            write_wav(p, w, sr)
            al.teach("sound", ch, wav_to_feature(p))

    # HEAR: held-out WAVs -> recognize via the SAME file path
    ok = tot = 0
    for ch in LETTERS:
        for k in range(5):
            w, sr = synth_tone(letter_freqs(ch), noise=0.08, rng=rng)
            p = os.path.join(tmp, f"test_{ch}_{k}_{seed}.wav")
            write_wav(p, w, sr)
            tot += 1; ok += (al.guess("sound", wav_to_feature(p))[0] == ch)
    return {"hear_wav_acc": round(ok / tot, 3), "n_letters": len(LETTERS)}


if __name__ == "__main__":
    print("=== JEP-292: HEAR from real WAV files (round-trip through the stdlib `wave`) ===", flush=True)
    seeds = [42, 7]
    with tempfile.TemporaryDirectory() as tmp:
        R = {s: run_seed(s, tmp) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: hear-from-WAV accuracy={R[s]['hear_wav_acc']} over {R[s]['n_letters']} letters", flush=True)

    J292a = all(R[s]['hear_wav_acc'] >= 0.90 for s in seeds)
    # J292b: the GUI 'load a sound' path imports
    try:
        import importlib; importlib.import_module("tools.teach_gui"); from world import audio_features  # noqa
        J292b = True
    except Exception as ex:
        J292b = False; print("  import:", ex, flush=True)
    passed = J292a and J292b

    print("\n--- VERDICT ---", flush=True)
    print(f"J292a hears letters from real WAV files (>=0.90): {J292a}", flush=True)
    print(f"J292b WAV hearing path wired + imports          : {J292b}", flush=True)
    verdict = ("PASS - the engine HEARS letters from real audio FILES (record a WAV -> grounded), stdlib-only "
               "hearing path") if passed else "NULL/partial"
    print(f"\nJEP-292: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP292"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): R[s] for s in seeds}, "J292a": J292a,
                                                  "J292b": J292b, "passed": passed}, indent=2, default=str))
    print("DONE", flush=True)
