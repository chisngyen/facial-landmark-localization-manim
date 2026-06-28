#!/usr/bin/env bash
# Render all 15 shots at 1080p, concat them, and mux the narration track.
# Output: videos/ch12_final.mp4  (the exact published video).
# Requires: manimgl + ffmpeg on PATH, and assets_full.zip extracted into ./assets/.
set -e

SHOTS=(shot00_book_intro shot01_hook shot02_title_intro shot03_landmark_genealogy
       shot04_framework shot05_pca_math shot06_eye_localization shot07_rfe_asm
       shot08_algorithm_walkthrough shot09_experiments shot10_recap shot11_conclusions
       shot12_modern_bridge shot13_further_reading shot14_end_card)

mkdir -p videos/full_hd
: > videos/full_hd/concat.txt

for f in "${SHOTS[@]}"; do
    CLS=$(grep -oE "class (Section01_[A-Za-z0-9_]+)" "source/$f.py" | head -1 | awk '{print $2}')
    echo ">> rendering $f :: $CLS"
    manimgl "source/$f.py" "$CLS" -w --hd --video_dir videos/full_hd --file_name "$f"
    echo "file '$f.mp4'" >> videos/full_hd/concat.txt
done

echo ">> concat + mux narration"
ffmpeg -y -f concat -safe 0 -i videos/full_hd/concat.txt -c copy videos/full_hd/_video.mp4
ffmpeg -y -i videos/full_hd/_video.mp4 -i videos/Audio_full.wav \
       -c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 videos/ch12_final.mp4
rm -f videos/full_hd/_video.mp4

echo "DONE -> videos/ch12_final.mp4"
