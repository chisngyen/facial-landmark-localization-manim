"""
Shot 06 — Experiments (§12.5) — 3-beat plot sequence.
"""
from manimlib import *

import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_RED, TONE_FG, TONE_MUTED, TONE_GREY,
    MuseumScene, m_text,
    HERO_FRONTAL, HERO_YAW30_V3, ASSETS_DIR,
    ChapterRibbon, count_up, typewriter_anim,
)

_HERO_LIGHTING_SIDE_V3 = str(ASSETS_DIR / "hero_lighting_side_v3.png")


class Section01_Shot09_Experiments(MuseumScene):
    def construct(self):
        self.add_museum_bg(accent="amber")
        ribbon = ChapterRibbon(section="12.5 · experiments")
        self.add(ribbon)
        title = m_text("Experiments  —  RFE-ASM  vs  ASM",
                        color=TONE_FG).scale(0.62).to_edge(UP, buff=0.4)
        self.play(FadeIn(title), run_time=0.456)
        self.wait(3.6)   # VO "Does any of this actually work? Time to measure."

        def _legend(dot_colors_labels, x_anchor, y_anchor):
            """Build legend rows: small filled square swatch + label. Returns VGroup."""
            grp = VGroup()
            row_y = y_anchor
            for color, lbl in dot_colors_labels:
                d = Rectangle(width=0.40, height=0.18, fill_color=color,
                              fill_opacity=1.0, stroke_width=0)
                t = m_text(lbl, scale=0.42, color=color)
                d.move_to(np.array([x_anchor, row_y, 0]))
                t.next_to(d, RIGHT, buff=0.15)
                grp.add(d, t)
                row_y -= 0.50
            return grp

        def _axis_tick_labels(axes, x_vals, y_vals, x_off=0.30, y_off=0.30, scale=0.36):
            """Add numeric tick labels to a Manim Axes."""
            grp = VGroup()
            origin = axes.c2p(0, 0)
            for xv in x_vals:
                pt = axes.c2p(xv, 0)
                t = m_text(f"{xv:g}", scale=scale, color=TONE_MUTED).set_opacity(0.95)
                t.move_to(np.array([pt[0], pt[1] - y_off, 0]))
                grp.add(t)
            for yv in y_vals:
                pt = axes.c2p(0, yv)
                t = m_text(f"{yv:g}", scale=scale, color=TONE_MUTED).set_opacity(0.95)
                t.move_to(np.array([pt[0] - x_off, pt[1], 0]))
                grp.add(t)
            return grp

        # (per-landmark scatter moved to AFTER the bars — see "Beat 4" below, so the
        #  two error plots sit together at the end and datasets lead the section.)

        # --- Beat 2: per-dataset reveal — description + icon FIRST, then bars ---
        datasets = ["BioID", "FERET", "AR"]
        ds_descs = [
            "1521 portraits  .  controlled lighting",
            "14k images  .  pose + expression variation",
            "126 subjects  .  occlusion + illumination",
        ]
        asm_acc = [78, 82, 75]
        rfe_acc = [89, 93, 88]
        bar_w = 0.70
        baseline = -2.0
        scale_h = 26.0

        # Legend: grey swatch + "ASM"  /  amber swatch + "RFE-ASM" stacked
        _leg_grey_sw = Rectangle(width=0.40, height=0.20, fill_color=TONE_GREY,
                                 fill_opacity=0.90, stroke_width=0)
        _leg_grey_lbl = m_text("ASM",     scale=0.42, color=TONE_GREY)
        _leg_grey_lbl.next_to(_leg_grey_sw, RIGHT, buff=0.18)
        _leg_grey = VGroup(_leg_grey_sw, _leg_grey_lbl)

        _leg_amber_sw = Rectangle(width=0.40, height=0.20, fill_color=TONE_AMBER,
                                  fill_opacity=0.95, stroke_width=0)
        _leg_amber_lbl = m_text("RFE-ASM", scale=0.42, color=TONE_AMBER)
        _leg_amber_lbl.next_to(_leg_amber_sw, RIGHT, buff=0.18)
        _leg_amber = VGroup(_leg_amber_sw, _leg_amber_lbl)

        leg2 = VGroup(_leg_grey, _leg_amber).arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        leg2.to_edge(RIGHT, buff=0.55).shift(UP*1.8)
        # "head to head" — show the ASM vs RFE-ASM legend, then hold to the datasets (+11.4)
        self.play(FadeIn(leg2), run_time=0.45)   # VO "We put RFE-ASM head to head with plain ASM."
        self.wait(6.5)

        # ============================================================
        # Phase A v4: 3 datasets enter at center, slot into 2-top/1-bottom layout
        # ============================================================
        ds_section_header = m_text("the  3  datasets", scale=0.54, color=TONE_FG).to_edge(UP, buff=1.10)
        self.play(FadeIn(ds_section_header, shift=0.08*DOWN), run_time=0.45)

        _DS_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "datasets")

        # Final slot positions: 2 on top, 1 bottom-center
        slot_positions = [
            np.array([-3.7, 0.65, 0]),   # top-left  (BioID)
            np.array([+3.7, 0.65, 0]),   # top-right (FERET)
            np.array([ 0.0, -1.75, 0]),  # bottom-center (AR)
        ]
        center_entry = np.array([0, 0.30, 0])
        SLOT_SCALE = 0.78

        datasets_info = [
            ("bioid", "BioID  ·  controlled lighting",   1521,  "portraits"),
            ("feret", "FERET  ·  pose + expression",    14000,  "images"),
            ("ar",    "AR  ·  occlusion + illumination",  126,  "subjects"),
        ]

        def build_card(dataset_dir, label_text, stat_value, stat_suffix):
            """Build a card (thumb row + label + stat) positioned at center_entry.
            Returns thumb_row, label, stat — none added to scene yet."""
            import os
            files = sorted(os.listdir(f"{_DS_ASSETS}/{dataset_dir}"))[:4]
            thumbs = []
            for fname in files:
                img = ImageMobject(f"{_DS_ASSETS}/{dataset_dir}/{fname}")
                img.set_height(1.10)
                thumbs.append(img)
            thumb_row = Group(*thumbs).arrange(RIGHT, buff=0.20)
            label = m_text(label_text, scale=0.34, color=TONE_AMBER)
            stat = m_text(f"{stat_value:,}  {stat_suffix}", scale=0.30, color=TONE_CYAN)
            # Stack via a temp container so we can move the whole layout to center_entry
            stack = Group(thumb_row,
                          label.next_to(thumb_row, DOWN, buff=0.18),
                          stat.next_to(thumb_row, DOWN, buff=0.18))
            # Re-stack with stat below label (use separate next_to chain)
            label.next_to(thumb_row, DOWN, buff=0.18)
            stat.next_to(label,     DOWN, buff=0.10)
            stack = Group(thumb_row, label, stat)
            stack.move_to(center_entry)
            return thumb_row, thumbs, label, stat

        placed_cards = []
        for i, (dataset_dir, label_text, stat_value, stat_suffix) in enumerate(datasets_info):
            thumb_row, thumbs, label, stat = build_card(
                dataset_dir, label_text, stat_value, stat_suffix)
            # Add thumb row with thumbs invisible (FadeIn would re-arrange, breaking layout)
            for t in thumbs:
                t.set_opacity(0)
            self.add(thumb_row)

            # 1) Lagged fade-in of thumbs at center
            self.play(
                LaggedStart(*[t.animate.set_opacity(1.0) for t in thumbs],
                            lag_ratio=0.12),
                run_time=0.50,
            )
            # 2) Label + stat fade in (use FadeIn — it adds + animates from 0)
            self.play(
                FadeIn(label, shift=0.08*UP),
                FadeIn(stat,  shift=0.08*UP),
                run_time=0.40,
            )
            self.wait(0.30)
            # 3) Slide whole card into final slot (scale down so 3 cards breathe)
            card = Group(thumb_row, label, stat)
            self.play(
                card.animate.scale(SLOT_SCALE).move_to(slot_positions[i]),
                run_time=0.55,
            )
            placed_cards.append(card)

        self.wait(0.6)

        # Fade everything out before Phase B
        self.play(
            FadeOut(ds_section_header),
            *[FadeOut(c) for c in placed_cards],
            run_time=0.5,
        )

        # === Phase B (3b1b kinetic): accuracy bars + gridlines + count-up ===
        # leg2 already shown in the intro; hold so the bars land on "First, accuracy" (+19.4)
        self.wait(2.5)

        gl_x0, gl_x1 = -4.7, 4.7
        # baseline axis + faint gridlines at 50 / 75 / 100 %, drawing on
        baseaxis = Line(np.array([gl_x0, baseline, 0]), np.array([gl_x1, baseline, 0]))
        baseaxis.set_stroke(TONE_MUTED, 1.6, opacity=0.6)
        grid, gridlbls = VGroup(), VGroup()
        for pct in (50, 75, 100):
            gy = baseline + pct / scale_h
            ln = Line(np.array([gl_x0, gy, 0]), np.array([gl_x1, gy, 0]))
            ln.set_stroke(TONE_MUTED, 1.0, opacity=0.18)
            grid.add(ln)
            t = m_text(f"{pct}", scale=0.26, color=TONE_MUTED).set_opacity(0.5)
            t.move_to(np.array([gl_x0 - 0.40, gy, 0]))
            gridlbls.add(t)
        self.play(ShowCreation(baseaxis),
                  LaggedStartMap(ShowCreation, grid, lag_ratio=0.2),
                  FadeIn(gridlbls), run_time=0.65)

        # Pre-build bars (collapsed), dataset names, deltas.
        asm_bars, rfe_bars, ds_labels, delta_labels = [], [], [], []
        for i, ds in enumerate(datasets):
            x_center = -3 + i * 3
            h1 = asm_acc[i] / scale_h
            h2 = rfe_acc[i] / scale_h
            b1 = Rectangle(width=bar_w, height=h1, fill_color=TONE_GREY,
                           fill_opacity=0.85, stroke_width=0)
            b2 = Rectangle(width=bar_w, height=h2, fill_color=TONE_AMBER,
                           fill_opacity=0.9, stroke_width=0)
            b1.stretch(0.001, 1).move_to(np.array([x_center - 0.40, baseline, 0]))
            b2.stretch(0.001, 1).move_to(np.array([x_center + 0.40, baseline, 0]))
            asm_bars.append((b1, h1, x_center))
            rfe_bars.append((b2, h2, x_center))
            ds_labels.append(m_text(ds, color=TONE_MUTED).scale(0.46).move_to(
                np.array([x_center, baseline - 0.50, 0])))
            delta = rfe_acc[i] - asm_acc[i]
            dl = m_text(f"+{delta}%", color=TONE_AMBER, scale=0.44)
            dl.move_to(np.array([x_center + 0.40, baseline + h2 + 0.52, 0]))
            delta_labels.append(dl)

        def _countup_bars(bars, accs, color):
            """Add bars + a DecimalNumber per bar that counts up AND rides the
            growing bar's top (3b1b style — the number tracks the bar tip)."""
            for b, _, _ in bars:
                self.add(b)
            trs, decs = [], []
            off = -0.40 if color == TONE_GREY else 0.40
            for (b, h, xc), acc in zip(bars, accs):
                tr = ValueTracker(0)
                dec = DecimalNumber(0, num_decimal_places=0, color=color, font_size=30)

                def _upd(m, t=tr, bar=b, x=xc + off):
                    m.set_value(t.get_value())
                    m.move_to(np.array([x, bar.get_top()[1] + 0.24, 0]))

                dec.add_updater(_upd)
                self.add(dec)
                trs.append(tr); decs.append(dec)
            return trs, decs

        # ASM grey bars grow + count up; dataset names appear.
        asm_trs, asm_decs = _countup_bars(asm_bars, asm_acc, TONE_GREY)
        self.play(
            *[b.animate.stretch_to_fit_height(h).move_to(
                np.array([xc - 0.40, baseline + h / 2, 0]))
              for b, h, xc in asm_bars],
            *[FadeIn(d, shift=0.05 * UP) for d in ds_labels],
            *[tr.animate.set_value(v) for tr, v in zip(asm_trs, asm_acc)],
            run_time=0.85, rate_func=smooth,
        )
        for d in asm_decs:
            d.clear_updaters()
        asm_static = [m_text(f"{asm_acc[i]}%", color=TONE_GREY).scale(0.5)
                      .move_to(asm_decs[i].get_center()) for i in range(3)]
        self.play(*[FadeIn(s) for s in asm_static],
                  *[FadeOut(d) for d in asm_decs], run_time=0.18)
        self.wait(0.25)

        # RFE amber bars grow + count up, overtopping.
        rfe_trs, rfe_decs = _countup_bars(rfe_bars, rfe_acc, TONE_AMBER)
        self.play(
            *[b.animate.stretch_to_fit_height(h).move_to(
                np.array([xc + 0.40, baseline + h / 2, 0]))
              for b, h, xc in rfe_bars],
            *[tr.animate.set_value(v) for tr, v in zip(rfe_trs, rfe_acc)],
            run_time=0.80, rate_func=smooth,
        )
        for d in rfe_decs:
            d.clear_updaters()
        rfe_static = [m_text(f"{rfe_acc[i]}%", color=TONE_AMBER).scale(0.5)
                      .move_to(rfe_decs[i].get_center()) for i in range(3)]
        self.play(*[FadeIn(s) for s in rfe_static],
                  *[FadeOut(d) for d in rfe_decs], run_time=0.18)

        # Winner pulse + delta callouts.
        all_b2 = [b for b, _, _ in rfe_bars]
        self.play(*[b.animate.set_fill(WHITE, 1.0) for b in all_b2],
                  *[FadeIn(d, shift=0.06 * UP) for d in delta_labels], run_time=0.22)
        self.play(*[b.animate.set_fill(TONE_AMBER, 0.9) for b in all_b2], run_time=0.22)

        self.wait(2.5)   # accuracy bars hold → timing "how fast?" on "...isn't slower" (+27.7)
        # --- Merge transition: shrink the accuracy chart + park it LEFT (stays on screen)
        #     so the timing chart joins on the RIGHT — one combined results view, no hard cut. ---
        acc_panel = VGroup(baseaxis, grid, gridlbls, *ds_labels, *delta_labels,
                           *asm_static, *rfe_static,
                           *[b for b, _, _ in asm_bars], *[b for b, _, _ in rfe_bars])
        self.play(
            FadeOut(leg2),
            acc_panel.animate.scale(0.55).move_to(np.array([-3.85, -0.30, 0])),
            run_time=0.70, rate_func=smooth,
        )
        acc_title = m_text("accuracy  (%)", scale=0.46, color=TONE_FG)
        acc_title.move_to(np.array([-3.85, 1.70, 0]))
        self.play(FadeIn(acc_title, shift=0.05 * UP), run_time=0.30)

        # --- Beat 2c: timing comparison as horizontal bar chart (RIGHT panel) ---
        timing_header = m_text("how fast?", scale=0.46, color=TONE_FG).move_to(np.array([2.55, 1.70, 0]))

        # Bars laid out horizontally — length encodes ms (lower = better).
        # X axis spans 0..300 ms. Bar origin x = LEFT_X; tip x = LEFT_X + (ms/300) * AXIS_W
        LEFT_X = 0.90
        AXIS_W = 3.30
        ms_max = 300.0
        rows_data = [
            ("ASM   (baseline)",  250.0, "~250 ms",  TONE_GREY,  +0.90),
            ("RFE-ASM",           100.0, " <100 ms", TONE_AMBER, -0.30),
            ("deep CNN baseline",  30.0, " ~30 ms",  TONE_CYAN,  -1.50),
        ]

        # X axis ruler
        ruler_y = -2.20
        ruler = Line(np.array([LEFT_X, ruler_y, 0]),
                     np.array([LEFT_X + AXIS_W, ruler_y, 0])).set_stroke(TONE_MUTED, 1.2).set_opacity(0.55)
        ticks = VGroup()
        for ms in (0, 100, 200, 300):
            x = LEFT_X + (ms / ms_max) * AXIS_W
            tick = Line(np.array([x, ruler_y - 0.06, 0]), np.array([x, ruler_y + 0.06, 0])).set_stroke(TONE_MUTED, 1.2)
            lbl = m_text(f"{ms}", scale=0.28, color=TONE_MUTED).set_opacity(0.75)
            lbl.move_to(np.array([x, ruler_y - 0.28, 0]))
            ticks.add(tick, lbl)
        x_axis_lbl = m_text("inference time (ms,  single CPU thread,  lower = better)",
                            scale=0.30, color=TONE_MUTED).set_opacity(0.85)
        x_axis_lbl.move_to(np.array([LEFT_X + AXIS_W/2, ruler_y - 0.68, 0]))

        bar_h = 0.45
        bars = []
        bar_labels = []
        method_labels = []
        speedup_labels = []
        baseline_ms = 250.0
        for method, ms, ms_label, color, y in rows_data:
            method_t = m_text(method, scale=0.40, color=color)
            method_t.move_to(np.array([LEFT_X, y + 0.40, 0]), aligned_edge=LEFT)
            method_labels.append(method_t)

            tip_x = LEFT_X + (ms / ms_max) * AXIS_W
            bar = Rectangle(width=max(tip_x - LEFT_X, 0.01), height=bar_h,
                            fill_color=color, fill_opacity=0.85, stroke_width=0)
            bar.move_to(np.array([(LEFT_X + tip_x) / 2, y, 0]))
            # Start collapsed at LEFT_X for grow-in animation
            bar_target = bar.copy()
            bar.stretch_to_fit_width(0.01)
            bar.move_to(np.array([LEFT_X + 0.005, y, 0]))
            bars.append((bar, bar_target))

            ms_t = m_text(ms_label, scale=0.46, color=color)
            ms_t.next_to(bar_target, RIGHT, buff=0.15)
            bar_labels.append(ms_t)

            # Speedup annotation for non-baseline rows.
            if ms < baseline_ms:
                ratio = baseline_ms / ms
                speedup_t = m_text(f"x{ratio:.1f} faster", scale=0.32, color=color)
                speedup_t.next_to(ms_t, RIGHT, buff=0.30)
                speedup_t.set_opacity(0.85)
                speedup_labels.append(speedup_t)
            else:
                speedup_labels.append(None)

        self.play(FadeIn(timing_header, shift=0.08*DOWN), run_time=0.570)
        self.play(ShowCreation(ruler), FadeIn(ticks), FadeIn(x_axis_lbl), run_time=0.700)
        # Reveal each method row sequentially: label fades in, bar grows, value fades in
        seq = []
        for i, ((bar, target), ml, vl) in enumerate(zip(bars, method_labels, bar_labels)):
            self.add(bar)
            self.play(FadeIn(ml, shift=0.05*RIGHT), run_time=0.260)

            # Numeric ms counter synced to bar grow
            ms_value = rows_data[i][1]
            ms_color = rows_data[i][3]
            ms_tracker = ValueTracker(0)
            ms_decimal = DecimalNumber(0, num_decimal_places=0, color=ms_color, font_size=24)
            ms_decimal.add_updater(lambda m, t=ms_tracker: m.set_value(t.get_value()))
            ms_decimal.next_to(target, RIGHT, buff=0.15)
            self.add(ms_decimal)

            self.play(
                Transform(bar, target),
                ms_tracker.animate.set_value(ms_value),
                run_time=0.35,
            )
            ms_decimal.clear_updaters()
            self.remove(ms_decimal)

            self.play(FadeIn(vl, shift=0.05*RIGHT), run_time=0.220)
            if speedup_labels[i] is not None:
                self.play(FadeIn(speedup_labels[i], shift=0.05*RIGHT), run_time=0.180)
        self.wait(9.5)   # timing chart holds → per-landmark scatter on "Now zoom into the points" (+43.2)
        all_bars = VGroup(*[b for b, _ in bars])
        all_speedups = [s for s in speedup_labels if s is not None]
        self.play(FadeOut(VGroup(timing_header, ruler, ticks, x_axis_lbl,
                                  *method_labels, *bar_labels, *all_speedups, all_bars,
                                  acc_panel, acc_title)),
                  run_time=0.600)

        # --- Beat 4 (moved): per-landmark error scatter — now sits with the curve ---
        self.wait(0.4)
        axes1 = Axes(x_range=[0, 17, 4], y_range=[0, 8, 2], width=10, height=4.5,
                     axis_config={"stroke_color": TONE_MUTED})
        axes1.move_to(ORIGIN + DOWN*0.3)
        x_lbl = m_text("landmark index", color=TONE_FG).scale(0.62).next_to(axes1, DOWN, buff=0.3)
        y_lbl = m_text("mean error (px)", color=TONE_FG).scale(0.62).rotate(PI/2).next_to(axes1, LEFT, buff=0.3)

        asm_err = [5.8, 5.5, 5.0, 4.8, 4.6, 4.4, 4.2, 4.1, 4.0, 4.1, 4.2, 4.4, 4.6, 4.8, 5.0, 5.5, 5.8]
        rfe_err = [4.2, 3.9, 3.6, 3.4, 3.2, 3.0, 2.9, 2.8, 2.7, 2.8, 2.9, 3.0, 3.2, 3.4, 3.6, 3.9, 4.2]
        asm_dots = VGroup(*[Dot(axes1.c2p(i+1, e), radius=0.13).set_fill(TONE_GREY, 1.0).set_stroke(width=0)
                             for i, e in enumerate(asm_err)])
        rfe_dots = VGroup(*[Dot(axes1.c2p(i+1, e), radius=0.13).set_fill(TONE_AMBER, 1.0).set_stroke(width=0)
                             for i, e in enumerate(rfe_err)])
        ticks1 = _axis_tick_labels(axes1, x_vals=[0, 4, 8, 12, 16], y_vals=[0, 2, 4, 6, 8])
        leg1 = _legend([(TONE_AMBER, "RFE-ASM"), (TONE_GREY, "ASM")],
                       x_anchor=5.4, y_anchor=2.10)
        sub1 = m_text("per-landmark mean error", scale=0.44, color=TONE_MUTED)
        sub1.next_to(title, DOWN, buff=0.12)

        self.play(FadeIn(axes1), FadeIn(x_lbl), FadeIn(y_lbl), FadeIn(ticks1),
                  FadeIn(sub1, shift=0.05*DOWN), run_time=0.570)
        self.play(LaggedStartMap(FadeIn, asm_dots, lag_ratio=0.05), run_time=0.70)
        self.play(LaggedStartMap(FadeIn, rfe_dots, lag_ratio=0.05), run_time=0.70)
        self.play(FadeIn(leg1), run_time=0.25)
        self.wait(4.0)   # scatter holds → CED curve on "the cumulative curve rises sooner" (+52.1)
        # Merge: shrink the scatter + park it LEFT (keep), so the cumulative curve
        # joins on the RIGHT — both error views on one screen (same idea as the bars).
        scatter_panel = VGroup(axes1, x_lbl, y_lbl, ticks1, asm_dots, rfe_dots)
        # leg1 rises to TOP-CENTER as ONE shared legend representing BOTH error panels.
        self.play(
            FadeOut(sub1),
            leg1.animate.move_to(np.array([0.0, 2.55, 0])),
            scatter_panel.animate.scale(0.52).move_to(np.array([-3.6, -0.35, 0])),
            run_time=0.70, rate_func=smooth,
        )
        scatter_title = m_text("per-landmark error", scale=0.42, color=TONE_FG)
        scatter_title.move_to(np.array([-3.6, 1.70, 0]))
        self.play(FadeIn(scatter_title, shift=0.05 * UP), run_time=0.30)

        # --- Beat 3: cumulative error distribution (RIGHT panel) ---
        axes3 = Axes(x_range=[0, 10, 2], y_range=[0, 1, 0.2], width=5.0, height=3.40,
                     axis_config={"stroke_color": TONE_MUTED}).move_to(np.array([3.35, -0.35, 0]))
        x3 = m_text("error threshold (px)", color=TONE_FG).scale(0.44).next_to(axes3, DOWN, buff=0.22)
        y3 = m_text("cumulative fraction", color=TONE_FG).scale(0.44).rotate(PI/2).next_to(axes3, LEFT, buff=0.22)

        try:
            asm_curve = axes3.get_graph(lambda x: float(1 - np.exp(-x / 4.5)), x_range=[0, 10],
                                         color=TONE_GREY, stroke_width=3)
            rfe_curve = axes3.get_graph(lambda x: float(1 - np.exp(-x / 2.5)), x_range=[0, 10],
                                         color=TONE_AMBER, stroke_width=3)
        except AttributeError:
            asm_curve = ParametricCurve(lambda t: axes3.c2p(t, 1 - np.exp(-t / 4.5)),
                                         t_range=[0, 10], color=TONE_GREY, stroke_width=3)
            rfe_curve = ParametricCurve(lambda t: axes3.c2p(t, 1 - np.exp(-t / 2.5)),
                                         t_range=[0, 10], color=TONE_AMBER, stroke_width=3)
        ticks3 = _axis_tick_labels(axes3, x_vals=[0, 5, 10], y_vals=[0, 0.5, 1.0],
                                   x_off=0.28, y_off=0.24, scale=0.28)
        sub3 = m_text("cumulative error", scale=0.42, color=TONE_FG)
        sub3.move_to(np.array([3.35, 1.70, 0]))
        self.wait(1.0)  # __TRANS_HOLD__
        self.play(FadeIn(axes3), FadeIn(x3), FadeIn(y3), FadeIn(ticks3),
                  FadeIn(sub3, shift=0.05*DOWN), run_time=0.600)
        self.play(ShowCreation(asm_curve), run_time=0.70)
        self.play(ShowCreation(rfe_curve), run_time=0.70)

        # Shaded gap between RFE-ASM (top, amber) and ASM (bottom, grey)
        shaded = VMobject()
        n_samples = 40
        xs = np.linspace(0, 10, n_samples)
        upper = [axes3.c2p(x, 1 - np.exp(-x / 2.5)) for x in xs]
        lower = [axes3.c2p(x, 1 - np.exp(-x / 4.5)) for x in reversed(xs)]
        shaded.set_points_as_corners(upper + lower + [upper[0]])
        shaded.set_fill(TONE_AMBER, opacity=0.18).set_stroke(width=0)
        self.play(FadeIn(shaded), run_time=0.5)
        self.wait(13.3)   # CED holds → VO "More accurate. And faster. That's the result." (close)
        self.play(FadeOut(VGroup(axes3, x3, y3, ticks3, asm_curve, rfe_curve, leg1, sub3, title, shaded,
                                  scatter_panel, scatter_title)), run_time=0.40)
