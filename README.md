# Facial Landmark Localization — a Manim explainer

A ~9-minute, 3Blue1Brown-style video that visualizes **Chapter 12 — "Facial Landmark
Localization"** from the *Handbook of Face Recognition* (2nd ed., Xiaoqing Ding & Liting
Wang, 2011): the **Active Shape Model (ASM)** and its refined variant **RFE-ASM**, built
entirely with **Manim (ManimGL)**.

Individual project — **CSC14006 Pattern Recognition**, FIT, VNU-HCM University of Science.
Author: **Trần Chí Nguyên** (MSSV 23122044).

## Watch

- ▶ **YouTube (full, 16:9, EN/VI subs):** https://youtu.be/GdUN7_CgPqc
- 📘 Facebook: https://www.facebook.com/share/v/1CcyEGoUk8/

`#fithcmus #patternrecognition #ai #ml`

## What's inside

15 shots, one file per shot in [`source/`](source/), each one concrete step of the
algorithm made kinetic (mean shape → covariance → eigenvector → shape modes → ASM search
→ experiments → modern bridge). `source/ch12_scenes.py` re-exports every scene class.

| # | File | Step |
|---|------|------|
| 00–02 | book_intro · hook · title_intro | Intro, the "88 points" hook, the 6 questions |
| 03 | landmark_genealogy | Where landmarks help; why a fixed box fails |
| 04–05 | framework · pca_math | detect→crop→find→refine; PCA shape model |
| 06–08 | eye_localization · rfe_asm · algorithm_walkthrough | Eyes first; x = x̄ + Φ·b modes; ASM converging |
| 09 | experiments | RFE-ASM vs ASM (accuracy · speed · error · CED) |
| 10–14 | recap · conclusions · modern_bridge · further_reading · end_card | Recap; ASM→FAN→MediaPipe→FLAME |

## Reproduce the video 100%

**Requirements:** Python 3.11, [ManimGL](https://github.com/3b1b/manim) (`pip install
manimgl`), and `ffmpeg` on PATH. (No LaTeX needed — text is `Text`-based.)

```bash
# 1. clone
git clone https://github.com/chisngyen/facial-landmark-localization-manim.git
cd facial-landmark-localization-manim
pip install -r requirements.txt

# 2. get the heavy render assets (3D hero stills, app sequences, book frames)
#    download assets_full.zip from the repo's "Releases" page, then:
#    unzip it so the folders land in ./assets/  (assets/shot03v2, assets/apps, assets/book_frames)

# 3a. render ONE shot (quick check, no LaTeX, asset-free math shot)
manimgl source/shot07_rfe_asm.py Section01_Shot07_RFE_ASM -w -l

# 3b. render the WHOLE video at 1080p, concat + mux the narration
bash render_all.sh        # → videos/ch12_final.mp4  (the exact video above)
```

The narration track (`videos/Audio_full.wav`) and subtitles (`videos/ch12_final*.srt`)
are included, so `render_all.sh` reproduces the final muxed video.

**On reproducibility:** every shot is deterministic (fixed RNG seeds), so the *content,
layout, timing and assets* reproduce exactly. For a **pixel-identical** result use the
same toolchain that produced it: **ManimGL 1.7.2** (pinned in `requirements.txt`) and the
**Cascadia Mono** font installed — without that font Manim falls back to another
monospace face (same content, slightly different glyphs).

> Light assets (`assets/datasets`, `assets/shot11`) ship in the repo. The large ones
> (`shot03v2` ≈ 346 MB hero renders, `apps`, `book_frames`) are in **Releases** — GitHub
> isn't meant to hold big binaries inline.

## Source

Ding, X. & Wang, L. (2011). *Facial Landmark Localization.* In S. Z. Li & A. K. Jain
(eds.), **Handbook of Face Recognition** (2nd ed.), Ch. 12, pp. 305–320. Springer.
