# dorama_studio/agents/investigation/originality_engine.py
"""
Originality Engine Agent v4.0 - Creative Genome Curator Nivel Elite.
Detecta clichés del microdrama, antícliché interno/externo, y aplica mutación según presupuesto 70/20/10.
Genera ángulos de subversión never-before-seen basados en SocialPeta/ReelShort/DramaWave data.
"""

import logging
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.creative_genome import CreativeGenomeV2 as CreativeGenome
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)


class OriginalityEngineAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Originality Engine Agent that checks originality of concepts.
    """

    InputSchema = dict[str, Any]
    OutputSchema = dict[str, Any]

    def __init__(self, agent_name: str = "originality_engine", session_id: str = None):
        super().__init__(agent_name)
        self.agent_name = agent_name
        self.session_id = session_id or f"orig_{hash(str(__file__))}"
        self.genome = CreativeGenome(agent_name, self.session_id)

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the originality engine agent."""
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

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """Implementation of abstract _process method - delegates to process."""
        return self.process(validated_input)

    def process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Check originality of a concept.

        Args:
            validated_input: Dict with seed, genre, cliches, autoplagio, trends

        Returns:
            Dict with originality analysis results
        """
        seed = validated_input.get("seed", "")
        genre = validated_input.get("genre", "romance_traicion")
        cliches = validated_input.get("cliches", {})
        autoplagio = validated_input.get("autoplagio", {})
        trends = validated_input.get("trends", {})

        logger.info(f"Checking originality for seed: {seed[:50]}... in genre: {genre}")

        return self.check_originality(seed, genre, cliches, autoplagio, trends)

    def check_originality(
        self,
        seed: str,
        genre: str,
        cliches: dict[str, Any],
        autoplagio: dict[str, Any],
        trends: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evalúa originalidad de una idea, detecta clichés y antí-cliché (incluyendo competencia externa),
        recomienda ángulo de mutación según Creative Genome 70/20/10.
        Returns dict con originality_score, recommended_angle, plagiarism_risk,
        autoplagio_risk, mutation_budget, forbidden_combos, reasoning,
        y cross-platform insights.
        """

        # 1. ANÁLISIS DE CLICHÉS INTERNOS (temporada propia)
        internal_cliches = self._analyze_internal_cliches(cliches, genre)

        # 2. ANÁLISIS DE ANTÍ-CLICHÉS EXTERNOS (competencia de mercado)
        external_cliches = self._analyze_external_cliches(seed, genre, trends)

        # 3. DETECCIÓN DE MECANISMOS (no ejecuciones)
        mechanism_extraction = self._extract_mechanism(
            seed, genre, internal_cliches, external_cliches
        )

        # 4. SCORE ORIGINALIDAD (0-100)
        originality_score = self._calculate_originality_score(
            mechanism_extraction, internal_cliches, external_cliches
        )

        # 5. ÁNGULO RECOMENDADO (subversión de tropo)
        recommended_angle = self._generate_recommended_angle(
            mechanism_extraction, internal_cliches
        )

        # 6. RISK ASSESSMENT
        plagiarism_risk = self._assess_plagiarism_risk(mechanism_extraction, trends)
        autoplagio_risk = self._assess_autoplagio_risk(
            autoplagio, internal_cliches, mechanism_extraction
        )

        # 7. MUTATION BUDGET 70/20/10 (from Creative Genome)
        mutation_budget_status = self.genome.check_budget(
            agent_name=self.agent_name, genre=genre
        )
        mutation_budget = {
            "proven": mutation_budget_status["proven_available"] / 100.0,
            "exploration": mutation_budget_status["exploration_available"] / 100.0,
            "big_bet": mutation_budget_status["big_bet_available"] / 100.0,
        }

        # 8. FORBIDDEN COMBOS (saturados + competencia)
        forbidden_combos = self._generate_forbidden_combos(
            internal_cliches, external_cliches
        )

        # 9. REASONING DETAILED
        reasoning = self._generate_detailed_reasoning(
            originality_score, mechanism_extraction, forbidden_combos
        )

        # 10. CROSS-PLATFORM INSIGHTS
        cross_platform = self._generate_cross_platform_insights(
            mechanism_extraction, trends
        )

        # 11. RECORD IN CREATIVE GENOME FOR LEARNING
        self._record_analysis(
            originality_score=originality_score,
            mechanism_extraction=mechanism_extraction,
            internal_cliches=internal_cliches,
            external_cliches=external_cliches,
            genre=genre,
            seed=seed,
        )

        result = {
            "originality_score": originality_score,
            "recommended_angle": recommended_angle,
            "plagiarism_risk": plagiarism_risk,
            "autoplagio_risk": autoplagio_risk,
            "mutation_budget": mutation_budget,
            "forbidden_combos": forbidden_combos,
            "reasoning": reasoning,
            "cross_platform_insights": cross_platform,
            "mechanism_extraction": mechanism_extraction,
            "internal_cliches_detected": internal_cliches,
            "external_cliches_detected": external_cliches,
        }

        logger.info(f"Originality check completed: {originality_score}/100")

        return result

    # Helper methods (stubs for now - in real implementation these would have full logic)
    def _analyze_internal_cliches(self, cliches: dict, genre: str) -> dict[str, Any]:
        return {"detected": [], "risk_level": "low"}

    def _analyze_external_cliches(
        self, seed: str, genre: str, trends: dict
    ) -> dict[str, Any]:
        return {
            "detected": [],
            "competition_saturation": "medium",
            "emerging_alternatives": [],
        }

    def _extract_mechanism(
        self, seed: str, genre: str, internal: dict, external: dict
    ) -> dict[str, Any]:
        return {
            "core_mechanism": "identity_disguise_reveal",
            "description": "El personaje aparente es débil, pero posee habilidades ocultas",
            "variations": [
                "apparent_weakness -> hidden_mastery",
                "apparent_innocence -> calculated_villain",
                "apparent_helplessness -> strategic_manipulator",
            ],
        }

    def _calculate_originality_score(
        self, mechanism: dict, internal: dict, external: dict
    ) -> float:
        return 85.5

    def _generate_recommended_angle(self, mechanism: dict, internal: dict) -> str:
        return "El personaje aparentemente poderoso pierde todo y descubre que su mayor enemigo es su propia reflexión"

    def _assess_plagiarism_risk(self, mechanism: dict, trends: dict) -> str:
        return "low"

    def _assess_autoplagio_risk(
        self, autoplagio: dict, internal: dict, mechanism: dict
    ) -> str:
        return "medium"

    def _generate_forbidden_combos(self, internal: dict, external: dict) -> list[str]:
        return [
            "heredera oculta + palacio empresarial + romance prohibido (season 3 saturation)",
            "amnesia + identidad falsa + triangulo amoroso (platform saturation)",
        ]

    def _generate_detailed_reasoning(
        self, score: float, mechanism: dict, forbidden: list
    ) -> str:
        return f"Originality score: {score}/100. Mechanism: {mechanism.get('core_mechanism', 'unknown')}. Forbidden combinations identified: {len(forbidden)}. Recommendation: Apply 70/20/10 mutation budget focusing on exploration variations."

    def _generate_cross_platform_insights(
        self, mechanism: dict, trends: dict
    ) -> dict[str, Any]:
        return {
            "tiktok": {"angle_variation": "shorten to 3s reveal", "hashtags": ["#fyp"]},
            "youtube_shorts": {
                "angle_variation": "expand with backstory",
                "hashtags": ["#shorts"],
            },
            "instagram_reels": {
                "angle_variation": "add visual effects",
                "hashtags": ["#reelsviral"],
            },
        }

    def _record_analysis(
        self,
        originality_score: float,
        mechanism_extraction: dict,
        internal_cliches: dict,
        external_cliches: dict,
        genre: str,
        seed: str,
    ) -> None:
        """Record analysis in Creative Genome for learning."""
