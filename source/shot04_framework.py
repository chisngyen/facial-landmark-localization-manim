"""
Shot 09 — §12.2 Framework: 2-stage pipeline (local detectors + shape constraint).

Plays between shot02 and shot03 in the final concat order.
"""
from manimlib import *

import os, sys, pathlib
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_FG, TONE_MUTED, TONE_RED, TONE_GREY,
    MuseumScene, m_text, HERO_FRONTAL, HERO_WITH_LANDMARKS_BAKED,
    ChapterRibbon,
)

_ASSETS = pathlib.Path(__file__).parent.parent / "assets" / "shot03v2"


class Section01_Shot04_Framework(MuseumScene):
    """§12.2 — Inside the localization framework."""

    def construct(self):
        self.add_museum_bg(accent="amber")

        # Section heading top-left — persistent chapter ribbon
        ribbon = ChapterRibbon(section="framework")
        self.add(ribbon)
        self.wait(0.13)

        # Centerpiece question
        q = m_text("How does the system actually work?",
                   scale=0.78, color=TONE_FG)
        self.play(FadeIn(q, scale=1.04), run_time=1.0)
        self.wait(1.67)
        self.play(FadeOut(q, shift=0.2 * UP), run_time=0.6)

        # ---- Beat 1: Two-stage pipeline ----
        # [Image] → [Local feature detector] → [Shape constraint] → [Landmarks]
        def stage_box(label, accent, sub=None):
            box = RoundedRectangle(width=2.7, height=1.1, corner_radius=0.10)
            box.set_stroke(accent, 2.2).set_fill("#0c0c14", 0.0)
            t = m_text(label, scale=0.44, color=accent)
            t.move_to(box.get_center() + (UP * 0.10 if sub else 0))
            grp = VGroup(box, t)
            if sub:
                st = m_text(sub, scale=0.28, color=TONE_MUTED)
                st.next_to(t, DOWN, buff=0.12)
                grp.add(st)
            return grp

        b1 = stage_box("image", TONE_MUTED, sub="raw pixels")
        b2 = stage_box("local detectors", TONE_CYAN, sub="per-landmark")
        b3 = stage_box("ASM constraint", TONE_AMBER, sub="shape prior")
        b4 = stage_box("landmarks", TONE_FG, sub="aligned output")

        boxes = [b1, b2, b3, b4]
        xs = [-5.5, -1.85, 1.85, 5.5]
        for b, x in zip(boxes, xs):
            b.move_to(np.array([x, 1.2, 0]))

        # Arrows between boxes
        def arrow_between(a, b, color):
            return Arrow(
                start=a.get_right() + RIGHT * 0.05,
                end=b.get_left() + LEFT * 0.05,
                buff=0,
                stroke_width=3.0,
                color=color,
            )

        arrows = [
            arrow_between(b1, b2, TONE_MUTED),
            arrow_between(b2, b3, TONE_CYAN),
            arrow_between(b3, b4, TONE_AMBER),
        ]

        # Reveal pipeline boxes + arrows — boxes scale-up from 95% instead of shift
        def box_scale_in(box, run_time):
            box.scale(0.95).set_opacity(0)
            return box.animate.scale(1 / 0.95).set_opacity(1)

        self.wait(0.16)  # __TRANS_HOLD__
        self.play(box_scale_in(b1, 0.847), run_time=0.847, rate_func=smooth)
        self.play(GrowArrow(arrows[0]), box_scale_in(b2, 1.036),
                  run_time=1.036, rate_func=smooth)
        self.play(GrowArrow(arrows[1]), box_scale_in(b3, 1.036),
                  run_time=1.036, rate_func=smooth)
        self.play(GrowArrow(arrows[2]), box_scale_in(b4, 1.036),
                  run_time=1.036, rate_func=smooth)

        # Caption under pipeline
        cap = m_text("two stages — detect locally,  constrain globally",
                     scale=0.42, color=TONE_AMBER)
        cap.move_to(np.array([0, 0.20, 0]))
        self.play(FadeIn(cap, shift=0.08 * UP), run_time=0.7)
        self.wait(2.5)

        # ---- Beat 2: training flow — abstract diagram below pipeline ----
        # 3 annotated face thumbnails → arrow → "PCA" → mean shape + eigenmodes
        train_label = m_text("training", scale=0.44, color=TONE_CYAN)
        train_label.move_to(np.array([-5.5, -0.80, 0]))
        train_label.set_opacity(0.85)

        # Mini face thumbnails (3 stacked at left)
        thumbs = Group()
        for i, p in enumerate([HERO_FRONTAL, HERO_FRONTAL, HERO_FRONTAL]):
            try:
                img = ImageMobject(p).set_height(0.95)
            except Exception:
                img = Square(side_length=0.95).set_stroke(TONE_GREY, 1.5).set_fill("#1a1a22", 1.0)
            img.move_to(np.array([-4.6 + i * 0.30, -1.90 + i * 0.20, 0]))
            thumbs.add(img)

        annot_dots = VGroup()
        for x_off, y_off in [(-4.6, -1.90), (-4.3, -1.70), (-4.0, -1.50)]:
            # Few dots per thumbnail to suggest landmarks
            for dx, dy in [(-0.18, 0.10), (0.18, 0.10), (0.00, -0.05), (0.00, -0.20)]:
                annot_dots.add(Dot(radius=0.025, color=TONE_AMBER)
                               .move_to(np.array([x_off + dx, y_off + dy, 0])))

        # PCA box mid
        pca = stage_box("PCA", TONE_AMBER, sub="eigendecomposition")
        pca.scale(0.85).move_to(np.array([-1.0, -1.80, 0]))

        # Output: mean + eigenmodes label
        out_label = m_text("mean  +  eigenmodes", scale=0.42, color=TONE_FG)
        out_label.move_to(np.array([3.3, -1.80, 0]))

        # Arrows
        arr_t1 = arrow_between(thumbs[-1], pca, TONE_CYAN)
        # thumbs is a Group, can't use get_right cleanly — define manually
        arr_t1 = Arrow(
            start=np.array([-3.5, -1.65, 0]),
            end=pca.get_left() + LEFT * 0.05,
            buff=0,
            stroke_width=2.6,
            color=TONE_CYAN,
        )
        arr_t2 = Arrow(
            start=pca.get_right() + RIGHT * 0.05,
            end=np.array([2.0, -1.80, 0]),
            buff=0,
            stroke_width=2.6,
            color=TONE_AMBER,
        )

        self.play(
            FadeIn(train_label, shift=0.05 * DOWN),
            LaggedStartMap(FadeIn, thumbs, lag_ratio=0.20),
            run_time=1.695,
        )
        self.play(FadeIn(annot_dots), run_time=0.753)
        self.play(GrowArrow(arr_t1), FadeIn(pca, scale=0.95), run_time=1.318)
        self.play(GrowArrow(arr_t2), FadeIn(out_label, shift=0.08 * RIGHT), run_time=1.318)

        # Dashed link from "local detectors" box down to PCA — visual bridge
        dashed_link = DashedLine(
            start=b2.get_bottom() + DOWN * 0.05,
            end=pca.get_top() + UP * 0.05,
            dash_length=0.10,
        ).set_stroke(TONE_CYAN, 1.8).set_opacity(0.75)
        self.play(ShowCreation(dashed_link), run_time=0.6)
        self.wait(2.12)

        # Final takeaway
        takeaway = m_text(
            "model built once,  reused on every new face",
            scale=0.48, color=TONE_AMBER,
        ).to_edge(DOWN, buff=0.30)
        self.play(FadeIn(takeaway, shift=0.10 * UP), run_time=0.8)
        self.wait(3.15)

        # Fade out everything (ribbon stays — persistent UI)
        all_mobs = VGroup(cap, takeaway, train_label, out_label, dashed_link)
        for b in boxes:
            all_mobs.add(b)
        for a in arrows + [arr_t1, arr_t2]:
            all_mobs.add(a)
        all_mobs.add(annot_dots, pca)
        self.play(FadeOut(all_mobs), FadeOut(thumbs), run_time=1.318)
