"""
BOLD hero "wow" demo — cinematic facial-landmark hero.

Pure-Manim composite over a designed cool tech backdrop:
  - hero head (alpha v3) large on the right third
  - a glowing landmark constellation anchored to the calibrated v3 UV centers,
    igniting region-by-region, with mesh lines on eyes / mouth / jaw
  - HUD callouts (leader line + label + tiny readout) on each region
  - drifting blueprint grid + drifting particles for atmosphere
  - large title block on the left
No audio timing constraints (voice is re-recorded later).
"""
from manimlib import *

import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    MuseumScene, m_text, FONT,
    TONE_CYAN, TONE_AMBER, TONE_FG, TONE_MUTED,
    HERO_FRONTAL, uv_to_manim, ensure_tech_backdrop,
    FACE_EYE_L_UV, FACE_EYE_R_UV, FACE_NOSE_UV, FACE_MOUTH_UV,
)


def _constellation_uvs():
    """~40 landmark UVs built around the 4 calibrated v3 centers so they align
    to the real face. Returns (eye_ring_L, eye_ring_R, mouth_loop, jaw_arc, extras)."""
    el, er, no, mo = FACE_EYE_L_UV, FACE_EYE_R_UV, FACE_NOSE_UV, FACE_MOUTH_UV
    midx = (el[0] + er[0]) / 2

    def ring(c, rx, ry, n):
        return [(c[0] + rx * np.cos(k * 2 * np.pi / n),
                 c[1] + ry * np.sin(k * 2 * np.pi / n)) for k in range(n)]

    eye_L = ring(el, 0.035, 0.018, 8)
    eye_R = ring(er, 0.035, 0.018, 8)
    mouth = ring(mo, 0.058, 0.024, 10)
    brows = []
    for c in (el, er):
        for k in range(5):
            t = k / 4.0
            brows.append((c[0] + (t - 0.5) * 0.09,
                          c[1] - 0.052 - 0.010 * (1 - abs(2 * t - 1))))
    nose = [(midx, el[1] + 0.02 + (k / 3.0) * (no[1] - el[1] - 0.02)) for k in range(4)]
    nose += [(no[0] - 0.03, no[1]), (no[0], no[1] + 0.02), (no[0] + 0.03, no[1])]
    jaw = []
    for k in range(11):
        t = k / 10.0
        th = (t - 0.5) * 2.2
        jaw.append((mo[0] + 0.165 * np.sin(th), mo[1] + 0.10 + 0.060 * (1 - np.cos(th))))
    return eye_L, eye_R, mouth, brows, nose, jaw


class HeroWow(MuseumScene):
    def construct(self):
        # ---------- designed backdrop ----------
        png = ensure_tech_backdrop()
        if png and os.path.exists(png):
            bg = ImageMobject(png)
            bg.set_height(FRAME_HEIGHT * 1.02)
            bg.set_width(FRAME_WIDTH * 1.02, stretch=True)
            self.add(bg)

        # ---------- drifting blueprint grid ----------
        grid = VGroup()
        for x in np.arange(-9, 9.01, 0.9):
            grid.add(Line(np.array([x, -5, 0]), np.array([x, 5, 0]))
                     .set_stroke(TONE_CYAN, 1.0, opacity=0.05))
        for y in np.arange(-5, 5.01, 0.9):
            grid.add(Line(np.array([-9, y, 0]), np.array([9, y, 0]))
                     .set_stroke(TONE_CYAN, 1.0, opacity=0.05))
        self.add(grid)
        gphase = ValueTracker(0.0)
        grid.add_updater(lambda m: m.move_to(np.array([
            0.30 * np.sin(gphase.get_value() * 0.30),
            0.20 * np.cos(gphase.get_value() * 0.20), 0])))
        always(gphase.increment_value, 1.0 / 30.0)

        # ---------- drifting particles ----------
        rng = np.random.RandomState(7)
        particles = VGroup()
        pdata = []
        for _ in range(36):
            px = rng.uniform(-7.0, 7.0)
            py = rng.uniform(-4.0, 4.0)
            d = Dot(radius=rng.uniform(0.012, 0.03)).set_fill(TONE_CYAN, rng.uniform(0.12, 0.35)).set_stroke(width=0)
            d.move_to(np.array([px, py, 0]))
            particles.add(d)
            pdata.append((px, py, rng.uniform(0, 2 * np.pi), rng.uniform(0.15, 0.5)))
        self.add(particles)
        pphase = ValueTracker(0.0)

        def _drift_particles(m):
            t = pphase.get_value()
            for d, (px, py, ph, sp) in zip(m, pdata):
                d.move_to(np.array([px + 0.25 * np.sin(t * sp + ph),
                                    py + 0.18 * np.cos(t * sp * 0.8 + ph), 0]))
        particles.add_updater(_drift_particles)
        always(pphase.increment_value, 1.0 / 30.0)

        # ---------- hero head ----------
        head = ImageMobject(HERO_FRONTAL)
        head.set_height(6.8)
        head.move_to(np.array([3.0, 0.05, 0]))
        head.set_opacity(0)
        self.add(head)
        self.play(head.animate.set_opacity(1.0), run_time=1.0)

        # subtle head "breath"
        hphase = ValueTracker(0.0)
        h0 = head.get_height()
        c0 = head.get_center().copy()
        head.add_updater(lambda m: m.set_height(
            h0 * (1.0 + 0.006 * np.sin(hphase.get_value() * 0.6))).move_to(c0))
        always(hphase.increment_value, 1.0 / 30.0)

        # ---------- landmark constellation ----------
        eye_L, eye_R, mouth, brows, nose, jaw = _constellation_uvs()

        def dots_from(uvs, color, r=0.045):
            g = VGroup()
            for uv in uvs:
                p = uv_to_manim(uv, head)
                dot = Dot(radius=r).set_fill(color, 1.0).set_stroke(color, 1.0, opacity=0.4)
                dot.move_to(p)
                dot.save_state()
                dot.set_opacity(0).scale(0.1)
                g.add(dot)
            return g

        g_brows = dots_from(brows, TONE_CYAN)
        g_eyeL = dots_from(eye_L, TONE_AMBER)
        g_eyeR = dots_from(eye_R, TONE_AMBER)
        g_nose = dots_from(nose, TONE_CYAN)
        g_mouth = dots_from(mouth, TONE_AMBER)
        g_jaw = dots_from(jaw, TONE_CYAN)
        for g in (g_brows, g_eyeL, g_eyeR, g_nose, g_mouth, g_jaw):
            self.add(g)

        def mesh_loop(uvs, color):
            pts = [uv_to_manim(uv, head) for uv in uvs] + [uv_to_manim(uvs[0], head)]
            ln = VMobject().set_points_as_corners(pts)
            return ln.set_stroke(color, 1.4, opacity=0.45)

        def mesh_path(uvs, color):
            pts = [uv_to_manim(uv, head) for uv in uvs]
            ln = VMobject().set_points_as_corners(pts)
            return ln.set_stroke(color, 1.4, opacity=0.45)

        ml_eyeL = mesh_loop(eye_L, TONE_AMBER)
        ml_eyeR = mesh_loop(eye_R, TONE_AMBER)
        ml_mouth = mesh_loop(mouth, TONE_AMBER)
        ml_jaw = mesh_path(jaw, TONE_CYAN)

        # ignite region by region (waves), then draw the mesh
        wave = [g_brows, g_eyeL, g_eyeR, g_nose, g_mouth, g_jaw]
        for g in wave:
            self.play(LaggedStart(*[Restore(d) for d in g], lag_ratio=0.05),
                      run_time=0.45)
        self.play(ShowCreation(ml_eyeL), ShowCreation(ml_eyeR),
                  ShowCreation(ml_mouth), ShowCreation(ml_jaw), run_time=0.9)

        # ---------- HUD callouts ----------
        def callout(anchor_uv, label, readout, label_pos, color):
            a = uv_to_manim(anchor_uv, head)
            anchor_dot = Dot(radius=0.05).set_fill(color, 1.0).set_stroke(WHITE, 1.0)
            anchor_dot.move_to(a)
            elbow = np.array([label_pos[0], a[1], 0])
            leader = VMobject().set_points_as_corners([a, elbow, label_pos])
            leader.set_stroke(color, 1.4, opacity=0.7)
            lab = m_text(label, scale=0.34, color=color)
            lab.move_to(label_pos, aligned_edge=LEFT if label_pos[0] > a[0] else RIGHT)
            read = m_text(readout, scale=0.24, color=TONE_MUTED)
            read.next_to(lab, DOWN, buff=0.08, aligned_edge=LEFT)
            grp = VGroup(leader, anchor_dot, lab, read)
            return grp

        hud = [
            callout(FACE_EYE_L_UV, "EYE REGION", "12 pts · ±0.8px", np.array([-2.4, 2.4, 0]), TONE_AMBER),
            callout(FACE_NOSE_UV, "NOSE BRIDGE", "5 pts", np.array([6.4, 0.6, 0]), TONE_CYAN),
            callout(FACE_MOUTH_UV, "MOUTH CONTOUR", "18 pts", np.array([-2.6, -1.6, 0]), TONE_AMBER),
            callout((0.5, 0.74), "JAWLINE", "17 pts", np.array([-2.2, -3.2, 0]), TONE_CYAN),
        ]
        for h in hud:
            self.play(ShowCreation(h[0]), FadeIn(h[1], scale=0.5),
                      FadeIn(h[2], shift=0.1 * RIGHT), FadeIn(h[3]), run_time=0.4)

        # ---------- title block ----------
        t1 = m_text("FACIAL  LANDMARK", scale=0.66, color=TONE_FG)
        t2 = m_text("LOCALIZATION", scale=0.66, color=TONE_AMBER)
        t1.to_corner(UL, buff=0.7)
        t2.next_to(t1, DOWN, buff=0.14, aligned_edge=LEFT)
        rule = Line(t2.get_left(), t2.get_left() + RIGHT * 4.2).set_stroke(TONE_AMBER, 2.0)
        rule.next_to(t2, DOWN, buff=0.22, aligned_edge=LEFT)
        sub = m_text("mapping the geometry of a face — one point at a time",
                     scale=0.32, color=TONE_MUTED)
        sub.next_to(rule, DOWN, buff=0.20, aligned_edge=LEFT)
        self.play(Write(t1), run_time=0.7)
        self.play(Write(t2), run_time=0.6)
        self.play(ShowCreation(rule), FadeIn(sub, shift=0.08 * RIGHT), run_time=0.5)

        self.wait(1.6)

        # ---------- close ----------
        head.clear_updaters()
        grid.clear_updaters()
        particles.clear_updaters()
        self.play(
            *[FadeOut(m) for m in [grid, particles, t1, t2, rule, sub,
                                   ml_eyeL, ml_eyeR, ml_mouth, ml_jaw,
                                   g_brows, g_eyeL, g_eyeR, g_nose, g_mouth, g_jaw,
                                   *hud]],
            head.animate.set_opacity(0.0),
            run_time=0.8,
        )
