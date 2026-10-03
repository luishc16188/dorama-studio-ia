# dorama_studio/agents/narrative/cta_writer.py
"""
CTA Writer Agent - Engagement Architect que crea dilemas morales tribales que obligan a comentar.
Nunca crea CTAs genéricos como "suscríbete", siempre preguntas que dividen a la audiencia en bandos opuestos.
"""

import logging
from typing import Any, TypeVar

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)

# Define type variables for Generic BaseAgent
InputType = TypeVar("InputType", bound=dict[str, Any])
OutputType = TypeVar("OutputType", bound=dict[str, Any])


class CTAWriterAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    CTA Writer Agent that creates tribal CTAs.
    """

    InputSchema = dict[str, Any]
    OutputSchema = dict[str, Any]

    def __init__(self):
        super().__init__("CTAWriterAgent")

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Write tribal CTA from cliffhanger and context.

        Args:
            validated_input: Dict with episode_num, cliffhanger, characters, platform, genome_engagement

        Returns:
            Dict with cta_options, selected cta, and reasoning
        """
        episode_num = validated_input.get("episode_num", 1)
        cliffhanger = validated_input.get("cliffhanger", {})
        characters = validated_input.get("characters", [])
        platform = validated_input.get("platform", "tiktok")
        genome_engagement = validated_input.get("genome_engagement", {})

        logger.info(f"Writing tribal CTA for episode {episode_num} on {platform}")

        return self.write_tribal_cta(
            episode_num, cliffhanger, characters, platform, genome_engagement
        )

    def process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Write tribal CTA from cliffhanger and context.

        Args:
            validated_input: Dict with episode_num, cliffhanger, characters, platform, genome_engagement

        Returns:
            Dict with cta_options, selected cta, and reasoning
        """
        return self._process(validated_input)

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the CTA writer agent."""
        result = self.process(input_data)
        # Return dict-like object with payload attribute for test compatibility
        class ResultWrapper:
            def __init__(self, payload):
                self.payload = payload
            def get(self, key, default=None):
                if isinstance(self.payload, dict):
                    return self.payload.get(key, default)
                return default
            def __getitem__(self, key):
                if isinstance(self.payload, dict):
                    return self.payload[key]
                raise KeyError(key)
            def __contains__(self, key):
                if isinstance(self.payload, dict):
                    return key in self.payload
                return False
        return ResultWrapper(result)

    def write_tribal_cta(
        self,
        episode_num: int,
        cliffhanger: dict[str, Any],
        characters: list[dict[str, Any]],
        platform: str,
        genome_engagement: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Escribe CTA tribal basado en el cliffhanger y personajes.
        Returns dict con cta_options, selected cta, y reasoning.
        Nunca genera "suscríbete", "sígueme", etc. Siempre pregunta tribal que crea bandos.
        """
        # Implementación determinista/mock para testing

        # Determinar tipo de CTA basado en cliffhanger y engagement de personajes
        # En implementación real, esto sería más sofisticado

        cta_options = [
            {
                "type": "moral_dilemma",
                "text": "Él la salvó... pero mintió sobre su identidad real. ¿Perdonarías la mentira que te salvó la vida?",
                "visual": "split_screen_freeze",
                "audio_cue": "heartbeat_slow_fade_into_silence",
                "platform_adapted": {
                    "tiktok": "Equipo VERDAD vs Equipo AMOR 👉 Comenta tu bando",
                    "youtube_shorts": "Vota en Comunidad: ¿Perdonarías la mentira salvadora?",
                    "instagram_reels": "Encuesta: 💗 Perdonar / ❌ No perdonar",
                },
            },
            {
                "type": "revenge_choice",
                "text": "¿Destruirás el Motor Central que da energía a toda la ciudad... o le das una oportunidad de redimirse?",
                "visual": "text_overlay_yellow_bold",
                "audio_cue": "unresolved_sting",
                "platform_adapted": {
                    "tiktok": "SÍ = Destruir sistema / NO = Dar segunda oportunidad 👉",
                    "youtube_shorts": "Vota: ¿Merece segunda oportunidad el sistema energético?",
                    "instagram_reels": "Encuesta: 🔥 Destruir / 💗 Renovar",
                },
            },
            {
                "type": "team_war",
                "text": "Equipo TECNÓCRATAS (progreso a cualquier costo) vs Equipo GUARDIANES (protección de tradición) — ¿qué bando eliges?",
                "visual": "split_screen_portraits",
                "audio_cue": "tribal_drum_beat",
                "platform_adapted": {
                    "tiktok": "Team TÉCNO ⚡ vs Team GUARDIA 🛡️",
                    "youtube_shorts": "Comunidad: ¿Progreso a cualquier costo o preservación cuidadosa?",
                    "instagram_reels": "Encuesta: ⚡ Progreso / 🛡️ Tradición",
                },
            },
        ]

        # Seleccionar CTA basado en análisis de engagement y cliffhanger
        selected = cta_options[
            0
        ]  # Por defecto moral dilemma, en real sería más inteligente

        reasoning = f"Basado en cliffhanger '{cliffhanger.get('leads_to_next', 'revelación de identidad')}'+ character engagement patterns, el dilema moral maximiza comentarios polarizados y teorías de audiencia."

        return {
            "cta_options": cta_options,
            "selected": selected,
            "reasoning": reasoning,
        }
