"""
Shared museum-tone palette + helpers for the Chapter 12 redesign.

All shots import from here so tone stays consistent
— changing a colour here changes every shot.
"""
from manimlib import *

import os
import pathlib

# --- Palette ---
TONE_BG_TOP = "#0e0e12"
TONE_BG_BOT = "#1a1a22"
TONE_CYAN = "#5fc9f8"
TONE_AMBER = "#ffb347"
TONE_RED = "#ff6060"
TONE_GREY = "#6a6a78"
TONE_FG = "#e8e9ef"
TONE_MUTED = "#8c8c9a"

FONT = "Cascadia Mono"   # Monospace typewriter font for consistent code/math feel across all shots

# --- Premium typography (editorial upgrade, source_premium only) ---
FONT_DISPLAY = "Cambria"   # refined serif for hero titles → editorial contrast vs the mono body
FONT_SANS = "Corbel"       # humanist sans for prose/questions — cleaner than mono for reading

# --- Paths ---
# Re-use mannequin renders as the chapter-wide asset family
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS_DIR = _PROJECT_ROOT / "assets" / "shot03v2"
BG_GRADIENT_PNG = str(ASSETS_DIR / "bg_gradient.png")

# v3 hero set rendered from face_3d_v3.blend (region-aware shader + 68 landmark spheres parented to head).
# Set USE_V3 = False to revert to original kuuttisiitonen renders.
USE_V3 = True
_V3 = "_v3" if USE_V3 else ""

HERO_FRONTAL = str(ASSETS_DIR / f"hero_frontal_alpha{_V3}.png")
HERO_POSE_YAW30 = str(ASSETS_DIR / "hero_pose_yaw30.png")
HERO_POSE_PITCH15 = str(ASSETS_DIR / "hero_pose_pitch15.png")
HERO_LIGHTING_SIDE = str(ASSETS_DIR / "hero_lighting_side.png")
HERO_EYE_CLOSEUP = str(ASSETS_DIR / "hero_eye_closeup.png")       # rendered in scope 3
HERO_WITH_BBOX = str(ASSETS_DIR / "hero_with_bbox.png")           # rendered in scope 3
HERO_WITH_LANDMARKS = str(ASSETS_DIR / "hero_with_landmarks.png") # rendered in scope 3
HERO_EYE_GLOW = str(ASSETS_DIR / f"hero_eye_glow{_V3}.png")             # amber-emissive eye (Beat 1 zoom peak)
HERO_EYE_CLOSEUP_GLOW = str(ASSETS_DIR / "hero_eye_closeup_glow.png")  # tight eye close-up with glow
HERO_WITH_LANDMARKS_BAKED = str(ASSETS_DIR / f"hero_frontal_with_landmarks{_V3}.png")  # 68 emissive spheres parented to head (v3) or 88 amber spheres baked (orig)
HERO_WITH_LANDMARKS_GLOW = str(ASSETS_DIR / f"hero_frontal_with_landmarks_glow{_V3}.png")  # landmarks + eye glow
HERO_TURNTABLE_DIR = ASSETS_DIR / "hero_turntable"
MORPH_PATHS = [str(ASSETS_DIR / f"morph_{i}.png") for i in range(8)]
LERP_PATHS = [str(ASSETS_DIR / "morph_lerp_b1" / f"frame_{i:02d}.png") for i in range(21)]

# v3 variety set — different angles + close-ups so we don't reuse one image to death
HERO_FRONT_V3       = str(ASSETS_DIR / "hero_front_v3.png")
HERO_YAW30_V3       = str(ASSETS_DIR / "hero_yaw30_v3.png")
HERO_YAW_NEG30_V3   = str(ASSETS_DIR / "hero_yaw_neg30_v3.png")
HERO_PROFILE_R_V3   = str(ASSETS_DIR / "hero_profile_R_v3.png")
HERO_3Q_V3          = str(ASSETS_DIR / "hero_3q_v3.png")
HERO_LOOKUP_V3      = str(ASSETS_DIR / "hero_lookup_v3.png")
HERO_EYE_MACRO_V3   = str(ASSETS_DIR / "hero_eye_macro_v3.png")
HERO_EYE_MACRO_GLOW_V3 = str(ASSETS_DIR / "hero_eye_macro_glow_v3.png")
HERO_MOUTH_MACRO_V3 = str(ASSETS_DIR / "hero_mouth_macro_v3.png")
HERO_JAW_MACRO_V3   = str(ASSETS_DIR / "hero_jaw_macro_v3.png")

# Sway sequences (60 frames each, 30fps → 2s loop)
HERO_SWAY_NORMAL_DIR    = str(ASSETS_DIR / "hero_sway_normal")
HERO_SWAY_LANDMARKS_DIR = str(ASSETS_DIR / "hero_sway_landmarks")
HERO_SWAY_FRAMES = 60

# Shot01 hook turntable: 360 frames @ 30fps = 12.0s, face with 46 landmark dots
# appearing in 5 anatomical waves (forehead/temples/eyes-nose/mouth-chin/jaw).
HOOK_FRAMES_DIR = str(_PROJECT_ROOT / "assets" / "shot01v3" / "hook_frames")
HOOK_FRAMES_COUNT = 360

# Face feature UV coordinates inside the active hero base image.
# v3 renders are reframed (different camera) so UVs differ from the original set.
if USE_V3:
    # Hand-tuned against hero_frontal_alpha_v3.png — matches shot10's working
    # _v3_landmark_template anchors. Earlier values (eye too central, mouth too high)
    # placed the ring between nose and lips; corrected here.
    FACE_EYE_L_UV = (0.390, 0.290)
    FACE_EYE_R_UV = (0.610, 0.290)
    FACE_NOSE_UV  = (0.500, 0.470)
    FACE_MOUTH_UV = (0.500, 0.660)
else:
    FACE_EYE_L_UV = (0.408, 0.225)
    FACE_EYE_R_UV = (0.548, 0.217)
    FACE_NOSE_UV = (0.500, 0.420)
    FACE_MOUTH_UV = (0.500, 0.520)
HERO_MANIM_H = 5.0

# Vertical offset applied to all landmark UVs (used inside build_landmark_uv)
# — shifts the canonical template down to the new face's eye/mouth positions.
_LANDMARK_Y_SHIFT = 0.08


# --- Helpers ---

def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def ensure_atmosphere_bg(accent="amber", cache_key=None):
    """Render an atmospheric bg PNG: top→bottom gradient + radial spotlight in accent color
    + vignette darkening. Returns the PNG path. Cached so each shot gets called once."""
    accent_map = {
        "amber": ("#2d2218", "#0e0e12", (0.50, 0.50), 0.28),  # centered + soft spotlight
        "cyan":  ("#152633", "#0e0e12", (0.60, 0.30), 0.55),  # cool spotlight upper-right
        "red":   ("#2c1517", "#0e0e12", (0.50, 0.50), 0.45),
        "violet":("#251c33", "#0e0e12", (0.50, 0.50), 0.50),
        "neutral":("#1a1a22","#0e0e12", (0.50, 0.50), 0.40),
    }
    top_hex, bot_hex, focus, halo_strength = accent_map.get(accent, accent_map["neutral"])
    key = cache_key or accent
    out_path = str(ASSETS_DIR / f"bg_atm_{key}.png")
    if os.path.exists(out_path):
        return out_path
    try:
        from PIL import Image
        import numpy as _np
        H, W = 540, 960
        top = _np.array(_hex_to_rgb(top_hex), dtype=_np.float32)
        bot = _np.array(_hex_to_rgb(bot_hex), dtype=_np.float32)
        ramp = _np.linspace(0, 1, H, dtype=_np.float32)[:, None]
        arr = (top[None, None, :] * (1 - ramp[:, :, None]) +
               bot[None, None, :] * ramp[:, :, None])
        arr = _np.broadcast_to(arr, (H, W, 3)).astype(_np.float32).copy()
        # Radial spotlight (accent halo)
        ys, xs = _np.mgrid[0:H, 0:W].astype(_np.float32)
        cx, cy = focus[0] * W, focus[1] * H
        r = _np.sqrt((xs - cx)**2 + (ys - cy)**2)
        r_norm = r / (W * 0.55)
        halo = _np.exp(-(r_norm**2) * 1.8) * halo_strength
        halo_color = top * 1.4
        arr += halo[:, :, None] * (halo_color - arr) * 0.6
        # Vignette: darken edges
        ys2, xs2 = _np.mgrid[0:H, 0:W].astype(_np.float32)
        dx = (xs2 - W/2) / (W/2); dy = (ys2 - H/2) / (H/2)
        vig = 1.0 - 0.40 * _np.clip(_np.sqrt(dx**2 + dy**2) - 0.55, 0, 1.0)
        arr *= vig[:, :, None]
        arr = _np.clip(arr, 0, 255).astype(_np.uint8)
        # Subtle noise / grain
        grain = (_np.random.RandomState(7).randn(H, W, 1) * 2.5).astype(_np.int16)
        arr = _np.clip(arr.astype(_np.int16) + grain, 0, 255).astype(_np.uint8)
        Image.fromarray(arr).save(out_path)
        return out_path
    except Exception as e:
        return None


def ensure_premium_bg(accent="amber", cache_key=None):
    """Refined near-black atmosphere for the premium pass: deep vertical gradient
    + a soft off-center accent glow + strong vignette + fine grain. Rendered at
    1080p and kept subtle so text stays crisp. Cached per accent."""
    accent_glow = {
        "amber":  ((255, 179, 71),  (0.50, 0.74), 0.11),   # warm, low + centered
        "cyan":   ((95, 201, 248),  (0.66, 0.30), 0.10),
        "violet": ((150, 120, 220), (0.50, 0.30), 0.10),
        "red":    ((255, 96, 96),   (0.50, 0.42), 0.10),
        "neutral":((120, 120, 140), (0.50, 0.50), 0.07),
    }
    glow_rgb, focus, strength = accent_glow.get(accent, accent_glow["neutral"])
    key = cache_key or accent
    out_path = str(ASSETS_DIR / f"bg_premium_{key}.png")
    if os.path.exists(out_path):
        return out_path
    try:
        from PIL import Image
        import numpy as _np
        H, W = 1080, 1920
        top = _np.array((10, 10, 14), dtype=_np.float32)
        bot = _np.array((20, 20, 28), dtype=_np.float32)
        ramp = _np.linspace(0, 1, H, dtype=_np.float32)[:, None, None]
        arr = top[None, None, :] * (1 - ramp) + bot[None, None, :] * ramp
        arr = _np.broadcast_to(arr, (H, W, 3)).astype(_np.float32).copy()
        ys, xs = _np.mgrid[0:H, 0:W].astype(_np.float32)
        cx, cy = focus[0] * W, focus[1] * H
        r = _np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) / (W * 0.60)
        glow = _np.exp(-(r ** 2) * 2.2) * strength
        arr += glow[:, :, None] * _np.array(glow_rgb, dtype=_np.float32)[None, None, :]
        dx = (xs - W / 2) / (W / 2)
        dy = (ys - H / 2) / (H / 2)
        vig = 1.0 - 0.55 * _np.clip(_np.sqrt(dx ** 2 + dy ** 2) - 0.35, 0, 1.0)
        arr *= vig[:, :, None]
        arr = _np.clip(arr, 0, 255)
        grain = _np.random.RandomState(11).randn(H, W, 1) * 2.0
        arr = _np.clip(arr + grain, 0, 255).astype(_np.uint8)
        Image.fromarray(arr).save(out_path)
        return out_path
    except Exception:
        return None


def ensure_tech_backdrop(cache_key="tech_cyan", focus=(0.62, 0.50),
                         glow_rgb=(60, 150, 210), strength=0.16):
    """Designed cinematic backdrop for the BOLD pass: near-black + a cool cyan
    radial light (off-center, behind the hero) + vignette + grain. Grid lines are
    drawn live in-scene (so they can drift), not baked here. 1080p, cached."""
    out_path = str(ASSETS_DIR / f"bg_{cache_key}.png")
    if os.path.exists(out_path):
        return out_path
    try:
        from PIL import Image
        import numpy as _np
        H, W = 1080, 1920
        base = _np.array((8, 8, 12), dtype=_np.float32)
        arr = _np.broadcast_to(base, (H, W, 3)).astype(_np.float32).copy()
        ys, xs = _np.mgrid[0:H, 0:W].astype(_np.float32)
        cx, cy = focus[0] * W, focus[1] * H
        r = _np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2) / (W * 0.55)
        glow = _np.exp(-(r ** 2) * 1.6) * strength
        arr += glow[:, :, None] * _np.array(glow_rgb, dtype=_np.float32)[None, None, :]
        dx = (xs - W / 2) / (W / 2)
        dy = (ys - H / 2) / (H / 2)
        vig = 1.0 - 0.50 * _np.clip(_np.sqrt(dx ** 2 + dy ** 2) - 0.40, 0, 1.0)
        arr *= vig[:, :, None]
        arr = _np.clip(arr, 0, 255)
        grain = _np.random.RandomState(5).randn(H, W, 1) * 2.0
        arr = _np.clip(arr + grain, 0, 255).astype(_np.uint8)
        Image.fromarray(arr).save(out_path)
        return out_path
    except Exception:
        return None


def ensure_bg_gradient_png():
    """Back-compat: redirect to atmospheric neutral bg."""
    return ensure_atmosphere_bg("neutral")


def museum_bg(accent="neutral"):
    """Atmospheric bg with optional accent halo. Falls back to flat fill if PIL missing."""
    png = ensure_atmosphere_bg(accent)
    if png and os.path.exists(png):
        img = ImageMobject(png)
        img.set_height(FRAME_HEIGHT * 1.02)
        img.set_width(FRAME_WIDTH * 1.02, stretch=True)
        return img
    rect = Rectangle(width=FRAME_WIDTH * 1.02, height=FRAME_HEIGHT * 1.02)
    rect.set_stroke(width=0).set_fill("#131319", 1.0)
    return rect


def m_text(txt, scale=0.5, color=None, font=FONT):
    """Plain Text with explicit fill color (no backstroke — cleanest rendering)."""
    t = Text(txt, font=font)
    t.scale(scale)
    t.set_fill(color if color is not None else TONE_FG, 1.0)
    t.set_stroke(width=0)
    return t


def soft_glow(mob, color=TONE_AMBER, layers=4, base_width=2.0, spread=6.0,
              max_opacity=0.13):
    """Fake bloom: stacked low-opacity stroked copies behind a text/vector mob.

    Gives titles a soft accent halo without any blur pass (ManimGL has none).
    Returned VGroup is meant to sit *behind* the original mob.
    """
    g = VGroup()
    for i in range(layers):
        c = mob.copy()
        c.set_fill(opacity=0)
        c.set_stroke(color, width=base_width + i * spread,
                     opacity=max_opacity * (1 - i / max(1, layers)))
        g.add(c)
    return g


def m_title(txt, scale=0.8, color=None, font=FONT_DISPLAY, glow=True,
            glow_color=None, weight=NORMAL):
    """Editorial display title (serif by default) with an optional soft bloom.

    Returns a VGroup(halo, text) when glow=True, else a plain Text. The VGroup
    still supports .scale/.set_opacity/.to_edge/.next_to and FadeIn/FadeOut, but
    do NOT feed it to typewriter_anim (that iterates submobjects as characters).
    """
    color = color if color is not None else TONE_FG
    t = Text(txt, font=font, weight=weight)
    t.scale(scale)
    t.set_fill(color, 1.0)
    t.set_stroke(width=0)
    if not glow:
        return t
    glow_color = glow_color if glow_color is not None else color
    halo = soft_glow(t, color=glow_color)
    return VGroup(halo, t)


def m_body(txt, scale=0.5, color=None, font=FONT_SANS):
    """Humanist-sans prose helper (plain Text → safe for typewriter_anim)."""
    color = color if color is not None else TONE_FG
    t = Text(txt, font=font)
    t.scale(scale)
    t.set_fill(color, 1.0)
    t.set_stroke(width=0)
    return t


def hairline(p1, p2, color=TONE_AMBER, width=1.6, glow=True):
    """Thin divider with a faint wider glow underneath for depth."""
    line = Line(np.array(p1, dtype=float), np.array(p2, dtype=float))
    line.set_stroke(color, width, opacity=0.9)
    if not glow:
        return line
    halo = Line(np.array(p1, dtype=float), np.array(p2, dtype=float))
    halo.set_stroke(color, width * 5, opacity=0.10)
    return VGroup(halo, line)


def museum_head(image_path=HERO_FRONTAL, height=HERO_MANIM_H):
    img = ImageMobject(image_path)
    img.set_height(height)
    return img


def amber_dot(pos, radius=0.040):
    return Dot(point=pos, radius=radius).set_fill(TONE_AMBER, 1.0).set_stroke(width=0)


def cyan_dot(pos, radius=0.055):
    return Dot(point=pos, radius=radius).set_fill(TONE_CYAN, 1.0).set_stroke(width=0)


def hud_corners(mob, arm=0.35, buff=0.18, stroke_w=4.0, color=None, width=None, height=None):
    """Corner brackets around a mobject (HUD style).

    If `width` / `height` are explicitly provided, they override the default (based on
    mobject bbox + buff). Useful for ImageMobjects whose bbox includes transparent alpha
    padding wider than the visible subject.
    """
    color = color if color is not None else TONE_CYAN
    w = width if width is not None else (mob.get_width() + 2 * buff)
    h = height if height is not None else (mob.get_height() + 2 * buff)
    cx, cy, _ = mob.get_center()
    corners = VGroup()
    for dx in (-1, 1):
        for dy in (-1, 1):
            x = cx + dx * w / 2
            y = cy + dy * h / 2
            corners.add(Line(
                np.array([x - dx * arm, y, 0]),
                np.array([x, y, 0])
            ).set_stroke(color, stroke_w))
            corners.add(Line(
                np.array([x, y - dy * arm, 0]),
                np.array([x, y, 0])
            ).set_stroke(color, stroke_w))
    return corners


def dashed_rect(center, width, height, color, n_dashes=24, stroke_w=4.0):
    """Dashed rectangle via 4 DashedLines."""
    hw = width / 2
    hh = height / 2
    cx, cy, cz = center
    corners = [
        (np.array([cx - hw, cy - hh, cz]), np.array([cx + hw, cy - hh, cz])),
        (np.array([cx + hw, cy - hh, cz]), np.array([cx + hw, cy + hh, cz])),
        (np.array([cx + hw, cy + hh, cz]), np.array([cx - hw, cy + hh, cz])),
        (np.array([cx - hw, cy + hh, cz]), np.array([cx - hw, cy - hh, cz])),
    ]
    group = VGroup()
    for a, b in corners:
        dl = DashedLine(a, b, dash_length=0.12, positive_space_ratio=0.55)
        dl.set_stroke(color, stroke_w)
        group.add(dl)
    return group


def uv_to_manim(uv, hero_img):
    """Convert UV (0..1 top-left origin) in hero image to Manim world coords."""
    w = hero_img.get_width()
    h = hero_img.get_height()
    center = hero_img.get_center()
    u, v = uv
    x = center[0] + (u - 0.5) * w
    y = center[1] + (0.5 - v) * h
    return np.array([x, y, 0.0])


def build_landmark_uv():
    """Return 88 canonical (u,v) tuples — shared between all shots that draw landmarks.

    UV template measured from actual kuuttisiitonen render (eyes ~0.22, mouth ~0.52, jaw ~0.57).
    """
    pts = []
    # Eyes: 12 points (6 per eye) — tight ellipse around each eye
    for side_x in (0.408, 0.548):
        for i in range(6):
            theta = i * (2 * np.pi / 6)
            ex = side_x + 0.024 * np.cos(theta)
            ey = 0.222 + 0.008 * np.sin(theta)
            pts.append((ex, ey))
    # Eyebrows: 10 points (5 per brow) — just above eyes, slight arch
    for side_cx in (0.408, 0.548):
        for i in range(5):
            t = i / 4.0
            bx = side_cx + (t - 0.5) * 0.060
            by = 0.185 - 0.004 * (1 - abs(2 * t - 1))
            pts.append((bx, by))
    # Nose bridge: 5 points descending from between eyes to mid-nose
    for i in range(5):
        t = i / 4.0
        pts.append((0.500, 0.225 + t * 0.175))
    # Nose tip + nostrils (4 points)
    pts.extend([(0.478, 0.415), (0.500, 0.425), (0.522, 0.415), (0.500, 0.395)])
    # Mouth: 18 points — outline ellipse
    for i in range(18):
        theta = (i / 18.0) * 2 * np.pi
        mx = 0.500 + 0.045 * np.cos(theta)
        my = 0.520 + 0.015 * np.sin(theta)
        pts.append((mx, my))
    # Jawline: 17 points — arc from left jaw corner → chin → right jaw corner
    for i in range(17):
        t = i / 16.0
        theta = (t - 0.5) * 2.4
        jx = 0.500 + 0.118 * np.sin(theta)
        jy = 0.555 + 0.045 * (1 - np.cos(theta))
        pts.append((jx, jy))
    # Extras (22): forehead row + cheek filler
    remaining = 88 - len(pts)
    for i in range(remaining):
        t = i / max(1, remaining - 1)
        if i < remaining // 2:
            u = 0.42 + t * 2 * 0.16
            v = 0.135 + 0.005 * np.sin(t * 6)
        else:
            side = -1 if i % 2 == 0 else 1
            u = 0.500 + side * (0.085 + 0.020 * ((i * 13) % 7) / 7.0)
            v = 0.320 + 0.020 * np.sin(t * 4)
        pts.append((u, v))
    return pts[:88]


from manimlib import InteractiveScene


def m_math(s: str, scale: float = 0.6, color: str = TONE_FG, **kw) -> Text:
    t = Text(s, font="Cascadia Mono", color=color, **kw)
    t.scale(scale)
    return t


class LandmarkCloud(VGroup):
    def __init__(self, points, dot_radius: float = 0.05, color: str = TONE_AMBER, **kw):
        super().__init__(**kw)
        self.points_arr = np.asarray(points, dtype=float)
        for p in self.points_arr:
            d = Dot(radius=dot_radius, color=color, fill_opacity=0.95)
            d.move_to(np.array([p[0], p[1], 0.0]))
            self.add(d)

    def morph_to(self, new_points):
        new_points = np.asarray(new_points, dtype=float)
        anims = []
        for dot, target in zip(self.submobjects, new_points):
            anims.append(dot.animate.move_to(np.array([target[0], target[1], 0.0])))
        return anims


class SlidingKernel(VGroup):
    def __init__(self, grid_shape=(8, 8), kernel_size: int = 3, cell: float = 0.25, **kw):
        super().__init__(**kw)
        self.grid_shape = grid_shape
        self.k = kernel_size
        self.cell = cell
        rows, cols = grid_shape
        self.grid = VGroup()
        for r in range(rows):
            for c in range(cols):
                sq = Square(side_length=cell, stroke_color=TONE_MUTED, stroke_width=1, fill_opacity=0)
                sq.move_to(np.array([(c - cols/2 + 0.5) * cell, (rows/2 - r - 0.5) * cell, 0]))
                self.grid.add(sq)
        self.add(self.grid)
        self.kernel_box = Square(side_length=cell * kernel_size,
                                 stroke_color=TONE_AMBER, stroke_width=3, fill_opacity=0.0)
        self._place_kernel(0, 0)
        self.add(self.kernel_box)

    def _kernel_center(self, i: int, j: int) -> np.ndarray:
        """World-space center of the kernel at grid cell (i, j) — follows the
        group's current translation so move_to() doesn't teleport kernel out."""
        rows, cols = self.grid_shape
        cx = (j + self.k/2 - cols/2) * self.cell
        cy = (rows/2 - i - self.k/2) * self.cell
        return self.grid.get_center() + np.array([cx, cy, 0.0])

    def _place_kernel(self, i: int, j: int):
        self.kernel_box.move_to(self._kernel_center(i, j))

    def slide_to(self, i: int, j: int):
        return self.kernel_box.animate.move_to(self._kernel_center(i, j))


def cameo(scene, image_path: str, height: float = 4.5, hold: float = 0.6,
          fade: float = 0.4):
    img = ImageMobject(image_path)
    img.set_height(height)
    img.move_to(ORIGIN)
    img.set_opacity(0)
    scene.add(img)
    scene.play(img.animate.set_opacity(1), run_time=fade)
    scene.wait(hold)
    scene.play(img.animate.set_opacity(0), run_time=fade)
    scene.remove(img)


class MuseumScene(InteractiveScene):
    """Base scene for all shots — true-black camera + museum gradient bg auto-added."""

    def setup(self):
        super().setup()
        try:
            self.camera.background_color = BLACK
            if hasattr(self.camera, "background_rgba"):
                self.camera.background_rgba = (0, 0, 0, 1)
        except Exception:
            pass

    def add_museum_bg(self, accent="neutral"):
        # BOLD pass: every shot gets a designed cool tech backdrop (near-black +
        # soft cyan depth + vignette + grain) PLUS a faint live atmosphere (drifting
        # blueprint grid + sparse particles) so nothing reads as flat/static black.
        png = ensure_tech_backdrop(cache_key="tech_global", focus=(0.5, 0.42),
                                   glow_rgb=(45, 110, 170), strength=0.12)
        img = VGroup()
        if png and os.path.exists(png):
            img = ImageMobject(png)
            img.set_height(FRAME_HEIGHT * 1.02)
            img.set_width(FRAME_WIDTH * 1.02, stretch=True)
            self.add(img)
        try:
            self.add_tech_atmosphere()
        except Exception:
            pass
        return img

    def add_tech_atmosphere(self, grid_op=0.035, n_particles=16):
        """Faint drifting blueprint grid + sparse particle field — added behind shot
        content so every shot feels alive. Stored on self._atmosphere."""
        grid = VGroup()
        for x in np.arange(-9, 9.01, 1.2):
            grid.add(Line(np.array([x, -5, 0]), np.array([x, 5, 0]))
                     .set_stroke(TONE_CYAN, 1.0, opacity=grid_op))
        for y in np.arange(-5, 5.01, 1.2):
            grid.add(Line(np.array([-9, y, 0]), np.array([9, y, 0]))
                     .set_stroke(TONE_CYAN, 1.0, opacity=grid_op))
        self.add(grid)
        gp = ValueTracker(0.0)
        grid.add_updater(lambda m: m.move_to(np.array([
            0.25 * np.sin(gp.get_value() * 0.25),
            0.16 * np.cos(gp.get_value() * 0.18), 0])))
        always(gp.increment_value, 1.0 / 30.0)

        rng = np.random.RandomState(7)
        parts = VGroup()
        pd = []
        for _ in range(n_particles):
            px = rng.uniform(-7, 7); py = rng.uniform(-4, 4)
            d = Dot(radius=rng.uniform(0.010, 0.022)).set_fill(
                TONE_CYAN, rng.uniform(0.08, 0.20)).set_stroke(width=0)
            d.move_to(np.array([px, py, 0]))
            parts.add(d)
            pd.append((px, py, rng.uniform(0, 2 * np.pi), rng.uniform(0.15, 0.4)))
        self.add(parts)
        pp = ValueTracker(0.0)

        def _drift(m):
            t = pp.get_value()
            for d, (px, py, ph, sp) in zip(m, pd):
                d.move_to(np.array([px + 0.20 * np.sin(t * sp + ph),
                                    py + 0.14 * np.cos(t * sp * 0.8 + ph), 0]))
        parts.add_updater(_drift)
        always(pp.increment_value, 1.0 / 30.0)
        self._atmosphere = (grid, parts)
        return self._atmosphere

    def add_camera_breath(self, amp=0.005, period=8.0):
        """Subtle scale-pulse on camera frame — adds life. Opt-in.
        Call once after self.add_museum_bg(). amp=0.5%, period=8s default."""
        breath = ValueTracker(0.0)
        original = self.camera.frame.get_height()
        def upd(frame):
            t = breath.get_value()
            scale = 1.0 + amp * np.sin(2 * np.pi * t / period)
            frame.set_height(original * scale)
        self.camera.frame.add_updater(upd)
        always(breath.increment_value, 1.0 / 30.0)


class AnimatedHead(Group):
    """ImageMobject sequence player for head sway / turntable.

    Loops through `frames_dir/frame_NNN.png` (60 frames by default at 30 fps).
    Add to scene then call .start_loop(scene, run_time=...) or rely on the updater
    that ticks frame index based on elapsed scene time."""

    def __init__(self, frames_dir, n_frames=60, fps=30, height=4.0, loop=True):
        super().__init__()
        import os as _os
        self._frames_dir = frames_dir
        self._n = n_frames
        self._fps = fps
        self._height = height
        self._loop = loop
        # Pre-load all frames once (fast — they're small PNGs)
        self._mobs = []
        for i in range(n_frames):
            p = _os.path.join(frames_dir, f"frame_{i:03d}.png")
            if not _os.path.exists(p):
                continue
            m = ImageMobject(p); m.set_height(height); m.set_opacity(0)
            self._mobs.append(m)
        # First frame visible
        if self._mobs:
            self._mobs[0].set_opacity(1)
        self.add(*self._mobs)
        self._t0 = None  # set on first updater call

    def get_height_anchor(self):
        return self._mobs[0] if self._mobs else self

    def attach_updater(self, scene):
        """Tick frame index from accumulated scene dt. Honors `self.fade_factor` (default 1.0)
        so caller can cross-fade by animating that attribute."""
        n = len(self._mobs)
        period = n / self._fps
        state = {"t": 0.0}
        if not hasattr(self, "fade_factor"):
            self.fade_factor = 1.0
        def _u(group, dt):
            state["t"] += dt
            t = state["t"] % period if self._loop else min(state["t"], period - 1/self._fps)
            idx = int(t * self._fps) % n
            ff = getattr(group, "fade_factor", 1.0)
            for i, m in enumerate(self._mobs):
                m.set_opacity(ff if i == idx else 0.0)
        self.add_updater(_u)
        return self


def animated_head(frames_dir, n_frames=60, fps=30, height=4.0):
    return AnimatedHead(frames_dir, n_frames=n_frames, fps=fps, height=height)


# --- 2D landmark shape + eigenmodes (for ASM illustration) ---
def _mean_shape_88():
    """88 (x, y, 0) coords from build_landmark_uv(), centered & scaled.
    UV face span is tight (eyes/jaw within u~0.4-0.6, v~0.2-0.6) so we need
    aggressive scaling to fill a Manim frame: ~3 units wide, ~5 units tall."""
    uvs = build_landmark_uv()
    pts = []
    for u, v in uvs:
        x = (u - 0.5) * 14.0   # face width ~3 manim units (UV span ~0.22)
        y = (0.5 - v) * 12.0   # face height ~5 manim units (UV span ~0.38)
        pts.append((x, y, 0.0))
    arr = np.array(pts)
    # Center vertically: face features cluster above 0 in raw mapping
    arr[:, 1] -= (arr[:, 1].min() + arr[:, 1].max()) / 2
    return arr

MEAN_SHAPE_88 = _mean_shape_88()


def eigenmode_displacement(mode_idx, b, base_shape=None):
    """Fabricated eigenmode deformations for ASM illustration.
    mode 1 = horizontal stretch, mode 2 = smile curve, mode 3 = head tilt."""
    if base_shape is None:
        base_shape = MEAN_SHAPE_88
    out = base_shape.copy()
    if mode_idx == 1:
        out[:, 0] *= (1.0 + b * 0.18)
    elif mode_idx == 2:
        mouth_idx = list(range(31, 49))
        for i in mouth_idx:
            x_rel = out[i, 0] / 0.5
            x_rel = max(min(x_rel, 1.0), -1.0)
            out[i, 1] += b * 0.10 * (1.0 - x_rel**2)
    elif mode_idx == 3:
        theta = b * 0.12
        c, s = np.cos(theta), np.sin(theta)
        x = out[:, 0].copy()
        y = out[:, 1].copy()
        out[:, 0] = c * x - s * y
        out[:, 1] = s * x + c * y
    return out


class LandmarkFace2D(VGroup):
    """2D face from MEAN_SHAPE_88 + optional b coefficients.
    Renders: 88 dots + thin spline outlines for jaw and mouth.
    Usage:
        face = LandmarkFace2D(b=(1.5, 0.0, 0.0)).scale(1.5)
        face.update_b((2.0, 0.5, 0.0))   # mutate in-place
    """
    def __init__(self, b=(0.0, 0.0, 0.0), dot_color=None, outline_color=None,
                 dot_radius=0.045, outline_stroke=2.5, **kwargs):
        super().__init__(**kwargs)
        self._b = list(b) + [0.0] * (3 - len(b))
        self._dot_color = dot_color if dot_color is not None else TONE_CYAN
        self._outline_color = outline_color if outline_color is not None else TONE_AMBER
        self._dot_radius = dot_radius
        self._outline_stroke = outline_stroke
        pts = self._deformed_points()
        self.dots = VGroup(*[
            Dot(point=p, radius=dot_radius).set_fill(self._dot_color, 1.0).set_stroke(width=0)
            for p in pts
        ])
        self.outline = self._build_outline(pts)
        self.add(self.outline, self.dots)

    def _deformed_points(self):
        pts = MEAN_SHAPE_88.copy()
        for idx, bval in enumerate(self._b, start=1):
            if abs(bval) > 1e-6:
                pts = eigenmode_displacement(idx, bval, pts)
        return pts

    def _build_outline(self, pts):
        jaw = pts[49:66]
        mouth = pts[31:49]
        outline = VGroup()
        jaw_curve = VMobject().set_points_smoothly([np.array(p) for p in jaw])
        jaw_curve.set_stroke(self._outline_color, self._outline_stroke, opacity=0.55)
        outline.add(jaw_curve)
        mouth_loop = list(mouth) + [mouth[0]]
        mouth_curve = VMobject().set_points_smoothly([np.array(p) for p in mouth_loop])
        mouth_curve.set_stroke(self._outline_color, self._outline_stroke, opacity=0.45)
        outline.add(mouth_curve)
        return outline

    def update_b(self, new_b):
        self._b = list(new_b) + [0.0] * (3 - len(new_b))
        pts = self._deformed_points()
        for dot, p in zip(self.dots, pts):
            dot.move_to(p)
        new_outline = self._build_outline(pts)
        self.outline.become(new_outline)
        return self


class ParticleSwarm(Group):
    """88 dots: scatter / swirl / converge / snap. See plan for usage."""
    def __init__(self, n=88, target_positions=None, color=None, radius=0.05,
                 scatter_range=6.5, seed=7, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.targets = target_positions if target_positions is not None else MEAN_SHAPE_88
        self.color = color if color is not None else TONE_CYAN
        rng = np.random.RandomState(seed)
        self.start_positions = np.zeros((n, 3))
        self.start_positions[:, 0] = rng.uniform(-scatter_range, scatter_range, n)
        self.start_positions[:, 1] = rng.uniform(-3.5, 3.5, n)
        self.swirl_phase = rng.uniform(0, 2 * np.pi, n)
        self.swirl_freq = rng.uniform(0.8, 1.6, n)
        self.swirl_radius = rng.uniform(0.4, 1.2, n)
        self.dots = [
            Dot(point=p, radius=radius).set_fill(self.color, 0.0).set_stroke(width=0)
            for p in self.start_positions
        ]
        for d in self.dots:
            self.add(d)

    def scatter(self, scene, duration=1.5):
        scene.play(*[d.animate.set_fill(self.color, 0.85) for d in self.dots],
                   run_time=duration)

    def swirl(self, scene, duration=2.5):
        t_tracker = ValueTracker(0.0)
        anchors = [d.get_center().copy() for d in self.dots]
        def make_updater(idx, anchor):
            def upd(d):
                t = t_tracker.get_value()
                ph = self.swirl_phase[idx] + self.swirl_freq[idx] * t
                r = self.swirl_radius[idx]
                d.move_to(anchor + np.array([r * np.cos(ph) * 0.5, r * np.sin(ph) * 0.4, 0]))
            return upd
        for i, d in enumerate(self.dots):
            d.add_updater(make_updater(i, anchors[i]))
        scene.play(t_tracker.animate.set_value(2 * np.pi), run_time=duration, rate_func=linear)
        for d in self.dots:
            d.clear_updaters()

    def converge(self, scene, duration=3.0, oval_scale=0.6):
        oval_targets = self.targets * oval_scale * 1.4
        scene.play(*[d.animate.move_to(oval_targets[i]) for i, d in enumerate(self.dots)],
                   run_time=duration, rate_func=smooth)

    def snap_to_targets(self, scene, duration=1.0, flash=True):
        anims = [d.animate.move_to(self.targets[i]) for i, d in enumerate(self.dots)]
        if flash:
            anims += [d.animate.set_fill(TONE_AMBER, 1.0) for d in self.dots]
        scene.play(*anims, run_time=duration, rate_func=rush_into)


class PhaseIndicator(VGroup):
    """Vertical list of phase labels; one lights up at a time."""
    def __init__(self, phases, scale=0.42, gap=0.45, **kwargs):
        super().__init__(**kwargs)
        self._labels = []
        for i, p in enumerate(phases):
            t = m_text(f"[{i+1}]  {p}", scale=scale, color=TONE_MUTED)
            t.move_to(np.array([0.0, -i * gap, 0]))
            self._labels.append(t)
            self.add(t)
        self.active_idx = None

    def set_active(self, idx, color=None):
        color = color if color is not None else TONE_AMBER
        anims = []
        for i, lab in enumerate(self._labels):
            target_color = color if i == idx else TONE_MUTED
            anims.append(lab.animate.set_fill(target_color, 1.0))
        self.active_idx = idx
        return AnimationGroup(*anims, lag_ratio=0)


class ProfileScanGroup(VGroup):
    """Normal vector + intensity strip + peak marker."""
    def __init__(self, landmark_pos, normal_dir, length=1.0,
                 strip_width=0.08, peak_offset=0.20, **kwargs):
        super().__init__(**kwargs)
        n = np.asarray(normal_dir, dtype=float)
        n = n / (np.linalg.norm(n) + 1e-9)
        start = np.asarray(landmark_pos) - n * (length / 2)
        end = np.asarray(landmark_pos) + n * (length / 2)
        self.normal_line = Line(start, end).set_stroke(TONE_CYAN, 2.0)
        self.add(self.normal_line)

        n_steps = 16
        peak_t = peak_offset + 0.5
        self.strip = VGroup()
        for i in range(n_steps):
            t = i / (n_steps - 1)
            pos = start + n * t * length
            perp = np.array([-n[1], n[0], 0])
            intensity = float(np.exp(-((t - peak_t) ** 2) * 18))
            rect = Rectangle(width=strip_width, height=length / n_steps * 0.9)
            rect.set_fill(TONE_AMBER, opacity=0.15 + 0.7 * intensity)
            rect.set_stroke(width=0)
            rect.rotate(np.arctan2(n[1], n[0]) - np.pi / 2)
            rect.move_to(pos + perp * 0.10)
            self.strip.add(rect)
        self.add(self.strip)

        self.peak = Dot(radius=0.06).set_fill(TONE_AMBER, 1.0).set_stroke(WHITE, 1.0)
        self.peak.move_to(start + n * peak_t * length)
        self.peak.set_opacity(0)
        self.add(self.peak)


# --- Block 0 polish helpers (chapter ribbon, typewriter, count_up, bridge base) ---

def ChapterRibbon(section=None, chapter_text="Chapter 12 · Facial Landmark Localization"):
    """Top-left corner ribbon — DISABLED per user request 2026-05-26.

    Returns an empty VGroup so all existing call-sites (`ribbon = ChapterRibbon(...)`
    + `self.add(ribbon)`) continue to work without rendering anything visible.
    Keep the function signature intact in case we want to re-enable later.
    """
    return VGroup()


def _ChapterRibbon_disabled_original(section=None, chapter_text="Chapter 12 · Facial Landmark Localization"):
    """Original ribbon implementation — kept for reference. See ChapterRibbon above."""
    chap = Text(
        chapter_text,
        font=FONT,
        weight=NORMAL,
        t2c={"Chapter 12": TONE_AMBER},
    )
    chap.set_fill(TONE_MUTED, 1.0)
    chap.set_stroke(width=0)
    try:
        chap["Chapter 12"].set_fill(TONE_AMBER, 1.0)
    except Exception:
        pass
    chap.scale(0.32)
    parts = [chap]
    if section is not None:
        sub = Text(section, font=FONT, weight=NORMAL)
        sub.set_fill(TONE_MUTED, 1.0)
        sub.set_stroke(width=0)
        sub.scale(0.26)
        sub.set_opacity(0.7)
        sub.next_to(chap, DOWN, buff=0.08, aligned_edge=LEFT)
        parts.append(sub)
    group = VGroup(*parts)
    group.to_corner(UL, buff=0.35)
    return group


def typewriter_anim(text_mobj, char_duration=0.04, jitter=0.005):
    """Returns a LaggedStart animation revealing one character at a time.

    Parameters
    ----------
    text_mobj : Text | VGroup
        A Manim Text mobject. Each submobject is one char.
    char_duration : float
        Per-char fade duration.
    jitter : float
        Small randomization to avoid metronomic feel.
    """
    import random
    chars = list(text_mobj)
    anims = []
    for c in chars:
        c.save_state()
        c.set_opacity(0)
        c.shift(0.05 * DOWN)
        anims.append(Restore(c, run_time=char_duration + random.uniform(0, jitter)))
    return LaggedStart(*anims, lag_ratio=0.7)


def count_up(value_tracker, end_value, duration, ease=smooth):
    """Animates a ValueTracker from current to end_value over duration.

    Caller binds a DecimalNumber to it via add_updater for display.
    Returns an Animation usable in self.play().
    """
    return value_tracker.animate(run_time=duration, rate_func=ease).set_value(end_value)


class BridgeBase(InteractiveScene):
    """Base class for standalone bridge clips between shots.

    Bridges:
    - Are 1.0-1.5s total
    - Use neutral black bg (no atmospheric accent — between accents)
    - Declare in/out anchor positions matched to neighbor frame pixel positions
    """
    DURATION_MIN = 1.0
    DURATION_MAX = 1.5

    def setup(self):
        super().setup()
        try:
            self.camera.background_color = BLACK
            if hasattr(self.camera, "background_rgba"):
                self.camera.background_rgba = (0, 0, 0, 1)
        except Exception:
            pass
        self._in_anchor = None
        self._out_anchor = None

    def set_in_anchor(self, mobj_position):
        """Position (np.array) this bridge picks up from previous shot's last frame."""
        self._in_anchor = mobj_position

    def set_out_anchor(self, mobj_position):
        """Position (np.array) this bridge lands for next shot's first frame."""
        self._out_anchor = mobj_position


def play_bridge_animation(scene, from_label, to_label, sub_text, step=None, total=12):
    """Render a polished 2.3s bridge transition with motion personality.

    Sequence (~2.3s):
      0.00-0.45s: Left dot + 'from_label' typewriter cascade
      0.45-0.95s: Amber arrow draws-on left->right; travelling dot animates along arrow
      0.95-1.35s: Right dot + 'to_label' typewriter cascade
      1.35-1.75s: Underline draws-on + Sub-text fades in (BELOW underline with gap)
      1.75-2.05s: Hold so the audience can read the sub-text
      2.05-2.30s: Quick fade-out (overlaps next shot's fade-in)

    step/total kept for API compatibility but no longer rendered.
    """
    # Build the main row first (off-screen / opacity 0) so we can compute positions.
    left_text = m_text(from_label, scale=0.50, color=TONE_AMBER)
    right_text = m_text(to_label, scale=0.50, color=TONE_AMBER)
    # Arrange: [left_text]  ->  [right_text], horizontal row
    # Total width: left + gap + arrow + gap + right
    arrow_len = 1.0
    gap = 0.40
    # Position left_text to the left, right_text to the right with space for arrow between
    main_row = VGroup(left_text, right_text)
    # Manually position: center the whole row at ORIGIN
    total_w = left_text.get_width() + gap + arrow_len + gap + right_text.get_width()
    x_start = -total_w / 2
    left_text.move_to(np.array([x_start + left_text.get_width()/2, 0, 0]))
    right_x = x_start + left_text.get_width() + gap + arrow_len + gap + right_text.get_width()/2
    right_text.move_to(np.array([right_x, 0, 0]))
    # Arrow: from end of left_text + gap to start of right_text - gap
    arrow_start_x = x_start + left_text.get_width() + gap
    arrow_end_x = arrow_start_x + arrow_len
    arrow = Arrow(
        start=np.array([arrow_start_x, 0, 0]),
        end=np.array([arrow_end_x, 0, 0]),
        stroke_color=TONE_AMBER,
        stroke_width=3.0,
        buff=0,
    )
    # Flanking dots
    dot_l = Dot(radius=0.07, color=TONE_AMBER).next_to(left_text, LEFT, buff=0.30)
    dot_r = Dot(radius=0.07, color=TONE_AMBER).next_to(right_text, RIGHT, buff=0.30)
    # Underline below main row, between dots
    underline = Line(
        np.array([dot_l.get_right()[0] + 0.10, -0.45, 0]),
        np.array([dot_r.get_left()[0] - 0.10, -0.45, 0]),
    ).set_stroke(TONE_AMBER, 1.5).set_opacity(0.65)
    # Sub-text BELOW underline (not main row) — give breathing room
    sub = m_text(sub_text, scale=0.34, color=TONE_MUTED)
    sub.next_to(underline, DOWN, buff=0.25)
    sub.set_opacity(0.85)
    # Travelling dot along arrow path
    travel_dot = Dot(radius=0.05, color="#ffd17a").set_stroke(width=0)
    travel_dot.move_to(arrow.get_start())
    travel_dot.set_opacity(0)

    # === Phase 1: Left side reveal (0.00-0.45s) ===
    scene.play(
        FadeIn(dot_l, scale=0.5),
        typewriter_anim(left_text, char_duration=0.018),
        run_time=0.45,
    )

    # === Phase 2: Arrow draws + travel dot (0.45-0.95s) ===
    travel_dot.set_opacity(1.0)
    scene.add(travel_dot)
    scene.play(
        GrowArrow(arrow),
        travel_dot.animate.move_to(arrow.get_end()),
        run_time=0.50,
        rate_func=smooth,
    )
    travel_dot.set_opacity(0)

    # === Phase 3: Right side reveal (0.95-1.35s) ===
    scene.play(
        FadeIn(dot_r, scale=0.5),
        typewriter_anim(right_text, char_duration=0.018),
        run_time=0.40,
    )

    # === Phase 4: Underline + sub-text (1.35-1.75s) ===
    scene.play(
        ShowCreation(underline),
        FadeIn(sub, shift=0.08 * DOWN),
        run_time=0.40,
    )

    # === Phase 5: Hold so audience can read sub-text (1.75-2.05s) ===
    scene.wait(0.30)

    # === Phase 6: Quick fade out (2.05-2.30s) — overlaps next shot's fade-in ===
    fade_targets = [left_text, right_text, arrow, dot_l, dot_r, sub, underline]
    scene.play(*[FadeOut(m) for m in fade_targets], run_time=0.25)
