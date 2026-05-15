"""Grid — voxel dimensions + temperature field.

The temperature is exponentially-smoothed local free-quanta density,
updated each tick from the Quanta positions. In F0 the temperature is
computed and stored but does not gate any binding (no binding rule
exists yet). It will gate binding from F1 onward.
"""
from __future__ import annotations
from typing import Sequence
import numpy as np


class Grid:
    """3D voxel grid with an exponentially-smoothed temperature field.

    `dims` is (Lx, Ly, Lz) in voxel counts.
    `voxel_size` is the physical extent of one voxel.
    `T_smoothing` is α in T(t+1) = α * density + (1-α) * T(t).
    Default α = 0.1 gives a ~10-tick effective memory.
    """

    def __init__(self, dims: tuple[int, int, int],
                 voxel_size: float = 1.0,
                 T_smoothing: float = 0.1):
        self.dims = tuple(int(d) for d in dims)
        if len(self.dims) != 3 or any(d < 1 for d in self.dims):
            raise ValueError(
                f"Grid dims must be a 3-tuple of positive ints, got {self.dims}"
            )
        self.voxel_size = float(voxel_size)
        if self.voxel_size <= 0.0:
            raise ValueError(
                f"Grid voxel_size must be positive, got {self.voxel_size}"
            )
        self.T_smoothing = float(T_smoothing)
        self.T = np.zeros(self.dims, dtype=np.float64)

    def pos_to_voxel(self, pos: Sequence[float]) -> tuple[int, int, int]:
        """Map a continuous position to a clipped voxel index."""
        x, y, z = pos
        ix = int(np.clip(x / self.voxel_size, 0, self.dims[0] - 1))
        iy = int(np.clip(y / self.voxel_size, 0, self.dims[1] - 1))
        iz = int(np.clip(z / self.voxel_size, 0, self.dims[2] - 1))
        return ix, iy, iz

    def update_temperature(self, density: np.ndarray,
                            spatial_sigma: float = 0.0) -> None:
        """Exponential smoothing: T(t+1) = α * density + (1-α) * T(t).

        When `spatial_sigma > 0`, apply a gaussian spatial filter to T
        after the EMA update. This is a physically reasonable thermal
        diffusion model and damps Poisson density-shot-noise that would
        otherwise dominate the FFT of the horizontal T profile (R-1c-tris
        diagnosis: short-range Poisson noise drowns the smooth thermal
        gradient that drives Bénard convection).
        """
        if density.shape != self.dims:
            raise ValueError(
                f"density shape {density.shape} != grid dims {self.dims}"
            )
        a = self.T_smoothing
        self.T = a * density + (1.0 - a) * self.T
        if spatial_sigma > 0.0:
            from scipy.ndimage import gaussian_filter
            self.T = gaussian_filter(self.T, sigma=spatial_sigma,
                                       mode="nearest")
