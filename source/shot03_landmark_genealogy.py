"""Shot 03 — Landmark Genealogy.

Render:
    "D:/Downloads/Tools/Anaconda/Scripts/manimgl.exe" \
        source/shot03_LandmarkGenealogy.py Section01_Shot03_LandmarkGenealogy \
        -w -l --video_dir videos --file_name shot03_LandmarkGenealogy

Replaces shot03_ZoomIntoTopic. See
docs/superpowers/specs/2026-05-25-shot03-landmark-genealogy-design.md.
"""
from manimlib import *
import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    MuseumScene, m_text,
    TONE_AMBER, TONE_CYAN, TONE_FG, TONE_MUTED, TONE_RED,
    HERO_FRONTAL, FACE_EYE_L_UV,
    ChapterRibbon, typewriter_anim,
    hud_corners, dashed_rect,
)
from dot_morph import (
    make_target_face_canonical,
    make_target_id_card, make_target_mesh3d, make_target_sketch,
    make_target_pose_triad, make_target_smile, make_target_beauty_glow,
    morph_dots, N, POSE_TRIAD_SLICES,
)


def _dim_img(path, factor=0.7):
    """Darkened copy (RGB*factor, alpha kept) of a bright hero PNG so the face
    sits naturally on the dark premium background. Cached next to the source."""
    import os
    from PIL import Image
    import numpy as _np
    path = str(path)
    d = os.path.join(os.path.dirname(path), "dim")
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, f"{factor:.2f}_" + os.path.basename(path))
    if not os.path.exists(out):
        arr = _np.array(Image.open(path).convert("RGBA")).astype(_np.float32)
        arr[..., :3] *= factor
        Image.fromarray(_np.clip(arr, 0, 255).astype("uint8")).save(out)
    return out


FACE_CENTER = np.array([-3.5, 0.0, 0.0])
FACE_HEIGHT = 4.4
TARGET_CENTER = (3.0, 0.0)
LABEL_Y = -2.2


class Section01_Shot03_LandmarkGenealogy(MuseumScene):
    """45 s sequence: 6 dot-morph targets → eye zoom → 3 failure cases → shatter."""

    def construct(self):
        self.add_museum_bg(accent="amber")
        ribbon = ChapterRibbon(section="12.1")
        self.add(ribbon)

        # ---- 0.0 – 2.0 s: head + title ----
        face = ImageMobject(_dim_img(HERO_FRONTAL)).set_height(FACE_HEIGHT)
        face.move_to(FACE_CENTER)
        title = m_text("Where landmarks help", scale=0.50, color=TONE_AMBER).move_to([0, 3.4, 0])
        self.play(FadeIn(face), FadeIn(title, shift=0.10*DOWN), run_time=1.0)
        self.wait(1.5)

        # ---- 2.0 – 3.5 s: 88 dots emerge from face ----
        face_pts = make_target_face_canonical(face_center=tuple(FACE_CENTER[:2]),
                                              face_height=FACE_HEIGHT)
        dots = VGroup(*[
            Dot(radius=0.05).set_fill(TONE_AMBER, 1.0).set_stroke(width=0)
            .move_to(np.array([face_pts[i, 0], face_pts[i, 1], 0]))
            .set_opacity(0.0)
            for i in range(N)
        ])
        self.add(dots)
        # Face fades to ghost while dots fade in.
        self.play(
            face.animate.set_opacity(0.25),
            *[d.animate.set_opacity(1.0) for d in dots],
            run_time=1.5,
        )
        # Stash references for subsequent tasks.
        self._face = face
        self._dots = dots
        self._title = title
        self._face_pts = face_pts

        # ---- Applications: 6 ANIMATED cards (Three.js / canvas frame sequences) ----
        import os as _os
        from hero_kit import SeqCard
        _SEQ = _os.path.join(_os.path.dirname(_THIS_DIR), "assets", "apps", "seq")
        self.play(*[d.animate.set_opacity(0.0) for d in dots], run_time=0.4)
        self.remove(dots)

        card_center = np.array([3.0, 0.30, 0])
        label_y = -2.15
        connector = Line(np.array([-1.7, 0.1, 0]), np.array([0.9, 0.30, 0]))
        connector.set_stroke(TONE_AMBER, 1.4, opacity=0.35)
        self.play(ShowCreation(connector), run_time=0.4)

        # (mode, label, accent, height, width)  width set → wide card (expr)
        # Order matches the narration sequence: recognition → 3D → cartoon/stylize
        # → pose → expression (cards advance ~9.6s ≈ the VO's ~10s/app cadence).
        app_specs = [
            ("recog",  "Face recognition",    "#46e06a", 3.7,  None),
            ("recon",  "3D reconstruction",   TONE_CYAN,  3.7,  None),
            ("avatar", "Avatar / stylize",    "#a070ff",  3.7,  None),
            ("pose",   "Pose estimation",     TONE_AMBER, 3.7,  None),
            ("expr",   "Expression analysis", TONE_AMBER, None, 5.6),
        ]

        def build_deco(label, accent, h, w):
            cw = w if w is not None else h
            ch = 3.55 if w is not None else h
            rect = Rectangle(width=cw, height=ch).move_to(card_center)
            border = rect.copy().set_stroke(accent, 2.0, opacity=0.85).set_fill(opacity=0)
            brackets = hud_corners(rect, color=accent, arm=0.32, stroke_w=3.0,
                                   width=cw + 0.12, height=ch + 0.12)
            lab = m_text(label, scale=0.48, color=accent)
            lab.move_to(np.array([card_center[0], label_y, 0]))
            deco = VGroup(border, brackets, lab)
            extra = VGroup()
            if label == "Face recognition":
                tag = m_text("✓ MATCH", scale=0.34, color="#46e06a")
                tag.move_to(np.array([card_center[0] + cw / 2 - 0.55,
                                      card_center[1] + ch / 2 - 0.30, 0]))
                extra = VGroup(tag)
            return deco, extra

        # Per-card holds so each card SWITCHES on its narration cue (card1 appears
        # ~+5.3 after the intro; switch→recon@11.2, →stylize@21.3, →pose@29.1,
        # →expr@36.8). Last card (expr) dwells through "beautification".
        HOLDS = [4.9, 9.6, 7.3, 7.2, 9.0]
        prev_card = prev_deco = prev_extra = None
        for i, (mode, label, accent, h, w) in enumerate(app_specs):
            card = SeqCard(_os.path.join(_SEQ, mode), 30, card_center, height=h, width=w, fps=20)
            self.add(card)
            card.add_updater(lambda g, dt: g.tick(dt))
            deco, extra = build_deco(label, accent, h, w)
            if prev_card is None:
                self.play(card.vis.animate.set_value(1.0), *[FadeIn(m) for m in deco],
                          run_time=0.5)
            else:
                self.play(
                    prev_card.vis.animate.set_value(0.0),
                    *[FadeOut(m) for m in prev_deco], *[FadeOut(m) for m in prev_extra],
                    card.vis.animate.set_value(1.0), *[FadeIn(m) for m in deco],
                    run_time=0.5,
                )
                prev_card.clear_updaters(); self.remove(prev_card)
            if len(extra) > 0:
                self.play(*[FadeIn(m) for m in extra], run_time=0.30)
            self.wait(HOLDS[i])
            prev_card, prev_deco, prev_extra = card, deco, extra

        self.play(
            prev_card.vis.animate.set_value(0.0),
            *[FadeOut(m) for m in prev_deco], *[FadeOut(m) for m in prev_extra],
            FadeOut(connector),
            self._face.animate.set_opacity(1.0),
            run_time=0.6,
        )
        prev_card.clear_updaters(); self.remove(prev_card)
        self.play(FadeOut(self._title), run_time=0.50)
        self.wait(5.8)   # face holds through "...beautification" → eye-box VO starts (+52.9)

        # ---- 24.0 – 26.5 s: zoom into right eye, draw rectangle, caption ----
        # Right eye UV in the canonical face is at (0.408, 0.222) per build_landmark_uv.
        # Compute screen position of the right eye on the face mobject.
        # FACE_EYE_L_UV is calibrated for the v3 hero (the eye on the LEFT
        # side of the image = subject's right eye).
        right_eye_uv = np.array(FACE_EYE_L_UV)
        face_w = self._face.get_height() * (16.0 / 9.0)
        face_h = self._face.get_height()
        face_center = self._face.get_center()
        eye_screen = face_center + np.array([
            (right_eye_uv[0] - 0.5) * face_w,
            (0.5 - right_eye_uv[1]) * face_h,
            0.0,
        ])
        # Scale face by 1.8 and shift so eye is centered at (0, 0).
        zoom = 1.8
        # After scaling, eye offset from face center is multiplied by zoom.
        eye_offset = (eye_screen - face_center) * zoom
        target_face_center = -eye_offset                                # so eye lands at origin
        self.play(
            self._face.animate.scale(zoom).move_to(target_face_center),
            run_time=1.5,
            rate_func=smooth,
        )
        # Build the rectangle as 4 explicit DashedLines, one per edge.
        # DashedVMobject distributes dashes proportionally to perimeter, so the
        # short vertical edges of a 2.0x0.9 rect end up with only ~3 short dashes
        # that vanish over skin. Per-edge construction gives full control.
        rect_w, rect_h = 2.0, 0.9
        rect_x = rect_w / 2
        rect_y = rect_h / 2
        edge_kwargs = dict(dash_length=0.14, positive_space_ratio=0.55,
                           stroke_color=TONE_AMBER, stroke_width=5.5)
        rect_top    = DashedLine(np.array([-rect_x, +rect_y, 0]),
                                 np.array([+rect_x, +rect_y, 0]), **edge_kwargs)
        rect_bot    = DashedLine(np.array([-rect_x, -rect_y, 0]),
                                 np.array([+rect_x, -rect_y, 0]), **edge_kwargs)
        rect_left   = DashedLine(np.array([-rect_x, -rect_y, 0]),
                                 np.array([-rect_x, +rect_y, 0]), **edge_kwargs)
        rect_right  = DashedLine(np.array([+rect_x, -rect_y, 0]),
                                 np.array([+rect_x, +rect_y, 0]), **edge_kwargs)
        rect = VGroup(rect_top, rect_bot, rect_left, rect_right)
        self.play(ShowCreation(rect), run_time=1.0)
        # Caption below.
        caption = m_text("a heuristic — find the eye in this box",
                         scale=0.38, color=TONE_FG)
        caption.move_to([0, 2.6, 0])
        self.play(FadeIn(caption, shift=0.05*UP), run_time=1.0)
        self._rect = rect
        self._caption = caption
        self._rect_screen_center = np.array([0.0, 0.0, 0.0])
        # Box demonstrated on the clean face — VO: "...darkest spot. It works. Then the
        # real world shows up." Holds until the first failure (shadow) at +72.3.
        self.wait(13.0)

        # ---- 26.5 – 31.5 s: B1 Illumination — cross-dissolve + shadow overlay ----
        from museum_tone import ASSETS_DIR
        lit_face = ImageMobject(_dim_img(ASSETS_DIR / "hero_lighting_side_v3.png"))
        lit_face.set_height(self._face.get_height()).move_to(self._face.get_center())
        lit_face.set_opacity(0.0)
        self.add(lit_face)
        self.play(
            self._face.animate.set_opacity(0.0),
            lit_face.animate.set_opacity(1.0),
            FadeOut(self._caption),
            run_time=1.5,
        )
        # Shadow overlay inside rectangle.
        shadow = Rectangle(width=2.0, height=0.9,
                           fill_color=BLACK, fill_opacity=0.0,
                           stroke_width=0).move_to([0, 0, 0])
        self.add(shadow)
        # Rectangle stroke pulse red.
        self.play(
            shadow.animate.set_fill(opacity=0.7),
            self._rect.animate.set_stroke(TONE_RED, 5.5),
            run_time=1.5,
        )
        cap1 = m_text("shadow swallows the edge", scale=0.48, color="#ff4848")
        cap1.set_stroke("#ff4848", 1.2)
        cap1.move_to([0, 2.6, 0])
        self.play(FadeIn(cap1, shift=0.05*DOWN), run_time=0.5)
        self.wait(3.0)   # ILLUMINATION dwell — VO "...the edge is gone." → POSE @ +79.7
        self.play(
            FadeOut(cap1),
            shadow.animate.set_fill(opacity=0.0),
            self._rect.animate.set_stroke(TONE_AMBER, 5.5),
            run_time=0.5,
        )
        self.remove(shadow)
        # Restore the frontal face for B2 — short crossfade (was instant cut, jarring).
        self.play(
            lit_face.animate.set_opacity(0.0),
            self._face.animate.set_opacity(1.0),
            run_time=0.4,
        )
        self.remove(lit_face)

        # ---- 31.5 – 36.5 s: B2 Pose — quick swap to yaw30 (slow crossfade was jarring) ----
        yaw_face = ImageMobject(_dim_img(ASSETS_DIR / "hero_yaw30_v3.png"))
        yaw_face.set_height(self._face.get_height()).move_to(self._face.get_center())
        yaw_face.set_opacity(0.0)
        self.add(yaw_face)
        # Fast crossfade: 0.6s — fast enough that the eye doesn't dwell on the
        # different pose positions between frontal and yaw30 stills.
        self.play(
            self._face.animate.set_opacity(0.0),
            yaw_face.animate.set_opacity(1.0),
            run_time=0.6,
        )
        # Hold for the spoken caption duration that was previously inside the 2.5s
        self.wait(2.0)
        # Measured by iris detection on hero_yaw30_v3.png: the boxed eye (subject's right,
        # frontal uv 0.397 = screen origin) drifts to yaw uv (0.323, 0.285) — i.e. LEFT in
        # image space. Zoomed face W≈14.08, H≈7.92, so screen ≈ ((0.323-0.397)*14.08,
        # (0.292-0.285)*7.92) = (-1.04, +0.06). (Earlier (0.85,-0.05) pointed the wrong way.)
        apparent_eye = np.array([-0.97, 0.01, 0.0])
        # Small red dot marks where the eye actually IS now (anchor for "drift" target).
        eye_marker = Dot(point=apparent_eye, radius=0.10, color=TONE_RED)
        eye_marker.set_fill(TONE_RED, 1.0).set_stroke(width=0)
        # The yaw_face image was added AFTER self._rect, so it covers the box (z-order).
        # Bring the rect back to front so the "box" context is visible during this beat.
        self.bring_to_front(self._rect)
        # Pulse the box red so context is clear (box says "eye should be HERE" — but it isn't).
        self.play(self._rect.animate.set_stroke(TONE_RED, 6.0), run_time=0.25)
        # Arrow from the box (screen origin) to where the eye actually is.
        arrow = Arrow(np.array([0, 0, 0]), apparent_eye,
                      stroke_color=TONE_RED, stroke_width=6.0, buff=0.10)
        self.play(GrowArrow(arrow), FadeIn(eye_marker, scale=0.5), run_time=0.4)
        cap2 = m_text("the eye drifts outside the box", scale=0.48, color="#ff4848")
        cap2.set_stroke("#ff4848", 1.2)
        cap2.move_to([0, 2.6, 0])
        self.play(FadeIn(cap2, shift=0.05*DOWN), run_time=0.5)
        self.wait(1.55)   # POSE dwell — VO "...out of the box." → SCALE @ +86.0
        self.play(FadeOut(cap2), FadeOut(arrow), FadeOut(eye_marker),
                  self._rect.animate.set_stroke(TONE_AMBER, 5.5),
                  run_time=0.5)
        # Restore frontal face — short crossfade (was 0.1s near-instant, jarring).
        self.play(yaw_face.animate.set_opacity(0.0),
                  self._face.animate.set_opacity(1.0), run_time=0.5)
        self.remove(yaw_face)

        # ---- 36.5 – 41.5 s: B3 Scale — face too small, then too large ----
        # Save current scale + position so we can restore later.
        face_orig_height = self._face.get_height()
        face_orig_center = self._face.get_center()
        # Shrink to 0.45×.
        self.play(
            self._face.animate.scale(0.45),
            run_time=2.0,
        )
        cap3 = m_text("the box no longer fits the face", scale=0.48, color="#ff4848")
        cap3.set_stroke("#ff4848", 1.2)
        cap3.move_to([0, 2.6, 0])
        self.play(FadeIn(cap3, shift=0.05*DOWN), run_time=0.5)
        self.wait(2.5)
        self.play(FadeOut(cap3), run_time=0.3)
        # Overshoot: scale up to 3.5× of the shrunk size (≈ 1.6× original).
        self.play(self._face.animate.scale(3.5), run_time=1.0)
        cap3b = m_text("…or the face overflows it", scale=0.56, color="#ff4848")
        cap3b.set_stroke("#ff4848", 1.2)
        cap3b.move_to([0, 3.4, 0])
        self.play(FadeIn(cap3b, shift=0.05*DOWN), run_time=0.3)
        self.wait(2.5)   # SCALE dwell — VO "...stops fitting at all." → exhibit/shatter
        self.play(FadeOut(cap3b), run_time=0.3)
        # Restore for the closing shatter.
        self.play(
            self._face.animate.set_height(face_orig_height).move_to(face_orig_center),
            run_time=0.0,
        )
        self.play(self._face.animate.set_opacity(0.5), run_time=0.3)

        # ---- 41.5 – 44.5 s: shatter + foreshadow + exhibit row ----
        # Glow pulse on the rectangle.
        self.play(self._rect.animate.set_stroke(TONE_RED, 7.0), run_time=0.30)
        self.play(self._rect.animate.set_stroke(TONE_RED, 5.5), run_time=0.30)
        # Decompose the dashed rectangle into individual segments.
        segments = list(self._rect.submobjects)
        # Random shift + rotate + fade for each segment.
        rng = np.random.default_rng(7)
        shatter_anims = []
        for seg in segments:
            angle = rng.uniform(-1, 1) * (45 * DEGREES)
            shift = rng.uniform(-1, 1, size=3) * np.array([0.6, 0.6, 0.0])
            shift[1] = -abs(shift[1]) - 0.3                       # gravity: always down
            shatter_anims.append(seg.animate
                                 .rotate(angle)
                                 .shift(shift)
                                 .set_opacity(0))
        self.play(
            LaggedStart(*shatter_anims, lag_ratio=0.05),
            FadeOut(self._face),
            run_time=1.2,
        )
        self.wait(5.0)   # VO "...three ways to break." settles before the hand-off
        # Foreshadow title + subtitle hand-off to next shot.
        foreshadow = m_text("we need a smarter search",
                            scale=0.62, color=TONE_AMBER)
        foreshadow.move_to([0, 0.5, 0])
        subtitle = m_text("next: the framework  →",
                          scale=0.30, color=TONE_CYAN)
        subtitle.move_to([0, -0.15, 0])
        # Thin amber rule beneath the title.
        rule = Line([-2.2, 0.15, 0], [+2.2, 0.15, 0])
        rule.set_stroke(TONE_AMBER, 1.4).set_opacity(0.55)
        self.play(typewriter_anim(foreshadow, char_duration=0.05), run_time=1.0)
        self.wait(3.0)   # VO "The answer isn't a better box..."
        # Search-radius collapse — visual metaphor for "smarter search".
        search_radius = Circle(radius=2.5, stroke_color=TONE_AMBER, stroke_width=1.8,
                               fill_opacity=0.0)
        search_radius.set_stroke(opacity=0.0)
        search_radius.move_to(foreshadow.get_center())
        self.add(search_radius)
        self.play(search_radius.animate.set_stroke(opacity=0.7), run_time=0.3)
        self.play(search_radius.animate.scale(0.25), run_time=0.8, rate_func=smooth)
        self.play(search_radius.animate.set_stroke(opacity=0.0), run_time=0.2)
        self.play(
            ShowCreation(rule),
            FadeIn(subtitle, shift=0.05*UP),
            run_time=0.5,
        )

        # Exhibit row: 3 uniform-size labeled thumbnails of the three failure cases.
        from museum_tone import ASSETS_DIR
        thumb_specs = [
            ("hero_lighting_side_v3.png", "ILLUMINATION"),
            ("hero_yaw30_v3.png",         "POSE"),
            ("hero_front_v3.png",         "SCALE"),
        ]
        thumb_y = -2.30
        label_y = -3.20
        xs = [-4.30, 0.0, +4.30]
        thumb_h = 1.50
        thumbs = []
        thumb_labels = []
        for x, (fname, label_txt) in zip(xs, thumb_specs):
            img = ImageMobject(_dim_img(ASSETS_DIR / fname)).set_height(thumb_h)
            img.move_to(np.array([x, thumb_y, 0]))
            img.set_opacity(0.0)
            thumbs.append(img)
            lbl = m_text(label_txt, scale=0.26, color=TONE_MUTED)
            lbl.move_to(np.array([x, label_y, 0]))
            lbl.set_opacity(0.0)
            thumb_labels.append(lbl)
        # Add to scene first (ImageMobject needs to be added to be animated).
        for t in thumbs:
            self.add(t)
        for lbl in thumb_labels:
            self.add(lbl)
        # Reveal in LaggedStart: thumb i fades in with its label as one unit.
        reveal_anims = []
        for t, lbl in zip(thumbs, thumb_labels):
            reveal_anims.append(
                AnimationGroup(
                    t.animate.set_opacity(1.0),
                    lbl.animate.set_opacity(1.0),
                    lag_ratio=0.0,
                )
            )
        self.play(LaggedStart(*reveal_anims, lag_ratio=0.18), run_time=0.9)
        self.wait(12.2)   # VO "...the few ways it's allowed to move. That's the framework we build next." + gap to shot04
        # Global fade-out.
        all_vec = VGroup(foreshadow, subtitle, rule, *thumb_labels)
        all_img = Group(*thumbs)
        for seg in segments:
            all_vec.add(seg)
        self.play(FadeOut(all_vec), FadeOut(all_img), run_time=0.7)
