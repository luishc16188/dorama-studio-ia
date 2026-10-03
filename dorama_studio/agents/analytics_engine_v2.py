"""
Analytics Engine v2 - Fase 14
Motor de analíticas avanzado con métricas de producción, calidad, compromiso y aprendizaje.
Soporta análisis por episodio, temporada, proyecto y comparativas A/B.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import AnalyticsReport

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Tipos de métricas recopiladas."""
    QUALITY_SCORE = "quality_score"
    QUALITY_STATE = "quality_state"
    RENDER_TIME = "render_time_sec"
    MEDIA_DURATION = "media_duration_sec"
    REGENERATION_COUNT = "regeneration_count"
    TOKEN_USAGE = "token_usage"
    COST_USD = "cost_usd"
    LATENCY_MS = "latency_ms"
    ENGAGEMENT_RATE = "engagement_rate"
    RETENTION_RATE = "retention_rate"
    VIEW_COUNT = "view_count"
    COMPLETION_RATE = "completion_rate"
    SHARE_RATE = "share_rate"
    COMMENT_SENTIMENT = "comment_sentiment"


@dataclass
class EpisodeMetric:
    """Métrica individual de un episodio."""
    episode_id: str
    project_id: str
    season_id: str
    episode_number: int
    timestamp: float
    metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    platform_metrics: dict[str, dict] = field(default_factory=dict)  # por plataforma


@dataclass
class SeasonAnalytics:
    """Analíticas agregadas por temporada."""
    season_id: str
    project_id: str
    total_episodes: int
    avg_quality_score: float
    quality_distribution: dict[str, int]  # pass/fail/warning
    avg_render_time: float
    total_regenerations: int
    total_cost_usd: float
    total_tokens: int
    platform_performance: dict[str, dict]  # por plataforma
    top_performing_episodes: list[str]
    weakest_dimensions: list[str]
    improvement_trend: float  # tendencia de mejora (%)


@dataclass
class ComparativeAnalytics:
    """Analíticas comparativas A/B."""
    experiment_id: str
    variant_a: str
    variant_b: str
    metric: MetricType
    sample_a: list[float]
    sample_b: list[float]
    p_value: float
    significant: bool
    lift: float  # porcentaje de mejora
    confidence_interval: tuple


class AnalyticsEngineV2(BaseAgent[dict[str, Any], AnalyticsReport]):
    """
    Motor de Analíticas v2 - Recopila, procesa y reporta métricas de:
    - Calidad de producción (QC multimodal)
    - Rendimiento de generación (tiempo, costo, tokens)
    - Compromiso de audiencia (vistas, retención, engagement)
    - Aprendizaje y evolución (Creative Genome)
    - Experimentos A/B
    """

    def __init__(self, storage_path: str = "analytics_data"):
        super().__init__("AnalyticsEngineV2")
        self.storage_path = storage_path
        self.episode_metrics: list[EpisodeMetric] = []
        self.season_cache: dict[str, SeasonAnalytics] = {}
        self.experiment_results: list[ComparativeAnalytics] = []

    def _process(self, validated_input: dict[str, Any]) -> AnalyticsReport:
        """
        Procesa solicitud de analíticas.

        Args:
            validated_input: Dict con:
                - action: "record" | "report" | "compare" | "trend"
                - episode: EpisodeSpecV2 (para record)
                - quality_report: QualityReport (para record)
                - platform_data: Dict (para record)
                - project_id, season_id, episode_ids (para report)
                - experiment_config (para compare)

        Returns:
            AnalyticsReport con métricas e insights
        """
        action = validated_input.get("action", "report")

        if action == "record":
            return self._record_metrics(validated_input)
        elif action == "report":
            return self._generate_report(validated_input)
        elif action == "compare":
            return self._run_comparison(validated_input)
        elif action == "trend":
            return self._analyze_trend(validated_input)
        else:
            return AnalyticsReport(
                error_rate=1.0,
                avg_quality=0.0,
                notes=[f"Unknown action: {action}"]
            )

    def _record_metrics(self, data: dict[str, Any]) -> AnalyticsReport:
        """Registra métricas de un episodio."""
        episode = data.get("episode")
        quality_report = data.get("quality_report")
        platform_data = data.get("platform_data", {})
        render_time = data.get("render_time_sec", 0)
        token_usage = data.get("token_usage", 0)
        cost_usd = data.get("cost_usd", 0)
        regeneration_count = data.get("regeneration_count", 0)

        if not episode:
            return AnalyticsReport(error_rate=1.0, avg_quality=0.0, notes=["No episode provided"])

        episode_id = f"ep_{episode.episode_number}_{episode.project_id}"
        timestamp = time.time()

        metrics = {
            MetricType.QUALITY_SCORE: quality_report.score if quality_report else 0,
            MetricType.QUALITY_STATE: quality_report.state.value if quality_report else "unknown",
            MetricType.RENDER_TIME: render_time,
            MetricType.MEDIA_DURATION: episode.target_duration_sec,
            MetricType.REGENERATION_COUNT: regeneration_count,
            MetricType.TOKEN_USAGE: token_usage,
            MetricType.COST_USD: cost_usd,
        }

        # Métricas de plataforma
        platform_metrics = {}
        for platform, pdata in platform_data.items():
            platform_metrics[platform] = {
                MetricType.VIEW_COUNT: pdata.get("views", 0),
                MetricType.ENGAGEMENT_RATE: pdata.get("engagement_rate", 0),
                MetricType.RETENTION_RATE: pdata.get("retention_rate", 0),
                MetricType.COMPLETION_RATE: pdata.get("completion_rate", 0),
                MetricType.SHARE_RATE: pdata.get("share_rate", 0),
            }

        episode_metric = EpisodeMetric(
            episode_id=episode_id,
            project_id=episode.project_id,
            season_id=data.get("season_id", "s01"),
            episode_number=episode.episode_number,
            timestamp=timestamp,
            metrics=metrics,
            platform_metrics=platform_metrics
        )

        self.episode_metrics.append(episode_metric)
        self._invalidate_cache(data.get("season_id", "s01"))

        return AnalyticsReport(
            report={
                "error_rate": 0.0,
                "avg_quality": metrics[MetricType.QUALITY_SCORE],
                "notes": [f"Metrics recorded for episode {episode.episode_number}"]
            }
        )

    def _generate_report(self, data: dict[str, Any]) -> AnalyticsReport:
        """Genera reporte analítico."""
        project_id = data.get("project_id", "proj_001")
        season_id = data.get("season_id", "s01")
        episode_ids = data.get("episode_ids", [])

        # Filtrar métricas relevantes
        relevant_metrics = self.episode_metrics
        if episode_ids:
            relevant_metrics = [m for m in relevant_metrics if m.episode_id in episode_ids]
        elif season_id:
            relevant_metrics = [m for m in relevant_metrics if m.season_id == season_id]
        elif project_id:
            relevant_metrics = [m for m in relevant_metrics if m.project_id == project_id]

        if not relevant_metrics:
            return AnalyticsReport(
                error_rate=0.0,
                avg_quality=0.0,
                notes=["No metrics available for report"]
            )

        # Calcular estadísticas
        quality_scores = [m.metrics.get(MetricType.QUALITY_SCORE, 0) for m in relevant_metrics]
        render_times = [m.metrics.get(MetricType.RENDER_TIME, 0) for m in relevant_metrics]
        regen_counts = [m.metrics.get(MetricType.REGENERATION_COUNT, 0) for m in relevant_metrics]
        costs = [m.metrics.get(MetricType.COST_USD, 0) for m in relevant_metrics]
        tokens = [m.metrics.get(MetricType.TOKEN_USAGE, 0) for m in relevant_metrics]

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        pass_count = sum(1 for q in quality_scores if q >= 70)
        error_rate = 1 - (pass_count / len(quality_scores)) if quality_scores else 0

        # Métricas de plataforma
        platform_aggregated = {}
        for m in relevant_metrics:
            for platform, p_metrics in m.platform_metrics.items():
                if platform not in platform_aggregated:
                    platform_aggregated[platform] = {k: [] for k in p_metrics}
                for k, v in p_metrics.items():
                    platform_aggregated[platform][k].append(v)

        platform_summary = {}
        for platform, pdata in platform_aggregated.items():
            platform_summary[platform] = {
                k: sum(v) / len(v) if v else 0 for k, v in pdata.items()
            }

        # Identificar dimensiones débiles
        weakest_dims = self._identify_weakest_dimensions(relevant_metrics)

        notes = [
            f"Episodios analizados: {len(relevant_metrics)}",
            f"Calidad promedio: {avg_quality:.1f}/100",
            f"Tasa de éxito QC: {pass_count}/{len(quality_scores)}",
            f"Tiempo promedio render: {sum(render_times)/len(render_times):.1f}s",
            f"Regeneraciones totales: {sum(regen_counts)}",
            f"Costo total: ${sum(costs):.2f}",
            f"Tokens totales: {sum(tokens)}",
            f"Plataformas: {list(platform_summary.keys())}",
            f"Dimensiones a mejorar: {', '.join(weakest_dims[:5])}"
        ]

        return AnalyticsReport(
            report={
                "error_rate": error_rate,
                "avg_quality": avg_quality,
                "notes": notes
            }
        )

    def _run_comparison(self, data: dict[str, Any]) -> AnalyticsReport:
        """Ejecuta análisis comparativo A/B."""
        experiment_id = data.get("experiment_id", f"exp_{int(time.time())}")
        variant_a = data.get("variant_a", "control")
        variant_b = data.get("variant_b", "treatment")
        metric_type = MetricType(data.get("metric", "quality_score"))
        sample_a = data.get("sample_a", [])
        sample_b = data.get("sample_b", [])

        if not sample_a or not sample_b:
            return AnalyticsReport(
                error_rate=1.0,
                avg_quality=0.0,
                notes=["Insufficient samples for comparison"]
            )

        # T-test simple (Welch's t-test)
        import statistics
        mean_a = statistics.mean(sample_a)
        mean_b = statistics.mean(sample_b)
        var_a = statistics.variance(sample_a) if len(sample_a) > 1 else 0
        var_b = statistics.variance(sample_b) if len(sample_b) > 1 else 0

        n_a, n_b = len(sample_a), len(sample_b)
        se = ((var_a / n_a) + (var_b / n_b)) ** 0.5 if (var_a + var_b) > 0 else 1
        t_stat = (mean_b - mean_a) / se if se > 0 else 0

        # Aproximación simple de p-value (two-tailed)
        df = n_a + n_b - 2
        p_value = 2 * (1 - abs(t_stat) / (abs(t_stat) + df ** 0.5)) if df > 0 else 1
        significant = p_value < 0.05

        lift = ((mean_b - mean_a) / mean_a * 100) if mean_a > 0 else 0

        # Confidence interval
        margin = 1.96 * se
        ci = (mean_b - mean_a - margin, mean_b - mean_a + margin)

        comp = ComparativeAnalytics(
            experiment_id=experiment_id,
            variant_a=variant_a,
            variant_b=variant_b,
            metric=metric_type,
            sample_a=sample_a,
            sample_b=sample_b,
            p_value=p_value,
            significant=significant,
            lift=lift,
            confidence_interval=ci
        )

        self.experiment_results.append(comp)

        notes = [
            f"Experimento: {experiment_id}",
            f"Variante A ({variant_a}): media={mean_a:.2f}, n={n_a}",
            f"Variante B ({variant_b}): media={mean_b:.2f}, n={n_b}",
            f"Lift: {lift:.1f}%",
            f"P-value: {p_value:.4f}",
            f"Significativo: {'Sí' if significant else 'No'}",
            f"IC 95%: [{ci[0]:.2f}, {ci[1]:.2f}]"
        ]

        return AnalyticsReport(
            report={
                "error_rate": 0.0 if significant else 0.5,
                "avg_quality": mean_b,
                "notes": notes
            }
        )

    def _analyze_trend(self, data: dict[str, Any]) -> AnalyticsReport:
        """Analiza tendencia de mejora a lo largo del tiempo."""
        project_id = data.get("project_id", "proj_001")
        season_id = data.get("season_id")
        window = data.get("window", 10)  # últimos N episodios

        relevant = [m for m in self.episode_metrics if m.project_id == project_id]
        if season_id:
            relevant = [m for m in relevant if m.season_id == season_id]

        relevant.sort(key=lambda x: x.timestamp)
        recent = relevant[-window:] if len(relevant) >= window else relevant

        if len(recent) < 3:
            return AnalyticsReport(
                error_rate=0.5,
                avg_quality=0.0,
                notes=["Insuficientes datos para análisis de tendencia (mín 3 episodios)"]
            )

        # Calcular pendiente de calidad
        quality_scores = [m.metrics.get(MetricType.QUALITY_SCORE, 0) for m in recent]
        x = list(range(len(quality_scores)))
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(quality_scores)
        sum_xy = sum(x[i] * quality_scores[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
        trend_pct = slope * 100 / (sum_y / n) if sum_y > 0 else 0

        # Tendencia de regeneraciones (deberían disminuir)
        regen_counts = [m.metrics.get(MetricType.REGENERATION_COUNT, 0) for m in recent]
        regen_slope = (n * sum(x[i] * regen_counts[i] for i in range(n)) - sum_x * sum(regen_counts)) / \
                      (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0

        notes = [
            f"Ventana analizada: {len(recent)} episodios",
            f"Tendencia calidad: {slope:.2f} pts/ep ({trend_pct:+.1f}%)",
            f"Tendencia regeneraciones: {regen_slope:.2f} regen/ep",
            f"Calidad actual: {quality_scores[-1]:.1f}",
            f"Mejora desde inicio: {quality_scores[-1] - quality_scores[0]:+.1f} pts",
            "Tendencia: " + ("MEJORANDO" if slope > 0.1 else "ESTABLE" if abs(slope) <= 0.1 else "EMPEORANDO")
        ]

        return AnalyticsReport(
            report={
                "error_rate": 0.0,
                "avg_quality": quality_scores[-1],
                "notes": notes
            }
        )

    def _identify_weakest_dimensions(self, metrics: list[EpisodeMetric]) -> list[str]:
        """Identifica dimensiones de calidad consistentemente bajas."""
        # En producción, esto analizaría los QualityReport detallados
        # Por ahora, devolvemos dimensiones comunes
        return [
            "micro_expresiones_presentes",
            "silencio_antes_revelacion",
            "foley_amplificado",
            "sub_bass_stinger",
            "formula_fraccional_aplicada"
        ]

    def _invalidate_cache(self, season_id: str) -> None:
        """Invalida cache de temporada."""
        if season_id in self.season_cache:
            del self.season_cache[season_id]

    def get_season_analytics(self, season_id: str) -> SeasonAnalytics | None:
        """Obtiene analíticas completas de temporada."""
        if season_id in self.season_cache:
            return self.season_cache[season_id]

        season_metrics = [m for m in self.episode_metrics if m.season_id == season_id]
        if not season_metrics:
            return None

        # Agregar métricas
        quality_scores = [m.metrics.get(MetricType.QUALITY_SCORE, 0) for m in season_metrics]
        render_times = [m.metrics.get(MetricType.RENDER_TIME, 0) for m in season_metrics]
        regen_counts = [m.metrics.get(MetricType.REGENERATION_COUNT, 0) for m in season_metrics]
        costs = [m.metrics.get(MetricType.COST_USD, 0) for m in season_metrics]
        tokens = [m.metrics.get(MetricType.TOKEN_USAGE, 0) for m in season_metrics]

        quality_dist = {"pass": 0, "fail": 0, "warning": 0}
        for q in quality_scores:
            if q >= 80:
                quality_dist["pass"] += 1
            elif q >= 60:
                quality_dist["warning"] += 1
            else:
                quality_dist["fail"] += 1

        # Top performing
        sorted_episodes = sorted(season_metrics, key=lambda m: m.metrics.get(MetricType.QUALITY_SCORE, 0), reverse=True)
        top_episodes = [m.episode_id for m in sorted_episodes[:3]]

        # Weakest dimensions
        weakest = self._identify_weakest_dimensions(season_metrics)

        # Tendencia de mejora
        season_metrics.sort(key=lambda x: x.episode_number)
        quality_trend = 0
        if len(season_metrics) >= 3:
            x = list(range(len(season_metrics)))
            y = [m.metrics.get(MetricType.QUALITY_SCORE, 0) for m in season_metrics]
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
            quality_trend = slope * 100 / (sum_y / n) if sum_y > 0 else 0

        analytics = SeasonAnalytics(
            season_id=season_id,
            project_id=season_metrics[0].project_id,
            total_episodes=len(season_metrics),
            avg_quality_score=sum(quality_scores) / len(quality_scores),
            quality_distribution=quality_dist,
            avg_render_time=sum(render_times) / len(render_times),
            total_regenerations=sum(regen_counts),
            total_cost_usd=sum(costs),
            total_tokens=sum(tokens),
            platform_performance={},
            top_performing_episodes=top_episodes,
            weakest_dimensions=weakest,
            improvement_trend=quality_trend
        )

        self.season_cache[season_id] = analytics
        return analytics

    def run(self, input_data: dict[str, Any]) -> AnalyticsReport:
        """Ejecuta el motor de analíticas."""
        return self.process(input_data)
