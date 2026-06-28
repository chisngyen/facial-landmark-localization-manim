"""
Shot 10 — algorithm in action: iterations 0→15 with face + landmarks + residual + b bars.

Render:
    "D:/Downloads/Tools/Anaconda/Scripts/manimgl.exe" source/shot10_AlgorithmWalkthrough.py \
        Section01_Shot08_AlgorithmWalkthrough -w -l --video_dir videos --file_name shot10_AlgorithmWalkthrough
"""
from manimlib import *

import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    MuseumScene, m_text, TONE_CYAN, TONE_AMBER, TONE_FG, TONE_MUTED,
    HERO_FRONTAL,
    ChapterRibbon,
)


class Section01_Shot08_AlgorithmWalkthrough(MuseumScene):
    def construct(self):
        self.add_museum_bg(accent="amber")

        ribbon = ChapterRibbon(section="12.4 · algorithm in action")
        self.add(ribbon)

        # ---- Header ----
        header = m_text("algorithm in action", scale=0.42, color=TONE_FG)
        header.to_edge(UP, buff=0.25).to_edge(LEFT, buff=0.40)
        update_rule_lbl = m_text("update rule", scale=0.34, color=TONE_MUTED)
        update_rule_lbl.to_edge(UP, buff=0.25).to_edge(RIGHT, buff=0.40)
        update_rule = m_text("b_(t+1) = P^T (x_t − x̄)", scale=0.46, color=TONE_AMBER)
        update_rule.next_to(update_rule_lbl, DOWN, aligned_edge=RIGHT, buff=0.10)
        update_rule_sub = m_text("project residual onto principal modes", scale=0.30, color=TONE_MUTED)
        update_rule_sub.next_to(update_rule, DOWN, aligned_edge=RIGHT, buff=0.05)
        self.play(FadeIn(header), FadeIn(update_rule_lbl), FadeIn(update_rule),
                  FadeIn(update_rule_sub), run_time=0.5)

        # ---- ASM fitting sequence (Three.js render) on the right ----
        ASM_DIR = os.path.join(os.path.dirname(_THIS_DIR), "assets", "apps", "seq", "asm")
        converge_frames = []
        i = 0
        while True:
            p = os.path.join(ASM_DIR, f"frame_{i:03d}.png")
            if not os.path.exists(p):
                break
            img = ImageMobject(p).set_height(5.6)
            img.move_to(np.array([3.1, -0.1, 0]))
            img.set_opacity(0)
            converge_frames.append(img)
            i += 1
        self.add(*converge_frames)
        # Show frame 0 (mean-shape init)
        converge_frames[0].set_opacity(1)
        self.play(converge_frames[0].animate.set_opacity(1), run_time=0.6)
        last_visible_frame = 0

        # ---- Iteration counter (large amber number) ----
        iter_label = m_text("iteration", scale=0.40, color=TONE_MUTED)
        iter_label.move_to(np.array([-4.0, 2.0, 0]))
        iter_tracker = ValueTracker(0)
        iter_num = DecimalNumber(0, num_decimal_places=0, color=TONE_AMBER, font_size=66)
        iter_num.move_to(np.array([-4.0, 1.3, 0]))
        iter_num.add_updater(lambda m: m.set_value(int(iter_tracker.get_value())))
        cur_state = m_text("init (mean shape)", scale=0.36, color=TONE_FG)
        cur_state.move_to(np.array([-4.0, 0.65, 0]))
        self.play(FadeIn(iter_label), FadeIn(iter_num), FadeIn(cur_state), run_time=0.5)
        self.wait(0.26)

        # ---- Residual chart ----
        chart_box = Rectangle(width=2.6, height=1.4).set_stroke(TONE_FG, 1.6).set_fill(opacity=0)
        chart_box.move_to(np.array([-4.0, -0.7, 0]))
        chart_label = m_text("residual  e", scale=0.32, color=TONE_CYAN)
        chart_label.next_to(chart_box, UP, aligned_edge=LEFT, buff=0.10)
        iter_axis_label = m_text("iter", scale=0.26, color=TONE_MUTED)
        iter_axis_label.next_to(chart_box, RIGHT, buff=0.05)
        self.play(FadeIn(chart_box), FadeIn(chart_label), FadeIn(iter_axis_label), run_time=0.5)

        # ---- Shape b bars ----
        # Bars grow UPWARD from baseline. Label must go BELOW the baseline so it
        # doesn't get covered when bars grow tall (max bar height ~0.85).
        BARS_BASELINE_Y = -2.50
        bar_colors = [TONE_AMBER, TONE_CYAN, TONE_FG]
        bars = VGroup()
        for i, col in enumerate(bar_colors):
            r = Rectangle(width=0.30, height=0.05)
            r.set_fill(col, 1.0).set_stroke(width=0)
            r.move_to(np.array([-4.7 + i*0.40, BARS_BASELINE_Y, 0]), aligned_edge=DOWN)
            bars.add(r)
        # Label BELOW baseline — clear of growing bars.
        bars_label = m_text("shape  b₁ , b₂ , b₃", scale=0.30, color=TONE_MUTED)
        bars_label.move_to(np.array([-4.0, BARS_BASELINE_Y - 0.30, 0]))
        self.play(FadeIn(bars_label), FadeIn(bars), run_time=0.5)
        self.wait(0.14)

        # ---- Animate iterations 1 → 15 ----
        # Generate progressively converged positions and update everything in steps
        residual_pts = [chart_box.get_corner(UL) + np.array([0.1, -0.1, 0])]
        residual_curve = VMobject().set_stroke(TONE_CYAN, 3.0)
        residual_curve.set_points_as_corners([residual_pts[0], residual_pts[0]])
        self.add(residual_curve)

        target_b_heights = [0.85, 0.55, 0.30]  # final bar heights

        key_frames = [3, 7, 11, 14]
        state_labels = {3: "shape prior pulls back", 7: "converging", 11: "almost there", 14: "settled"}

        for it in range(1, 15):
            frac = it / 14.0
            # Faster animations at later iterations
            rt = 0.55 if it in key_frames else 0.18

            # Update iteration counter (clean count-up — no glyph-morph garble)
            anims = [iter_tracker.animate.set_value(it)]
            if it in state_labels:
                new_state = m_text(state_labels[it], scale=0.36, color=TONE_FG).move_to(cur_state.get_center())
                anims.append(FadeOut(cur_state))
                anims.append(FadeIn(new_state))
                cur_state = new_state

            # Map iteration → frame in the 40-frame ASM fit sequence
            target_idx = min(int(round((it / 14.0) * (len(converge_frames) - 1))),
                             len(converge_frames) - 1)
            if target_idx != last_visible_frame:
                anims.append(converge_frames[last_visible_frame].animate.set_opacity(0))
                anims.append(converge_frames[target_idx].animate.set_opacity(1))
                last_visible_frame = target_idx

            # Grow bars
            new_bars = VGroup()
            for i, col in enumerate(bar_colors):
                h = 0.05 + target_b_heights[i] * frac
                r = Rectangle(width=0.30, height=h).set_fill(col, 1.0).set_stroke(width=0)
                r.move_to(np.array([-4.7 + i*0.40, BARS_BASELINE_Y, 0]), aligned_edge=DOWN)
                new_bars.add(r)
            anims.append(Transform(bars, new_bars))

            self.play(*anims, run_time=rt, rate_func=linear if it not in key_frames else smooth)

            # Extend residual curve
            box_l = chart_box.get_left()[0]
            box_b = chart_box.get_bottom()[1]
            box_w = chart_box.get_width()
            box_h = chart_box.get_height()
            x = box_l + 0.10 + (it / 14) * (box_w - 0.15)
            # Residual drops fast at first then plateaus
            y = box_b + 0.05 + (box_h - 0.1) * (1.0 - frac**0.6)
            residual_pts.append(np.array([x, y, 0]))
            residual_curve.set_points_as_corners(residual_pts)

        self.wait(0.18)

        # Final caption
        final_cap = m_text("from rough init  →  fit in  ~14 iterations",
                           scale=0.46, color=TONE_AMBER)
        final_cap.to_edge(DOWN, buff=0.40)
        self.play(FadeIn(final_cap, shift=0.10*UP), run_time=0.5)
        self.wait(0.35)

        iter_num.clear_updaters()
        self.play(FadeOut(Group(header, update_rule_lbl, update_rule, update_rule_sub,
                                *converge_frames, iter_label, iter_num, cur_state, chart_box,
                                chart_label, iter_axis_label, bars_label, bars,
                                residual_curve, final_cap)),
                  run_time=0.6)
