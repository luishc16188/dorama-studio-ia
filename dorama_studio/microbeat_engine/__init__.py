"""
MicroBeat Engine - Fase 7
Motor de micro-beats de 2.5s dentro de beats de 10s.
Implementa Fórmula Fractal H→P→Q→E→R→Q2→C y Quality Gate 100pts (15 dims).
"""

from .fractal_engine import FractalEngine, FractalPattern
from .microbeat_engine import EpisodeMicroBeatPlan, MicroBeatEngine
from .microbeat_schema import FractalStage, MicroBeat, MicroBeatType
from .quality_gate import QualityDimension, QualityGate, QualityThreshold

__all__ = [
    "MicroBeat",
    "MicroBeatType",
    "FractalStage",
    "FractalEngine",
    "FractalPattern",
    "QualityGate",
    "QualityDimension",
    "QualityThreshold",
    "MicroBeatEngine",
    "EpisodeMicroBeatPlan",
]
