"""Pre-registered tests for the R-1b pressure-gradient horizontal force.

Contract (locked in QUEUE.yaml R-1b):

- test_horizontal_force_responds_to_T_gradient:
    >=80% of alive quanta acquire non-zero horizontal velocity under a
    horizontal T gradient.

- test_horizontal_force_zero_when_no_gradient:
    mean horizontal velocity < 0.01 under uniform T (negative control
    against spurious firing).

The substrate places one quantum per voxel center so density is exactly
uniform (rho=1 everywhere). Under that layout the pressure proxy P=rho*T
reduces to T, so the only signal driving the force is the T gradient.
That makes the two tests a positive/negative pair: a buggy gate would
break the second, a no-op force would break the first.
"""
from __future__ import annotations
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.pressure import apply_pressure_gradient_force


def _grid_with_one_quantum_per_voxel(dims=(10, 5, 5), voxel_size=1.0):
    """Build a (grid, quanta) pair with one alive quantum at every voxel
    center, all velocities zero. Returns (grid, quanta, n_alive)."""
    Lx, Ly, Lz = dims
    g = Grid(dims=dims, voxel_size=voxel_size)
    q = Quanta(max_quanta=Lx * Ly * Lz)
    for i in range(Lx):
        for j in range(Ly):
            for k in range(Lz):
                pos = ((i + 0.5) * voxel_size,
                       (j + 0.5) * voxel_size,
                       (k + 0.5) * voxel_size)
                slot = q.add(pos=pos, vel=(0.0, 0.0, 0.0),
                              freq=1.0, polarity=1, energy=1.0)
                assert slot >= 0
    return g, q, q.n_alive()


def test_horizontal_force_responds_to_T_gradient():
    """Warm left (x=0), cold right (x=Lx-1). With rho=1 and T(x) the only
    varying field, the pressure-gradient force gives every quantum the
    same sign of vel_x. Pre-registered threshold: >=80% of alive quanta
    acquire non-zero horizontal velocity. (We expect 100% here, the 80%
    band exists so a half-built force can't pass.)"""
    g, q, n_alive = _grid_with_one_quantum_per_voxel(dims=(10, 5, 5))
    Lx = g.dims[0]
    # T = warm_value * (1 - x/(Lx-1))  → linear from 10.0 at x=0 to 0.0 at x=Lx-1
    x_idx = np.arange(Lx, dtype=np.float64)
    T_profile = 10.0 * (1.0 - x_idx / (Lx - 1))
    g.T[:, :, :] = T_profile[:, None, None]

    apply_pressure_gradient_force(q, g, pressure_coeff=1.0, dt=0.1)

    alive = q.alive
    vel = q.vel[alive]
    n_horizontal_movers = int(((np.abs(vel[:, 0]) > 0.0) |
                                (np.abs(vel[:, 1]) > 0.0)).sum())
    frac = n_horizontal_movers / n_alive
    assert frac >= 0.80, (
        f"horizontal force fired on only {frac:.1%} of alive quanta "
        f"({n_horizontal_movers}/{n_alive}); pre-registered threshold 80%"
    )

    # With dT/dx < 0 and P=T, -∂P/∂x > 0 → vel_x > 0 (away from warm).
    # Interior voxels see a clean gradient; boundary voxels use one-sided
    # diffs and still get vel_x > 0. So mean vel_x must be strictly positive.
    assert vel[:, 0].mean() > 0.0, (
        f"mean vel_x = {vel[:, 0].mean():.3e} — force did not push from "
        "warm (low x) toward cold (high x)"
    )

    # The orthogonal directions must stay quiet — T varies only in x, so
    # ∂P/∂y and ∂P/∂z are zero by construction.
    assert np.allclose(vel[:, 1], 0.0, atol=1e-12), (
        f"vel_y leaked: max |vel_y| = {np.abs(vel[:, 1]).max():.3e}"
    )
    assert np.allclose(vel[:, 2], 0.0, atol=1e-12), (
        f"vel_z leaked: max |vel_z| = {np.abs(vel[:, 2]).max():.3e}"
    )


def test_horizontal_force_zero_when_no_gradient():
    """Uniform T everywhere, same uniform density. P = rho*T is constant,
    so ∇P is zero and the force is a no-op. Pre-registered threshold:
    mean horizontal velocity magnitude < 0.01. Negative control — confirms
    the force only fires on real gradients."""
    g, q, n_alive = _grid_with_one_quantum_per_voxel(dims=(10, 5, 5))
    g.T[:, :, :] = 2.5  # uniform, non-zero

    apply_pressure_gradient_force(q, g, pressure_coeff=1.0, dt=0.1)

    alive = q.alive
    vel = q.vel[alive]
    horizontal_mag = np.sqrt(vel[:, 0] ** 2 + vel[:, 1] ** 2)
    mean_mag = float(horizontal_mag.mean())
    assert mean_mag < 0.01, (
        f"mean horizontal velocity = {mean_mag:.6e} >= 0.01 under uniform T; "
        "force is firing on noise"
    )
    # With perfectly uniform density and uniform T, P is exact-constant and
    # the gradient is exactly zero. This is stricter than the pre-registered
    # 0.01 bound and acts as a guard against silent regressions.
    assert mean_mag < 1e-12, (
        f"mean horizontal velocity = {mean_mag:.6e} above floating-point noise; "
        "implementation has a spurious bias"
    )
