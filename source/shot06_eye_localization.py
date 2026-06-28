"""
Shot 04 — Eye Localization (redesigned, clearer).
Layout: sliding kernel → heatmap on the LEFT, formula BELOW the heatmap, the
real FACE on the RIGHT. When argmax fires on the heatmap, a connector draws to
the localized eye centre on the face and it lights up. No establishing/profile/
hero-payoff beats — one tight story: response peak ⇒ eye location.
"""
from manimlib import *

import os, sys
import numpy as np
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_RED, TONE_FG, TONE_MUTED, TONE_BG_BOT,
    HERO_FRONTAL, ASSETS_DIR,
    MuseumScene, m_text, m_math, SlidingKernel, uv_to_manim,
    FACE_EYE_L_UV, FACE_EYE_R_UV,
    ChapterRibbon,
)


def _dim_img(path, factor=0.6):
    """Darkened copy of a bright hero PNG so the face sits on the dark bg."""
    from PIL import Image
    path = str(path)
    d = os.path.join(os.path.dirname(path), "dim")
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, f"{factor:.2f}_" + os.path.basename(path))
    if not os.path.exists(out):
        arr = np.array(Image.open(path).convert("RGBA")).astype(np.float32)
        arr[..., :3] *= factor
        Image.fromarray(np.clip(arr, 0, 255).astype("uint8")).save(out)
    return out


class Section01_Shot06_EyeLocalization(MuseumScene):
    def construct(self):
        self.add_museum_bg(accent="amber")
        ribbon = ChapterRibbon(section="12.3 · eye localization")
        self.add(ribbon)

        title = m_text("Eye localization = response peak",
                       color=TONE_FG).scale(0.6).to_edge(UP, buff=0.4)
        self.play(FadeIn(title), run_time=0.45)

        # ---- Right: the real face (dimmed to match the dark tone) ----
        face = ImageMobject(_dim_img(HERO_FRONTAL, 0.6)).set_height(5.2)
        face.move_to(np.array([3.6, 0.1, 0]))
        face.set_opacity(0)
        self.add(face)

        # peak target (the eye) — shared by the heatmap and the face scan window
        peak_i, peak_j = 3, 5
        eye_anchor = uv_to_manim(FACE_EYE_L_UV, face)

        def _face_pos(i, j):
            return eye_anchor + np.array([(j - peak_j) * 0.40, (peak_i - i) * 0.40, 0])

        # ---- Left: sliding-kernel grid + formula BELOW it ----
        sk = SlidingKernel(grid_shape=(8, 8), kernel_size=3, cell=0.30)
        sk.move_to(np.array([-3.8, 0.55, 0]))
        sk._place_kernel(2, 2)
        formula = m_math("R(x,y) = Σ I(x+i, y+j) · K(i,j)", scale=0.40, color=TONE_FG)
        formula.move_to(np.array([-3.8, -2.30, 0]))

        # template-matching window that scans the FACE in sync with the kernel
        win = Square(side_length=0.85).set_fill(opacity=0)
        win.set_stroke(TONE_AMBER, 2.4, opacity=0.0).move_to(_face_pos(2, 2))
        self.add(win)

        self.play(FadeIn(sk), face.animate.set_opacity(1.0),
                  win.animate.set_stroke(TONE_AMBER, 2.4, opacity=0.9), run_time=0.7)
        self.play(FadeIn(formula, shift=0.05 * UP), run_time=0.4)

        # scan path — kernel + face window zig-zag together, amber afterglow trail
        scan_path = [(1, 1), (1, 4), (2, 2), (3, 0), (4, 3), (3, 5)]
        trail = []
        for (i, j) in scan_path:
            self.play(sk.slide_to(i, j), win.animate.move_to(_face_pos(i, j)), run_time=0.40)
            glow = Square(side_length=0.30, stroke_width=0,
                          fill_color=TONE_AMBER, fill_opacity=0.0)
            glow.move_to(sk.grid[i * 8 + j].get_center())
            self.add(glow); trail.append(glow)
            self.play(glow.animate.set_fill(TONE_AMBER, 0.45), run_time=0.10)
            self.play(glow.animate.set_fill(TONE_AMBER, 0.18), run_time=0.08)

        # ---- heatmap reveal ----
        rows, cols = 8, 8
        cells, max_resp = [], 0.0
        for r in range(rows):
            for c in range(cols):
                d = np.hypot(r - peak_i, c - peak_j)
                resp = float(np.exp(-d * d / 4.0))
                max_resp = max(max_resp, resp)
                cells.append((r, c, resp))
        heat = VGroup()
        for (r, c, resp) in cells:
            col = interpolate_color(TONE_BG_BOT, TONE_AMBER, resp / max_resp)
            sq = Square(side_length=0.30, stroke_width=0.5, stroke_color=TONE_MUTED,
                        fill_color=col, fill_opacity=0.9)
            sq.move_to(sk.grid[r * cols + c].get_center())
            heat.add(sq)
        ordered = VGroup(*[sq for _, sq in sorted(
            [(np.hypot(cells[i][0] - peak_i, cells[i][1] - peak_j), sq)
             for i, sq in enumerate(heat)], key=lambda x: x[0])])
        self.play(FadeOut(sk), FadeOut(VGroup(*trail)),
                  LaggedStartMap(FadeIn, ordered, lag_ratio=0.04), run_time=1.1)
        self.wait(2.51)

        # ---- argmax peak ----
        peak_cell = sk.grid[peak_i * cols + peak_j].get_center()
        peak_dot = Dot(radius=0.11, color=TONE_RED).move_to(peak_cell)
        peak_label = m_math("argmax", scale=0.5, color=TONE_RED).next_to(peak_dot, UP, buff=0.12)
        self.play(FadeIn(peak_dot, scale=0.3), FadeIn(peak_label), run_time=0.4)
        self.play(peak_dot.animate.scale(1.4), run_time=0.12)
        self.play(peak_dot.animate.scale(1 / 1.4), run_time=0.12)

        # ---- argmax ⇒ the localized eye centre on the face ----
        eyeL = uv_to_manim(FACE_EYE_L_UV, face)
        connector = VMobject().set_points_smoothly(
            [peak_cell, (peak_cell + eyeL) / 2 + UP * 0.5, eyeL])
        connector.set_stroke(TONE_AMBER, 2.0, opacity=0.8)
        eye_dot = Dot(radius=0.10).set_fill(TONE_AMBER, 1.0).set_stroke(WHITE, 1.0).move_to(eyeL)
        eye_dot.set_opacity(0)
        ring = Circle(radius=0.12).set_stroke(TONE_AMBER, 2.2).set_fill(opacity=0).move_to(eyeL).set_opacity(0)
        cap = m_text("the strongest response = the eye centre",
                     scale=0.34, color=TONE_AMBER).next_to(face, DOWN, buff=0.25)
        self.add(ring)
        self.play(ShowCreation(connector), run_time=0.55)
        # the scan window closes in onto the eye it matched
        self.play(win.animate.set_stroke(TONE_AMBER, 3.0, opacity=1.0).scale(0.5),
                  FadeIn(eye_dot, scale=0.4), FadeIn(cap, shift=0.05 * UP), run_time=0.45)
        self.play(ring.animate.set_opacity(0.85).scale(2.3), run_time=0.4)
        self.play(ring.animate.set_opacity(0), run_time=0.25)
        self.wait(3.02)

        # ---- the other eye localizes too (two anchors) ----
        eyeR = uv_to_manim(FACE_EYE_R_UV, face)
        eye_dot2 = Dot(radius=0.10).set_fill(TONE_AMBER, 1.0).set_stroke(WHITE, 1.0).move_to(eyeR)
        eye_dot2.set_opacity(0)
        ring2 = Circle(radius=0.12).set_stroke(TONE_AMBER, 2.2).set_fill(opacity=0).move_to(eyeR).set_opacity(0)
        self.add(ring2)
        self.play(FadeIn(eye_dot2, scale=0.4),
                  ring2.animate.set_opacity(0.85).scale(2.3), run_time=0.45)
        self.play(ring2.animate.set_opacity(0), run_time=0.25)
        self.wait(5.54)

        # ---- fade out ----
        self.play(FadeOut(Group(face, title, formula, peak_dot, peak_label,
                                connector, eye_dot, eye_dot2, cap, win, ordered)),
                  run_time=0.6)
