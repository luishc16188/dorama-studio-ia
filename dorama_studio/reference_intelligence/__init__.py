"""
Reference Intelligence & Production DNA - Phase 5
Converts reference videos into production rules (HookRules, BeatStructureRules, VisualMotifRules, AudioSignatureRules).
"""

from .contracts import (
    AudioSignature,
    BeatStructure,
    HookRule,
    ProductionDNA,
    ReferenceAnalysis,
    VisualMotif,
)
from .parser import ReferenceIntelligenceAgent, VideoAnalyzer

__all__ = [
    "HookRule",
    "BeatStructure",
    "VisualMotif",
    "AudioSignature",
    "ProductionDNA",
    "ReferenceAnalysis",
    "VideoAnalyzer",
    "ReferenceIntelligenceAgent",
]
