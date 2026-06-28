"""Shot 03.5 v2 — PCA Math walk-through.

Render:
    "D:/Downloads/Tools/Anaconda/Scripts/manimgl.exe" \
        source/shot03_5_PCA_Math.py Section01_Shot05_PCA_Math \
        -w -l --video_dir videos --file_name shot03_5_PCA_Math

Replaces shot03_5_PCA_Math (kept as fallback).
See docs/superpowers/specs/2026-05-25-shot03_5-pca-redesign-design.md.
"""
from manimlib import *
import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from museum_tone import (
    MuseumScene, m_text, FONT,
    TONE_CYAN, TONE_AMBER, TONE_FG, TONE_MUTED,
    ChapterRibbon, typewriter_anim,
)
from pca_anim import (TOY_POINTS_3D, V0_INIT, project_iso,
                      compute_covariance, power_iterate, format_matrix_3x3)


# Palette additions (only used by this scene; not exported to museum_tone).
PCA_RED    = "#ff6060"   # covariance operator / matrix C / outer products
PCA_VIOLET = "#a070ff"   # iterating candidate vector v


def _matrix_heatmap(matrix, cell_size=0.32, gap=0.02, max_abs=None):
    """N×N colored grid — warm = positive, cool = negative, intensity = magnitude."""
    import numpy as np
    M = np.asarray(matrix, dtype=float)
    n = M.shape[0]
    if max_abs is None:
        max_abs = max(abs(M).max(), 1e-6)

    def val_to_color_opacity(v):
        t = float(v) / max_abs
        t = max(-1.0, min(1.0, t))
        if t >= 0:
            col = "#ff8a6b" if t > 0.6 else "#ffc36a"   # soft coral → warm amber
        else:
            col = "#5fc9f8" if t > -0.6 else "#3080d0"
        opacity = 0.12 + 0.72 * abs(t)
        return col, opacity

    cells = []
    grid_w = n * cell_size + (n - 1) * gap
    for i in range(n):
        for j in range(n):
            color, op = val_to_color_opacity(M[i, j])
            cell = Square(side_length=cell_size, fill_color=color,
                          fill_opacity=op, stroke_color="#1a1a22", stroke_width=0.3)
            x = -grid_w / 2 + cell_size / 2 + j * (cell_size + gap)
            y = +grid_w / 2 - cell_size / 2 - i * (cell_size + gap)
            cell.move_to(np.array([x, y, 0]))
            cells.append(cell)
    return VGroup(*cells)


def _make_pseudo_outer(size, seed):
    """Generate a believable rank-1-ish outer product pattern at given size.

    For shot03_5 visuals: a real face-landmark outer product would be a large
    matrix (88×2 = 176 dim) with diagonal dominance and block correlation.
    The toy 3D math is honest, but a 12×12 pattern reads as 'real covariance'
    on screen.
    """
    import numpy as np
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(size)
    v /= np.linalg.norm(v)
    M = np.outer(v, v)
    # Boost diagonal a touch so it always reads
    M += np.eye(size) * 0.10
    return M


def _make_pseudo_covariance(size, seed=0):
    """Symmetric PSD matrix that looks like a real covariance: diagonal-heavy,
    block-correlated, with a sprinkle of cross-feature off-diagonal."""
    import numpy as np
    rng = np.random.default_rng(seed)
    # Sum of a few rank-1 outer products → PSD
    M = np.zeros((size, size))
    for _ in range(6):
        v = rng.standard_normal(size)
        v /= np.linalg.norm(v)
        M += np.outer(v, v) * rng.uniform(0.5, 1.5)
    # Strong diagonal
    M += np.eye(size) * 2.0
    # Block correlation (neighbors): smooth decay
    for i in range(size):
        for j in range(size):
            decay = np.exp(-abs(i - j) / 3.0)
            M[i, j] += decay * 0.5
    return M


class Section01_Shot05_PCA_Math(MuseumScene):
    """Six-phase PCA walk-through. ≈ 32 s total."""

    def construct(self):
        self.add_museum_bg(accent="amber")
        ribbon = ChapterRibbon(section="12.2 · the math")
        self.add(ribbon)

        # ============================================================
        # Phase 0 (0.0 – 3.0 s) — title + 3D scene
        # ============================================================
        title = m_text("How PCA finds the modes", scale=0.55, color=TONE_AMBER)
        title.move_to(np.array([0, 3.4, 0]))
        subtitle = m_text("find the direction of maximum variance",
                          scale=0.32, color=TONE_MUTED)
        subtitle.next_to(title, DOWN, buff=0.12)
        self.play(FadeIn(title, shift=0.10*DOWN), FadeIn(subtitle), run_time=0.8)

        # Minimal 3D scene — just 3 axes (iso-projected), no floor plane.
        # Cleaner, more 3b1b-style. Dots use project_iso so they sit consistently.
        FLOOR_Y = -0.2
        AXIS_EXTENT = 2.5
        def _iso_pt(p3):
            xy = project_iso(np.array(p3, dtype=np.float64))
            return np.array([xy[0], xy[1], 0.0])
        ax_v = Line(_iso_pt([0, FLOOR_Y, 0]), _iso_pt([0, 2.2, 0])).set_stroke(WHITE, 1.5)
        ax_x = Line(_iso_pt([-AXIS_EXTENT, FLOOR_Y, 0]), _iso_pt([AXIS_EXTENT, FLOOR_Y, 0])).set_stroke(WHITE, 1.5)
        ax_z = Line(_iso_pt([0, FLOOR_Y, -AXIS_EXTENT]), _iso_pt([0, FLOOR_Y, AXIS_EXTENT])).set_stroke(WHITE, 1.5)
        self.play(ShowCreation(ax_v), ShowCreation(ax_x), ShowCreation(ax_z), run_time=0.7)
        self.wait(0.2)

        # ============================================================
        # Phase 1 (3.0 – 6.0 s) — 5 data points appear
        # ============================================================
        pts2d = project_iso(TOY_POINTS_3D)
        dots = VGroup(*[
            Dot(point=np.array([pts2d[i, 0], pts2d[i, 1], 0]), radius=0.10)
            .set_fill(TONE_CYAN, 1.0).set_stroke(width=0)
            for i in range(5)
        ])
        self.play(LaggedStartMap(FadeIn, dots, lag_ratio=0.18), run_time=1.2)
        caption = m_text("x_i  ←  5 data points", scale=0.30, color=TONE_CYAN)
        caption.move_to(np.array([0, -3.4, 0]))
        self.play(FadeIn(caption), run_time=0.3)
        self.wait(1.66)

        # ============================================================
        # Phase 2 (6.0 – 10.0 s) — compute mean: data converges, leaves a white dot
        # ============================================================
        mean3d, residuals3d, outers, C, eigvals, eigvecs = compute_covariance(TOY_POINTS_3D)
        mean2d = project_iso(mean3d)
        mean_xyz = np.array([mean2d[0], mean2d[1], 0])

        # Hero entrance: large at center, then shrink to corner
        f_mean_big = m_text("x̄ = (1/N) Σ x_i", scale=0.7, color=TONE_FG).move_to(ORIGIN)
        self.play(typewriter_anim(f_mean_big, char_duration=0.04), FadeOut(caption), run_time=0.7)
        self.wait(0.2)
        # Now build the final small position and transform
        f_mean = m_text("x̄ = (1/N) Σ x_i", scale=0.34, color=TONE_FG)
        f_mean.move_to(np.array([-5.5, 2.2, 0]), aligned_edge=LEFT)
        self.play(Transform(f_mean_big, f_mean), run_time=0.5)
        # Replace reference so subsequent code (which uses f_mean) still works
        f_mean = f_mean_big  # the transformed mobject

        original_positions = [d.get_center().copy() for d in dots]
        self.play(
            *[d.animate.move_to(mean_xyz) for d in dots],
            run_time=1.0,
        )
        mean_dot = Dot(point=mean_xyz, radius=0.12).set_fill(TONE_FG, 1.0).set_stroke(width=0)
        self.add(mean_dot)
        self.wait(1.66)
        self.play(
            *[d.animate.move_to(original_positions[i]) for i, d in enumerate(dots)],
            run_time=0.8,
        )
        caption_mean = m_text("x̄  ←  mean", scale=0.30, color=TONE_FG)
        caption_mean.move_to(np.array([0, -3.4, 0]))
        self.play(FadeIn(caption_mean), run_time=0.3)
        self.wait(0.2)

        # Stash for next bundle.
        self._dots = dots
        self._original_positions = original_positions
        self._mean_dot = mean_dot
        self._mean_xyz = mean_xyz
        self._caption = caption_mean
        self._title = title
        self._subtitle = subtitle
        # plane/grid removed (minimal 3D scene); keep attrs as empty for compat.
        self._plane = VGroup()
        self._grid = VGroup()
        self._axes = VGroup(ax_v, ax_x, ax_z)
        self._f_mean = f_mean
        self._pts2d = pts2d
        self._C = C
        self._eigvals = eigvals
        self._eigvecs = eigvecs
        self._outers = outers
        self._residuals3d = residuals3d

        # ============================================================
        # Phase 3 (10.0 – 13.0 s) — residual arrows from each dot to mean
        # ============================================================
        residual_arrows = VGroup(*[
            Arrow(self._original_positions[i], self._mean_xyz,
                  stroke_color=TONE_MUTED, stroke_width=2.2, buff=0.08)
            for i in range(5)
        ])
        self.play(LaggedStartMap(GrowArrow, residual_arrows, lag_ratio=0.15),
                  run_time=1.5)
        caption_res = m_text("x_i − x̄  ←  residual", scale=0.30, color=TONE_MUTED)
        caption_res.move_to(np.array([0, -3.4, 0]))
        self.play(FadeOut(self._caption), FadeIn(caption_res), run_time=0.3)
        self.wait(1.66)
        self._caption = caption_res
        # ≈ 13.0 s

        # ============================================================
        # Phase 4 (13.0 – 21.0 s) — build C from 5 outer products
        # ============================================================
        f_cov = m_text("C = (1/N) Σ (x_i − x̄)(x_i − x̄)^T", scale=0.32, color=PCA_RED)
        f_cov.next_to(self._f_mean, DOWN, aligned_edge=LEFT, buff=0.20)
        self.play(typewriter_anim(f_cov, char_duration=0.025), run_time=0.7)

        # 5 mini-matrix slots on the right — 12×12 pseudo outer products.
        # For face landmark PCA the real covariance is ~176×176; we suggest
        # the scale with denser heatmaps. (Comment: rank-1 outer of random
        # unit vectors + slight diagonal — visually consistent with truth.)
        slot_x = 5.5
        slot_ys = [+2.7, +1.35, 0.0, -1.35, -2.7]
        OUTER_SIZE = 12
        pseudo_outers = [_make_pseudo_outer(OUTER_SIZE, seed=17 + i) for i in range(5)]
        shared_max = max(abs(o).max() for o in pseudo_outers)
        mini_matrices = []
        for i in range(5):
            grid = _matrix_heatmap(pseudo_outers[i], cell_size=0.085, gap=0.005,
                                   max_abs=shared_max)
            grid.move_to(np.array([slot_x, slot_ys[i], 0]))
            grid.set_opacity(0)
            mini_matrices.append(grid)
            self.add(grid)

        # Loop: highlight each (dot, arrow), spawn its mini-matrix.
        for i in range(5):
            self.play(
                self._dots[i].animate.set_fill(WHITE, 1.0),
                residual_arrows[i].animate.set_stroke(PCA_RED, 3.0),
                mini_matrices[i].animate.set_opacity(1.0),
                run_time=0.35,
            )
            self.play(
                self._dots[i].animate.set_fill(TONE_CYAN, 1.0),
                residual_arrows[i].animate.set_stroke(TONE_MUTED, 2.2),
                run_time=0.15,
            )
        # ≈ 17.5 s

        # Big C heatmap: 12×12 pseudo-covariance — diagonal-dominant, block-correlated.
        big_C = _make_pseudo_covariance(OUTER_SIZE, seed=3)
        C_grid = _matrix_heatmap(big_C, cell_size=0.22, gap=0.012,
                                 max_abs=abs(big_C).max())
        C_label = m_text("C  =", scale=0.50, color=PCA_RED)
        C_label.next_to(C_grid, LEFT, buff=0.30)
        C_group = VGroup(C_label, C_grid)
        C_group.move_to(np.array([4.4, -0.3, 0]))
        C_border = SurroundingRectangle(C_group, color=PCA_RED, buff=0.22,
                                        stroke_width=1.5)
        # Subtle dark panel + thin coral border (was a heavy red fill at 0.55).
        C_border.set_stroke("#ff8a6b", 1.2, opacity=0.5).set_fill("#15121c", 0.5)
        C_cap = m_text("12×12 covariance — pattern that emerges at face-landmark scale",
                       scale=0.20, color=TONE_MUTED)
        C_cap.next_to(C_border, DOWN, buff=0.15)
        self.play(
            *[mm.animate.set_opacity(0) for mm in mini_matrices],
            FadeIn(C_group),
            ShowCreation(C_border),
            FadeIn(C_cap),
            run_time=1.5,
        )
        for mm in mini_matrices:
            self.remove(mm)
        self.wait(2.22)
        # ≈ 21.2 s

        self._residual_arrows = residual_arrows
        self._f_cov = f_cov
        self._C_group = C_group
        self._C_border = C_border
        self._C_cap = C_cap

        # ============================================================
        # Phase 5 (21.2 – 28.0 s) — power iteration: v rotates, then turns amber
        # ============================================================
        iter_caption = m_text("iterate:  v ← C·v / |C·v|", scale=0.34, color=PCA_VIOLET)
        iter_caption.move_to(np.array([0, -3.3, 0]))
        self.play(FadeOut(self._caption), run_time=0.2)
        self.play(typewriter_anim(iter_caption, char_duration=0.025), run_time=0.6)
        self._caption = iter_caption

        iterates3d = power_iterate(self._C, V0_INIT, n_iters=5)
        ARROW_LEN = 1.8
        def tip_xyz(v3):
            v2 = project_iso(v3)
            return np.array([v2[0] * ARROW_LEN, v2[1] * ARROW_LEN, 0])
        v_arrow = Arrow(ORIGIN, tip_xyz(iterates3d[0]),
                        stroke_color=PCA_VIOLET, stroke_width=5.5, buff=0)
        self.play(GrowArrow(v_arrow), run_time=0.4)

        counter = m_text("iter 0/5", scale=0.24, color=PCA_VIOLET)
        counter.move_to(np.array([5.6, -3.0, 0]), aligned_edge=RIGHT)
        self.play(FadeIn(counter), run_time=0.2)

        for k in range(1, 6):
            new_counter = m_text(f"iter {k}/5", scale=0.24, color=PCA_VIOLET)
            new_counter.move_to(np.array([5.6, -3.0, 0]), aligned_edge=RIGHT)
            self.play(
                v_arrow.animate.put_start_and_end_on(ORIGIN, tip_xyz(iterates3d[k])),
                Transform(counter, new_counter),
                run_time=0.55,
            )
            # Tiny brightness pulse to mark each iteration step
            self.play(v_arrow.animate.set_stroke(width=7.0), run_time=0.06)
            self.play(v_arrow.animate.set_stroke(width=5.5), run_time=0.06)

        self.play(v_arrow.animate.set_color(TONE_AMBER), run_time=0.4)
        self.play(FadeOut(counter), run_time=0.3)

        # ============================================================
        # Phase 6 (28.0 – 32.0 s) — reveal p₁ + ellipse + close
        # ============================================================
        v_final = iterates3d[-1]
        v_final_2d = project_iso(v_final)
        angle = float(np.arctan2(v_final_2d[1], v_final_2d[0]))
        lam1 = float(self._eigvals[0])
        lam2 = float(self._eigvals[1])
        w = 2.4 * float(np.sqrt(lam1))
        h = 2.4 * float(np.sqrt(lam2))
        ellipse = Ellipse(width=w, height=h)
        ellipse.set_stroke(TONE_AMBER, 1.6, opacity=0.65)
        ellipse.set_fill(TONE_AMBER, 0.08)
        ellipse.rotate(angle)
        self.play(ShowCreation(ellipse), run_time=0.7)

        cap_p1 = m_text("p₁  =  direction of max variance",
                        scale=0.40, color=TONE_AMBER)
        cap_p1.move_to(np.array([0, -2.55, 0]))
        sub_p1 = m_text(f"C·p₁ = λ₁·p₁    (λ₁ ≈ {lam1:.2f})",
                        scale=0.28, color=TONE_MUTED)
        sub_p1.next_to(cap_p1, DOWN, buff=0.15)
        self.play(FadeOut(self._caption), FadeIn(cap_p1), FadeIn(sub_p1), run_time=0.4)
        self.wait(2.22)

        # Global fade-out.
        vec_left = VGroup(self._title, self._subtitle, self._plane, self._grid,
                          self._axes, self._f_mean, self._f_cov,
                          self._residual_arrows, self._mean_dot,
                          self._C_group, self._C_border, self._C_cap,
                          v_arrow, ellipse, cap_p1, sub_p1)
        img_left = Group(*self._dots)
        self.play(FadeOut(vec_left), FadeOut(img_left), run_time=0.6)
