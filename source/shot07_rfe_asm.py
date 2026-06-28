"""Shot 05 v2 — Active Shape Model walk-through.

Render:
    "D:/Downloads/Tools/Anaconda/Scripts/manimgl.exe" \
        source/shot05_RFE_ASM.py Section01_Shot07_RFE_ASM \
        -w -l --video_dir videos --file_name shot05_RFE_ASM

Replaces shot05_RFE_ASM (kept as fallback).
"""
from manimlib import *
import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    MuseumScene, m_text,
    TONE_CYAN, TONE_AMBER, TONE_FG, TONE_MUTED,
    ChapterRibbon,
)
from asm_modes import (MEAN_SHAPE_88, N, FACE_HEIGHT,
                       apply_all_modes)

ASM_RED    = "#ff6060"
ASM_VIOLET = "#a070ff"


class Section01_Shot07_RFE_ASM(MuseumScene):
    """Six-phase ASM walk-through. ≈ 42 s total."""

    def construct(self):
        self.add_museum_bg(accent="amber")

        ribbon = ChapterRibbon(section="12.4 · active shape model")
        self.add(ribbon)

        # ============================================================
        # Phase 0 (0.0 – 3.0 s) — formula title + subtitle
        # ============================================================
        f_x   = m_text("x",   scale=0.85, color=TONE_CYAN)
        f_eq  = m_text("=",   scale=0.85, color=TONE_FG)
        f_xb  = m_text("x̄",   scale=0.85, color=TONE_FG)
        f_plus= m_text("+",   scale=0.85, color=TONE_FG)
        f_phi = m_text("Φ",   scale=0.85, color=ASM_RED)
        f_dot = m_text("·",   scale=0.85, color=TONE_FG)
        f_b   = m_text("b",   scale=0.85, color=ASM_VIOLET)
        formula = VGroup(f_x, f_eq, f_xb, f_plus, f_phi, f_dot, f_b)
        formula.arrange(RIGHT, buff=0.25)
        formula.move_to(np.array([0, 2.8, 0]))
        sub = m_text("Active Shape Model: any face = mean + Σ b_k · φ_k",
                     scale=0.32, color=TONE_MUTED)
        sub.next_to(formula, DOWN, buff=0.25)
        self.play(FadeIn(formula, shift=0.1*DOWN), run_time=0.8)
        self.play(FadeIn(sub), run_time=0.5)
        self.wait(9.0)   # formula holds — VO "...mean face plus a few learned adjustments." (→ mean +10.3)

        # ============================================================
        # Phase 1 (3.0 – 8.0 s) — mean face (white dots) appears
        # ============================================================
        face_center_y = -0.3
        white_dots = VGroup(*[
            Dot(point=np.array([MEAN_SHAPE_88[i, 0],
                                MEAN_SHAPE_88[i, 1] + face_center_y, 0]),
                radius=0.045)
            .set_fill(TONE_FG, 1.0).set_stroke(width=0)
            .set_opacity(0.0)
            for i in range(N)
        ])
        self.add(white_dots)
        self.play(LaggedStartMap(lambda m: m.animate.set_opacity(0.85),
                                 white_dots, lag_ratio=0.015),
                  run_time=1.2)
        xbar_label = m_text("x̄  — mean shape", scale=0.28, color=TONE_FG)
        xbar_label.move_to(np.array([1.95, 0.95, 0]), aligned_edge=LEFT)
        xbar_lead = Line(
            np.array([1.92, 0.90, 0]),
            np.array([1.55, 0.55, 0]),
            color=TONE_MUTED, stroke_width=1.0,
        ).set_opacity(0.55)
        self.play(FadeIn(xbar_label), ShowCreation(xbar_lead), run_time=0.5)
        caption = m_text("the mean shape — same for everyone",
                         scale=0.32, color=TONE_FG)
        caption.move_to(np.array([0, -3.5, 0]))
        self.play(FadeIn(caption), run_time=0.4)
        self.wait(1.6)   # mean shape — VO "...the same for everyone." (→ mode 1 +14.0)

        # Stash for later phases.
        self._formula = formula
        self._sub = sub
        self._white_dots = white_dots
        self._xbar_label = xbar_label
        self._xbar_lead = xbar_lead
        self._caption = caption
        self._face_center_y = face_center_y

        # ============================================================
        # Phase 2 (8.0 – 18.0 s) — Mode 1 (width): b₁ slider runs
        # ============================================================
        cyan_dots = VGroup(*[
            Dot(point=np.array([MEAN_SHAPE_88[i, 0],
                                MEAN_SHAPE_88[i, 1] + self._face_center_y, 0]),
                radius=0.045)
            .set_fill(TONE_CYAN, 1.0).set_stroke(width=0)
            .set_opacity(0.0)
            for i in range(N)
        ])
        self.add(cyan_dots)
        self.play(
            *[d.animate.set_opacity(1.0) for d in cyan_dots],
            *[d.animate.set_opacity(0.40) for d in self._white_dots],
            run_time=0.6,
        )
        self.play(FadeOut(self._caption), run_time=0.3)

        def make_slider(b_label_text, color, y_pos, label_text_color=None):
            x_left, x_right = -4.5, -2.0
            track = Line(np.array([x_left, y_pos, 0]),
                         np.array([x_right, y_pos, 0]))
            track.set_stroke(TONE_MUTED, 1.6).set_opacity(0.7)
            ticks = VGroup()
            for tx in (x_left, (x_left + x_right) / 2, x_right):
                tick = Line(np.array([tx, y_pos - 0.06, 0]),
                            np.array([tx, y_pos + 0.06, 0]))
                tick.set_stroke(TONE_MUTED, 1.4)
                ticks.add(tick)
            handle = Dot(point=np.array([(x_left + x_right) / 2, y_pos, 0]),
                         radius=0.075).set_fill(color, 1.0).set_stroke(width=0)
            label = m_text(b_label_text, scale=0.30,
                           color=label_text_color if label_text_color else color)
            label.move_to(np.array([x_left - 0.40, y_pos, 0]), aligned_edge=RIGHT)
            return track, ticks, handle, label, x_left, x_right

        def slider_x(handle_track_left, handle_track_right, b):
            t = (b + 2.0) / 4.0
            return handle_track_left + t * (handle_track_right - handle_track_left)

        s1_track, s1_ticks, s1_handle, s1_label, s1L, s1R = make_slider(
            "b₁", ASM_VIOLET, y_pos=-2.60)
        s1_track.set_stroke(ASM_VIOLET, 1.6)
        self.play(ShowCreation(s1_track), FadeIn(s1_ticks),
                  FadeIn(s1_handle), FadeIn(s1_label), run_time=0.5)

        mode_label = m_text("mode 1: width", scale=0.32, color=TONE_AMBER)
        mode_label.move_to(np.array([-3.25, -2.15, 0]))
        self.play(FadeIn(mode_label), run_time=0.4)

        phi_label = m_text("Φ  =", scale=0.32, color=ASM_RED)
        phi_label.move_to(np.array([2.2, -2.5, 0]), aligned_edge=RIGHT)
        cols = VGroup()
        for k in range(4):
            col_x = 2.5 + k * 0.55
            col = m_text(f"φ{['₁','₂','₃','₄'][k]}", scale=0.32, color=ASM_RED)
            col.move_to(np.array([col_x, -2.5, 0]))
            cols.add(col)
        phi_group = VGroup(phi_label, cols)
        self.play(FadeIn(phi_group), run_time=0.4)
        col1_box = SurroundingRectangle(cols[0], color=ASM_RED, buff=0.10,
                                        stroke_width=2.0).set_opacity(0.7)
        self.play(ShowCreation(col1_box), run_time=0.3)

        from asm_modes import apply_mode_1_width
        def deform_to_b1(b_val, run_time):
            new_pts = apply_mode_1_width(MEAN_SHAPE_88, b_val)
            self.play(
                s1_handle.animate.move_to(np.array([slider_x(s1L, s1R, b_val),
                                                     -2.60, 0])),
                *[cyan_dots[i].animate.move_to(np.array([new_pts[i, 0],
                                                          new_pts[i, 1] + self._face_center_y,
                                                          0]))
                  for i in range(N)],
                run_time=run_time,
            )
        deform_to_b1(+2.0, 1.8)   # slider sweeps with VO "...wider,
        deform_to_b1( 0.0, 1.3)
        deform_to_b1(-2.0, 1.8)   # ...then narrower."
        deform_to_b1(+0.8, 1.3)
        self.wait(2.7)            # → mode 2 height +25.4

        # Make make_slider and slider_x available to subsequent phases.
        self._make_slider = make_slider
        self._slider_x = slider_x
        self._cyan_dots = cyan_dots
        self._mode_label = mode_label
        self._b1_track = s1_track
        self._b1_ticks = s1_ticks
        self._b1_handle = s1_handle
        self._b1_label = s1_label
        self._phi_group = phi_group
        self._phi_cols = cols
        self._col_box = col1_box
        self._b_state = [0.8, 0.0, 0.0, 0.0]

        # ============================================================
        # Phase 3 (≈18 – 26 s) — Mode 2 (height): b₂ slider runs
        # ============================================================
        s2_track, s2_ticks, s2_handle, s2_label, s2L, s2R = make_slider(
            "b₂", ASM_VIOLET, y_pos=-2.95)
        s2_track.set_stroke(ASM_VIOLET, 1.6)
        self.play(ShowCreation(s2_track), FadeIn(s2_ticks),
                  FadeIn(s2_handle), FadeIn(s2_label), run_time=0.5)

        new_mode_label = m_text("mode 2: height", scale=0.32, color=TONE_AMBER)
        new_mode_label.move_to(np.array([-3.25, -2.15, 0]))
        self.play(Transform(self._mode_label, new_mode_label), run_time=0.4)

        col2_box = SurroundingRectangle(self._phi_cols[1], color=ASM_RED,
                                        buff=0.10, stroke_width=2.0).set_opacity(0.7)
        self.play(Transform(self._col_box, col2_box), run_time=0.4)

        def deform_b1b2(b2_val, run_time):
            self._b_state[1] = b2_val
            new_pts = apply_all_modes(MEAN_SHAPE_88, self._b_state)
            self.play(
                s2_handle.animate.move_to(np.array([slider_x(s2L, s2R, b2_val),
                                                     -2.95, 0])),
                *[self._cyan_dots[i].animate.move_to(np.array([new_pts[i, 0],
                                                                 new_pts[i, 1] + self._face_center_y,
                                                                 0]))
                  for i in range(N)],
                run_time=run_time,
            )
        deform_b1b2(+1.5, 1.3)   # VO "...height — taller,
        deform_b1b2(0.0, 0.9)
        deform_b1b2(-1.5, 1.3)   # ...then shorter."
        deform_b1b2(-0.5, 0.9)
        self.wait(1.2)           # → mode 3/4 +32.3

        self._b2_track = s2_track
        self._b2_ticks = s2_ticks
        self._b2_handle = s2_handle
        self._b2_label = s2_label

        # ============================================================
        # Phase 4 (≈26 – 34 s) — Modes 3 (smile) + 4 (brow) quick
        # ============================================================
        s3_track, s3_ticks, s3_handle, s3_label, s3L, s3R = make_slider(
            "b₃", ASM_VIOLET, y_pos=-3.25)
        s3_track.set_stroke(ASM_VIOLET, 1.6)
        self.play(ShowCreation(s3_track), FadeIn(s3_ticks),
                  FadeIn(s3_handle), FadeIn(s3_label), run_time=0.4)

        mode3_label = m_text("mode 3: smile", scale=0.32, color=TONE_AMBER)
        mode3_label.move_to(np.array([-3.25, -2.15, 0]))
        self.play(Transform(self._mode_label, mode3_label), run_time=0.3)
        col3_box = SurroundingRectangle(self._phi_cols[2], color=ASM_RED,
                                        buff=0.10, stroke_width=2.0).set_opacity(0.7)
        self.play(Transform(self._col_box, col3_box), run_time=0.3)

        def deform_b3(b3_val, run_time):
            self._b_state[2] = b3_val
            new_pts = apply_all_modes(MEAN_SHAPE_88, self._b_state)
            self.play(
                s3_handle.animate.move_to(np.array([slider_x(s3L, s3R, b3_val),
                                                     -3.25, 0])),
                *[self._cyan_dots[i].animate.move_to(np.array([new_pts[i, 0],
                                                                 new_pts[i, 1] + self._face_center_y,
                                                                 0]))
                  for i in range(N)],
                run_time=run_time,
            )
        deform_b3(+1.5, 0.8)
        deform_b3(0.0, 0.5)
        deform_b3(+0.8, 0.5)

        s4_track, s4_ticks, s4_handle, s4_label, s4L, s4R = make_slider(
            "b₄", ASM_VIOLET, y_pos=-3.55)
        s4_track.set_stroke(ASM_VIOLET, 1.6)
        self.play(ShowCreation(s4_track), FadeIn(s4_ticks),
                  FadeIn(s4_handle), FadeIn(s4_label), run_time=0.4)
        mode4_label = m_text("mode 4: brow lift", scale=0.32, color=TONE_AMBER)
        mode4_label.move_to(np.array([-3.25, -2.15, 0]))
        self.play(Transform(self._mode_label, mode4_label), run_time=0.3)
        col4_box = SurroundingRectangle(self._phi_cols[3], color=ASM_RED,
                                        buff=0.10, stroke_width=2.0).set_opacity(0.7)
        self.play(Transform(self._col_box, col4_box), run_time=0.3)

        def deform_b4(b4_val, run_time):
            self._b_state[3] = b4_val
            new_pts = apply_all_modes(MEAN_SHAPE_88, self._b_state)
            self.play(
                s4_handle.animate.move_to(np.array([slider_x(s4L, s4R, b4_val),
                                                     -3.55, 0])),
                *[self._cyan_dots[i].animate.move_to(np.array([new_pts[i, 0],
                                                                 new_pts[i, 1] + self._face_center_y,
                                                                 0]))
                  for i in range(N)],
                run_time=run_time,
            )
        deform_b4(+1.2, 0.8)
        deform_b4(+0.5, 0.5)
        self.wait(3.3)   # smile + brow shown — VO "...lifts the brows." (→ composite +40.7)

        # Stash s3/s4 mobjects for the final fade.
        self._s3 = (s3_track, s3_ticks, s3_handle, s3_label)
        self._s4 = (s4_track, s4_ticks, s4_handle, s4_label)

        # ============================================================
        # Phase 5 (≈34 – 40 s) — composite + amber pulse
        # ============================================================
        final_caption = m_text("any face = x̄ + Σ b_k · φ_k",
                               scale=0.40, color=TONE_AMBER)
        final_caption.move_to(np.array([0, -2.15, 0]))
        self.play(FadeOut(self._mode_label), FadeIn(final_caption), run_time=0.6)

        # Amber pulse on cyan dots.
        self.play(*[d.animate.set_fill(TONE_AMBER, 1.0) for d in self._cyan_dots],
                  run_time=0.5)
        self.wait(4.0)   # VO "That's the whole model. A mean shape and a handful of numbers..."
        self.play(*[d.animate.set_fill(TONE_CYAN, 1.0) for d in self._cyan_dots],
                  run_time=0.5)
        self.wait(4.2)   # VO "...Dial them in and you rebuild any face."

        # ============================================================
        # Phase 6 (≈40 – 42 s) — fade out
        # ============================================================
        s3_track, s3_ticks, s3_handle, s3_label = self._s3
        s4_track, s4_ticks, s4_handle, s4_label = self._s4
        all_vec = VGroup(
            self._formula, self._sub, self._xbar_label, self._xbar_lead, final_caption,
            self._b1_track, self._b1_ticks, self._b1_handle, self._b1_label,
            self._b2_track, self._b2_ticks, self._b2_handle, self._b2_label,
            s3_track, s3_ticks, s3_handle, s3_label,
            s4_track, s4_ticks, s4_handle, s4_label,
            self._phi_group, self._col_box,
        )
        all_dots = Group(*self._white_dots, *self._cyan_dots)
        self.play(FadeOut(all_vec), FadeOut(all_dots), run_time=0.7)
