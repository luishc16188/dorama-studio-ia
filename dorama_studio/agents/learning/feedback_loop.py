# dorama_studio/agents/learning/feedback_loop.py
"""
Feedback Loop Agent - Creative Genome Curator.
Memoria permanente + Re-prompt automático + Presupuesto 70/20/10.
Construye Creative Genome persistente y devuelve direct_instructions para inyectar en agentes.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)


class FeedbackLoopAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Feedback Loop Agent that curates feedback and updates Creative Genome.
    """

    InputSchema = dict[str, Any]
    OutputSchema = dict[str, Any]

    def __init__(self):
        super().__init__("FeedbackLoopAgent")

    def process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Curate feedback based on analytics and update Creative Genome.

        Args:
            validated_input: Dict with analytics_report, next_episode_num, season_arc,
                           character_bible, genome_state, untested_ideas

        Returns:
            Dict with genome_updates, narrative_adjustments, hook_recommendation,
            character_adjustments, visual_adjustments, audio_adjustments, direct_instructions,
            experiment_budget, next_hypothesis
        """
        analytics_report = validated_input.get("analytics_report", {})
        next_episode_num = validated_input.get("next_episode_num", 1)
        season_arc = validated_input.get("season_arc", {})
        character_bible = validated_input.get("character_bible", [])
        genome_state = validated_input.get("genome_state", {})
        untested_ideas = validated_input.get("untested_ideas", [])

        logger.info(f"Curating feedback for episode {next_episode_num}")

        return self.curate_feedback(
            analytics_report,
            next_episode_num,
            season_arc,
            character_bible,
            genome_state,
            untested_ideas,
        )

    def curate_feedback(
        self,
        analytics_report: dict[str, Any],
        next_episode_num: int,
        season_arc: dict[str, Any],
        character_bible: list[dict[str, Any]],
        genome_state: dict[str, Any],
        untested_ideas: list[str],
    ) -> dict[str, Any]:
        """
        Curatea feedback basado en analíticas y actualiza Creative Genome.
        Returns dict con genome_updates, narrative_adjustments, hook_recommendation,
        character_adjustments, visual_adjustments, audio_adjustments, direct_instructions,
        experiment_budget, y next_hypothesis.
        """
        # Implementación determinista/mock para testing

        genome_updates = {
            "winning_hooks": [
                {
                    "episode": 1,
                    "category": "visual_shock",
                    "mechanism": "revelación mediante reflejo en objeto",
                    "retention_3s": 82,
                }
            ],
            "losing_hooks": [
                {
                    "episode": 2,
                    "category": "revelation_puro",
                    "reason": "demasiado diálogo explicativo",
                }
            ],
            "saturated_tropes": ["heredera oculta + romance prohibido"],
            "winning_characters": ["char_001 (CEO frío con secreto)"],
            "weak_characters": ["char_003 (rival sin motivación clara)"],
            "best_cliffhangers": [
                "ep 3: decisión imposible con cuenta regresiva visual"
            ],
            "best_visual_motifs": ["anillo brillante como símbolo de poder oculto"],
            "best_audio_motifs": ["sub-bass 40Hz como señal de traición inminente"],
            "audience_comments_themes": [
                "teorías sobre la verdadera identidad",
                "debates sobre perdonar la mentira",
            ],
        }

        narrative_adjustments = {
            "pacing": "acelerar Escalation 15%",
            "twist_timing": "mover Twist1 a segundo 40 exacto",
            "character_focus": ["char_003"],
            "tone_shift": "más tensión fría, menos melancolía",
        }

        hook_recommendation = {
            "category": "visual_shock",
            "mechanism": "revelación por objeto no diálogo",
            "novelty_target": 90,
            "avoid_categories": ["revelation"],
        }

        character_adjustments = [
            {
                "character": "char_003",
                "action": "increase_screen_time_20pct",
                "reason": "high_engagement_sentiment_0.82",
                "psychological_shift": "revelar ghost_parcial",
            }
        ]

        visual_adjustments = {
            "lighting": "más rim_light frío",
            "lens": "más 85mm ECU",
            "color_palette": "shift hacia cyan/magenta",
        }

        audio_adjustments = {
            "music_genre": "más synth_pulse",
            "sfx_timing": "sub-bass en cada twist",
            "silence_drops": "pre-cliffhanger obligatorio",
        }

        direct_instructions = {
            "master_writer": "Escribe Escalation con 40% menos diálogo, más object_reveal + reaction_shots. Twist1 en s.40 exacto.",
            "hook_engine": "Genera 120 hooks. Prioriza visual_shock+betrayal combo. Novelty target >85. Evita revelation puro.",
            "storyboard_agent": "Añade pattern_interrupt en s.20 (whip_pan) y s.35 (match_cut_ring). Shot_intent obligatorio por shot.",
            "editor_agent": "Punch-in 15% cada 2.5s. Silence_drop 0.2s pre-cliffhanger. LUT kdrama_cold_blue.",
        }

        experiment_budget = {
            "exploitation": 0.70,  # lo que funciona
            "adjacent_variation": 0.20,  # variaciones adyacentes
            "radical": 0.10,  # experimentos radicales
        }

        next_hypothesis = "Hipótesis: hook visual_shock+object_reveal retiene 15% más que hook dialogue-heavy. Test: ep N+1 abre con ECU anillo + sub-bass, 0 diálogo primeros 3s."

        return {
            "genome_updates": genome_updates,
            "narrative_adjustments": narrative_adjustments,
            "hook_recommendation": hook_recommendation,
            "character_adjustments": character_adjustments,
            "visual_adjustments": visual_adjustments,
            "audio_adjustments": audio_adjustments,
            "direct_instructions": direct_instructions,
            "experiment_budget": experiment_budget,
            "next_hypothesis": next_hypothesis,
        }
