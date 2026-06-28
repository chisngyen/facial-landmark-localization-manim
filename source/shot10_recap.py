"""
Shot 07.5 — Recap as a visual pipeline.

Three nodes (Procrustes → PCA → Iterative fit) connected by arrows, each with a
mini-animation of the algorithm step rather than only an equation. Single amber
accent (different from shot03's tri-color failure modes).
"""
from manimlib import *

import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    TONE_CYAN, TONE_AMBER, TONE_RED, TONE_FG, TONE_MUTED,
    MuseumScene, m_text,
)


def _face_shape(scale=1.0, offset=(0.0, 0.0), rot=0.0):
    """Return a list of np.array positions forming a stylised landmark cloud
    (8 points: 2 eyes, nose, 3 mouth, 2 chin)."""
    raw = [
        (-0.22, +0.18),  # eye_L
        (+0.22, +0.18),  # eye_R
        ( 0.00, +0.00),  # nose
        (-0.16, -0.20),  # mouth_L
        ( 0.00, -0.24),  # mouth_C
        (+0.16, -0.20),  # mouth_R
        (-0.22, -0.34),  # chin_L
        (+0.22, -0.34),  # chin_R
    ]
    cos_a, sin_a = np.cos(rot), np.sin(rot)
    out = []
    for x, y in raw:
        xr = x * cos_a - y * sin_a
        yr = x * sin_a + y * cos_a
        out.append(np.array([xr * scale + offset[0],
                             yr * scale + offset[1], 0.0]))
    return out


def _make_cloud(pts, color, radius=0.045, opacity=0.85):
    grp = VGroup()
    for p in pts:
        d = Dot(radius=radius, color=color, fill_opacity=opacity)
        d.move_to(p)
        grp.add(d)
    return grp


class Section01_Shot10_Recap(MuseumScene):
    """Three-node pipeline: Procrustes → PCA → Iterative fit."""

    def construct(self):
        self.add_museum_bg(accent="amber")

        # ---- Heading ----
        head = m_text("how it actually works", scale=0.58, color=TONE_FG)
        head.to_edge(UP, buff=0.55)
        sub = m_text("the ASM pipeline, end to end", scale=0.38, color=TONE_MUTED)
        sub.next_to(head, DOWN, buff=0.12)
        self.play(FadeIn(head, shift=0.08 * DOWN), FadeIn(sub), run_time=0.652)
        self.wait(0.04)

        # Layout: 3 nodes side by side with arrows between
        node_w, node_h = 3.40, 2.30
        node_cx = [-4.65, 0.00, +4.65]
        node_cy = 0.40   # vertical centre for visuals
        visual_box_h = 1.60  # within node, visual occupies upper portion

        # ---- Node frames removed per user request — no box borders.
        # Spatial structure is still defined by node_cx + node_cy used by the
        # cloud + face anims below, just without the visible rectangles.
        frames = []  # kept as empty list so downstream `*frames` references stay valid

        # Connector arrows
        arrows = []
        for i in range(2):
            x0 = node_cx[i] + node_w / 2 + 0.06
            x1 = node_cx[i+1] - node_w / 2 - 0.06
            a = Arrow(np.array([x0, node_cy - 0.05, 0]),
                      np.array([x1, node_cy - 0.05, 0]),
                      stroke_color=TONE_AMBER, stroke_width=4.0, buff=0.05)
            arrows.append(a)

        # No frames to draw — replaced ShowCreation pass with a small pause so
        # downstream beat timing stays roughly the same as the original.
        self.wait(0.20)

        # ---- Captions below each node (title + equation + 1-line caption) ----
        cap_data = [
            ("Procrustes",
             "min  Σ_i  || T(x_i) − x̄ ||^2",
             "align every training shape"),
            ("PCA  basis",
             "x = x̄ + P · b",
             "mean + a few coefficients"),
            ("Iterative fit",
             "b ← P^T (x_obs − x̄)",
             "snap to a new face in ~15 steps"),
        ]
        caps = []
        for cx, (title, eq, c) in zip(node_cx, cap_data):
            t_t = m_text(title, scale=0.50, color=TONE_AMBER)
            t_t.move_to(np.array([cx, node_cy - node_h / 2 - 0.28, 0]))
            eq_t = m_text(eq, scale=0.36, color=TONE_FG)
            eq_t.move_to(np.array([cx, node_cy - node_h / 2 - 0.72, 0]))
            cap_t = m_text(c, scale=0.30, color=TONE_MUTED)
            cap_t.move_to(np.array([cx, node_cy - node_h / 2 - 1.10, 0]))
            caps.append(VGroup(t_t, eq_t, cap_t))

        # =========================================================
        # NODE 1 — Procrustes: 5 misaligned clouds → 1 aligned cloud
        # =========================================================
        n1_cx, n1_cy = node_cx[0], node_cy + 0.10
        rng = np.random.default_rng(42)

        misaligned = VGroup()
        per_cloud_dots = []
        for k in range(5):
            ox = (rng.random() - 0.5) * 0.55
            oy = (rng.random() - 0.5) * 0.45
            rot = (rng.random() - 0.5) * 0.6
            scl = 0.85 + (rng.random() - 0.5) * 0.30
            pts = _face_shape(scale=1.40 * scl,
                              offset=(n1_cx + ox, n1_cy + oy), rot=rot)
            cloud = _make_cloud(pts, color=TONE_MUTED, radius=0.044, opacity=0.55)
            per_cloud_dots.append((cloud, pts))
            misaligned.add(cloud)

        # Reveal misaligned clouds
        self.play(LaggedStartMap(FadeIn, misaligned, lag_ratio=0.10),
                  FadeIn(caps[0]), run_time=0.760)
        self.wait(0.03)

        # Converge to mean — animate each dot toward the canonical face position
        target_pts = _face_shape(scale=1.40, offset=(n1_cx, n1_cy), rot=0.0)
        merge_anims = []
        for cloud, _ in per_cloud_dots:
            for d, tp in zip(cloud, target_pts):
                merge_anims.append(d.animate.move_to(tp).set_opacity(0.20))
        self.play(*merge_anims, run_time=1.000, rate_func=smooth)

        # One amber "mean" cloud appears on top
        mean_cloud = _make_cloud(target_pts, color=TONE_AMBER, radius=0.068, opacity=0.95)
        self.play(FadeIn(mean_cloud, scale=1.10), run_time=0.500)

        # Cinematic "THIS is the mean" amber burst — 4 particles per mean point
        n1_burst = VGroup()
        n1_burst_anims = []
        rng1 = np.random.default_rng(7)
        for tp in target_pts:
            for k in range(4):
                theta = (k / 4) * TAU + rng1.uniform(-0.2, 0.2)
                dir_v = np.array([np.cos(theta), np.sin(theta), 0])
                p = Dot(radius=0.030)
                p.set_fill(TONE_AMBER, opacity=1.0).set_stroke(width=0)
                p.move_to(tp)
                n1_burst.add(p)
                n1_burst_anims.append(
                    p.animate.move_to(tp + 0.30 * dir_v).set_opacity(0)
                )
        self.add(n1_burst)
        self.play(*n1_burst_anims, run_time=0.42,
                  rate_func=lambda t: 1 - (1 - t) ** 2)
        self.remove(n1_burst)

        self.wait(0.03)

        # Show arrow to next node
        self.play(GrowArrow(arrows[0]), run_time=0.420)

        # =========================================================
        # NODE 2 — PCA: mean cloud + a `b` slider that morphs it
        # =========================================================
        n2_cx, n2_cy = node_cx[1], node_cy + 0.10
        pca_pts = _face_shape(scale=1.40, offset=(n2_cx, n2_cy), rot=0.0)
        pca_cloud = _make_cloud(pca_pts, color=TONE_AMBER, radius=0.068, opacity=0.95)
        self.play(FadeIn(pca_cloud, scale=1.05),
                  FadeIn(caps[1]), run_time=0.540)

        # Tiny b-coefficient bars below the cloud
        bar_baseline_y = n2_cy - 0.90
        bv_colors = [TONE_AMBER, TONE_CYAN, TONE_FG]
        bv_w, bv_gap = 0.12, 0.08
        total_w = 3 * bv_w + 2 * bv_gap
        bv_x0 = n2_cx - total_w / 2
        bv_label = m_text("b", scale=0.34, color=TONE_MUTED)
        bv_label.move_to(np.array([n2_cx - total_w / 2 - 0.20, bar_baseline_y + 0.12, 0]))

        def _make_b_bars(vals):
            g = VGroup()
            for i, (col, v) in enumerate(zip(bv_colors, vals)):
                h = max(abs(v) * 0.30, 0.02)
                bar = Rectangle(width=bv_w, height=h, fill_color=col,
                                fill_opacity=0.85, stroke_width=0)
                x = bv_x0 + bv_w / 2 + i * (bv_w + bv_gap)
                bar.move_to(np.array([x, bar_baseline_y + h / 2, 0]))
                g.add(bar)
            return g

        b_bars = _make_b_bars([0.0, 0.0, 0.0])
        self.play(FadeIn(b_bars), FadeIn(bv_label), run_time=0.380)

        # Animate b changing — cloud subtly stretches/squeezes (mode 1 = width)
        def cloud_at(b1, b2):
            """Return target positions for given (b1, b2)."""
            out = []
            for p in pca_pts:
                dx = (p[0] - n2_cx) * (1.0 + 0.30 * b1)
                dy = (p[1] - n2_cy) * (1.0 + 0.20 * b2)
                out.append(np.array([n2_cx + dx, n2_cy + dy, 0]))
            return out

        for b1, b2 in [(+0.7, 0.0), (-0.5, +0.4), (0.0, 0.0)]:
            new_pts = cloud_at(b1, b2)
            dot_anims = [d.animate.move_to(np.array(p)) for d, p in zip(pca_cloud, new_pts)]
            new_bars = _make_b_bars([b1, b2, 0.0])
            self.play(
                *dot_anims,
                Transform(b_bars, new_bars),
                run_time=0.520, rate_func=smooth,
            )

        self.wait(0.20)
        self.play(GrowArrow(arrows[1]), run_time=0.420)

        # =========================================================
        # NODE 3 — Iterative fit: a target outline + dots snapping in
        # =========================================================
        n3_cx, n3_cy = node_cx[2], node_cy + 0.10
        target_face_pts = _face_shape(scale=1.40, offset=(n3_cx, n3_cy), rot=0.0)

        # Target outline (faded) — show where dots should land
        target_outline = _make_cloud(target_face_pts, color=TONE_MUTED,
                                      radius=0.075, opacity=0.25)
        self.play(FadeIn(target_outline), FadeIn(caps[2]), run_time=0.420)

        # Initial cloud — offset + rotated (mean shape misaligned on test face)
        init_offset = (0.35, 0.20)
        init_rot = 0.18
        init_pts = _face_shape(scale=1.05, offset=(n3_cx + init_offset[0],
                                                    n3_cy + init_offset[1]),
                               rot=init_rot)
        fit_cloud = _make_cloud(init_pts, color=TONE_AMBER, radius=0.068, opacity=0.95)
        self.play(FadeIn(fit_cloud, scale=1.10), run_time=0.380)

        # 8-step smooth convergence with per-step glow pulse — mirrors shot10
        N3_STEPS = 8
        for step_i in range(N3_STEPS):
            t = (step_i + 1) / N3_STEPS
            te = 1 - (1 - t) ** 1.6
            new_pts = [(1 - te) * ip + te * tp
                       for ip, tp in zip(init_pts, target_face_pts)]
            dot_anims = [d.animate.move_to(p) for d, p in zip(fit_cloud, new_pts)]
            self.play(*dot_anims, run_time=0.22, rate_func=smooth)
            # per-step glow pulse — tick feel
            self.play(
                *[d.animate.scale(1.08).set_fill("#ffd17a", opacity=1.0)
                  for d in fit_cloud],
                run_time=0.03,
            )
            self.play(
                *[d.animate.scale(1 / 1.08).set_fill(TONE_AMBER, opacity=0.95)
                  for d in fit_cloud],
                run_time=0.03,
            )

        # Cyan particle burst — 4 per dot, radial outward, signals convergence
        n3_burst = VGroup()
        n3_burst_anims = []
        rng3 = np.random.default_rng(13)
        for d in fit_cloud:
            dot_pos = d.get_center()
            for k in range(4):
                theta = (k / 4) * TAU + rng3.uniform(-0.2, 0.2)
                dir_v = np.array([np.cos(theta), np.sin(theta), 0])
                p = Dot(radius=0.030)
                p.set_fill(TONE_CYAN, opacity=1.0).set_stroke(width=0)
                p.move_to(dot_pos)
                n3_burst.add(p)
                n3_burst_anims.append(
                    p.animate.move_to(dot_pos + 0.28 * dir_v).set_opacity(0)
                )
        self.add(n3_burst)
        self.play(*n3_burst_anims, run_time=0.45,
                  rate_func=lambda t: 1 - (1 - t) ** 2)
        self.remove(n3_burst)

        self.wait(0.04)

        # ---- Forward-looking closing line ----
        forward = m_text(
            "before deep learning did it end-to-end  —  this is how it was done.",
            scale=0.42, color=TONE_AMBER,
        )
        forward.to_edge(DOWN, buff=0.75)
        self.play(FadeIn(forward, shift=0.10 * UP), run_time=0.760)
        self.wait(2.04)

        # Clean fade
        all_mobs = VGroup(
            head, sub, forward,
            *frames, *arrows, *caps,
            misaligned, mean_cloud,
            pca_cloud, b_bars, bv_label,
            target_outline, fit_cloud,
        )
        self.play(FadeOut(all_mobs), run_time=0.700)
