# dorama_studio/agents/investigation/viral_analyst.py
"""
Viral Analyst Agent - Forense de retención segundo a segundo.
Descompone videos top en curvas de dopamina por segundo y aísla elementos exactos que causan retención.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)


class ViralAnalystAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Viral Analyst Agent that analyzes viral video patterns.
    """

    InputSchema = dict[str, Any]
    OutputSchema = dict[str, Any]

    def __init__(self):
        super().__init__("ViralAnalystAgent")

    def run(self, input_data: Any) -> dict[str, Any]:
        """Execute the agent with input data."""
        return self.process(input_data)

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze viral patterns from video data.

        Args:
            validated_input: Dict with video_data and genre

        Returns:
            Dict with viral analysis results
        """
        video_data = validated_input.get("video_data", [])
        genre = validated_input.get("genre", "romance_traicion")

        logger.info(
            f"Analyzing viral patterns for {genre} from {len(video_data)} videos"
        )

        return self.analyze_viral_patterns(video_data, genre)

    def analyze_viral_patterns(
        self, video_data: list[dict], genre: str
    ) -> dict[str, Any]:
        """
        Analiza videos virales para extraer mecanismos de retención y crear un "Viral Blueprint".
        Returns dict with hook_analysis, structure_analysis, character_analysis, visual_analysis,
        audio_analysis, cta_analysis, outlier_mechanisms, actionable_insights, and viral_ruleset.
        """
        # Implementación determinista/mock para testing

        hook_analysis = {
            "winning_patterns": [
                "revelación visual en 0-3s con sub-bass 40Hz",
                "pregunta retórica que crea asimetría de información",
                "micro-expresión de shock seguida de acción inmediata",
            ],
            "failed_patterns": [
                "exposición verbal >3s sin cambio visual",
                "genérico sin elemento de sorpresa",
                "ritmo plano >2.5s sin pattern interrupt",
            ],
            "intrigue_scores": {"0-10s": 95, "10-20s": 75, "20-30s": 80},
            "novelty_scores": {"0-10s": 88, "10-20s": 65, "20-30s": 72},
        }

        structure_analysis = {
            "beat_timing": {
                "hook": "0-10s",
                "context": "10-20s",
                "problem": "20-30s",
                "escalation": "30-40s",
                "twist1": "40-50s",
                "conflict2": "50-60s",
                "revelation": "60-70s",
                "cliffhanger": "70-80s",
                "cta": "80-90s",
            },
            "twist_placement": [45, 47, 48],  # segundos óptimos para twist
            "pacing_curve": [
                85,
                70,
                80,
                90,
                95,
                85,
                75,
                85,
                90,
                88,
            ],  # energía por cada 10s
            "curiosity_loops": [
                "pregunta del objeto misterioso",
                "doble agenda del aliado",
            ],
        }

        character_analysis = {
            "archetypes_that_work": ["ruler_with_secret", "rebel_in_disguise"],
            "chemistry_patterns": ["tension_protector_vs_cold_ceo"],
            "intro_timing": [5, 8, 12],  # momentos óptimos para presentar personajes
            "engagement_by_role": {
                "protagonist": 0.92,
                "antagonist": 0.85,
                "love_interest": 0.78,
                "mentor": 0.65,
            },
        }

        visual_analysis = {
            "camera_patterns": [
                "ECU eyes->phone",
                "whip_pan_reaction",
                "rack_focus_revelation",
            ],
            "lighting_mood": ["tension_cyan", "romance_gold", "danger_red"],
            "composition_rules": [
                "regla_de_tercios_con_space_negativo",
                "enmarcado_con_objetos_simbolicos",
            ],
            "pattern_interrupt_signatures": [
                "zoom_punch_eyes",
                "whip_pan_90deg",
                "speed_ramp_impact",
            ],
        }

        audio_analysis = {
            "music_genres": ["tense_orchestral_pulse", "emotional_synth_peak"],
            "sfx_timing": [
                "sub_bass_drop_0s",
                "silence_pre_twist_0.5s",
                "heartbeat_swell_confrontation",
            ],
            "voice_directing": [
                "prosody_pitch_minus_2st_ceo",
                "breath_hold_before_revelation",
            ],
            "silence_drop_moments": [
                34.5,
                60.5,
                70.5,
            ],  # segundos antes de twist/revelation/cliffhanger
        }

        cta_analysis = {
            "narrative_vs_generic": {"narrative": 0.92, "generic": 0.35},
            "conversion_rates": {
                "tiktok": 0.084,
                "youtube_shorts": 0.072,
                "instagram_reels": 0.068,
            },
            "comment_trigger_types": [
                "moral_dilemma",
                "identity_tease",
                "revenge_choice",
                "team_war",
            ],
        }

        outlier_mechanisms = [
            {
                "video": "vid_0042_tiktok",
                "mechanism": "revelación mediante reflejo en objeto, no diálogo",
                "why_it_worked": "evita exposición verbal, crea momento 'aha' visual",
                "replicable": True,
            }
        ]

        actionable_insights = [
            "Priorizar hooks visuales sobre dialogados en primeros 3s",
            "Insertar pattern interrupt cada 2.0-2.5s máximo",
            "Usar silencio de 0.5s ANTES de twists y revelaciones",
            "Desarrollar arquetipos con contradicción psicológica clara",
        ]

        viral_ruleset = [
            "regla 1: Máx 2.5s sin cambio visual/auditivo significativo",
            "regla 2: Hook debe generar shock visual + pregunta en 0-3s",
            "regla 3: Cada beat debe tener un 'info beat' revelatorio",
            "regla 4: El diálogo debe ser ≤15 palabras y en español latino natural",
            "regla 5: Cliffhanger debe cortar frase en medio, nunca completar",
        ]

        return {
            "hook_analysis": hook_analysis,
            "structure_analysis": structure_analysis,
            "character_analysis": character_analysis,
            "visual_analysis": visual_analysis,
            "audio_analysis": audio_analysis,
            "cta_analysis": cta_analysis,
            "outlier_mechanisms": outlier_mechanisms,
            "actionable_insights": actionable_insights,
            "viral_ruleset": viral_ruleset,
        }
