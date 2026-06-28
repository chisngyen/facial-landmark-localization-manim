"""
Shot 08 — End card: source, citation, credits.
"""
from manimlib import *

import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_FG, TONE_MUTED,
    MuseumScene, m_text,
    ChapterRibbon, typewriter_anim,
)


class Section01_Shot14_EndCard(MuseumScene):
    """Closing card: paper source, citation, credits."""

    def construct(self):
        self.add_museum_bg(accent="amber")

        ribbon = ChapterRibbon(section=None)  # closing card — no sub-label
        self.add(ribbon)

        # Top: thanks
        thanks = m_text("Thanks for watching.", scale=0.78, color=TONE_AMBER)
        thanks.move_to(np.array([0, 2.30, 0]))

        # Rule
        rule = Line(
            np.array([-3.20, 1.70, 0]),
            np.array([+3.20, 1.70, 0]),
        ).set_stroke(TONE_MUTED, 1.2).set_opacity(0.50)

        # Source paper
        src_label = m_text("source", scale=0.34, color=TONE_MUTED)
        src_label.set_opacity(0.70)
        src_label.move_to(np.array([0, 1.20, 0]))

        src_title = m_text(
            "Handbook of Face Recognition  (2nd ed.)",
            scale=0.44, color=TONE_FG,
        )
        src_title.move_to(np.array([0, 0.78, 0]))

        src_chapter = m_text(
            "Chapter 12  —  Facial Landmark Localization",
            scale=0.40, color=TONE_CYAN,
        )
        src_chapter.move_to(np.array([0, 0.30, 0]))

        src_authors = m_text(
            "Xiaoqing Ding  &  Liting Wang   ·   Tsinghua University",
            scale=0.32, color=TONE_MUTED,
        )
        src_authors.set_opacity(0.80)
        src_authors.move_to(np.array([0, -0.20, 0]))

        # Reveal sequence — typewriter cascade mirroring shot 00
        self.play(typewriter_anim(thanks, char_duration=0.04), run_time=1.0)
        self.play(ShowCreation(rule), run_time=0.613)
        self.play(typewriter_anim(src_label, char_duration=0.025), run_time=0.5)
        self.play(typewriter_anim(src_title, char_duration=0.035), run_time=0.85)
        self.play(typewriter_anim(src_chapter, char_duration=0.035), run_time=0.75)
        self.play(typewriter_anim(src_authors, char_duration=0.025), run_time=0.7)

        # Video author line
        author = m_text("Video by  Trần Chí Nguyên", scale=0.42, color=TONE_AMBER)
        author.move_to(np.array([0, -1.30, 0]))

        self.play(
            typewriter_anim(author, char_duration=0.035),
            run_time=0.90,
        )

        self.wait(0.42)

        # Fade everything together
        flat = VGroup(thanks, rule, src_label, src_title, src_chapter,
                      src_authors, author)
        self.play(FadeOut(flat), run_time=1.226)
