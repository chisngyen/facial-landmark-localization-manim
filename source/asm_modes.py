"""asm_modes — pure-numpy helpers for the shot05 Active Shape Model walk-through.

4 hand-designed deformation modes that behave like the first 4 eigenmodes of a
face PCA model: width, height, smile, brow-lift. No Manim imports at module top.
"""
from __future__ import annotations

import os, sys
import numpy as np

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from dot_morph import _LANDMARK_UV_V3

N = 88
FACE_HEIGHT = 4.0


def _uv_to_centered_xy(face_height=FACE_HEIGHT):
    uvs = np.array(_LANDMARK_UV_V3, dtype=np.float64)
    w = face_height * (16.0 / 9.0)
    h = face_height
    xs = (uvs[:, 0] - 0.5) * w
    ys = (0.5 - uvs[:, 1]) * h
    return np.stack([xs, ys], axis=1)


MEAN_SHAPE_88 = _uv_to_centered_xy(FACE_HEIGHT)
assert MEAN_SHAPE_88.shape == (N, 2)


def apply_mode_1_width(pts: np.ndarray, b: float) -> np.ndarray:
    out = np.array(pts, dtype=np.float64).copy()
    out[:, 0] *= (1.0 + 0.18 * b)
    return out


def apply_mode_2_height(pts: np.ndarray, b: float) -> np.ndarray:
    out = np.array(pts, dtype=np.float64).copy()
    out[:, 1] *= (1.0 + 0.15 * b)
    return out


_MOUTH_IDX = list(range(27, 37)) + list(range(56, 68))
_BROW_IDX = list(range(8, 20))


def apply_mode_3_smile(pts: np.ndarray, b: float) -> np.ndarray:
    out = np.array(pts, dtype=np.float64).copy()
    w = FACE_HEIGHT * (16.0 / 9.0)
    for i in _MOUTH_IDX:
        u = out[i, 0] / w + 0.5
        du = u - 0.5
        dy_uv = -b * 0.06 * (du * du / 0.0025)
        out[i, 1] += dy_uv * (-FACE_HEIGHT)
    return out


def apply_mode_4_brow(pts: np.ndarray, b: float) -> np.ndarray:
    out = np.array(pts, dtype=np.float64).copy()
    for i in _BROW_IDX:
        out[i, 1] += b * 0.08
    return out


def apply_all_modes(pts: np.ndarray, b_vec) -> np.ndarray:
    out = np.array(pts, dtype=np.float64).copy()
    b1, b2, b3, b4 = b_vec
    out = apply_mode_1_width(out, b1)
    out = apply_mode_2_height(out, b2)
    out = apply_mode_3_smile(out, b3)
    out = apply_mode_4_brow(out, b4)
    return out
