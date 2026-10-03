"""
Analytics Engine – Recolecta métricas de producción y aprendizaje.
Conecta a los artefactos de calidad, CreativeGenome y a los resultados de cada fase.
Devuelve un `AnalyticsReport` con métricas de compromiso, calidad y uso de recursos.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.analytics_db import (
    get_latest_metrics,
    get_project_summary,
    get_season_metrics,
    insert_episode_metric,
)
from dorama_studio.data.schemas import AnalyticsReport

logger = logging.getLogger(__name__)


class AnalyticsEngineAgent(BaseAgent[dict, AnalyticsReport]):
    """Analiza y reporta métricas de la ejecución."""

    def __init__(self):
        super().__init__("AnalyticsEngineAgent")

    def run(self, input_data: dict) -> AnalyticsReport:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, data: dict) -> AnalyticsReport:
        """
        data puede contener:
        - episode_id, season_id, project_id, episode_number
        - quality_score, quality_state, media_duration_sec, render_time_sec
        - qc_passed, regeneration_count
        - episodes: list[dict] para análisis batch
        """
        # Si viene un solo episodio, insertar métrica
        if "episode_id" in data:
            insert_episode_metric(
                episode_id=data["episode_id"],
                season_id=data.get("season_id", "s01"),
                project_id=data.get("project_id", "proj_001"),
                episode_number=data.get("episode_number", 1),
                quality_score=data.get("quality_score"),
                quality_state=data.get("quality_state"),
                media_duration_sec=data.get("media_duration_sec"),
                render_time_sec=data.get("render_time_sec"),
                qc_passed=data.get("qc_passed"),
                regeneration_count=data.get("regeneration_count", 0),
            )

        # Análisis batch si se provee lista
        episodes = data.get("episodes", [])
        if episodes:
            bads = 0
            total_quality = 0
            for ep in episodes:
                if ep.get("quality_state") == "fail":
                    bads += 1
                qs = ep.get("quality_score", 0)
                if qs:
                    total_quality += qs

            avg_quality = total_quality / len(episodes) if episodes else 0
            error_rate = bads / len(episodes) if episodes else 0
        else:
            # Usar DB para resumen
            project_id = data.get("project_id", "proj_001")
            summary = get_project_summary(project_id)
            avg_quality = summary.get("avg_quality", 0)
            error_rate = 0
            if summary.get("total_episodes"):
                passed = summary.get("passed_count", 0)
                error_rate = 1 - (passed / summary["total_episodes"])

        return AnalyticsReport(
            error_rate=error_rate,
            avg_quality=avg_quality or 0,
            notes=["Auto-metric from AnalyticsEngine", "DB-backed"],
        )

    def get_season_report(self, season_id: str) -> dict:
        """Reporte detallado por temporada."""
        metrics = get_season_metrics(season_id)
        if not metrics:
            return {"season_id": season_id, "episodes": 0, "message": "No data"}

        return {
            "season_id": season_id,
            "total_episodes": len(metrics),
            "avg_quality": sum(m.get("quality_score", 0) for m in metrics) / len(metrics),
            "passed": sum(1 for m in metrics if m.get("qc_passed")),
            "total_regenerations": sum(m.get("regeneration_count", 0) for m in metrics),
            "avg_render_time": sum(m.get("render_time_sec", 0) for m in metrics) / len(metrics),
            "episodes": metrics,
        }

    def get_latest(self, limit: int = 10) -> list[dict]:
        """Últimos episodios procesados."""
        return get_latest_metrics(limit)


# Alias
Analytics = AnalyticsEngineAgent
