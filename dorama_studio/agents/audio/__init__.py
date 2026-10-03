"""
Audio Package Init - Fase 12
Audio agents package for Dorama Studio IA V2.
"""

from __future__ import annotations

from .music_supervisor_agent import MusicSupervisorAgent
from .sound_designer_agent import SoundDesignerAgent
from .voice_director_agent import VoiceDirectorAgent

__all__ = [
    "VoiceDirectorAgent",
    "SoundDesignerAgent",
    "MusicSupervisorAgent"
]
