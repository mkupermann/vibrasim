"""TTS readout layer for the substrate.

The substrate fires audio_output atoms with a frequency-correlated pattern
when its trained visual is presented. This module turns those firing
patterns into intelligible speech by speaking a user-provided label
through the OS's TTS.

macOS uses the built-in `say` command (no extra deps).
Linux uses `espeak` if available; otherwise no-op with a warning.
Windows: best-effort via pyttsx3 if installed; otherwise no-op.

Usage from the GUI / talk loop:
    speaker = Speaker(label="water")
    # ... substrate runs ...
    if fires_audio_out > threshold:
        speaker.maybe_say()         # rate-limited
"""
from __future__ import annotations
import shutil
import subprocess
import sys
import time
from typing import Optional


class Speaker:
    """Rate-limited TTS speaker. `maybe_say()` is the trigger; it speaks
    the configured label at most once every `cooldown_seconds` so the
    substrate doesn't spam the speaker on every tick."""

    def __init__(self, label: str = "",
                 cooldown_seconds: float = 2.0,
                 voice: Optional[str] = None,
                 rate_wpm: int = 175):
        self.label = label
        self.cooldown_seconds = cooldown_seconds
        self.voice = voice
        self.rate_wpm = rate_wpm
        self._last_spoken_at: Optional[float] = None
        self._backend = self._detect_backend()
        self._proc: Optional[subprocess.Popen] = None

    @staticmethod
    def _detect_backend() -> str:
        if sys.platform == "darwin" and shutil.which("say"):
            return "macos-say"
        if shutil.which("espeak"):
            return "espeak"
        try:
            import pyttsx3  # noqa: F401
            return "pyttsx3"
        except ImportError:
            return "noop"

    def set_label(self, label: str) -> None:
        self.label = label

    def is_speaking(self) -> bool:
        if self._proc is None:
            return False
        return self._proc.poll() is None

    def maybe_say(self) -> bool:
        """Speak the label if (a) we have one, (b) backend available, and
        (c) cooldown elapsed since last speak. Returns True if spoken."""
        if not self.label or self._backend == "noop":
            return False
        if self.is_speaking():
            return False
        now = time.time()
        if (self._last_spoken_at is not None
                and now - self._last_spoken_at < self.cooldown_seconds):
            return False
        self._last_spoken_at = now
        try:
            self._speak_async(self.label)
            return True
        except Exception:
            return False

    def _speak_async(self, text: str) -> None:
        if self._backend == "macos-say":
            args = ["say", "-r", str(self.rate_wpm)]
            if self.voice:
                args.extend(["-v", self.voice])
            args.append(text)
            self._proc = subprocess.Popen(
                args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        elif self._backend == "espeak":
            args = ["espeak", "-s", str(self.rate_wpm)]
            if self.voice:
                args.extend(["-v", self.voice])
            args.append(text)
            self._proc = subprocess.Popen(
                args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        elif self._backend == "pyttsx3":
            import pyttsx3  # local import — avoid hard dep
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate_wpm)
            if self.voice:
                engine.setProperty("voice", self.voice)
            engine.say(text)
            engine.runAndWait()
            self._proc = None  # synchronous

    @property
    def backend(self) -> str:
        return self._backend
