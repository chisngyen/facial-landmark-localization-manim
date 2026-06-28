"""
Shot 07 — Conclusions reframed as timeline-as-hero + 3 callouts + closing line.

The era timeline is promoted from a mini-viz to the central visual; three
callouts (Delivered / Unsolved / What's Next) are pinned to milestone
positions via dashed connectors.
"""
from manimlib import *

import os, sys
import numpy as np
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_RED, TONE_FG, TONE_MUTED,
    MuseumScene, m_text,
    ChapterRibbon, AnimatedHead, HERO_SWAY_LANDMARKS_DIR, HERO_SWAY_FRAMES,
)


# ============================================================
# Icon + viz helpers
# ============================================================
def _draw_check(x_center, y_center, color, scale=0.8, stroke_w=6):
    """Cyan ✓ checkmark as VMobject (3-point path)."""
    pts = [
        np.array([x_center - 0.35*scale, y_center + 0.05*scale, 0]),
        np.array([x_center - 0.05*scale, y_center - 0.25*scale, 0]),
        np.array([x_center + 0.40*scale, y_center + 0.30*scale, 0]),
    ]
    check = VMobject().set_points_as_corners(pts)
    check.set_stroke(color, stroke_w)
    return check


def _draw_big_x(x_center, y_center, color, scale=0.8, stroke_w=9):
    """Bold X — two crossing Line objects. Returns (group, line1, line2)
    so the two lines can be individually animated for reveal."""
    half = 0.35 * scale
    line1 = Line(
        np.array([x_center - half, y_center - half, 0]),
        np.array([x_center + half, y_center + half, 0]),
    ).set_stroke(color, stroke_w)
    line2 = Line(
        np.array([x_center + half, y_center - half, 0]),
        np.array([x_center - half, y_center + half, 0]),
    ).set_stroke(color, stroke_w)
    return VGroup(line1, line2), line1, line2


def _draw_arrow_fwd(x_center, y_center, color, scale=0.8, stroke_w=8):
    """Forward → arrow (Line shaft + Polygon tip)."""
    half = 0.4 * scale
    shaft = Line(
        np.array([x_center - half, y_center, 0]),
        np.array([x_center + half * 0.65, y_center, 0]),
    ).set_stroke(color, stroke_w)
    tip = Polygon(
        np.array([x_center + half * 0.65, y_center + 0.12*scale, 0]),
        np.array([x_center + half, y_center, 0]),
        np.array([x_center + half * 0.65, y_center - 0.12*scale, 0]),
    ).set_fill(color, 1.0).set_stroke(width=0)
    return VGroup(shaft, tip)


def _era_timeline(x_center, y_center, accent, scale=1.0):
    """Horizontal timeline: 5 era milestones with year + acronym."""
    milestones = [
        ("1995", "ASM",         TONE_CYAN),
        ("2001", "AAM",         TONE_CYAN),
        ("2008", "CLM",         TONE_MUTED),
        ("2014", "CNN",         TONE_AMBER),
        ("2020+", "Trans.",     "#ffd17a"),
    ]
    n = len(milestones)
    width = scale * 1.7
    line = Line(
        np.array([x_center - width/2, y_center, 0]),
        np.array([x_center + width/2, y_center, 0]),
    ).set_stroke(accent, 1.4).set_opacity(0.55)
    g = VGroup(line)
    for i, (yr, era, col) in enumerate(milestones):
        x = x_center - width/2 + (width * i / (n-1))
        dot = Dot(point=np.array([x, y_center, 0]), radius=0.045)
        dot.set_fill(col, 1.0).set_stroke(width=0)
        yr_t = m_text(yr, scale=0.16, color=col)
        yr_t.move_to(np.array([x, y_center + 0.16, 0]))
        era_t = m_text(era, scale=0.14, color=TONE_MUTED)
        era_t.set_opacity(0.85)
        era_t.move_to(np.array([x, y_center - 0.18, 0]))
        g.add(dot, yr_t, era_t)
    return g


# ============================================================
# Main scene
# ============================================================
class Section01_Shot11_Conclusions(MuseumScene):
    """3 answer cards with icon + mini-viz + bullets."""

    def construct(self):
        self.add_museum_bg(accent="amber")

        ribbon = ChapterRibbon(section="12.6 · conclusions")
        self.add(ribbon)

        # Opener
        opener = m_text(
            "Back to where we started: what did we actually gain?",
            scale=0.60, color=TONE_FG,
        ).to_edge(UP, buff=0.75)
        self.play(FadeIn(opener, shift=0.1 * DOWN), run_time=0.75)
        self.wait(1.29)

        # ============================================================
        # Timeline as hero — promoted from mini-viz to main visual
        # ============================================================
        # Build a bigger timeline centered horizontally at y=+1.2
        milestones = [
            ("1995", "ASM",         TONE_CYAN),
            ("2001", "AAM",         TONE_CYAN),
            ("2008", "CLM",         TONE_MUTED),
            ("2014", "CNN",         TONE_AMBER),
            ("2020+", "Trans.",     "#ffd17a"),
        ]
        n_ms = len(milestones)
        tl_y = 1.2
        tl_width = 9.0  # generous, since this is the hero now
        tl_left = -tl_width / 2

        # Backbone line
        tl_line = Line(
            np.array([tl_left, tl_y, 0]),
            np.array([tl_left + tl_width, tl_y, 0]),
        ).set_stroke(TONE_AMBER, 2.0).set_opacity(0.7)

        # Milestone dots + labels
        ms_dots = []
        ms_year_labels = []
        ms_era_labels = []
        for i, (yr, era, col) in enumerate(milestones):
            x = tl_left + (tl_width * i / (n_ms - 1))
            dot = Dot(point=np.array([x, tl_y, 0]), radius=0.10).set_fill(col, 1.0).set_stroke(width=0)
            yr_t = m_text(yr, scale=0.32, color=col).move_to(np.array([x, tl_y + 0.40, 0]))
            era_t = m_text(era, scale=0.32, color=TONE_FG).move_to(np.array([x, tl_y - 0.40, 0]))
            ms_dots.append(dot)
            ms_year_labels.append(yr_t)
            ms_era_labels.append(era_t)

        # Draw backbone + dots together so the line isn't lonely on screen.
        self.play(
            ShowCreation(tl_line),
            LaggedStartMap(lambda m: FadeIn(m, scale=0.4), VGroup(*ms_dots), lag_ratio=0.10),
            run_time=0.80,
        )
        self.play(
            LaggedStartMap(FadeIn, VGroup(*ms_year_labels, *ms_era_labels), lag_ratio=0.05),
            run_time=0.60,
        )

        # Pulse ASM 1995 — "we are HERE"
        asm_dot = ms_dots[0]
        you_are_here = m_text("we are here", scale=0.28, color=TONE_CYAN).next_to(asm_dot, UP, buff=0.85)
        you_are_here.set_opacity(0.9)
        self.play(Indicate(asm_dot, color="#ffffff", scale_factor=1.8), run_time=0.50)
        self.play(FadeIn(you_are_here, shift=0.1*DOWN), run_time=0.40)
        self.wait(1.29)

        # 3 callouts pinned to timeline positions
        # Layout: text callouts sit below timeline at y=-1.5, connectors dashed
        callouts_y = -1.5

        def callout(icon_kind, accent, x, title, lines):
            """Build a callout block: icon + title + body lines."""
            # Icon: small, scale 0.4
            if icon_kind == "check":
                icon = _draw_check(x, callouts_y + 0.85, accent, scale=0.45, stroke_w=5)
            elif icon_kind == "x":
                icon, _, _ = _draw_big_x(x, callouts_y + 0.85, accent, scale=0.45, stroke_w=6)
            elif icon_kind == "arrow":
                icon = _draw_arrow_fwd(x, callouts_y + 0.85, accent, scale=0.55, stroke_w=5)
            else:
                icon = VGroup()
            title_t = m_text(title, scale=0.36, color=accent).move_to(np.array([x, callouts_y + 0.25, 0]))
            body_grp = VGroup()
            for i, ln in enumerate(lines):
                t = m_text(ln, scale=0.26, color=TONE_MUTED).move_to(np.array([x, callouts_y - 0.10 - i*0.32, 0]))
                t.set_opacity(0.85)
                body_grp.add(t)
            return VGroup(icon, title_t, body_grp), icon, title_t, body_grp

        # Build 3 callouts
        delivered_grp, d_icon, d_title, d_body = callout("check", TONE_CYAN, -4.5, "DELIVERED",
            ["Real-time RFE-ASM", "88 landmarks in < 100 ms", "tested on 6 datasets"])
        unsolved_grp, u_icon, u_title, u_body = callout("x", TONE_RED, 0.0, "UNSOLVED",
            ["Pose generalisation", "FRVT 2006 — pose still", "degrades sharply"])
        next_grp, n_icon, n_title, n_body = callout("arrow", TONE_AMBER, 4.5, "WHAT'S NEXT",
            ["2D -> 3D morphable", "deep landmark nets", "transformer / diffusion era"])

        # Connectors: dashed from timeline dot → callout icon
        def connector(from_dot, to_x, to_y, color):
            return DashedLine(
                from_dot.get_center(),
                np.array([to_x, to_y, 0]),
                color=color,
                stroke_width=1.2,
                dash_length=0.10,
            ).set_opacity(0.55)

        # Delivered → ASM 1995 (ms_dots[0])
        conn_d = connector(ms_dots[0], -4.5, callouts_y + 1.10, TONE_CYAN)
        # Unsolved → CLM 2008 (ms_dots[2], middle of timeline)
        conn_u = connector(ms_dots[2], 0.0, callouts_y + 1.10, TONE_RED)
        # Next → Transformer 2020+ (ms_dots[4])
        conn_n = connector(ms_dots[4], 4.5, callouts_y + 1.10, TONE_AMBER)

        # Reveal Delivered callout
        self.play(
            FadeOut(you_are_here),
            ShowCreation(conn_d),
            run_time=0.50,
        )
        self.play(
            ShowCreation(d_icon),
            FadeIn(d_title, shift=0.05*UP),
            LaggedStartMap(FadeIn, d_body, lag_ratio=0.20),
            run_time=0.80,
        )
        self.wait(1.29)

        # Reveal Unsolved
        self.play(ShowCreation(conn_u), run_time=0.40)
        self.play(
            ShowCreation(u_icon),
            FadeIn(u_title, shift=0.05*UP),
            LaggedStartMap(FadeIn, u_body, lag_ratio=0.20),
            run_time=0.80,
        )
        self.wait(1.29)

        # Reveal Next — pulse the CNN + Transformer dots
        self.play(ShowCreation(conn_n), run_time=0.40)
        self.play(
            ShowCreation(n_icon),
            FadeIn(n_title, shift=0.05*UP),
            LaggedStartMap(FadeIn, n_body, lag_ratio=0.20),
            Indicate(ms_dots[3], color="#ffffff", scale_factor=1.5),
            Indicate(ms_dots[4], color="#ffffff", scale_factor=1.5),
            run_time=0.80,
        )
        self.wait(1.61)

        # Final takeaway
        final = VGroup(
            m_text("A face is more than a box —", scale=0.48, color=TONE_FG),
            m_text("and with landmarks, we know  exactly where.",
                   scale=0.48, color=TONE_AMBER),
        ).arrange(DOWN, buff=0.14).to_edge(DOWN, buff=0.50)

        # (Removed: mini face-with-landmarks sway loop in bottom-right corner —
        # user requested cleaner final beat.)
        self.play(FadeIn(final, shift=0.15 * UP), run_time=0.75)
        self.wait(8.04)

        # Fade out everything
        all_mobs = VGroup(
            opener, final, tl_line,
            *ms_dots, *ms_year_labels, *ms_era_labels,
            conn_d, conn_u, conn_n,
            delivered_grp, unsolved_grp, next_grp,
        )
        self.play(FadeOut(all_mobs), run_time=0.60)
