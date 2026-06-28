"""
Shot 12 — Further reading: 6-card grid with paper thumbnails + references.

Each card: title + paper hero thumbnail + sub + arXiv/citation tag.
Two staggered fade-in waves (top row then bottom). Closes with MediaPipe repo
pointer.

Render:
    "D:/Downloads/Tools/Anaconda/Scripts/manimgl.exe" source/shot12_FurtherReading.py \
        Section01_Shot13_FurtherReading -w -l --video_dir videos --file_name shot12_FurtherReading
"""
from manimlib import *

import os, sys
import numpy as np
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_FG, TONE_MUTED, TONE_RED,
    MuseumScene, m_text, ChapterRibbon,
)


_REFS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "shot11","refs")

# 6 paper references: year, title, sub, citation, accent color, thumbnail path
CARDS = [
    # Top row (classical, pre-CNN era): cyan
    ("1995",  "Cootes — ASM",        "the shape model that started it all",
     "IVC 1995",          TONE_CYAN,  f"{_REFS_DIR}/asm_cootes.png"),
    ("2011",  "Ding & Wang",         "this chapter — RFE + 88-pt ASM",
     "Handbook Ch.12",    TONE_CYAN,  f"{_REFS_DIR}/ding_2011.png"),
    ("2013",  "Xiong — SDM",         "first ML method to beat ASM",
     "CVPR 2013",         TONE_CYAN,  f"{_REFS_DIR}/sdm.png"),
    # Bottom row (deep-learning / 3DMM era): amber
    ("2017",  "Bulat — FAN",         "heatmap CNN, pose-robust",
     "arXiv:1703.07332",  TONE_AMBER, f"{_REFS_DIR}/fan.png"),
    ("2020",  "Guo — 3DDFA v2",      "real-time 3D face from one image",
     "arXiv:2009.09960",  TONE_AMBER, f"{_REFS_DIR}/3ddfa.jpg"),
    ("2022",  "Daněček — EMOCA",     "expression + 3DMM, end-to-end",
     "arXiv:2204.11312",  TONE_AMBER, f"{_REFS_DIR}/emoca.png"),
]


def _make_card(year, title, sub, ref, accent, thumb_path, x, y,
               w=4.20, h=2.40):
    """Paper card: NO outer box, NO thumbnail frame — just year + title +
    image + sub + citation. Era encoded by accent color on year/citation only.
    Returns Group (Image isn't a VMobject)."""
    # Year (top-left of card area, small)
    yr = m_text(year, scale=0.36, color=accent)
    yr.move_to(np.array([x - w/2 + 0.40, y + h/2 - 0.26, 0]))

    # Title — centered horizontally near top
    title_t = m_text(title, scale=0.30, color=TONE_FG)
    title_t.move_to(np.array([x, y + h/2 - 0.26, 0]))

    # Thumbnail centered, aspect-preserving fit
    img = ImageMobject(thumb_path)
    img.set_height(1.10)
    if img.get_width() > 3.70:
        img.set_width(3.70)
    img.move_to(np.array([x, y + 0.08, 0]))

    # Sub line (below thumbnail)
    sub_t = m_text(sub, scale=0.22, color=TONE_MUTED)
    sub_t.move_to(np.array([x, y - h/2 + 0.46, 0]))

    # Citation (bottom) — colored to match era
    ref_t = m_text(ref, scale=0.20, color=accent)
    ref_t.move_to(np.array([x, y - h/2 + 0.22, 0]))
    ref_t.set_opacity(0.85)

    return Group(yr, title_t, img, sub_t, ref_t)


class Section01_Shot13_FurtherReading(MuseumScene):
    def construct(self):
        self.add_museum_bg(accent="amber")
        ribbon = ChapterRibbon(section="further reading")
        self.add(ribbon)

        # ============================================================
        # Header (~2s)
        # ============================================================
        head_top = m_text("Want to go deeper?", scale=0.58, color=TONE_FG)
        head_top.to_edge(UP, buff=0.30)
        head_sub = m_text("six papers, fifteen years, one rabbit hole.",
                          scale=0.30, color=TONE_MUTED)
        head_sub.next_to(head_top, DOWN, buff=0.14)

        self.play(FadeIn(head_top, shift=0.10 * DOWN), run_time=0.55)
        self.play(FadeIn(head_sub, shift=0.05 * DOWN), run_time=0.40)
        self.wait(0.49)

        # ============================================================
        # Card grid: 2 rows × 3 cols, cards now taller (2.40 vs 1.85)
        # ============================================================
        col_xs = [-4.55, 0.0, 4.55]
        row_ys = [0.65, -2.05]

        cards_top = []
        cards_bot = []
        for i, (year, title, sub, ref, accent, thumb) in enumerate(CARDS):
            row = 0 if i < 3 else 1
            col = i % 3
            card = _make_card(year, title, sub, ref, accent, thumb,
                              col_xs[col], row_ys[row])
            if row == 0:
                cards_top.append(card)
            else:
                cards_bot.append(card)

        # Reveal cards one-by-one in chronological order (1995 → 2022).
        # Top row (classical era) first, then bottom row (deep-learning era).
        all_cards_in_order = cards_top + cards_bot
        for card in all_cards_in_order:
            self.play(FadeIn(card, shift=0.15 * DOWN), run_time=0.55)
            self.wait(0.7)

        # Final dwell after all 6 visible — let viewer scan the whole grid
        self.wait(2.07)

        # Highlight Ding & Wang card (this chapter) — only this one gets a box
        ding_x, ding_y = col_xs[1], row_ys[0]
        chapter_box = RoundedRectangle(width=4.30, height=2.55,
                                        corner_radius=0.18)
        chapter_box.set_stroke(TONE_AMBER, 2.0).set_fill(TONE_AMBER, 0.05)
        chapter_box.move_to(np.array([ding_x, ding_y, 0]))

        callout = m_text("← this chapter", scale=0.28, color=TONE_AMBER)
        callout.next_to(chapter_box, UP, buff=0.10)
        callout.shift(1.40 * RIGHT)

        self.play(
            ShowCreation(chapter_box),
            FadeIn(callout, shift=0.05 * DOWN),
            run_time=0.85,
        )
        self.wait(2.48)
        self.play(FadeOut(callout), run_time=0.4)

        # Final dwell + fade
        self.wait(1.65)
        all_mobs = Group(
            *cards_top, *cards_bot, chapter_box,
            head_top, head_sub,
        )
        self.play(FadeOut(all_mobs), run_time=0.8)
