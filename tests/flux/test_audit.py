"""Tests for the EnergyAuditor."""
from __future__ import annotations
import pytest

from world.flux.quantum import Quanta
from world.flux.audit import EnergyAuditor, ConservationViolation


def test_auditor_starts_balanced():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    assert a.E_initial == 0.0
    assert a.E_injected_total == 0.0
    assert a.E_exported_total == 0.0


def test_auditor_record_injection_accumulates():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    a.record_injection(2.5)
    a.record_injection(1.5)
    assert a.E_injected_total == 4.0


def test_auditor_record_export_accumulates():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    a.record_export(0.5)
    a.record_export(0.5)
    assert a.E_exported_total == 1.0


def test_auditor_balance_holds_after_injection_and_persistence():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=3.0)
    a.record_injection(3.0)
    a.check()  # Should not raise


def test_auditor_balance_holds_after_export():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=5.0)
    a.record_injection(5.0)
    # Simulate boundary absorbing the quantum
    q.remove(0)
    a.record_export(5.0)
    a.check()  # Should not raise


def test_auditor_raises_on_violation():
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    # Inject 5 but only 4 actually appears in quanta -> imbalance
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=4.0)
    a.record_injection(5.0)
    with pytest.raises(ConservationViolation):
        a.check()
