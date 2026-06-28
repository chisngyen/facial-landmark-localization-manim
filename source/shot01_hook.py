"""
Shot 01 — Hook (§12.1 intro): "How do you put 88 dots exactly on a face?"
→ scattered-dot morph reveal → hero face + HUD callouts.
(Source recovered 2026-06-03 from bytecode after a rename mishap; verified by re-render.)
"""
from manimlib import *

import os, sys, pathlib, json

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    MuseumScene, m_text, ChapterRibbon, typewriter_anim, count_up,
    TONE_AMBER, TONE_MUTED, TONE_FG, TONE_CYAN,
    HERO_FRONTAL, HERO_WITH_LANDMARKS_BAKED,
    FACE_EYE_L_UV, FACE_NOSE_UV, FACE_MOUTH_UV,
)
from dot_morph import make_target_face_canonical
from hero_kit import add_tech_atmosphere, hud_callout

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


class Section01_Shot01_Hook(MuseumScene):
    def construct(self):
        self.add_museum_bg(accent="amber")
        ribbon = ChapterRibbon(section=None)
        self.add(ribbon)

        # ---- Phase 1: the question + an "88 dots" counter ----
        q1 = m_text("How do you put", scale=0.55, color=TONE_MUTED)
        q3 = m_text("exactly on a face?", scale=0.8, color=TONE_AMBER)
        q2_anchor = m_text("88 dots", scale=1.2, color=TONE_AMBER)
        q1.move_to(np.array([0.0, 1.0, 0.0]))
        q2_anchor.next_to(q1, DOWN, buff=0.25)

        n_tracker = ValueTracker(1)
        n_label = DecimalNumber(88, num_decimal_places=0, color=TONE_AMBER)
        n_label.set_height(q2_anchor.get_height())
        dots_text = m_text("dots", scale=1.2, color=TONE_AMBER)
        counter_group = VGroup(n_label, dots_text).arrange(RIGHT, buff=0.25)
        counter_group.move_to(q2_anchor.get_center())
        _counter_center = counter_group.get_center()
        n_label.set_value(1)

        def _update_counter(m):
            m.set_value(int(n_tracker.get_value()))
            counter_group.arrange(RIGHT, buff=0.25)
            counter_group.move_to(_counter_center)

        n_label.add_updater(_update_counter)
        q3.next_to(counter_group, DOWN, buff=0.30)
        q_group = Group(q1, counter_group, q3)

        self.play(FadeIn(q1, shift=0.10 * UP), run_time=0.50)
        self.add(counter_group)
        self.play(count_up(n_tracker, 88, duration=1.1, ease=smooth), run_time=1.1)
        n_label.clear_updaters()
        self.wait(0.28)
        self.play(FadeIn(q3, shift=0.10 * UP), run_time=0.50)
        self.wait(2.0)   # VO: "...has to find the parts." (+4.4) holds the question

        # ---- Phase 2: question fades out CLEANLY before face appears ----
        self.play(q_group.animate.set_opacity(0.0), run_time=0.60)
        self.remove(q_group)

        # ---- Phase 3: morph reveal — scattered dots fly in to landmark positions ----
        # Use the CLEAN hero v3 face (no baked dots) for base, and the with-landmarks
        # variant for the final cross-fade target.
        FACE_H = 5.4
        FACE_CENTER = np.array([0.0, -0.4, 0.0])
        base_img = ImageMobject(HERO_FRONTAL).set_height(FACE_H).move_to(FACE_CENTER)
        final_img = ImageMobject(HERO_WITH_LANDMARKS_BAKED).set_height(FACE_H).move_to(FACE_CENTER)
        base_img.set_opacity(0.0)
        final_img.set_opacity(0.0)
        # Only add base_img now; defer final_img until cross-fade so its baked
        # dots can't leak through during morph reveal.
        # BOLD: drifting tech atmosphere sits BEHIND the face.
        grid, particles, _atm = add_tech_atmosphere(self, n_particles=30)
        self.add(base_img)

        # Phase 3a: face fades in, then eye→nose→mouth light up in sync with the VO
        self.play(base_img.animate.set_opacity(1.0), run_time=0.80)

        def _uv_pt(img, uv):
            ul = img.get_corner(UL)
            return ul + np.array([uv[0] * img.get_width(), -uv[1] * img.get_height(), 0.0])

        def _marker(uv, color):
            ring = Circle(radius=0.42, color=color).set_stroke(color, 3.0)
            ring.move_to(_uv_pt(base_img, uv)).set_fill(color, 0.0)
            return ring

        eye_m = _marker(FACE_EYE_L_UV, TONE_AMBER)
        nose_m = _marker(FACE_NOSE_UV, TONE_CYAN)
        mouth_m = _marker(FACE_MOUTH_UV, TONE_AMBER)
        region_markers = Group(eye_m, nose_m, mouth_m)

        self.wait(0.9)                              # → VO "the eyes" (+6.7)
        self.play(ShowCreation(eye_m), run_time=0.4)
        self.wait(1.6)                              # → VO "the nose" (+8.7)
        self.play(ShowCreation(nose_m), run_time=0.4)
        self.wait(1.2)                              # → VO "the mouth" (+10.3)
        self.play(ShowCreation(mouth_m), run_time=0.4)
        self.wait(2.5)                              # hold → VO "88 tiny points" (+13.2)

        # Compute landmark targets (canonical 88 — matches shot03)
        targets_2d = make_target_face_canonical(
            face_center=(FACE_CENTER[0], FACE_CENTER[1]),
            face_height=FACE_H,
        )
        targets = [np.array([p[0], p[1], 0.0]) for p in targets_2d]

        # Create dots at scattered START positions (NOT added to scene yet)
        rng = np.random.default_rng(42)
        dots = []
        for tgt in targets:
            theta = rng.uniform(0, 2*np.pi)
            r = rng.uniform(4.5, 6.5)
            start = FACE_CENTER + np.array([r*np.cos(theta), r*np.sin(theta), 0.0])
            d = Dot(point=start, radius=0.045, color="#fff0c8").set_stroke(width=0)
            dots.append(d)
        dot_group = Group(*dots)

        # Phase 3b: dots FadeIn at scattered ring positions (FadeIn handles add + fade)
        self.play(
            LaggedStartMap(FadeIn, dot_group, lag_ratio=0.008),
            FadeOut(region_markers),
            run_time=0.50,
        )

        # Phase 3c: MORPH — build anims INSIDE the play call (avoid pre-collecting
        # `.animate.move_to(tgt)` which can mutate position before play in some
        # versions of ManimGL).
        self.play(
            LaggedStart(
                *[d.animate.move_to(tgt) for d, tgt in zip(dots, targets)],
                lag_ratio=0.004,
            ),
            run_time=1.3,   # VO: "Eighty-eight tiny points"
            rate_func=smooth,
        )
        # Tiny settle pulse
        self.play(dot_group.animate.scale(1.25), run_time=0.10)
        self.play(dot_group.animate.scale(1/1.25), run_time=0.15)

        # Phase 3d: cross-fade Manim dots → baked landmark image
        self.add(final_img)
        self.play(
            final_img.animate.set_opacity(1.0),
            base_img.animate.set_opacity(0.0),
            FadeOut(dot_group),
            run_time=0.45,
        )
        self.remove(dot_group, base_img)
        self.wait(0.2)

        # ---- Phase 4 (BOLD hero reveal): face slides into hero pose, HUD + title ----
        self.play(
            final_img.animate.set_height(6.6).move_to(np.array([3.0, 0.05, 0])),
            run_time=0.7, rate_func=smooth,
        )
        # All callouts stacked on the LEFT (right-aligned → text stays in frame),
        # below the title block — no overlap with subtitle, nothing off-screen.
        hud = [
            hud_callout(final_img, FACE_EYE_L_UV, "EYE REGION", "12 pts · ±0.8px",
                        np.array([-2.8, 1.25, 0]), TONE_AMBER),
            hud_callout(final_img, FACE_NOSE_UV, "NOSE BRIDGE", "5 pts",
                        np.array([-2.8, -0.15, 0]), TONE_CYAN),
            hud_callout(final_img, FACE_MOUTH_UV, "MOUTH CONTOUR", "18 pts",
                        np.array([-2.8, -1.55, 0]), TONE_AMBER),
            hud_callout(final_img, (0.41, 0.78), "JAWLINE", "17 pts",
                        np.array([-2.8, -2.95, 0]), TONE_CYAN),
        ]
        for h in hud:
            self.play(ShowCreation(h[0]), FadeIn(h[1], scale=0.5),
                      FadeIn(h[2], shift=0.1 * RIGHT), FadeIn(h[3]), run_time=0.18)

        t1 = m_text("88 LANDMARKS", scale=0.62, color=TONE_FG)
        t2 = m_text("ONE FACE", scale=0.62, color=TONE_AMBER)
        t1.to_corner(UL, buff=0.7)
        t2.next_to(t1, DOWN, buff=0.14, aligned_edge=LEFT)
        rule = Line(t2.get_left(), t2.get_left() + RIGHT * 3.4).set_stroke(TONE_AMBER, 2.0)
        rule.next_to(t2, DOWN, buff=0.20, aligned_edge=LEFT)
        sub = m_text("placed by hand — before neural networks could even try.",
                     scale=0.30, color=TONE_MUTED)
        sub.next_to(rule, DOWN, buff=0.18, aligned_edge=LEFT)
        self.play(Write(t1), run_time=0.35)
        self.play(Write(t2), run_time=0.3)
        self.play(ShowCreation(rule), FadeIn(sub, shift=0.08 * RIGHT), run_time=0.35)
        self.wait(0.2)   # VO: "...under a tenth of a second." + absorb

        # ---- Phase 5: fade out ----
        grid.clear_updaters(); particles.clear_updaters()
        self.play(
            *[FadeOut(m) for m in [final_img, grid, particles, t1, t2, rule, sub, *hud]],
            run_time=0.5,
        )
