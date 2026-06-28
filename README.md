# Facial Landmark Localization — a Manim explainer

Individual project for **CSC14006 Pattern Recognition** (Faculty of IT, VNU-HCM University
of Science). Student: **Trần Chí Nguyên — 23122044**.

A ~9-minute ManimGL video on Chapter 12, "Facial Landmark Localization," of the *Handbook
of Face Recognition* (2nd ed., Ding & Wang) — the Active Shape Model and RFE-ASM, through
to modern methods (FAN, MediaPipe, 3D mesh).

Video: https://youtu.be/GdUN7_CgPqc

## Run it

Needs Python 3.11, ManimGL 1.7.2 (`pip install -r requirements.txt`), ffmpeg on PATH, and
the Cascadia Mono font (so the text matches the video).

```bash
git clone https://github.com/chisngyen/facial-landmark-localization-manim.git
cd facial-landmark-localization-manim
pip install -r requirements.txt

# one shot
manimgl source/shot07_rfe_asm.py Section01_Shot07_RFE_ASM -w --hd

# the whole video: download assets_full.zip from Releases, unzip into ./assets/, then
bash render_all.sh        # -> videos/ch12_final.mp4
```

15 shots live in `source/`, one file per shot; `ch12_scenes.py` collects them all. The
narration (`videos/Audio_full.wav`) and subtitles are in `videos/`. The large render
assets (3D hero stills, ~346 MB) are in Releases — GitHub isn't meant to hold big binaries
inline.

## Source

Ding, X. & Wang, L. (2011). *Facial Landmark Localization.* In *Handbook of Face
Recognition*, 2nd ed., Ch. 12, pp. 305–320. Springer.
