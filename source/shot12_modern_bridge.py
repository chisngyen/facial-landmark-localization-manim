"""
Shot 11 — Beyond ASM: 15 years later.

Five-beat timeline bridging Ch.12 (2011 ASM/RFE) to modern landmark localization:
    2011 ASM → 2014 SDM → 2017 FAN → 2020 MediaPipe → 2022+ 3DMM/FLAME.

Each beat: era label (left) + hero face with method-specific landmarks (right)
+ caption. Closes with three trade-off pills.

Render:
    "D:/Downloads/Tools/Anaconda/Scripts/manimgl.exe" source/shot11_ModernBridge.py \
        Section01_Shot12_ModernBridge -w -l --video_dir videos --file_name shot11_ModernBridge
"""
from manimlib import *

import os, sys
import numpy as np
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_RED, TONE_FG, TONE_MUTED, TONE_GREY,
    MuseumScene, m_text, ChapterRibbon,
    HERO_FRONTAL, HERO_WITH_LANDMARKS_BAKED, HERO_PROFILE_R_V3,
    HERO_SWAY_LANDMARKS_DIR, HERO_SWAY_NORMAL_DIR, HERO_SWAY_FRAMES,
    AnimatedHead,
    uv_to_manim, build_landmark_uv,
    FACE_EYE_L_UV, FACE_EYE_R_UV, FACE_NOSE_UV, FACE_MOUTH_UV,
)


# ============================================================
# Helpers
# ============================================================
def _ref_inset(image_path, citation, center, width, accent=TONE_MUTED):
    """Reference paper figure as inset card: image + thin frame + citation.
    Used to show actual paper results alongside the educational visualizations.
    Returns a Group (Image + VMobjects)."""
    img = ImageMobject(image_path)
    img.set_width(width)
    img.move_to(center)
    h = img.get_height()
    frame = Rectangle(width=width + 0.08, height=h + 0.08)
    frame.set_stroke(accent, 1.2).set_fill(opacity=0)
    frame.set_opacity(0.55)
    frame.move_to(center)
    cit = m_text(citation, scale=0.20, color=accent).set_opacity(0.75)
    cit.move_to(np.array([center[0], center[1] - h/2 - 0.22, 0]))
    return Group(img, frame, cit)


def _make_hero(image_path, height=4.6, x=2.4):
    """Place a hero image at (x, slightly-above-center)."""
    img = ImageMobject(image_path)
    img.set_height(height)
    img.move_to(np.array([x, 0.10, 0]))
    return img


def _era_block(year, method, sub, x=-3.7, y_top=2.0, accent=TONE_AMBER):
    """Big left-side era label: YEAR / METHOD / one-line description."""
    yr = m_text(year, scale=0.80, color=accent)
    yr.move_to(np.array([x, y_top, 0]))
    method_t = m_text(method, scale=0.62, color=TONE_FG)
    method_t.next_to(yr, DOWN, buff=0.25, aligned_edge=LEFT)
    method_t.shift(0.05 * RIGHT)  # tiny optical align
    sub_t = m_text(sub, scale=0.30, color=TONE_MUTED)
    sub_t.next_to(method_t, DOWN, buff=0.20, aligned_edge=LEFT)
    return VGroup(yr, method_t, sub_t)


def _caption(text, y=-2.85, color=None, scale=0.34):
    """Bottom-centered caption line."""
    c = m_text(text, scale=scale, color=color if color else TONE_FG)
    c.move_to(np.array([0, y, 0]))
    return c


def _dense_mesh_from_anchors(hero_img, color=TONE_CYAN, radius=0.018,
                              opacity=0.85):
    """Generate ~200 dense mesh dots by interpolating between known face-feature
    UV anchors (eye L/R, nose, mouth from museum_tone.FACE_*_UV — measured from
    actual Blender render). No synthetic UVs; everything derived from real anchors.
    Mimics MediaPipe Face Mesh density."""
    pts_uv = []

    # 1) Eye contours (ellipse around each eye anchor) — 12 per eye
    for cx, cy in [FACE_EYE_L_UV, FACE_EYE_R_UV]:
        for i in range(12):
            th = (i / 12) * 2 * np.pi
            pts_uv.append((cx + 0.040 * np.cos(th),
                           cy + 0.012 * np.sin(th)))
        # Eye inner detail (small ring)
        for i in range(6):
            th = (i / 6) * 2 * np.pi
            pts_uv.append((cx + 0.020 * np.cos(th),
                           cy + 0.006 * np.sin(th)))

    # 2) Eyebrows (5 points per brow, above each eye anchor)
    for cx, cy in [FACE_EYE_L_UV, FACE_EYE_R_UV]:
        for i in range(5):
            t = i / 4.0
            pts_uv.append((cx + (t - 0.5) * 0.085,
                           cy - 0.060 - 0.005 * np.sin(t * np.pi)))

    # 3) Nose bridge from between-eyes to nose anchor (6 points)
    eye_mid_x = (FACE_EYE_L_UV[0] + FACE_EYE_R_UV[0]) / 2
    eye_y     = (FACE_EYE_L_UV[1] + FACE_EYE_R_UV[1]) / 2
    nose_x, nose_y = FACE_NOSE_UV
    for i in range(6):
        t = i / 5
        pts_uv.append((eye_mid_x + (nose_x - eye_mid_x) * t,
                       eye_y + (nose_y - eye_y) * t))
    # Nose tip wings (4 points around nose anchor)
    for i in range(4):
        th = (i / 4) * 2 * np.pi
        pts_uv.append((nose_x + 0.028 * np.cos(th),
                       nose_y + 0.020 * np.sin(th)))

    # 4) Mouth outline (20 points around mouth anchor)
    mouth_x, mouth_y = FACE_MOUTH_UV
    for i in range(20):
        th = (i / 20) * 2 * np.pi
        pts_uv.append((mouth_x + 0.075 * np.cos(th),
                       mouth_y + 0.025 * np.sin(th)))
    # Mouth inner line (8 points, smaller ellipse)
    for i in range(8):
        th = (i / 8) * 2 * np.pi
        pts_uv.append((mouth_x + 0.045 * np.cos(th),
                       mouth_y + 0.012 * np.sin(th)))

    # 5) Face oval — anchored to eye top + nose + mouth + chin extrapolated
    face_top_y    = eye_y - 0.12
    chin_y        = mouth_y + 0.14
    face_left_x   = FACE_EYE_L_UV[0] - 0.16
    face_right_x  = FACE_EYE_R_UV[0] + 0.16
    face_cx       = eye_mid_x
    face_cy       = (face_top_y + chin_y) / 2
    rx            = (face_right_x - face_left_x) / 2
    ry            = (chin_y - face_top_y) / 2
    for i in range(36):
        th = (i / 36) * 2 * np.pi - np.pi / 2
        pts_uv.append((face_cx + rx * np.sin(th),
                       face_cy - ry * np.cos(th)))

    # 6) Cheek mesh (jittered grid between eyes and mouth, on each side)
    for side in (-1, 1):
        for r_row in range(5):
            for r_col in range(5):
                u = eye_mid_x + side * (0.07 + r_col * 0.022)
                v = eye_y + 0.06 + r_row * 0.030
                pts_uv.append((u, v))

    # 7) Forehead (3-row grid between eyebrows and hairline)
    for r_row in range(3):
        for r_col in range(9):
            u = face_left_x + 0.05 + (r_col / 8) * (face_right_x - face_left_x - 0.10)
            v = face_top_y - 0.02 + r_row * 0.030
            pts_uv.append((u, v))

    # 8) Chin (3-row grid below mouth)
    for r_row in range(3):
        for r_col in range(7):
            u = mouth_x - 0.10 + (r_col / 6) * 0.20
            v = mouth_y + 0.05 + r_row * 0.026
            pts_uv.append((u, v))

    grp = VGroup()
    for u, v in pts_uv:
        pos = uv_to_manim((u, v), hero_img)
        d = Dot(point=pos, radius=radius)
        d.set_fill(color, opacity).set_stroke(width=0)
        grp.add(d)
    return grp


def _dense_face_mesh(hero_img, n_oval=40, color=TONE_CYAN, radius=0.020,
                     opacity=0.85):
    """Generate ~200 small dots in a face-mesh pattern over hero_img.
    Mimics MediaPipe Face Mesh dense overlay (468 in reality — we use ~200 visual).
    """
    cx, cy, _ = hero_img.get_center()
    w = hero_img.get_width()
    h = hero_img.get_height()

    pts = []

    # Face oval (40 dots around contour, slightly inset)
    for i in range(n_oval):
        theta = (i / n_oval) * 2 * np.pi - np.pi / 2  # start top
        # Egg-shape: narrower at top, rounder at bottom
        rx = 0.22 * w * (1 - 0.05 * np.cos(theta))
        ry = 0.36 * h * (1 + 0.10 * np.sin(theta - np.pi/2))
        x = cx + rx * np.sin(theta)
        y = cy + ry * np.cos(theta) - 0.02 * h
        pts.append((x, y))

    # Internal mesh: fan rows
    # Forehead arc (3 rows)
    for row in range(3):
        v = 0.18 + row * 0.04
        for i in range(7):
            u = 0.30 + i * 0.067
            pts.append((cx + (u - 0.5) * w * 0.78, cy + (0.5 - v) * h * 0.95))

    # Eye regions (left + right) — denser cluster
    for side_u in (0.32, 0.68):
        for ring in range(3):
            r = 0.022 + ring * 0.020
            n_r = 8 + ring * 4
            for k in range(n_r):
                th = (k / n_r) * 2 * np.pi
                u = side_u + r * np.cos(th)
                v = 0.34 + r * 0.55 * np.sin(th)
                pts.append((cx + (u - 0.5) * w * 0.78,
                            cy + (0.5 - v) * h * 0.95))

    # Nose bridge + tip
    for i in range(6):
        v = 0.36 + i * 0.030
        pts.append((cx, cy + (0.5 - v) * h * 0.95))
    for du in (-0.04, -0.02, 0.0, 0.02, 0.04):
        pts.append((cx + du * w * 0.78,
                    cy + (0.5 - 0.50) * h * 0.95))

    # Cheek mesh — two grids of dots
    for side in (-1, 1):
        for r in range(4):
            for c in range(4):
                u = 0.5 + side * (0.10 + c * 0.045)
                v = 0.38 + r * 0.04
                pts.append((cx + (u - 0.5) * w * 0.78,
                            cy + (0.5 - v) * h * 0.95))

    # Mouth area (2 ellipses)
    for ring in range(2):
        rx = 0.055 + ring * 0.025
        ry = 0.018 + ring * 0.008
        n_r = 14 + ring * 4
        for k in range(n_r):
            th = (k / n_r) * 2 * np.pi
            u = 0.5 + rx * np.cos(th)
            v = 0.605 + ry * np.sin(th)
            pts.append((cx + (u - 0.5) * w * 0.78,
                        cy + (0.5 - v) * h * 0.95))

    # Chin
    for i in range(5):
        u = 0.42 + i * 0.04
        pts.append((cx + (u - 0.5) * w * 0.78,
                    cy + (0.5 - 0.74) * h * 0.95))

    grp = VGroup()
    for (px, py) in pts:
        d = Dot(point=np.array([px, py, 0]), radius=radius)
        d.set_fill(color, opacity).set_stroke(width=0)
        grp.add(d)
    return grp


def _profile_landmark_uvs():
    """Return (u, v) anchors for key landmarks on profile face,
    pre-compressed for image's transparent padding."""
    raw_uvs = [
        # Brow
        (0.76, 0.30), (0.85, 0.275), (0.93, 0.30),
        # Eye
        (0.84, 0.36),
        # Nose bridge / tip
        (0.92, 0.43), (0.96, 0.48), (0.94, 0.52),
        # Lips
        (0.90, 0.60), (0.88, 0.66),
        # Chin
        (0.81, 0.74),
        # Jaw
        (0.68, 0.78), (0.50, 0.76),
        # Ear / temple
        (0.43, 0.46), (0.43, 0.32),
    ]
    # Compress toward 0.5 by factor 0.62 — tighter than before so high-u dots
    # land on the visible face silhouette, not in the alpha-padded right side.
    return [(0.5 + (u - 0.5) * 0.62, v) for (u, v) in raw_uvs]


def _heatmap_blob(center, color=TONE_CYAN, max_radius=0.34, n_rings=5):
    """Translucent gaussian-like blob = stacked concentric circles
    with decreasing opacity from center outward. Approximates FAN heatmap."""
    grp = VGroup()
    for i in range(n_rings):
        r = max_radius * (1 - i / n_rings)
        op = 0.10 + i * 0.10   # outer rings dimmer, inner brighter
        c = Circle(radius=r)
        c.set_fill(color, op).set_stroke(width=0)
        c.move_to(center)
        grp.add(c)
    return grp


def _profile_landmarks(hero_img, color=TONE_AMBER, radius=0.040):
    """Final landmark dots on profile face (post-argmax)."""
    cx, cy, _ = hero_img.get_center()
    w = hero_img.get_width()
    h = hero_img.get_height()
    grp = VGroup()
    for u, v in _profile_landmark_uvs():
        x = cx + (u - 0.5) * w
        y = cy + (0.5 - v) * h
        d = Dot(point=np.array([x, y, 0]), radius=radius)
        d.set_fill(color, 0.95).set_stroke(width=0)
        grp.add(d)
    return grp


def _profile_heatmaps(hero_img, color=TONE_CYAN):
    """Heatmap blobs at each landmark position — pre-argmax FAN output."""
    cx, cy, _ = hero_img.get_center()
    w = hero_img.get_width()
    h = hero_img.get_height()
    grp = VGroup()
    for u, v in _profile_landmark_uvs():
        x = cx + (u - 0.5) * w
        y = cy + (0.5 - v) * h
        blob = _heatmap_blob(np.array([x, y, 0]), color=color,
                              max_radius=0.22, n_rings=4)
        grp.add(blob)
    return grp


def _cnn_hourglass(x=-2.2, y=0.0):
    """Mini CNN hourglass diagram: input → conv stack → heatmap stack."""
    grp = VGroup()
    # Input thumbnail (small square)
    inp = Square(side_length=0.55).set_stroke(TONE_FG, 1.5).set_fill(TONE_FG, 0.05)
    inp.move_to(np.array([x - 1.5, y, 0]))
    inp_lbl = m_text("img", scale=0.18, color=TONE_MUTED).next_to(inp, DOWN, buff=0.10)

    # Hourglass: 4 layers descending, 4 layers ascending
    hg = VGroup()
    bar_color = TONE_CYAN
    layer_widths = [0.45, 0.32, 0.20, 0.32, 0.45]
    layer_xs = [x - 0.85, x - 0.42, x, x + 0.42, x + 0.85]
    for w_layer, xl in zip(layer_widths, layer_xs):
        r = Rectangle(width=0.20, height=w_layer)
        r.set_stroke(bar_color, 1.5).set_fill(bar_color, 0.18)
        r.move_to(np.array([xl, y, 0]))
        hg.add(r)
    hg_lbl = m_text("hourglass CNN", scale=0.18, color=TONE_MUTED)
    hg_lbl.next_to(hg, DOWN, buff=0.18)

    # Connector: input → hg
    conn1 = Arrow(inp.get_right(), hg.get_left(), buff=0.05,
                   stroke_width=2.0, max_tip_length_to_length_ratio=0.30)
    conn1.set_color(TONE_MUTED).set_opacity(0.7)

    # Output: heatmap stack (3 overlapping translucent rects)
    stack_x = x + 1.65
    heatmap_stack = VGroup()
    for i, off in enumerate([(-0.05, 0.05), (0.0, 0.0), (0.05, -0.05)]):
        r = Rectangle(width=0.50, height=0.50)
        r.set_stroke(TONE_AMBER, 1.2).set_fill(TONE_AMBER, 0.12)
        r.move_to(np.array([stack_x + off[0], y + off[1], 0]))
        heatmap_stack.add(r)
    hm_lbl = m_text("heatmaps", scale=0.18, color=TONE_AMBER)
    hm_lbl.next_to(heatmap_stack, DOWN, buff=0.20)

    # Connector: hg → heatmaps
    conn2 = Arrow(hg.get_right(), heatmap_stack.get_left() + np.array([-0.04, 0, 0]),
                   buff=0.05, stroke_width=2.0,
                   max_tip_length_to_length_ratio=0.30)
    conn2.set_color(TONE_MUTED).set_opacity(0.7)

    grp.add(inp, inp_lbl, conn1, hg, hg_lbl, conn2, heatmap_stack, hm_lbl)
    return grp, heatmap_stack


# ============================================================
# Main scene
# ============================================================
class Section01_Shot12_ModernBridge(MuseumScene):
    def construct(self):
        self.add_museum_bg(accent="amber")
        ribbon = ChapterRibbon(section="bridge · beyond ASM")
        self.add(ribbon)

        # ============================================================
        # Opener (~6s)
        # ============================================================
        opener_top = m_text("Chapter 12 was 2011.",
                            scale=0.66, color=TONE_MUTED)
        opener_bot = m_text("Here's the next 15 years.",
                            scale=0.66, color=TONE_AMBER)
        opener = VGroup(opener_top, opener_bot).arrange(DOWN, buff=0.20)
        opener.move_to(ORIGIN)
        self.play(FadeIn(opener_top, shift=0.10 * DOWN), run_time=0.7)
        self.wait(0.59)
        self.play(FadeIn(opener_bot, shift=0.10 * DOWN), run_time=0.7)
        self.wait(5.08)
        self.play(FadeOut(opener), run_time=0.5)

        # ============================================================
        # Beat 1 — 2011 ASM (~22s)
        # ============================================================
        era1 = _era_block("2011", "ASM / AAM", "shape model + profile search",
                          accent=TONE_AMBER)
        hero1 = _make_hero(HERO_WITH_LANDMARKS_BAKED, height=4.6)
        cap1 = _caption("This was the state of the art when Ch.12 was written.",
                        color=TONE_MUTED)

        self.play(FadeIn(era1, shift=0.10 * RIGHT), FadeIn(hero1), run_time=0.8)
        self.play(FadeIn(cap1, shift=0.10 * UP), run_time=0.5)
        self.wait(8.3)

        # Transition: dim hero, era1 slides up, prepare for next
        self.play(
            FadeOut(era1),
            FadeOut(cap1),
            hero1.animate.set_opacity(0.25),
            run_time=0.6,
        )

        # ============================================================
        # Beat 2 — 2013-14 SDM (~22s)
        # ============================================================
        era2 = _era_block("2012-13", "ESR / SDM", "cascade regression",
                          accent="#ffd17a")
        cap2 = _caption("Cao 2012 → Xiong 2013: regression cascades — points jump to target.",
                        color=TONE_MUTED)
        ref2 = _ref_inset(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "shot11","refs","sdm.png"),
            "Xiong & De la Torre · CVPR 2013 — SDM results on LFPW",
            center=np.array([-3.2, -0.50, 0]),
            width=3.6,
            accent=TONE_AMBER,
        )

        self.play(FadeIn(era2, shift=0.10 * RIGHT), run_time=0.6)
        self.play(FadeIn(cap2, shift=0.10 * UP),
                  FadeIn(ref2),
                  hero1.animate.set_opacity(1.0), run_time=0.6)

        # Cascade arrows: draw 3 short curved arrows pointing inward from
        # ghost positions to canonical landmark positions. Sample 4 landmark
        # UVs we know exist in HERO_WITH_LANDMARKS_BAKED.
        cascade_arrows = VGroup()
        # 6 anchor landmarks — more coverage. Each shows a 3-step cascade
        # (large ghost → smaller ghost → final) so the "jumping" reads clearly.
        anchor_uvs = [
            (0.40, 0.30),  # left eye
            (0.60, 0.30),  # right eye
            (0.50, 0.45),  # nose tip
            (0.50, 0.60),  # mouth top
            (0.36, 0.72),  # left jaw
            (0.64, 0.72),  # right jaw
        ]
        for u, v in anchor_uvs:
            target = uv_to_manim((u, v), hero1)
            # 3-step cascade: each step closer to target, brighter + bigger
            steps = [
                (0.85, 0.085, 0.45),  # step 0: far ghost, big dot, low opacity
                (0.45, 0.065, 0.70),  # step 1: mid ghost
                (0.18, 0.050, 0.95),  # step 2: near ghost
            ]
            prev_pt = None
            for step, (off_scale, dot_r, op) in enumerate(steps):
                off = np.array([np.cos(u * 13 + step * 1.7) * off_scale * 0.45,
                                np.sin(v * 17 + step * 2.1) * off_scale * 0.45,
                                0])
                pt = target + off
                ghost = Dot(point=pt, radius=dot_r)
                ghost.set_fill(TONE_CYAN, op).set_stroke(width=0)
                cascade_arrows.add(ghost)
                # Connect step-to-step with a small arrow
                if prev_pt is not None:
                    seg = Arrow(prev_pt, pt, buff=0.05,
                                 stroke_width=2.2,
                                 max_tip_length_to_length_ratio=0.35)
                    seg.set_color(TONE_CYAN).set_opacity(0.55 + step * 0.15)
                    cascade_arrows.add(seg)
                prev_pt = pt
            # Final arrow last ghost → target landmark
            final_arrow = Arrow(prev_pt, target, buff=0.04,
                                 stroke_width=3.0,
                                 max_tip_length_to_length_ratio=0.40)
            final_arrow.set_color(TONE_AMBER).set_opacity(1.0)
            cascade_arrows.add(final_arrow)

        self.play(LaggedStartMap(FadeIn, cascade_arrows, lag_ratio=0.04),
                  run_time=1.2)
        self.wait(14.4)

        # Cleanup beat 2
        self.play(
            FadeOut(era2),
            FadeOut(cap2),
            FadeOut(ref2),
            FadeOut(cascade_arrows),
            FadeOut(hero1),
            run_time=0.6,
        )

        # ============================================================
        # Beat 3 — 2017 FAN (CNN → heatmaps → argmax → BAKED landmarks)
        # Uses frontal hero (HERO_FRONTAL → reveals HERO_WITH_LANDMARKS_BAKED)
        # so landmark positions come from Blender bake, not synthetic UV.
        # ============================================================
        era3 = _era_block("2017", "FAN", "heatmap CNN, pose-robust",
                          x=-4.5, y_top=2.6, accent="#ffd17a")

        # Frontal face (no landmarks visible yet)
        hero3 = ImageMobject(HERO_FRONTAL)
        hero3.set_height(3.8)
        hero3.move_to(np.array([3.5, 0.20, 0]))

        # The same face WITH baked landmarks (revealed after argmax)
        hero3_with_lms = ImageMobject(HERO_WITH_LANDMARKS_BAKED)
        hero3_with_lms.set_height(3.8)
        hero3_with_lms.move_to(np.array([3.5, 0.20, 0]))
        hero3_with_lms.set_opacity(0)

        # CNN hourglass diagram (center-left)
        cnn_diagram, heatmap_stack = _cnn_hourglass(x=-2.5, y=0.20)

        # Heatmap blobs anchored at REAL face-feature UVs (eye L, eye R, nose, mouth)
        # — plus 4 more interpolated for forehead, chin, cheeks.
        heatmap_anchors = [
            FACE_EYE_L_UV,
            FACE_EYE_R_UV,
            FACE_NOSE_UV,
            FACE_MOUTH_UV,
            # Forehead (above eyes)
            (0.50, 0.18),
            # Cheeks (well inside face silhouette)
            (0.33, 0.42), (0.67, 0.42),
            # Chin (below mouth)
            (0.50, 0.76),
            # Jaw corners — pulled in to land on face, not floating in neck
            (0.36, 0.62), (0.64, 0.62),
        ]
        heatmaps = VGroup()
        for u, v in heatmap_anchors:
            pos = uv_to_manim((u, v), hero3)
            heatmaps.add(_heatmap_blob(pos, color=TONE_CYAN,
                                       max_radius=0.24, n_rings=5))

        bridge_arrow = Arrow(
            heatmap_stack.get_right() + np.array([0.10, 0, 0]),
            hero3.get_left() + np.array([-0.10, 0, 0]),
            buff=0.0, stroke_width=2.5,
            max_tip_length_to_length_ratio=0.25,
        ).set_color(TONE_MUTED).set_opacity(0.65)

        cap3 = _caption("Heatmap regression — every pixel votes for each landmark.",
                        color=TONE_MUTED)

        ref3 = _ref_inset(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "shot11","refs","fan.png"),
            "Bulat & Tzimiropoulos · ICCV 2017 — FAN 2D landmarks",
            center=np.array([-2.7, -1.45, 0]),
            width=3.6,
            accent=TONE_AMBER,
        )

        # 1) Era + face appear
        self.play(FadeIn(era3, shift=0.10 * RIGHT),
                  FadeIn(hero3), run_time=0.7)
        self.add(hero3_with_lms)  # behind layer, ready to reveal
        # 2) CNN pipeline reveals
        self.play(LaggedStartMap(FadeIn, cnn_diagram, lag_ratio=0.06),
                  run_time=1.4)
        # 3) Bridge arrow + heatmap blobs bloom + ref inset
        self.play(GrowArrow(bridge_arrow),
                  LaggedStartMap(FadeIn, heatmaps, lag_ratio=0.06),
                  FadeIn(cap3, shift=0.10 * UP),
                  FadeIn(ref3),
                  run_time=1.5)
        self.wait(5.9)
        # 4) argmax label, fade heatmaps + clean hero out, reveal baked-LM hero
        argmax_lbl = m_text("argmax", scale=0.24, color=TONE_AMBER)
        argmax_lbl.move_to(bridge_arrow.get_center() + np.array([0, 0.22, 0]))
        self.play(FadeIn(argmax_lbl, shift=0.05 * DOWN), run_time=0.4)
        self.play(
            FadeOut(heatmaps),
            hero3.animate.set_opacity(0),
            hero3_with_lms.animate.set_opacity(1.0),
            run_time=1.2,
        )
        self.wait(7.0)

        # Cleanup beat 3
        self.play(
            FadeOut(era3),
            FadeOut(cap3),
            FadeOut(ref3),
            FadeOut(cnn_diagram),
            FadeOut(bridge_arrow),
            FadeOut(argmax_lbl),
            FadeOut(hero3),
            FadeOut(hero3_with_lms),
            run_time=0.6,
        )

        # ============================================================
        # Beat 4 — 2020 MediaPipe (densification: 68 baked LMs → ~250 mesh dots)
        # Uses HERO_WITH_LANDMARKS_BAKED (real 68 LMs) as starting state,
        # then Manim-overlays dense mesh dots anchored to FACE_*_UV constants.
        # ============================================================
        era4 = _era_block("2020", "MediaPipe", "468 points, real-time on phone",
                          accent="#ffd17a")

        # Show baked-LM hero first (the same 68-LM render used in beat 1)
        hero4 = _make_hero(HERO_WITH_LANDMARKS_BAKED, height=4.6)

        # "68" → "468" counter label — placed top-right above hero (won't clash
        # with bottom-left ref inset).
        count_label = m_text("68", scale=0.90, color=TONE_AMBER)
        count_label.move_to(np.array([-3.0, 0.3, 0]))
        count_sub = m_text("landmarks", scale=0.26, color=TONE_MUTED)
        count_sub.next_to(count_label, DOWN, buff=0.12)

        dense = _dense_mesh_from_anchors(hero4, color=TONE_CYAN, radius=0.016,
                                          opacity=0.80)

        cap4 = _caption("Densification — 68 sparse → 468 mesh, real-time on phone.",
                        color=TONE_MUTED)

        ref4 = _ref_inset(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "shot11","refs","mediapipe.png"),
            "Google MediaPipe Face Mesh · 468 points + tessellation",
            center=np.array([-3.0, -1.30, 0]),
            width=2.8,
            accent=TONE_AMBER,
        )

        # 1) Era + face (with 68 baked LMs) + counter + ref inset
        self.play(FadeIn(era4, shift=0.10 * RIGHT),
                  FadeIn(hero4), run_time=0.7)
        self.play(FadeIn(count_label), FadeIn(count_sub),
                  FadeIn(cap4, shift=0.10 * UP),
                  FadeIn(ref4),
                  run_time=0.7)
        self.wait(4.0)
        # 2) Dense mesh fades in — slow lag for "blooming" effect.
        # Morph counter from "68" to "468" during the bloom.
        count_label_new = m_text("468", scale=1.10, color=TONE_AMBER)
        count_label_new.move_to(count_label.get_center())
        self.play(
            LaggedStartMap(FadeIn, dense, lag_ratio=0.004),
            Transform(count_label, count_label_new),
            run_time=2.2,
        )
        self.wait(13.0)

        # Cleanup beat 4
        self.play(
            FadeOut(era4),
            FadeOut(cap4),
            FadeOut(ref4),
            FadeOut(count_label),
            FadeOut(count_sub),
            FadeOut(dense),
            FadeOut(hero4),
            run_time=0.6,
        )

        # ============================================================
        # Beat 5 — 2022+ 3DMM / FLAME (~30s)
        # ============================================================
        era5 = _era_block("2022+", "FLAME / EMOCA", "3D morphable, end-to-end",
                          accent="#ffd17a")

        # Clean head sway — no eye glow, no landmarks. Uses HERO_SWAY_NORMAL_DIR.
        sway = AnimatedHead(HERO_SWAY_NORMAL_DIR,
                            n_frames=HERO_SWAY_FRAMES, fps=30, height=4.4)
        sway.move_to(np.array([3.4, 0.20, 0]))
        sway.attach_updater(self)
        self.add(sway)

        # EMOCA reference — bigger now, the actual demo of disentanglement.
        # Positioned center-left, with explanatory row labels.
        ref5 = _ref_inset(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "shot11","refs","emoca.png"),
            "Daněček et al · CVPR 2022 — same identity, different expressions.",
            center=np.array([-2.6, -1.2, 0]),
            width=4.6,
            accent=TONE_AMBER,
        )
        # Annotate the 3 rows of EMOCA image (input photo / coarse / detailed)
        # by adding small labels on its left side. EMOCA image has 3 rows;
        # ref5 = Group(img, frame, cit). img is first child.
        emoca_img = ref5[0]
        img_left  = emoca_img.get_left()[0]
        img_top   = emoca_img.get_top()[1]
        img_h     = emoca_img.get_height()
        row_h     = img_h / 3
        row_labels = VGroup()
        for i, txt in enumerate(["input", "coarse", "+ details"]):
            y = img_top - (i + 0.5) * row_h
            t = m_text(txt, scale=0.22, color=TONE_AMBER)
            t.set_opacity(0.85)
            t.move_to(np.array([img_left - 0.55, y, 0]))
            row_labels.add(t)

        cap5 = _caption("One photo → 3D mesh. End-to-end, expression-aware.",
                        color=TONE_MUTED)

        self.play(FadeIn(era5, shift=0.10 * RIGHT), run_time=0.6)
        self.play(
            FadeIn(ref5),
            LaggedStartMap(lambda m: FadeIn(m, shift=0.10 * RIGHT),
                           row_labels, lag_ratio=0.15),
            FadeIn(cap5, shift=0.10 * UP),
            run_time=1.5,
        )
        self.wait(15.0)

        # Cleanup beat 5
        sway.clear_updaters()
        self.play(
            FadeOut(era5),
            FadeOut(cap5),
            FadeOut(ref5),
            FadeOut(row_labels),
            FadeOut(sway),
            run_time=0.6,
        )

        # ============================================================
        # Closing — Trade-off triangle (~14s)
        # 3 corners (accuracy / interpretability / real-time) + 4 method dots
        # plotted by where each method sits in the trade-off space, connected
        # by a dashed historical trajectory line.
        # ============================================================
        head = m_text("The trade-off space", scale=0.52, color=TONE_FG)
        head.move_to(np.array([0, 3.2, 0]))

        # Triangle geometry — equilateral, ~3.6 manim units per side, centered
        # at (0, 0.2). Vertices computed from triangle math.
        tri_cx, tri_cy = 0.0, -0.10
        tri_size = 3.20  # half-base; vertical extent ~ size * sqrt(3) ≈ 2.77
        v_top   = np.array([tri_cx, tri_cy + tri_size * np.sqrt(3)/2 * 0.92, 0])
        v_left  = np.array([tri_cx - tri_size, tri_cy - tri_size * np.sqrt(3)/4 * 0.92, 0])
        v_right = np.array([tri_cx + tri_size, tri_cy - tri_size * np.sqrt(3)/4 * 0.92, 0])

        # Stroke-only triangle (3 edges as VMobject). Polygon fills by default,
        # so build from 3 Lines to guarantee transparent interior.
        triangle = VGroup(
            Line(v_top, v_left),
            Line(v_left, v_right),
            Line(v_right, v_top),
        )
        for seg in triangle:
            seg.set_stroke(TONE_MUTED, 1.8).set_opacity(0.75)

        # Corner labels (positioned just outside each vertex)
        corner_top = m_text("accuracy", scale=0.40, color=TONE_AMBER)
        corner_top.move_to(v_top + np.array([0, 0.30, 0]))
        corner_left = m_text("interpretability", scale=0.36, color=TONE_CYAN)
        corner_left.move_to(v_left + np.array([-0.50, -0.25, 0]))
        corner_right = m_text("real-time", scale=0.40, color=TONE_RED)
        corner_right.move_to(v_right + np.array([0.50, -0.25, 0]))

        # 4 method dots — positioned by trade-off profile.
        # Each (label, year, barycentric weights for [top, left, right], color)
        # Weights sum to 1; favoring a corner pulls dot toward that vertex.
        methods = [
            # ASM 2011: deep into interpretability corner
            ("ASM",        "2011", (0.15, 0.75, 0.10), TONE_CYAN),
            # FAN 2017: high accuracy, modest real-time potential
            ("FAN",        "2017", (0.55, 0.20, 0.25), TONE_AMBER),
            # MediaPipe 2020: real-time champion, decent accuracy
            ("MediaPipe",  "2020", (0.25, 0.10, 0.65), TONE_RED),
            # EMOCA 2022+: accuracy at the cost of everything else
            ("EMOCA",      "2022+",(0.82, 0.08, 0.10), "#ffd17a"),
        ]
        method_dots = []
        method_labels = []
        method_positions = []
        for name, yr, (wt, wl, wr), col in methods:
            pos = wt * v_top + wl * v_left + wr * v_right
            method_positions.append(pos)
            dot = Dot(point=pos, radius=0.090)
            dot.set_fill(col, 1.0).set_stroke(TONE_FG, 1.0)
            method_dots.append(dot)
            # Label: stacked name + year (bigger for 480p readability)
            lbl = VGroup(
                m_text(name, scale=0.34, color=col),
                m_text(yr,   scale=0.26, color=TONE_MUTED),
            ).arrange(DOWN, buff=0.05)
            # Offset label outward from triangle center to avoid covering dot
            from_center = pos - np.array([tri_cx, tri_cy, 0])
            from_center_norm = from_center / (np.linalg.norm(from_center) + 1e-6)
            lbl_pos = pos + from_center_norm * 0.55
            lbl.move_to(lbl_pos)
            method_labels.append(lbl)

        # Dashed trajectory line connecting dots in chronological order
        trajectory = VGroup()
        for i in range(len(method_positions) - 1):
            seg = DashedLine(method_positions[i], method_positions[i+1],
                              dash_length=0.10, positive_space_ratio=0.55)
            seg.set_stroke("#ffd17a", 1.6).set_opacity(0.65)
            trajectory.add(seg)

        tail = m_text("Three pulls — no method holds all three yet.",
                       scale=0.40, color=TONE_AMBER)
        tail.move_to(np.array([0, -3.30, 0]))

        # Animation sequence
        self.play(FadeIn(head, shift=0.10 * DOWN), run_time=0.5)
        self.play(ShowCreation(triangle), run_time=0.9)
        self.play(
            FadeIn(corner_top, shift=0.10 * DOWN),
            FadeIn(corner_left, shift=0.10 * RIGHT),
            FadeIn(corner_right, shift=0.10 * LEFT),
            run_time=0.8,
        )
        self.wait(0.59)
        # Plot methods chronologically with brief pause between each
        for dot, lbl in zip(method_dots, method_labels):
            self.play(FadeIn(dot, scale=0.5),
                      FadeIn(lbl, shift=0.05 * UP),
                      run_time=0.5)
            self.wait(0.44)
        # Draw trajectory connecting them
        self.play(LaggedStartMap(ShowCreation, trajectory, lag_ratio=0.25),
                  run_time=1.2)
        self.wait(0.59)
        self.play(FadeIn(tail, shift=0.10 * UP), run_time=0.6)
        self.wait(12.2)

        # Final fade
        triangle_grp = VGroup(triangle, corner_top, corner_left, corner_right,
                              *method_dots, *method_labels, trajectory)
        self.play(FadeOut(head), FadeOut(triangle_grp), FadeOut(tail),
                  run_time=0.7)
