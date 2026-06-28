"""ManimGL entry - Chapter 12 (Facial Landmark Localization).
Re-exports all scene classes; shots numbered in playback order.
"""
import os, sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from shot00_book_intro import Section01_Shot00_BookIntro
from shot01_hook import Section01_Shot01_Hook
from shot02_title_intro import Section01_Shot02_TitleIntro
from shot03_landmark_genealogy import Section01_Shot03_LandmarkGenealogy
from shot04_framework import Section01_Shot04_Framework
from shot05_pca_math import Section01_Shot05_PCA_Math
from shot06_eye_localization import Section01_Shot06_EyeLocalization
from shot07_rfe_asm import Section01_Shot07_RFE_ASM
from shot08_algorithm_walkthrough import Section01_Shot08_AlgorithmWalkthrough
from shot09_experiments import Section01_Shot09_Experiments
from shot10_recap import Section01_Shot10_Recap
from shot11_conclusions import Section01_Shot11_Conclusions
from shot12_modern_bridge import Section01_Shot12_ModernBridge
from shot13_further_reading import Section01_Shot13_FurtherReading
from shot14_end_card import Section01_Shot14_EndCard

__all__ = [
    "Section01_Shot00_BookIntro",
    "Section01_Shot01_Hook",
    "Section01_Shot02_TitleIntro",
    "Section01_Shot03_LandmarkGenealogy",
    "Section01_Shot04_Framework",
    "Section01_Shot05_PCA_Math",
    "Section01_Shot06_EyeLocalization",
    "Section01_Shot07_RFE_ASM",
    "Section01_Shot08_AlgorithmWalkthrough",
    "Section01_Shot09_Experiments",
    "Section01_Shot10_Recap",
    "Section01_Shot11_Conclusions",
    "Section01_Shot12_ModernBridge",
    "Section01_Shot13_FurtherReading",
    "Section01_Shot14_EndCard",
]
