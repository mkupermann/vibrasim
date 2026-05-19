"""R-15 acceptance: tuned-synthesis env wiring.

Pre-registered in R-15: with ``EQMOD_USE_TUNED_SYNTHESIS=1``,
``agent.flux.synthesis.get_synthesis_config`` returns a
``SynthesisConfig`` whose ``Q == 3.0`` and ``impulse_gain == 1.0`` —
the locked pair R-14 (commit ``e9c9275``) picked as the smallest in the
sweep ``Q in {3,5,10,30} x gain in {1,5,25,100}`` that satisfied the
sensitivity gates.

The default-baseline test is a defensive complement: without the env
flag, ``get_synthesis_config`` returns the F2 baseline (``Q=5.0``,
``impulse_gain=1.0``) so the existing R-3 synthesis tests remain green.
"""
from __future__ import annotations

from agent.flux.synthesis import (
    SynthesisConfig,
    TUNED_SYNTHESIS_IMPULSE_GAIN,
    TUNED_SYNTHESIS_Q,
    get_synthesis_config,
)


def test_env_loads_Q3_gain1(monkeypatch) -> None:
    monkeypatch.setenv("EQMOD_USE_TUNED_SYNTHESIS", "1")
    cfg = get_synthesis_config()
    assert isinstance(cfg, SynthesisConfig)
    assert cfg.Q == TUNED_SYNTHESIS_Q == 3.0
    assert cfg.impulse_gain == TUNED_SYNTHESIS_IMPULSE_GAIN == 1.0


def test_default_returns_baseline_synthesis(monkeypatch) -> None:
    monkeypatch.delenv("EQMOD_USE_TUNED_SYNTHESIS", raising=False)
    cfg = get_synthesis_config()
    assert isinstance(cfg, SynthesisConfig)
    assert cfg.Q == 5.0
    assert cfg.impulse_gain == 1.0


def test_env_off_value_returns_baseline(monkeypatch) -> None:
    """Any value other than ``"1"`` is treated as "off" — explicit contract."""
    monkeypatch.setenv("EQMOD_USE_TUNED_SYNTHESIS", "0")
    cfg = get_synthesis_config()
    assert cfg.Q == 5.0
    assert cfg.impulse_gain == 1.0


def test_overrides_win_over_env(monkeypatch) -> None:
    """Caller-provided overrides take precedence over env-selected defaults."""
    monkeypatch.setenv("EQMOD_USE_TUNED_SYNTHESIS", "1")
    cfg = get_synthesis_config(Q=7.5)
    assert cfg.Q == 7.5
    # impulse_gain wasn't overridden, so tuned value still applies.
    assert cfg.impulse_gain == 1.0
