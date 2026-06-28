"""
Shot 00 — BookIntro reframed as "What does a face actually tell us?"
Book materialises as the 'map of answers', spins on its axis (turntable),
zooms into Ch.12 callout.
"""
from manimlib import *

import os, sys, pathlib
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_FG, TONE_MUTED,
    MuseumScene, m_text, AnimatedHead,
    ChapterRibbon, typewriter_anim,
)

_ASSETS = pathlib.Path(__file__).parent.parent / "assets"
_BOOK_FRONT = str(_ASSETS / "book_front.png")
_BOOK_FRAMES_DIR = str(_ASSETS / "book_frames")


class Section01_Shot00_BookIntro(MuseumScene):
    """Opener: question → book turntable → Ch.12 title reveal."""

    def construct(self):
        self.add_museum_bg(accent="amber")

        # Persistent chapter ribbon (top-left); present from frame 1 to end.
        ribbon = ChapterRibbon(section=None)
        self.add(ribbon)

        # ----- Beat 1: Greeting -----
        hello = m_text("Hello.", scale=1.10, color=TONE_FG)
        hello.move_to(np.array([0, 0.30, 0]))
        welcome = m_text(
            "Welcome to a five-minute tour of  a classic computer-vision problem.",
            scale=0.40, color=TONE_MUTED,
        ).move_to(np.array([0, -0.70, 0]))
        self.play(FadeIn(hello, scale=1.05), run_time=0.454)
        self.wait(0.229)
        self.play(FadeIn(welcome, shift=0.08 * UP), run_time=0.353)
        self.wait(0.4)
        self.play(
            FadeOut(hello, shift=0.20 * UP),
            FadeOut(welcome, shift=0.10 * UP),
            run_time=0.600,
        )

        # ----- Beat 2: Literature framing -----
        topic = m_text(
            "Today's source:",
            scale=0.36, color=TONE_MUTED,
        ).move_to(np.array([0, 1.10, 0]))
        src_title = m_text(
            "Handbook of Face Recognition,  2nd ed.",
            scale=0.50, color=TONE_FG,
        ).move_to(np.array([0, 0.40, 0]))
        src_ch = m_text(
            "Chapter 12  —  Facial Landmark Localization",
            scale=0.42, color=TONE_AMBER,
        ).move_to(np.array([0, -0.30, 0]))
        src_authors = m_text(
            "Xiaoqing Ding  &  Liting Wang  ·  Tsinghua University",
            scale=0.30, color=TONE_MUTED,
        ).move_to(np.array([0, -1.10, 0]))
        self.wait(0.5)  # __TRANS_HOLD__
        self.play(typewriter_anim(topic, char_duration=0.025), run_time=0.45)
        self.play(typewriter_anim(src_title, char_duration=0.035), run_time=0.5)
        self.play(typewriter_anim(src_ch, char_duration=0.035), run_time=0.5)
        # Underline under Chapter 12 line — draws on after src_ch finishes.
        underline = Line(
            src_ch.get_left() + LEFT * 0.05,
            src_ch.get_right() + RIGHT * 0.05,
            color=TONE_AMBER,
            stroke_width=1.5,
        )
        underline.next_to(src_ch, DOWN, buff=0.08)
        self.play(ShowCreation(underline), run_time=0.4)
        # Authors at 70% opacity — saved state inside typewriter_anim then
        # carries this through, so each char restores to 0.7 opacity.
        src_authors.set_opacity(0.7)
        self.play(typewriter_anim(src_authors, char_duration=0.025), run_time=0.45)
        self.wait(0.15)
        self.play(
            FadeOut(topic), FadeOut(src_title),
            FadeOut(src_ch), FadeOut(underline), FadeOut(src_authors),
            run_time=0.600,
        )

        # ----- Beat 3 (hook question) removed — was redundant with shot 01 Hook.
        # The "88 dots" question now lives only in shot 01 with the count-up polish.

        # ----- Book turntable (spinning) -----
        # Load 90-frame Blender turntable; tick visible frame from accumulated dt.
        try:
            n_frames = 90
            book_imgs = []
            for i in range(1, n_frames + 1):
                p = _ASSETS / "book_frames" / f"frame_{i:04d}.png"
                if p.exists():
                    book_imgs.append(ImageMobject(str(p)))
            if not book_imgs:
                raise FileNotFoundError("no book_frames")
            for b in book_imgs:
                b.set_height(6.2)
                b.move_to(np.array([0, 0.95, 0]))
                b.set_opacity(0)
            book = Group(*book_imgs)
            self.add(book)
            book._frames = book_imgs
            book._n = len(book_imgs)
            book._fps = 30.0
            book._t_acc = 0.0
            book._fade = 0.0
            def _tick(grp, dt):
                grp._t_acc += dt
                period = grp._n / grp._fps
                t = grp._t_acc % period
                idx = int(t * grp._fps) % grp._n
                for i, m in enumerate(grp._frames):
                    m.set_opacity(grp._fade if i == idx else 0.0)
            book.add_updater(_tick)
            ft = ValueTracker(0.0)
            def _drive(_, dt):
                book._fade = ft.get_value()
            driver = Dot().set_opacity(0)
            self.add(driver)
            driver.add_updater(_drive)
            self.play(ft.animate.set_value(1.0), run_time=0.606)
        except Exception:
            # Fallback: stylised book rectangle
            book = RoundedRectangle(width=3.9, height=5.6, corner_radius=0.14)
            book.set_stroke(TONE_CYAN, 2.0).set_fill("#1c1c2a", 1.0)
            book.move_to(np.array([0, 0.50, 0]))
            self.play(FadeIn(book, scale=1.03), run_time=0.606)

        # Chapter title — bold hero treatment under the spinning book
        ch_title = m_text("CHAPTER 12", scale=0.98, color=TONE_AMBER)
        ch_title.move_to(np.array([0, -2.15, 0]))
        ch_sub = m_text("Facial Landmark Localization",
                        scale=0.48, color=TONE_FG)
        ch_sub.next_to(ch_title, DOWN, buff=0.16)
        hero_rule = Line(LEFT * 2.4, RIGHT * 2.4).set_stroke(TONE_AMBER, 2.0, opacity=0.8)
        hero_rule.next_to(ch_sub, DOWN, buff=0.18)

        # Chapter title entrance: zoom from 0.4 → 1.0 with overshoot bounce
        ch_title.scale(0.40)
        ch_title.set_opacity(0)
        self.add(ch_title)
        self.play(
            ch_title.animate.scale(1.0 / 0.40).set_opacity(1.0),
            run_time=0.278,
            rate_func=lambda t: smooth(t) ** 0.7,  # ease-out
        )
        # Tiny overshoot pulse for kinetic feel
        self.play(ch_title.animate.scale(1.08), run_time=0.076)
        self.play(ch_title.animate.scale(1.0 / 1.08), run_time=0.076)

        # Subtitle slides up from below with stagger
        ch_sub.set_opacity(0)
        ch_sub.shift(0.25 * DOWN)
        self.add(ch_sub)
        self.play(
            ch_sub.animate.set_opacity(1.0).shift(0.25 * UP),
            run_time=0.278,
            rate_func=smooth,
        )
        self.play(ShowCreation(hero_rule), run_time=0.35)
        self.wait(0.35)

        # Takeaway at the bottom
        takeaway = m_text(
            "A map of answers  —  6 questions, 6 sections.",
            scale=0.42, color=TONE_CYAN,
        ).to_edge(DOWN, buff=0.40)
        self.play(FadeIn(takeaway, shift=0.1 * UP), run_time=0.353)
        self.wait(0.25)

        if hasattr(book, "clear_updaters"):
            book.clear_updaters()
        self.play(FadeOut(Group(book, ch_title, ch_sub, hero_rule, takeaway)), run_time=0.353)
