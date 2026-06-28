"""
Shot 02 — TitleIntro: "6 questions we'll answer" — PREMIUM v2 (3Blue1Brown kinetic).

Direction: pure black, mono type (no serif). The "đẳng cấp" comes from MOTION:
  - title + subtitle WRITE on (stroke draw, 3b1b signature)
  - a vertical rail DRAWS downward
  - numbered nodes POP in along the rail
  - a glowing focus marker TRAVELS down the rail as each question lights up,
    with a single underline that slides to the active row.
Kept the original _QUESTIONS data + class name + ~14s envelope.
"""
from manimlib import *

import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_FG, TONE_MUTED, FONT,
    MuseumScene, m_text,
)


# Order matches the narration's spoken sequence (not §-order) so the travelling
# focus marker lands on each question exactly as it's said:
# eyes@+4.5 · framework@+6.8 · fit@+9.1 · work@+11.7 · next@+14.8 · problem(closing).
_QUESTIONS = [
    ("§12.3", "Where are the eyes?"),
    ("§12.2", "What's the framework?"),
    ("§12.4", "How do we fit landmarks?"),
    ("§12.5", "Does it really work?"),
    ("§12.6", "What's left?"),
    ("§12.1", "What's the problem?"),
]


def _focus_marker():
    """Glowing amber focus token: soft halo + ring + core dot (small — sits on a node)."""
    halo = Circle(radius=0.125).set_stroke(TONE_AMBER, 4.0, opacity=0.10).set_fill(opacity=0)
    ring = Circle(radius=0.078).set_stroke(TONE_AMBER, 2.2, opacity=0.95).set_fill(opacity=0)
    core = Dot(radius=0.034).set_fill(TONE_AMBER, 1.0).set_stroke(width=0)
    return VGroup(halo, ring, core)


class Section01_Shot02_TitleIntro(MuseumScene):
    """Kinetic ToC: rail + travelling focus marker over 6 questions."""

    def construct(self):
        self.add_museum_bg(accent="amber")

        # ---- Title: write-on (3b1b signature) ----
        title = m_text("Chapter 12  ·  Facial Landmark Localization",
                       scale=0.62, color=TONE_FG)
        title.to_edge(UP, buff=0.55)
        subtitle = m_text("Six questions.", scale=0.42, color=TONE_CYAN)
        subtitle.next_to(title, DOWN, buff=0.20)
        self.play(Write(title), run_time=1.10)
        self.play(Write(subtitle), run_time=0.55)
        # ~1.65s

        # ---- Geometry ----
        rail_x = -5.55
        num_x  = -6.05   # numbers right-aligned just left of rail
        q_x    = -5.15   # questions to the right of rail
        y_top, y_bot = 1.70, -2.45
        n = len(_QUESTIONS)
        row_ys = [y_top - i * (y_top - y_bot) / (n - 1) for i in range(n)]

        # ---- Vertical rail draws down ----
        rail = Line(np.array([rail_x, row_ys[0] + 0.30, 0]),
                    np.array([rail_x, row_ys[-1] - 0.30, 0]))
        rail.set_stroke(TONE_MUTED, 2.0, opacity=0.55)
        rail_glow = rail.copy().set_stroke(TONE_AMBER, 7.0, opacity=0.06)
        self.play(ShowCreation(rail), FadeIn(rail_glow), run_time=0.70)
        # ~2.35s

        # ---- Nodes + numbered question rows ----
        nodes, numerals, q_texts, row_groups = [], [], [], []
        for i, (sec, q) in enumerate(_QUESTIONS):
            y = row_ys[i]
            node = Circle(radius=0.075).set_stroke(TONE_MUTED, 2.2).set_fill(BLACK, 1.0)
            node.move_to(np.array([rail_x, y, 0]))

            numeral = m_text(str(i + 1), scale=0.40, color=TONE_MUTED)
            numeral.move_to(np.array([num_x, y, 0]), aligned_edge=RIGHT)
            numeral.set_opacity(0.55)

            q_t = m_text(q, scale=0.46, color=TONE_FG)
            q_t.move_to(np.array([q_x, y, 0]), aligned_edge=LEFT)
            q_t.set_opacity(0.55)

            nodes.append(node)
            numerals.append(numeral)
            q_texts.append(q_t)
            row_groups.append(VGroup(numeral, q_t))

        # Nodes pop in along the rail; rows slide in from the left, lagged.
        self.play(
            LaggedStart(*[GrowFromCenter(nd) for nd in nodes], lag_ratio=0.12),
            LaggedStart(*[FadeIn(numerals[i], shift=0.18 * RIGHT) for i in range(n)],
                        lag_ratio=0.12),
            LaggedStart(*[FadeIn(q_texts[i], shift=0.18 * RIGHT) for i in range(n)],
                        lag_ratio=0.12),
            run_time=1.45,
        )
        self.wait(0.28)   # → focus loop starts ~+4.0 so Q1 lands on "Where are the eyes?" (+4.5)
        # ~4.45s

        # ---- Travelling focus marker + sliding underline ----
        focus = _focus_marker().move_to(nodes[0].get_center())
        focus.set_opacity(0)

        def underline_for(i):
            ln = Line(q_texts[i].get_left() + np.array([-0.05, -0.26, 0]),
                      q_texts[i].get_right() + np.array([0.05, -0.26, 0]))
            return ln.set_stroke(TONE_AMBER, 2.2, opacity=0.85)

        underline = underline_for(0).set_opacity(0)
        self.add(rail_glow, underline, focus)

        # Per-question dwell tuned so the focus marker lands on each question as the
        # VO speaks it: Q1@+4.5, Q2@+6.8, Q3@+9.1, Q4@+11.7, Q5@+14.8, Q6@+16.8.
        dwell = [1.88, 1.88, 2.18, 2.68, 1.58, 0.3]

        prev = None
        for i in range(n):
            target_u = underline_for(i)
            anims = [
                focus.animate.move_to(nodes[i].get_center()).set_opacity(1.0),
                nodes[i].animate.set_fill(TONE_AMBER, 1.0).set_stroke(TONE_AMBER, 2.4),
                numerals[i].animate.set_color(TONE_AMBER).set_opacity(1.0),
                q_texts[i].animate.set_color(TONE_AMBER).set_opacity(1.0),
                Transform(underline, target_u),
            ]
            if prev is not None:
                anims += [
                    nodes[prev].animate.set_fill(BLACK, 1.0).set_stroke(TONE_MUTED, 2.2),
                    numerals[prev].animate.set_color(TONE_MUTED).set_opacity(0.45),
                    q_texts[prev].animate.set_color(TONE_FG).set_opacity(0.50),
                ]
            self.play(*anims, run_time=0.42, rate_func=smooth)
            self.wait(dwell[i])
            prev = i
        # ~10.8s

        # ---- Return focus to Q1, scale it up, closing line writes on ----
        target_u = underline_for(0)
        self.play(
            focus.animate.move_to(nodes[0].get_center()),
            Transform(underline, target_u),
            nodes[0].animate.set_fill(TONE_AMBER, 1.0).set_stroke(TONE_AMBER, 2.4),
            numerals[0].animate.set_color(TONE_AMBER).set_opacity(1.0),
            q_texts[0].animate.set_color(TONE_AMBER).set_opacity(1.0),
            nodes[prev].animate.set_fill(BLACK, 1.0).set_stroke(TONE_MUTED, 2.2),
            numerals[prev].animate.set_color(TONE_MUTED).set_opacity(0.30),
            q_texts[prev].animate.set_color(TONE_FG).set_opacity(0.30),
            *[q_texts[j].animate.set_opacity(0.22) for j in range(1, n)],
            *[numerals[j].animate.set_opacity(0.22) for j in range(1, n)],
            run_time=0.55,
        )
        self.play(
            row_groups[0].animate.scale(1.16, about_point=nodes[0].get_center()),
            focus.animate.scale(1.12),
            run_time=0.6, rate_func=smooth,
        )

        transition = m_text("Let's start at  12.1", scale=0.44, color=TONE_AMBER)
        transition.to_edge(DOWN, buff=0.45)
        self.play(Write(transition), run_time=0.75)
        self.wait(0.15)
        # ~13.8s

        # ---- Fade everything ----
        everything = VGroup(
            title, subtitle, rail, rail_glow, underline, focus, transition,
            *nodes, *numerals, *q_texts,
        )
        self.play(FadeOut(everything), run_time=0.65)
