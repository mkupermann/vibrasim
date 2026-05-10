"""Energy conservation audit.

Conservation law:
    E_initial + E_injected_total == E_in_quanta + E_exported_total
within tolerance `tol` × max(|E_initial + E_injected_total|, 1.0).

A failed audit halts the run (raises ConservationViolation). This is
non-negotiable per the spec §3: a failed audit means the code is broken,
not the physics. Production mode can disable the assertion via the
caller passing audit=None to tick(); default is enabled.
"""
from __future__ import annotations

from world.flux.quantum import Quanta


class ConservationViolation(AssertionError):
    """Raised when energy conservation is violated beyond tolerance."""


class EnergyAuditor:
    def __init__(self, quanta: Quanta, tol: float = 1e-9):
        self.quanta = quanta
        self.tol = float(tol)
        self.E_initial: float = 0.0
        self.E_injected_total: float = 0.0
        self.E_exported_total: float = 0.0
        self.tick_count: int = 0

    def record_initial(self) -> None:
        self.E_initial = self.quanta.total_energy()

    def record_injection(self, e: float) -> None:
        self.E_injected_total += float(e)

    def record_export(self, e: float) -> None:
        self.E_exported_total += float(e)

    def check(self) -> None:
        """Assert conservation. Raises ConservationViolation on
        imbalance."""
        E_in = self.quanta.total_energy()
        lhs = self.E_initial + self.E_injected_total
        rhs = E_in + self.E_exported_total
        scale = max(abs(lhs), 1.0)
        err = abs(lhs - rhs)
        if err > self.tol * scale:
            raise ConservationViolation(
                f"Energy conservation violated at tick {self.tick_count}: "
                f"E_initial({self.E_initial}) + E_injected({self.E_injected_total}) "
                f"= {lhs}; E_in_quanta({E_in}) + E_exported({self.E_exported_total}) "
                f"= {rhs}; diff={err}, tol={self.tol * scale}"
            )

    def step(self) -> None:
        self.tick_count += 1
