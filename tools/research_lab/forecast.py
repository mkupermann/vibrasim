"""Forecast scoring and enhancement for the research lab.

Rule: a miss never upgrades an acceptance threshold. A miss upgrades the
forecast *method* (what we predict and why), then we re-score on a new run.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ForecastCheck:
    id: str
    description: str
    passed: bool
    observed: Any
    predicted: str
    method_version: int = 1


@dataclass
class ExperimentScore:
    name: str
    checks: list[ForecastCheck]
    method_version: int
    scored_at: str
    notes: str = ""

    @property
    def score(self) -> float:
        if not self.checks:
            return 0.0
        return sum(1.0 for c in self.checks if c.passed) / len(self.checks)

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def misses(self) -> list[ForecastCheck]:
        return [c for c in self.checks if not c.passed]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["score"] = self.score
        d["all_passed"] = self.all_passed
        return d


class ForecastJournal:
    def __init__(self, path: Path):
        self.path = path
        self.entries: list[dict] = []
        self.method_version = 1
        self.method_notes: list[str] = [
            "v1: binary inequality checks on named metrics (FORECASTS.md)"
        ]

    def record(self, score: ExperimentScore) -> ExperimentScore:
        self.entries.append(score.to_dict())
        if not score.all_passed:
            enhanced = self._enhance(score)
            score.notes = (score.notes + " | " if score.notes else "") + enhanced
        self._flush()
        return score

    def _enhance(self, score: ExperimentScore) -> str:
        """Upgrade forecast method after a miss. Never change pass thresholds."""
        misses = score.misses()
        self.method_version += 1
        patterns = []
        for m in misses:
            patterns.append(f"{m.id}: predicted {m.predicted}, observed {m.observed}")
        note = (
            f"method v{self.method_version} after miss in {score.name}: "
            + "; ".join(patterns)
            + " — enhancement: report effect-size + seed spread alongside pass/fail, "
            "and split monotone vs peak forecasts when a curve can saturate at the horizon."
        )
        self.method_notes.append(note)
        return note

    def _flush(self) -> None:
        payload = {
            "method_version": self.method_version,
            "method_notes": self.method_notes,
            "entries": self.entries,
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def check(cid: str, description: str, passed: bool, observed: Any, predicted: str,
          method_version: int = 1) -> ForecastCheck:
    return ForecastCheck(
        id=cid, description=description, passed=bool(passed),
        observed=observed, predicted=predicted, method_version=method_version,
    )
