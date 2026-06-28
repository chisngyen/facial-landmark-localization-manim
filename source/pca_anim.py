"""pca_anim — pure-numpy helpers for the shot03_5 PCA walk-through.

No Manim imports at module top so the helpers stay unit-testable.
"""
from __future__ import annotations

import numpy as np


# Five hand-tuned 3D points. λ₁ ≈ 2.38 dominates λ₂ ≈ 0.73, so the principal
# axis is visually unambiguous and the power-iteration sequence converges in
# about 5 steps from a generic random init.
TOY_POINTS_3D = np.array([
    ( 1.2,  0.3,  0.7),
    (-1.1, -0.4,  0.5),
    ( 0.8, -0.2, -0.6),
    (-0.5,  0.6, -0.3),
    ( 1.0,  0.5,  1.0),
])

# Initial violet candidate vector for power iteration. Hand-picked so the
# first iterate visibly rotates rather than already pointing near p₁.
V0_INIT = np.array([0.20, 0.95, 0.25])
V0_INIT = V0_INIT / np.linalg.norm(V0_INIT)


def project_iso(p3d: np.ndarray) -> np.ndarray:
    """Project a (3,) or (N,3) world point to (2,) or (N,2) Manim-frame coords.

    Simple isometric: x' = x + 0.30·z, y' = y + 0.45·z. Matches the rotation
    used by the 3D plane in `Section01_Shot03_5_PCA_Math_v2` (≈ 70° around RIGHT).
    """
    p3d = np.asarray(p3d, dtype=np.float64)
    if p3d.ndim == 1:
        x, y, z = p3d
        return np.array([x + 0.30 * z, y + 0.45 * z], dtype=np.float64)
    xs = p3d[:, 0] + 0.30 * p3d[:, 2]
    ys = p3d[:, 1] + 0.45 * p3d[:, 2]
    return np.stack([xs, ys], axis=1)


def compute_covariance(pts: np.ndarray):
    """Return (mean, residuals, outer_products, C, eigvals, eigvecs).

    `pts` is (N, 3). Mean is (3,). residuals is (N, 3). outer_products is
    a list of (3, 3) per-sample (x_i − x̄)(x_i − x̄)ᵀ. C is the sample mean
    of those outer products (1/N · Σ). Eigvals sorted DESCENDING; eigvecs
    columns aligned to eigvals.
    """
    pts = np.asarray(pts, dtype=np.float64)
    mean = pts.mean(axis=0)
    residuals = pts - mean
    outer_products = [np.outer(r, r) for r in residuals]
    C = sum(outer_products) / len(outer_products)
    eigvals, eigvecs = np.linalg.eigh(C)
    # eigh returns ascending — flip to descending.
    order = np.argsort(-eigvals)
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    return mean, residuals, outer_products, C, eigvals, eigvecs


def power_iterate(C: np.ndarray, v0: np.ndarray, n_iters: int = 5):
    """Return the list [v0, v1, …, v_n_iters] of unit vectors from the
    power iteration v ← C·v / |C·v|.

    The list has length n_iters + 1 so the caller can animate n_iters arrow
    transitions (from v_k to v_{k+1}).
    """
    iterates = [v0 / np.linalg.norm(v0)]
    v = iterates[0].copy()
    for _ in range(n_iters):
        Cv = C @ v
        v = Cv / np.linalg.norm(Cv)
        iterates.append(v.copy())
    return iterates


def format_matrix_3x3(M: np.ndarray, decimals: int = 2) -> list[str]:
    """Format a (3, 3) matrix into 3 monospaced row strings with signs and
    a fixed cell width. Returns ['[ +1.99  +0.66  +0.38 ]', …] etc.
    """
    M = np.asarray(M, dtype=np.float64)
    assert M.shape == (3, 3), M.shape
    lines = []
    for row in M:
        cells = [f"{v:+.{decimals}f}" for v in row]
        lines.append("[ " + "  ".join(cells) + " ]")
    return lines
