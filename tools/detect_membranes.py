"""Detect membrane-like structures (closed molecular shells) in a snapshot.

A membrane is operationally defined as a connected component of molecules
whose positions lie approximately on the surface of a 3D sphere, with an
empty interior.

Usage:
    python tools/detect_membranes.py snapshot.npz [--format text|json]

See docs/superpowers/specs/2026-05-06-phase-3-membranes.md for the full spec.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np

from world.snapshot import load_snapshot


def fit_sphere(points: np.ndarray) -> tuple[np.ndarray, float, float]:
    """Least-squares sphere fit. Returns (centre, radius, sigma_r).

    points: (N, 3) array of positions.
    Linearised system from (x − cx)² + (y − cy)² + (z − cz)² = R²:
        2·cx·x + 2·cy·y + 2·cz·z + (R² − cx² − cy² − cz²) = x² + y² + z²
    Solve for [cx, cy, cz, D] where D = R² − |c|².
    """
    n = points.shape[0]
    A = np.column_stack([2 * points, np.ones(n)])
    b = (points ** 2).sum(axis=1)
    sol, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy, cz, D = sol
    centre = np.array([cx, cy, cz], dtype=np.float64)
    R_sq = D + centre @ centre
    radius = float(math.sqrt(max(R_sq, 0.0)))
    distances = np.linalg.norm(points - centre, axis=1)
    sigma_r = float(np.std(distances - radius))
    return centre, radius, sigma_r


def connected_components(positions: np.ndarray, r_neighbour: float) -> list[list[int]]:
    """Build adjacency graph: nodes within r_neighbour are connected.

    Returns a list of components, each as a list of indices.
    """
    n = positions.shape[0]
    if n == 0:
        return []
    visited = np.zeros(n, dtype=bool)
    components: list[list[int]] = []
    r_sq = r_neighbour * r_neighbour
    for start in range(n):
        if visited[start]:
            continue
        # BFS
        stack = [start]
        component: list[int] = []
        visited[start] = True
        while stack:
            i = stack.pop()
            component.append(i)
            d2 = ((positions - positions[i]) ** 2).sum(axis=1)
            neighbours = np.where((d2 < r_sq) & ~visited)[0]
            for j in neighbours:
                visited[j] = True
                stack.append(int(j))
        components.append(component)
    return components


def count_gaps(points_on_sphere: np.ndarray, centre: np.ndarray,
               n_polar: int = 6, n_az_max: int = 12) -> int:
    """Count distinct gap regions on the sphere surface (candidate permeability points).

    Equal-area binning: each polar ring has azimuth-bin count proportional to
    sin(polar_angle), so bins are roughly equal area. A bin is a "gap" if it
    contains ZERO points AND is large enough to matter (skip degenerate
    near-pole bins). Adjacent empty bins merge into one gap via flood-fill.

    For sparse Fibonacci shells (where individual bins may randomly be empty),
    this is a coarse measure — increase the input shell density or coarsen
    the bins for cleaner signal. The intention is to flag visible holes,
    not to count every microscopic gap.
    """
    if len(points_on_sphere) == 0:
        return 0
    directions = points_on_sphere - centre
    norms = np.linalg.norm(directions, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    directions = directions / norms

    azimuth = np.arctan2(directions[:, 1], directions[:, 0])  # -π..π
    polar = np.arccos(np.clip(directions[:, 2], -1.0, 1.0))    # 0..π

    # Per polar ring, how many azimuth bins (proportional to sin(polar) for equal area).
    # Use a discrete grid: for each ring r in [0, n_polar), polar_angle = (r+0.5)/n_polar * π.
    n_az_per_ring = []
    for r in range(n_polar):
        polar_angle = (r + 0.5) / n_polar * math.pi
        n_az = max(3, int(n_az_max * math.sin(polar_angle)))
        n_az_per_ring.append(n_az)

    # Build occupancy: occupied[r] is a list of n_az_per_ring[r] booleans
    occupied = [[False] * n_az_per_ring[r] for r in range(n_polar)]
    for az, pol in zip(azimuth, polar):
        r = int(pol / math.pi * n_polar)
        r = min(max(r, 0), n_polar - 1)
        n_az = n_az_per_ring[r]
        a = int((az + math.pi) / (2 * math.pi) * n_az) % n_az
        occupied[r][a] = True

    # Flood-fill gaps. Adjacency: same-ring-neighbours, and nearest-azimuth bins
    # in the rings above and below.
    visited = [[False] * n_az_per_ring[r] for r in range(n_polar)]
    gaps = 0
    for r in range(n_polar):
        for a in range(n_az_per_ring[r]):
            if occupied[r][a] or visited[r][a]:
                continue
            stack = [(r, a)]
            visited[r][a] = True
            while stack:
                cr, ca = stack.pop()
                # Same-ring neighbours
                for da in (-1, 1):
                    na = (ca + da) % n_az_per_ring[cr]
                    if not occupied[cr][na] and not visited[cr][na]:
                        visited[cr][na] = True
                        stack.append((cr, na))
                # Adjacent rings: map azimuth proportionally
                for dr in (-1, 1):
                    nr = cr + dr
                    if not (0 <= nr < n_polar):
                        continue
                    proportion = (ca + 0.5) / n_az_per_ring[cr]
                    target_a = int(proportion * n_az_per_ring[nr]) % n_az_per_ring[nr]
                    for offset in (-1, 0, 1):
                        nb = (target_a + offset) % n_az_per_ring[nr]
                        if not occupied[nr][nb] and not visited[nr][nb]:
                            visited[nr][nb] = True
                            stack.append((nr, nb))
            gaps += 1
    return gaps


def detect_membranes(world, *, r_membrane: float = None,
                      hollow_threshold: float = 0.6,
                      sigma_threshold: float = 0.20,
                      min_molecules: int = 12) -> list[dict]:
    """Find candidate membrane structures.

    See docs/superpowers/specs/2026-05-06-phase-3-membranes.md §3.
    """
    if r_membrane is None:
        r_membrane = float(world.config.r_2) * 2.0

    # Pull alive molecule positions (level 5+) from the world
    is_molecule = (world.k_level >= 5) & world.k_alive
    indices = np.where(is_molecule)[0]
    if len(indices) < min_molecules:
        return []
    positions = world.k_pos[indices]

    components = connected_components(positions, r_membrane)
    candidates: list[dict] = []

    for component in components:
        if len(component) < min_molecules:
            continue
        local_pts = positions[component]
        centre, radius, sigma_r = fit_sphere(local_pts)
        if radius == 0:
            continue
        sigma_norm = sigma_r / radius

        # Count interior nodes (any alive node inside hollow_threshold·R)
        interior_count = 0
        for i in range(world.k_count):
            if not world.k_alive[i]:
                continue
            if (i in (indices[c] for c in component)):
                continue
            d = np.linalg.norm(world.k_pos[i] - centre)
            if d < hollow_threshold * radius:
                interior_count += 1

        n_gaps = count_gaps(local_pts, centre)
        is_closed = (interior_count == 0) and (sigma_norm < sigma_threshold)

        candidates.append({
            "molecule_indices": [int(indices[c]) for c in component],
            "centre": centre.tolist(),
            "radius": radius,
            "sigma_r": sigma_r,
            "sigma_norm": sigma_norm,
            "interior_count": interior_count,
            "n_gaps": n_gaps,
            "closed": bool(is_closed),
            "n_molecules": len(component),
        })
    return candidates


def format_text(snapshot_path: Path, candidates: list[dict]) -> str:
    lines = [f"# membrane candidates in {snapshot_path.name}"]
    if not candidates:
        lines.append("# (no candidates with the default thresholds)")
        return "\n".join(lines)
    closed = [c for c in candidates if c["closed"]]
    lines.append(f"# {len(candidates)} candidate(s); {len(closed)} closed")
    for i, c in enumerate(candidates):
        flag = "✔ closed" if c["closed"] else "open"
        lines.append(
            f"  [{i}] n={c['n_molecules']:3d}  R={c['radius']:7.2f}  "
            f"σ_r/R={c['sigma_norm']:.3f}  interior={c['interior_count']:3d}  "
            f"gaps={c['n_gaps']:2d}  {flag}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools/detect_membranes.py")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--r-membrane", type=float, default=None)
    parser.add_argument("--hollow-threshold", type=float, default=0.6)
    parser.add_argument("--sigma-threshold", type=float, default=0.20)
    parser.add_argument("--min-molecules", type=int, default=12)
    args = parser.parse_args(argv)

    world = load_snapshot(args.snapshot)
    candidates = detect_membranes(
        world,
        r_membrane=args.r_membrane,
        hollow_threshold=args.hollow_threshold,
        sigma_threshold=args.sigma_threshold,
        min_molecules=args.min_molecules,
    )
    if args.format == "json":
        print(json.dumps({"snapshot": str(args.snapshot), "candidates": candidates}, indent=2))
    else:
        print(format_text(args.snapshot, candidates))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
