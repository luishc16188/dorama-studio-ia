"""Dorama Studio IA - Multi-agent automated microdrama creation system"""

# Public imports
from .agents.base_agent import BaseAgent
from .agents.contract import AgentContract, EpisodeSpecV2
from .contracts.character_bible import CharacterBible
from .contracts.episode_scorer import EpisodeScore
from .contracts.trend_signal import TrendSignal, ViralPotential
from .core.base_agent import AnalyticsOutput, BaseAgent as CoreBaseAgent, FeedbackLoop
from .core.error_memory import ErrorMemoryBank
from .video.model_router import ModelRouter, ShotSpec
from .visual.consistency_validator import CharacterConsistencyValidator

__version__ = '0.1.0'
__author__ = 'Dorama Studio Team'

__all__ = [
    'AnalyticsOutput',
    'BaseAgent',
    'CharacterBible',
    'CharacterConsistencyValidator',
    'EpisodeScore',
    'ErrorMemoryBank',
    'FeedbackLoop',
    'ModelRouter',
    'ShotSpec',
    'TrendSignal',
    'ViralPotential',
]
