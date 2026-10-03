"""
ViralAnalystAgent – Análisis de patrones virales con métricas reales.
"""

from __future__ import annotations

import time
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.persistence import persistence
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext


class ViralAnalystAgent(BaseAgent):
    InputSchema = PipelineContext
    OutputSchema = AgentResult

    def __init__(self):
        super().__init__("ViralAnalystAgent")
        self.agent_name = "ViralAnalystAgent"

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the viral analyst agent."""
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

    def _process(self, context: PipelineContext) -> AgentResult:
        start = time.time()
        try:
            trends = context.trends_data or {}
            genre = context.genre

            insights = self._analyze_viral_patterns(trends, genre)

            log_id = persistence.log_generation(
                project_id=context.project_id,
                agent_name=self.agent_name,
                input_data={"trends_count": len(trends.get("top_trends", []))},
                output_data=insights,
                model_used="viral_analysis_engine",
                latency_ms=int((time.time() - start) * 1000),
                episode_id=context.episode_id or "",
            )

            return AgentResult(
                success=True,
                agent_name=self.agent_name,
                output_data={"viral_insights": insights},
                context_updates={"viral_insights": insights},
                logs=[{"id": log_id, "data": insights}],
                latency_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            return AgentResult(
                success=False,
                agent_name=self.agent_name,
                error=str(e),
                recoverable=True,
                latency_ms=int((time.time() - start) * 1000),
            )

    def _analyze_viral_patterns(self, trends: dict, genre: str) -> dict:
        top_trends = trends.get("top_trends", [])

        # Análisis de patrones comunes en contenido viral
        pattern_scores = {
            "hook_strength": 0.0,
            "emotional_arc": 0.0,
            "visual_novelty": 0.0,
            "audio_sync": 0.0,
            "cliffhanger_potential": 0.0,
            "rewatch_value": 0.0,
            "shareability": 0.0,
            "comment_bait": 0.0,
        }

        # Heurísticas basadas en género
        genre_multipliers = {
            "romance_traicion": {
                "hook_strength": 1.2,
                "emotional_arc": 1.3,
                "cliffhanger_potential": 1.1,
            },
            "thriller_misterio": {
                "hook_strength": 1.3,
                "visual_novelty": 1.2,
                "rewatch_value": 1.4,
            },
            "fantasia_épica": {
                "visual_novelty": 1.4,
                "audio_sync": 1.1,
                "shareability": 1.2,
            },
        }.get(genre, {})

        for trend in top_trends:
            velocity = trend.get("velocity", 0.5)
            topic = trend.get("topic", "").lower()

            # Scoring basado en keywords virales
            if any(
                kw in topic
                for kw in ["secret", "hidden", "reveal", "twist", "identity"]
            ):
                pattern_scores["hook_strength"] += velocity * 0.15
                pattern_scores["cliffhanger_potential"] += velocity * 0.12

            if any(
                kw in topic
                for kw in ["love", "romance", "marriage", "heiress", "forbidden"]
            ):
                pattern_scores["emotional_arc"] += velocity * 0.15
                pattern_scores["shareability"] += velocity * 0.1

            if any(kw in topic for kw in ["magic", "chosen", "system", "loop", "time"]):
                pattern_scores["visual_novelty"] += velocity * 0.15
                pattern_scores["rewatch_value"] += velocity * 0.12

            if "fake" in topic or "enemies" in topic:
                pattern_scores["comment_bait"] += velocity * 0.1

        # Aplicar multiplicadores de género
        for k, v in pattern_scores.items():
            mult = genre_multipliers.get(k, 1.0)
            pattern_scores[k] = min(1.0, v * mult)

        actionable_insights = []
        for pattern, score in pattern_scores.items():
            if score > 0.7:
                actionable_insights.append(
                    {
                        "pattern": pattern,
                        "score": round(score, 2),
                        "recommendation": self._get_recommendation(pattern, score),
                    }
                )

        return {
            "pattern_scores": {k: round(v, 2) for k, v in pattern_scores.items()},
            "actionable_insights": actionable_insights,
            "top_trend_topics": [t["topic"] for t in top_trends[:5]],
            "genre": genre,
        }

    def _get_recommendation(self, pattern: str, score: float) -> str:
        recs = {
            "hook_strength": "Abrir con pregunta visual + audio disonante en primer frame",
            "emotional_arc": "Diseñar arco de 3 picos emocionales en 90s",
            "visual_novelty": "Usar lente anamórfico + color grading distinto por acto",
            "audio_sync": "Sincronizar Foley con micro-expresiones (frame-exacto)",
            "cliffhanger_potential": "Plantar loop cognitivo en beat 7, resolver en beat 9",
            "rewatch_value": "Esconder 3 detalles visuales que solo se ven en 2da vista",
            "shareability": "Incluir dilema moral binario en CTA final",
            "comment_bait": "Dejar pista ambigua sobre identidad del antagonista",
        }
        return recs.get(pattern, "Optimizar según métricas de plataforma")
