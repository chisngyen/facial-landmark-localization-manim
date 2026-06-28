"""
Reusable BOLD-pass hero machinery, shared by the head/content shots.

Keeps museum_tone (used by all 15 shots) stable while letting individual head
shots opt into: drifting tech atmosphere (grid + particles), a glowing landmark
constellation anchored to the calibrated v3 UV centers, and HUD callouts.
"""
from manimlib import *
import numpy as np

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_MUTED, m_text, uv_to_manim,
    FACE_EYE_L_UV, FACE_EYE_R_UV, FACE_NOSE_UV, FACE_MOUTH_UV,
)


def add_tech_atmosphere(scene, grid_op=0.05, n_particles=30, particle_op=(0.12, 0.32)):
    """Add a slow-drifting blueprint grid + particle field. Returns (grid, particles,
    trackers) — caller should clear_updaters() on grid/particles before fading out."""
    grid = VGroup()
    for x in np.arange(-9, 9.01, 0.9):
        grid.add(Line(np.array([x, -5, 0]), np.array([x, 5, 0]))
                 .set_stroke(TONE_CYAN, 1.0, opacity=grid_op))
    for y in np.arange(-5, 5.01, 0.9):
        grid.add(Line(np.array([-9, y, 0]), np.array([9, y, 0]))
                 .set_stroke(TONE_CYAN, 1.0, opacity=grid_op))
    scene.add(grid)
    gphase = ValueTracker(0.0)
    grid.add_updater(lambda m: m.move_to(np.array([
        0.30 * np.sin(gphase.get_value() * 0.30),
        0.20 * np.cos(gphase.get_value() * 0.20), 0])))
    always(gphase.increment_value, 1.0 / 30.0)

    rng = np.random.RandomState(7)
    particles = VGroup()
    pdata = []
    for _ in range(n_particles):
        px = rng.uniform(-7.0, 7.0); py = rng.uniform(-4.0, 4.0)
        d = Dot(radius=rng.uniform(0.012, 0.03)).set_fill(
            TONE_CYAN, rng.uniform(*particle_op)).set_stroke(width=0)
        d.move_to(np.array([px, py, 0]))
        particles.add(d)
        pdata.append((px, py, rng.uniform(0, 2 * np.pi), rng.uniform(0.15, 0.5)))
    scene.add(particles)
    pphase = ValueTracker(0.0)

    def _drift(m):
        t = pphase.get_value()
        for d, (px, py, ph, sp) in zip(m, pdata):
            d.move_to(np.array([px + 0.25 * np.sin(t * sp + ph),
                                py + 0.18 * np.cos(t * sp * 0.8 + ph), 0]))
    particles.add_updater(_drift)
    always(pphase.increment_value, 1.0 / 30.0)
    return grid, particles, (gphase, pphase)


def constellation_uvs():
    """~50 landmark UVs grouped by region, anchored to the 4 calibrated v3 centers."""
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


def build_constellation(head, r=0.045):
    """Return (waves, meshes): waves = list of VGroups (dots, hidden+scaled for Restore),
    meshes = list of VMobject outlines (eyes/mouth/jaw). Caller plays Restore then ShowCreation."""
    eye_L, eye_R, mouth, brows, nose, jaw = constellation_uvs()

    def dots_from(uvs, color):
        g = VGroup()
        for uv in uvs:
            d = Dot(radius=r).set_fill(color, 1.0).set_stroke(color, 1.0, opacity=0.4)
            d.move_to(uv_to_manim(uv, head))
            d.save_state(); d.set_opacity(0).scale(0.1)
            g.add(d)
        return g

    waves = [dots_from(brows, TONE_CYAN), dots_from(eye_L, TONE_AMBER),
             dots_from(eye_R, TONE_AMBER), dots_from(nose, TONE_CYAN),
             dots_from(mouth, TONE_AMBER), dots_from(jaw, TONE_CYAN)]

    def loop(uvs, color, closed=True):
        pts = [uv_to_manim(uv, head) for uv in uvs]
        if closed:
            pts = pts + [pts[0]]
        return VMobject().set_points_as_corners(pts).set_stroke(color, 1.4, opacity=0.45)

    meshes = [loop(eye_L, TONE_AMBER), loop(eye_R, TONE_AMBER),
              loop(mouth, TONE_AMBER), loop(jaw, TONE_CYAN, closed=False)]
    return waves, meshes


import os as _os


class SeqCard(Group):
    """Plays a frame sequence (frame_000.png ...) as an animated card. The visible
    frame ticks from accumulated dt; overall opacity is driven by `self.vis`
    (a ValueTracker) so it can cross-fade despite the per-frame updater.

    Usage:
        card = SeqCard(seq_dir, n=30, center=np.array([3,0.3,0]), height=3.7)
        scene.add(card); card.add_updater(lambda g, dt: g.tick(dt))
        scene.play(card.vis.animate.set_value(1.0))   # fade in
        scene.play(card.vis.animate.set_value(0.0))   # fade out
    """
    def __init__(self, frames_dir, n, center, height=None, width=None, fps=20,
                 loop=True, **kw):
        super().__init__(**kw)
        self.loop = loop
        self.frames = []
        for i in range(n):
            p = _os.path.join(frames_dir, f"frame_{i:03d}.png")
            if not _os.path.exists(p):
                continue
            m = ImageMobject(p)
            if width is not None:
                m.set_width(width)
            else:
                m.set_height(height)
            m.move_to(center)
            m.set_opacity(0)
            self.frames.append(m)
            self.add(m)
        self.n = len(self.frames)
        self.fps = fps
        self.vis = ValueTracker(0.0)
        self._t = 0.0

    def tick(self, dt):
        if self.n == 0:
            return
        self._t += dt
        if self.loop:
            idx = int(self._t * self.fps) % self.n
        else:
            idx = min(int(self._t * self.fps), self.n - 1)
        v = self.vis.get_value()
        for i, m in enumerate(self.frames):
            m.set_opacity(v if i == idx else 0.0)


def play_seq_beat(scene, seq_dir, n, center, height, hold=3.5, label=None,
                  accent=None, fps=20, loop=True, frame=False):
    """Show an animated Three.js sequence (SeqCard) as a self-contained beat:
    fade in → hold → fade out. Full-bleed by default (frame=False — no boxed-in
    square brackets); set frame=True for the corner-bracket look. loop=False plays
    once then holds the last frame (build-up sequences like pca / scan)."""
    from museum_tone import m_text, TONE_AMBER
    accent = accent if accent is not None else TONE_AMBER
    card = SeqCard(seq_dir, n, center, height=height, fps=fps, loop=loop)
    scene.add(card)
    card.add_updater(lambda g, dt: g.tick(dt))
    extras = []
    if frame:
        extras.append(hud_corners_for(center, height, accent))
    if label:
        lab = m_text(label, scale=0.5, color=accent)
        lab.move_to(np.array([center[0], -3.55, 0]))
        extras.append(lab)
    scene.play(card.vis.animate.set_value(1.0), *[FadeIn(m) for m in extras], run_time=0.6)
    scene.wait(hold)
    scene.play(card.vis.animate.set_value(0.0), *[FadeOut(m) for m in extras], run_time=0.5)
    card.clear_updaters()
    scene.remove(card)


def hud_corners_for(center, size, accent):
    """Corner brackets around a square region of side `size` centered at `center`."""
    ref = Square(side_length=size).move_to(center).set_stroke(width=0)
    from museum_tone import hud_corners
    return hud_corners(ref, color=accent, arm=0.34, stroke_w=3.0,
                       width=size + 0.12, height=size + 0.12)


def hud_callout(head, anchor_uv, label, readout, label_pos, color):
    """Leader line + anchor dot + label + small readout. Returns VGroup(leader, dot, lab, read)."""
    a = uv_to_manim(anchor_uv, head)
    dot = Dot(radius=0.05).set_fill(color, 1.0).set_stroke(WHITE, 1.0).move_to(a)
    # Smooth S-curve leader: leaves the face horizontally, eases to the label,
    # arrives horizontally — flowing, not a rigid right-angle elbow.
    sgn = 1.0 if a[0] > label_pos[0] else -1.0
    hx = 0.55
    p_a = a + np.array([-hx * sgn, 0, 0])
    p_l = label_pos + np.array([hx * sgn, 0, 0])
    leader = VMobject().set_points_smoothly([a, p_a, p_l, label_pos])
    leader.set_stroke(color, 1.4, opacity=0.7)
    edge = LEFT if label_pos[0] > a[0] else RIGHT
    lab = m_text(label, scale=0.32, color=color).move_to(label_pos, aligned_edge=edge)
    read = m_text(readout, scale=0.23, color=TONE_MUTED)
    read.next_to(lab, DOWN, buff=0.08, aligned_edge=edge)
    return VGroup(leader, dot, lab, read)
