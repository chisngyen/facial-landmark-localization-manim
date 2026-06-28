"""dot_morph — pure-numpy helpers for the 88-landmark 3b1b-style morph chain in shot03.

Each `make_target_*` returns a (88, 2) numpy array of (x, y) positions in
Manim frame units. No Manim imports at module top so the targets can be
unit-tested with stock Anaconda Python.

The face-canonical target maps `museum_tone.build_landmark_uv()` (which is in
UV [0,1] space) into a frame-space face mobject. The other six targets place
the 88 dots into shapes that *are* the icon — there is no separate "icon"
mobject anywhere in the redesign.
"""
from __future__ import annotations

import os, sys
import numpy as np

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import build_landmark_uv

N = 88


def make_target_face_canonical(face_center=(-3.5, 0.0), face_height=4.4) -> np.ndarray:
    """88 dots at landmark UVs mapped onto a face mobject. UVs come from
    Blender (`assets/face_3d_v3.blend`) projected through the active camera,
    plus procedural fillers — calibrated for `hero_front_v3.png`.
    """
    uvs = np.array(_LANDMARK_UV_V3)                              # (88, 2) in [0,1]
    w = face_height * (16.0 / 9.0)
    h = face_height
    cx, cy = face_center
    xs = cx + (uvs[:, 0] - 0.5) * w
    # UV v=0 is top of image; Manim y grows upward → flip
    ys = cy + (0.5 - uvs[:, 1]) * h
    return np.stack([xs, ys], axis=1).astype(np.float64)


# ---------------------------------------------------------------------------
# v3-hero-calibrated landmark UVs.
#
# 46 entries (indices 0–45) are exact projections of Blender objects
# LM_000..LM_045 from `assets/face_3d_v3.blend` through the active camera.
# 42 entries (indices 46–87) are procedurally placed fillers:
#   46–55   forehead arc (10 dots above brows)
#   56–67   mouth densification (12 dots interleaving the 10 real mouth pts)
#   68–75   jaw densification (8 dots between the 9 real jaw pts)
#   76–87   cheek + temple scatter (12 dots, 6 per side)
# Together they form a visually plausible 88-dot face that aligns with
# `hero_front_v3.png`. Re-derive if the Blender camera moves.
# ---------------------------------------------------------------------------

_LM_BLENDER_V3 = [
    # Eyes (0–7): 4 per eye, inner→outer
    (0.35526, 0.24895), (0.37615, 0.23842), (0.39883, 0.23875), (0.42193, 0.24992),
    (0.57807, 0.24992), (0.60117, 0.23875), (0.62385, 0.23842), (0.64474, 0.24895),
    # Brows (8–19): 6 per brow
    (0.42614, 0.28832), (0.41005, 0.29966), (0.36450, 0.30428), (0.34606, 0.29888),
    (0.36822, 0.26645), (0.41005, 0.27533),
    (0.65394, 0.29888), (0.63550, 0.30428), (0.58995, 0.29966), (0.57386, 0.28832),
    (0.58995, 0.27533), (0.63178, 0.26645),
    # Nose (20–26): bridge + tip + nostrils
    (0.50298, 0.28489), (0.50214, 0.34297), (0.50240, 0.40217), (0.50209, 0.46453),
    (0.46919, 0.47611), (0.53081, 0.47611), (0.50142, 0.49017),
    # Mouth (27–36): outer outline, 10 dots
    (0.54749, 0.65602), (0.53917, 0.66629), (0.51454, 0.67345), (0.48546, 0.67345),
    (0.46083, 0.66629), (0.45251, 0.65602), (0.46113, 0.64776), (0.48747, 0.64041),
    (0.51253, 0.64041), (0.53887, 0.64776),
    # Jaw (37–45): 9 dots from L jaw to chin to R jaw
    (0.35414, 0.62333), (0.37716, 0.71418), (0.41027, 0.77722), (0.45122, 0.81667),
    (0.50151, 0.83183), (0.54878, 0.81667), (0.58973, 0.77722), (0.62284, 0.71418),
    (0.64586, 0.62333),
]


def _procedural_fillers_v3():
    """42 procedural UVs (indices 46–87) that complement the 46 Blender landmarks.

    All placements are in the 16:9 hero frame's UV space [0,1]×[0,1] and were
    chosen by inspection of `hero_front_v3.png`:
      • Forehead arc sits above the brows (v ≈ 0.18–0.20).
      • Mouth densifiers interleave the 10 outer-outline mouth points with
        an inner row at v ≈ 0.660 (centerline between upper/lower lip).
      • Jaw densifiers sit midway between consecutive real jaw points.
      • Cheek/temple scatter avoids the eye and mouth regions.
    """
    pts = []
    # Forehead arc: 10 dots, u in [0.345, 0.655], v on a shallow downward arc.
    for i in range(10):
        t = i / 9.0
        u = 0.345 + 0.310 * t
        v = 0.195 - 0.015 * (1 - (2 * t - 1) ** 2)        # peak near center
        pts.append((u, v))
    # Mouth densification: 12 dots, two rows of 6 between the corner pts.
    for row, v in enumerate((0.655, 0.665)):
        for i in range(6):
            t = i / 5.0
            u = 0.460 + 0.080 * t
            pts.append((u, v))
    # Jaw densification: 8 dots between consecutive real jaw pts (37–45).
    jaw = _LM_BLENDER_V3[37:46]
    for i in range(8):
        a = jaw[i]; b = jaw[i + 1]
        pts.append(((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0))
    # Cheek/temple scatter: 6 per side, mid-cheek and temple.
    for side_u in (0.305, 0.695):
        # Mid-cheek column.
        for v in (0.420, 0.500, 0.580):
            pts.append((side_u, v))
        # Temple column slightly tighter.
        for v in (0.310, 0.380, 0.460):
            pts.append((side_u - 0.020 if side_u < 0.5 else side_u + 0.020, v))
    assert len(pts) == 42, len(pts)
    return pts


_LANDMARK_UV_V3 = _LM_BLENDER_V3 + _procedural_fillers_v3()
assert len(_LANDMARK_UV_V3) == 88, len(_LANDMARK_UV_V3)


def _face_landmarks_at(center, face_height=3.2, mouth_mood=0.0):
    """Map _LANDMARK_UV_V3 (88 UVs) to (88,2) at a frame-space center.

    `mouth_mood`:
        0   = neutral mouth (sketch target)
        +1  = upturned corners (smile)
        -1  = downturned corners (frown)

    The deformation lifts/drops mouth indices proportional to (u−0.5)².
    Real mouth indices are 27–36; procedural densifiers 56–67.
    """
    uvs = np.array(_LANDMARK_UV_V3, dtype=np.float64).copy()
    if mouth_mood != 0.0:
        mouth_idx = list(range(27, 37)) + list(range(56, 68))
        for i in mouth_idx:
            u, v = uvs[i]
            du = u - 0.500
            # 0.06 = corner-lift magnitude in UV space; normalizes by du²/0.0025
            # so a point at the mouth corner (|du|≈0.05) gets the full lift.
            uvs[i, 1] = v - mouth_mood * 0.06 * (du * du / 0.0025)
    w = face_height * (16.0 / 9.0)
    h = face_height
    cx, cy = center
    xs = cx + (uvs[:, 0] - 0.5) * w
    ys = cy + (0.5 - uvs[:, 1]) * h
    return np.stack([xs, ys], axis=1).astype(np.float64)


def match_targets(src_pts: np.ndarray, dst_pts: np.ndarray) -> np.ndarray:
    """Greedy nearest-neighbor permutation so dot i in `src` maps to one
    unused dot in `dst` that's closest. Returns int array `perm` such that
    src[i] should animate to dst[perm[i]].

    Greedy is O(n^2) which is fine for n=88. The Hungarian algorithm would
    be optimal but adds a scipy dep we don't need.
    """
    assert src_pts.shape == dst_pts.shape == (N, 2)
    perm = np.full(N, -1, dtype=np.int64)
    used = np.zeros(N, dtype=bool)
    # Iterate src in a deterministic order; visit src points whose nearest
    # available dst is furthest away FIRST (those are most constrained).
    order = np.argsort(-np.min(np.linalg.norm(
        src_pts[:, None, :] - dst_pts[None, :, :], axis=2), axis=1))
    for i in order:
        dists = np.linalg.norm(dst_pts - src_pts[i], axis=1)
        dists[used] = np.inf
        j = int(np.argmin(dists))
        perm[i] = j
        used[j] = True
    assert (perm >= 0).all()
    return perm


def make_target_id_card(center=(3.0, 0.0)) -> np.ndarray:
    """ID-card target: 88 dots forming a portrait-card outline + mini-face
    oval + barcode strip + corner crops + filler ID-detail dots.

    Allocation: 40 rect perimeter + 12 mini-face oval + 18 barcode + 8 corner
    crops + 10 detail-line filler = 88.
    """
    cx, cy = center
    pts = []
    # 40 dots on a 2.0 wide × 2.8 tall portrait rectangle perimeter.
    # 10 per side, clockwise from top-left corner inclusive.
    for i in range(10):
        t = i / 10.0
        pts.append((cx - 1.0 + 2.0 * t, cy + 1.4))               # top
    for i in range(10):
        t = i / 10.0
        pts.append((cx + 1.0, cy + 1.4 - 2.8 * t))               # right
    for i in range(10):
        t = i / 10.0
        pts.append((cx + 1.0 - 2.0 * t, cy - 1.4))               # bottom
    for i in range(10):
        t = i / 10.0
        pts.append((cx - 1.0, cy - 1.4 + 2.8 * t))               # left
    # 12 dots: mini-face oval in upper half, centered (cx, cy+0.5),
    # rx=0.35, ry=0.45.
    for i in range(12):
        theta = i * (2 * np.pi / 12)
        pts.append((cx + 0.35 * np.cos(theta), cy + 0.5 + 0.45 * np.sin(theta)))
    # 18 dots: barcode-strip row at y = cy - 1.0, spread x in [-0.6, +0.6].
    for i in range(18):
        t = i / 17.0
        pts.append((cx - 0.6 + 1.2 * t, cy - 1.0))
    # 8 dots: corner crop ticks (2 per corner, L-shape stub).
    corners = [(-1.0, +1.4), (+1.0, +1.4), (+1.0, -1.4), (-1.0, -1.4)]
    for dx, dy in corners:
        sx = -np.sign(dx); sy = -np.sign(dy)
        pts.append((cx + dx + 0.12 * sx, cy + dy))
        pts.append((cx + dx, cy + dy + 0.12 * sy))
    # 10 dots: detail-line filler in lower half (mock text lines).
    for i in range(10):
        row = i // 5                                              # 0 or 1
        col = i % 5
        pts.append((cx - 0.55 + col * 0.275, cy - 0.4 - row * 0.20))
    pts = np.array(pts, dtype=np.float64)
    assert pts.shape == (N, 2), f"id_card got {pts.shape}"
    return pts


def make_target_mesh3d(center=(3.0, 0.0), tilt_deg=15.0) -> np.ndarray:
    """3D-wireframe-egg target: 88 dots = 24 silhouette ellipse + 3 latitude
    rings (24 dots) + 3 longitude arcs (24 dots) + 16 cross-point filler.
    All rotated by `tilt_deg` to suggest 3D.
    """
    cx, cy = center
    rx, ry = 1.05, 1.40                                          # egg half-extents
    phi = np.deg2rad(tilt_deg)
    cosp, sinp = np.cos(phi), np.sin(phi)
    def rot(p):
        x, y = p
        return (cosp * x - sinp * y + cx, sinp * x + cosp * y + cy)
    pts = []
    # Silhouette ellipse: 24 dots.
    for i in range(24):
        theta = i * (2 * np.pi / 24)
        pts.append(rot((rx * np.cos(theta), ry * np.sin(theta))))
    # 3 horizontal latitude rings at y = -0.7, 0.0, +0.7. Each ring 8 dots
    # on an ellipse whose width tapers near the poles.
    for y0 in (-0.7, 0.0, +0.7):
        taper = (1.0 - (y0 / ry) ** 2) ** 0.5                    # narrower near top/bottom
        ring_rx = rx * taper
        for i in range(8):
            theta = i * (2 * np.pi / 8)
            pts.append(rot((ring_rx * np.cos(theta), y0)))
    # 3 vertical longitude arcs at x_offsets = -0.6, 0.0, +0.6. Each arc 8 dots.
    for x0 in (-0.6, 0.0, +0.6):
        taper = (1.0 - (x0 / rx) ** 2) ** 0.5
        arc_ry = ry * taper
        for i in range(8):
            t = -1 + 2 * i / 7
            pts.append(rot((x0, arc_ry * t)))
    # 16 cross-point filler: 4×4 grid inside the egg.
    for i in range(4):
        for j in range(4):
            x0 = -0.45 + i * 0.30
            y0 = -0.60 + j * 0.40
            pts.append(rot((x0, y0)))
    pts = np.array(pts, dtype=np.float64)
    assert pts.shape == (N, 2), f"mesh3d got {pts.shape}"
    return pts


def make_target_sketch(center=(3.0, 0.0)) -> np.ndarray:
    """Sketch target: face landmarks at `center`, neutral mouth. The scene
    recolors the dots WHITE so the result reads as pen-and-ink line work
    laid out exactly like the actual face geometry.
    """
    pts = _face_landmarks_at(center, face_height=3.2, mouth_mood=0.0)
    assert pts.shape == (N, 2)
    return pts


def make_target_pose_triad(center=(3.0, 0.0)) -> np.ndarray:
    """Pose-estimation target: 88 dots = 4 origin + 3 arrows × (24 shaft + 4
    head) = 4 + 84 = 88.

    Arrows: X right (+1.4, 0), Y up (0, +1.4), Z diagonal forward
    (+0.9, +0.6) to suggest a 3D triad on a 2D frame.

    Colors are NOT set here — `dot_morph.py` is pure numpy. The scene sets
    per-arrow colors after the morph using the slicing convention documented
    in the docstring (see scene code).
    """
    cx, cy = center
    pts = []
    # Origin: 4 dots in a tight diamond (single visual point).
    for dx, dy in [(0.0, 0.0), (0.04, 0.04), (-0.04, 0.04), (0.0, -0.05)]:
        pts.append((cx + dx, cy + dy))
    # Clean arrow: 20 shaft dots evenly spaced + 8 head dots forming a
    # proper triangle (4 per edge, V-shape converging to the tip).
    def arrow(tip):
        out = []
        tx, ty = tip
        L = (tx ** 2 + ty ** 2) ** 0.5
        ux, uy = tx / L, ty / L                                  # unit direction
        nx, ny = -uy, ux                                         # left normal
        # Shaft: 20 dots evenly spaced from 18% to 74% of length (less clump at origin)
        for i in range(20):
            t = 0.18 + (i / 19.0) * 0.56
            out.append((cx + tx * t, cy + ty * t))
        # Arrowhead: V-triangle. 4 levels from base (t=0.74) to tip (t=1.0),
        # widening from 0 at tip to 0.18 at base. 2 dots per level (left/right).
        for i in range(4):
            t      = 1.0 - (i / 3.0) * 0.26                      # 1.0 → 0.74
            width  = (i / 3.0) * 0.18                            # 0 → 0.18
            for sign in (+1, -1):
                out.append((cx + tx * t + nx * width * sign,
                            cy + ty * t + ny * width * sign))
        return out
    pts += arrow((+1.6, 0.0))                                    # X (red,  →)
    pts += arrow((0.0, +1.6))                                    # Y (green, ↑)
    pts += arrow((+1.0, +0.7))                                   # Z (blue, depth ↗)
    pts = np.array(pts, dtype=np.float64)
    assert pts.shape == (N, 2), f"pose_triad got {pts.shape}"
    return pts


# Slicing convention used by the scene to recolor the triad:
#   origin = pts[0:4],  X = pts[4:32],  Y = pts[32:60],  Z = pts[60:88]
POSE_TRIAD_SLICES = dict(origin=(0, 4), x=(4, 32), y=(32, 60), z=(60, 88))


def make_target_smile(center=(3.0, 0.0), mood=+1.0) -> np.ndarray:
    """Expression target: same face landmarks as the sketch target, but
    mouth indices deformed by `mood` to form a smile (+1) or frown (-1).
    The rest of the face stays still, so the smile→frown→smile micro-cycle
    reads as the SAME face changing expression — not a different shape.
    """
    pts = _face_landmarks_at(center, face_height=3.2, mouth_mood=float(mood))
    assert pts.shape == (N, 2)
    return pts


def make_target_beauty_glow(center=(3.0, 0.0)) -> np.ndarray:
    """Beauty-glow target: 17 jaw-arc (smooth parabola) + 12 eye circles
    (2 × 6) + 59 halo cloud forming a ring around the silhouette = 88.
    """
    cx, cy = center
    pts = []
    # Smooth jaw arc: 17 dots along a downward-opening parabola from
    # (-1.0, +0.2) down to (0, -1.2) up to (+1.0, +0.2).
    for i in range(17):
        t = -1 + 2 * i / 16
        x = 1.0 * t
        y = +0.2 - 1.4 * (1 - t ** 2)
        pts.append((cx + x, cy + y))
    # Two eye circles, 6 dots each. Centers at (-0.45, +0.40) and (+0.45, +0.40).
    for side in (-1, +1):
        for i in range(6):
            theta = i * (2 * np.pi / 6)
            pts.append((cx + side * 0.45 + 0.18 * np.cos(theta),
                        cy + 0.40 + 0.18 * np.sin(theta)))
    # Halo cloud: 59 dots in a ring around the silhouette, radius 1.30 to 1.55.
    rng = np.random.default_rng(2026)
    for i in range(59):
        theta = i * (2 * np.pi / 59) + rng.uniform(-0.03, 0.03)
        r = 1.30 + 0.25 * rng.uniform(0, 1)
        pts.append((cx + r * np.cos(theta), cy + r * np.sin(theta)))
    pts = np.array(pts, dtype=np.float64)
    assert pts.shape == (N, 2), f"beauty got {pts.shape}"
    return pts


def morph_dots(scene, dot_group, target_pts, run_time=1.0, lag=0.015):
    """Animate a VGroup of N Dot mobjects toward `target_pts` ((N,2) numpy).
    Uses `match_targets` to pair each source dot with its nearest target so
    paths don't cross.

    Manim-only import lives inside this function so the rest of the module
    stays Manim-free for unit tests.
    """
    from manimlib import LaggedStart
    import numpy as np
    assert len(dot_group.submobjects) == N
    src = np.array([d.get_center()[:2] for d in dot_group.submobjects])
    perm = match_targets(src, target_pts)
    anims = []
    for i, d in enumerate(dot_group.submobjects):
        tgt = np.array([target_pts[perm[i]][0], target_pts[perm[i]][1], 0.0])
        anims.append(d.animate.move_to(tgt))
    scene.play(LaggedStart(*anims, lag_ratio=lag), run_time=run_time)
