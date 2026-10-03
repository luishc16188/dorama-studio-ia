"""
Feedback Loop Agent v2 - Fase 14
Sistema de retroalimentación automatizada que convierte métricas y comentarios
en instrucciones accionables para mejora continua de la producción.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import (
    EpisodeSpecV2,
    QualityReport,
)
from dorama_studio.data.schemas import FeedbackInstructions

logger = logging.getLogger(__name__)


class FeedbackSource(str, Enum):
    """Fuentes de retroalimentación."""
    QUALITY_REPORT = "quality_report"
    ANALYTICS = "analytics"
    USER_COMMENT = "user_comment"
    A_B_TEST = "ab_test"
    REGENERATION_LOG = "regeneration_log"
    COST_ALERT = "cost_alert"
    LATENCY_ALERT = "latency_alert"


class FeedbackPriority(str, Enum):
    """Prioridad de la retroalimentación."""
    CRITICAL = "critical"      # Bloquea producción
    HIGH = "high"              # Afecta calidad significativamente
    MEDIUM = "medium"          # Mejora incremental
    LOW = "low"                # Optimización menor
    INFO = "info"              # Solo informativo


@dataclass
class FeedbackItem:
    """Item individual de retroalimentación."""
    source: FeedbackSource
    priority: FeedbackPriority
    dimension: str
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)
    suggested_action: str | None = None
    target_agent: str | None = None
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False


@dataclass
class FeedbackCluster:
    """Grupo de feedback relacionado por dimensión/agente."""
    dimension: str
    target_agent: str
    items: list[FeedbackItem] = field(default_factory=list)
    aggregated_priority: FeedbackPriority = FeedbackPriority.INFO
    consolidated_action: str | None = None


class FeedbackLoopV2(BaseAgent[dict[str, Any], FeedbackInstructions]):
    """
    Feedback Loop v2 - Sistema de retroalimentación inteligente que:
    1. Recopila feedback de múltiples fuentes (QC, analytics, usuarios, A/B tests)
    2. Agrupa y prioriza por dimensión y agente afectado
    3. Genera instrucciones específicas y accionables
    4. Rastrea resolución y cierra el ciclo
    5. Aprende patrones para predicción proactiva
    """

    def __init__(self):
        super().__init__("FeedbackLoopV2")
        self.feedback_history: list[FeedbackItem] = []
        self.active_clusters: dict[str, FeedbackCluster] = {}
        self.resolution_log: list[dict[str, Any]] = []

    def _process(self, validated_input: dict[str, Any]) -> FeedbackInstructions:
        """
        Procesa entrada de feedback y genera instrucciones.

        Args:
            validated_input: Dict con:
                - quality_report: QualityReport (opcional)
                - analytics_report: AnalyticsReport (opcional)
                - user_comments: List[str] (opcional)
                - ab_test_result: Dict (opcional)
                - cost_data: Dict (opcional)
                - latency_data: Dict (opcional)
                - episode: EpisodeSpecV2 (contexto)

        Returns:
            FeedbackInstructions con lista de instrucciones accionables
        """
        episode = validated_input.get("episode")
        all_feedback: list[FeedbackItem] = []

        # 1. Feedback desde Quality Report
        if quality_report := validated_input.get("quality_report"):
            all_feedback.extend(self._extract_from_quality_report(quality_report, episode))

        # 2. Feedback desde Analytics
        if analytics_report := validated_input.get("analytics_report"):
            all_feedback.extend(self._extract_from_analytics(analytics_report, episode))

        # 3. Feedback desde comentarios de usuario
        if user_comments := validated_input.get("user_comments"):
            all_feedback.extend(self._extract_from_user_comments(user_comments, episode))

        # 4. Feedback desde A/B test
        if ab_result := validated_input.get("ab_test_result"):
            all_feedback.extend(self._extract_from_ab_test(ab_result, episode))

        # 5. Feedback desde costos/latencia
        if cost_data := validated_input.get("cost_data"):
            all_feedback.extend(self._extract_from_cost_data(cost_data, episode))
        if latency_data := validated_input.get("latency_data"):
            all_feedback.extend(self._extract_from_latency_data(latency_data, episode))

        # Almacenar en historial
        self.feedback_history.extend(all_feedback)

        # Agrupar en clusters por agente/dimensión
        clusters = self._cluster_feedback(all_feedback)

        # Generar instrucciones consolidadas
        instructions = self._generate_instructions(clusters, episode)

        # Registrar clusters activos
        for cluster in clusters.values():
            self.active_clusters[cluster.dimension] = cluster

        return FeedbackInstructions(instructions=instructions)

    def _extract_from_quality_report(
        self, quality_report: QualityReport, episode: EpisodeSpecV2 | None
    ) -> list[FeedbackItem]:
        """Extrae feedback del reporte de calidad multimodal."""
        feedback = []

        if hasattr(quality_report, 'dimension_results'):
            for dim_result in quality_report.dimension_results:
                if not dim_result.passed:
                    priority = FeedbackPriority.HIGH if dim_result.score < 40 else FeedbackPriority.MEDIUM
                    feedback.append(FeedbackItem(
                        source=FeedbackSource.QUALITY_REPORT,
                        priority=priority,
                        dimension=dim_result.dimension.value,
                        message=dim_result.details,
                        evidence={"score": dim_result.score, "max_possible": 100},
                        suggested_action=dim_result.suggested_fix,
                        target_agent=self._map_dimension_to_agent(dim_result.dimension.value)
                    ))

        return feedback

    def _extract_from_analytics(
        self, analytics_report: Any, episode: EpisodeSpecV2 | None
    ) -> list[FeedbackItem]:
        """Extrae feedback del reporte de analíticas."""
        feedback = []

        if hasattr(analytics_report, 'notes'):
            for note in analytics_report.notes:
                # Parsear notas para detectar alertas
                if "tasa de éxito" in note.lower() and "0/" in note:
                    feedback.append(FeedbackItem(
                        source=FeedbackSource.ANALYTICS,
                        priority=FeedbackPriority.CRITICAL,
                        dimension="overall_qc_pass_rate",
                        message=note,
                        evidence={"analytics_note": note},
                        suggested_action="Revisar pipeline completo - tasa de éxito QC en 0%",
                        target_agent="PipelineOrchestrator"
                    ))
                elif "regeneraciones" in note.lower():
                    # Extraer número
                    import re
                    match = re.search(r'(\d+)', note)
                    if match and int(match.group(1)) > 3:
                        feedback.append(FeedbackItem(
                            source=FeedbackSource.ANALYTICS,
                            priority=FeedbackPriority.HIGH,
                            dimension="excessive_regeneration",
                            message=note,
                            evidence={"regeneration_count": int(match.group(1))},
                            suggested_action="Investigar causa raíz de fallos recurrentes en QC",
                            target_agent="SelectiveRegenerationOrchestrator"
                        ))

        return feedback

    def _extract_from_user_comments(
        self, comments: list[str], episode: EpisodeSpecV2 | None
    ) -> list[FeedbackItem]:
        """Extrae feedback de comentarios de usuarios."""
        feedback = []

        # Palabras clave que indican problemas específicos
        keyword_mapping = {
            "visual": ["pixelado", "borroso", "artefactos", "inconsistente", "cambio de cara"],
            "audio": ["audio bajo", "ruido", "desincronizado", "eco", "distorsión"],
            "ritmo": ["lento", "aburrido", "arrastrado", "rápido", "confuso"],
            "historia": ["inverosímil", "agujero", "no entiendo", "predecible", "cliché"],
            "subtítulos": ["subtítulo", "letra", "tamaño", "velocidad lectura", "desincronizado"]
        }

        for comment in comments:
            comment_lower = comment.lower()
            matched_dimensions = []

            for dim, keywords in keyword_mapping.items():
                if any(kw in comment_lower for kw in keywords):
                    matched_dimensions.append(dim)

            if matched_dimensions:
                for dim in matched_dimensions:
                    feedback.append(FeedbackItem(
                        source=FeedbackSource.USER_COMMENT,
                        priority=FeedbackPriority.MEDIUM,
                        dimension=dim,
                        message=f"Comentario usuario: {comment[:100]}",
                        evidence={"full_comment": comment},
                        suggested_action=self._get_user_feedback_action(dim),
                        target_agent=self._map_dimension_to_agent(dim)
                    ))

        return feedback

    def _extract_from_ab_test(
        self, ab_result: dict, episode: EpisodeSpecV2 | None
    ) -> list[FeedbackItem]:
        """Extrae feedback de resultados A/B test."""
        feedback = []

        if not ab_result.get("significant", False):
            feedback.append(FeedbackItem(
                source=FeedbackSource.A_B_TEST,
                priority=FeedbackPriority.LOW,
                dimension="ab_test_inconclusive",
                message=f"Test A/B no significativo: p={ab_result.get('p_value', 1):.4f}",
                evidence=ab_result,
                suggested_action="Aumentar tamaño de muestra o probar variante más distinta",
                target_agent="AnalyticsEngineV2"
            ))
        elif ab_result.get("lift", 0) < 0:
            feedback.append(FeedbackItem(
                source=FeedbackSource.A_B_TEST,
                priority=FeedbackPriority.MEDIUM,
                dimension="ab_test_negative_lift",
                message=f"Variante B peor que control: lift={ab_result.get('lift', 0):.1f}%",
                evidence=ab_result,
                suggested_action="Descartar variante B, analizar por qué falló",
                target_agent="AnalyticsEngineV2"
            ))

        return feedback

    def _extract_from_cost_data(
        self, cost_data: dict, episode: EpisodeSpecV2 | None
    ) -> list[FeedbackItem]:
        """Extrae feedback de datos de costo."""
        feedback = []

        cost_usd = cost_data.get("total_cost_usd", 0)
        budget_limit = cost_data.get("budget_limit_usd", 10000)

        if cost_usd > budget_limit:
            feedback.append(FeedbackItem(
                source=FeedbackSource.COST_ALERT,
                priority=FeedbackPriority.HIGH,
                dimension="budget_exceeded",
                message=f"Costo ${cost_usd:.2f} excede presupuesto ${budget_limit:.2f}",
                evidence=cost_data,
                suggested_action="Optimizar uso de modelos (usar fallbacks), reducir regeneraciones",
                target_agent="ModelRouter"
            ))
        elif cost_usd > budget_limit * 0.8:
            feedback.append(FeedbackItem(
                source=FeedbackSource.COST_ALERT,
                priority=FeedbackPriority.MEDIUM,
                dimension="budget_warning",
                message=f"Costo ${cost_usd:.2f} al {cost_usd/budget_limit*100:.0f}% del presupuesto",
                evidence=cost_data,
                suggested_action="Monitorear gastos, considerar optimizaciones",
                target_agent="ModelRouter"
            ))

        return feedback

    def _extract_from_latency_data(
        self, latency_data: dict, episode: EpisodeSpecV2 | None
    ) -> list[FeedbackItem]:
        """Extrae feedback de datos de latencia."""
        feedback = []

        avg_latency = latency_data.get("avg_latency_ms", 0)
        threshold = latency_data.get("threshold_ms", 30000)

        if avg_latency > threshold:
            feedback.append(FeedbackItem(
                source=FeedbackSource.LATENCY_ALERT,
                priority=FeedbackPriority.HIGH,
                dimension="latency_exceeded",
                message=f"Latencia {avg_latency:.0f}ms excede umbral {threshold}ms",
                evidence=latency_data,
                suggested_action="Usar modelos más rápidos, paralelizar llamadas, cachear prompts",
                target_agent="ModelRouter"
            ))

        return feedback

    def _map_dimension_to_agent(self, dimension: str) -> str:
        """Mapea dimensión a agente responsable."""
        mapping = {
            "hook_0_3s": "HookEngineAgent",
            "conflicto_concreto": "StoryArchitectAgent",
            "protagonista_deseo_claro": "CharacterDirectorAgent",
            "pregunta_abierta": "CliffhangerEngineAgent",
            "situacion_empeora": "RetentionEngineAgent",
            "respuesta_parcial": "MasterWriterAgent",
            "elemento_sorpresa": "OriginalityEngineAgent",
            "cliffhanger_fuerte": "CliffhangerEngineAgent",
            "impacto_emocional": "RetentionEngineAgent",
            "show_dont_tell": "DialoguePolisherAgent",
            "dialogo_avanza_historia": "DialoguePolisherAgent",
            "dialogo_delivery_presente": "VoiceDirectorAgent",
            "micro_expresiones_presentes": "ActingMotionPlannerAgent",
            "silencio_antes_revelacion": "AudioEngineerAgent",
            "formula_fraccional_aplicada": "StoryArchitectAgent",
            "resolucion_correcta": "VideoAgent",
            "frame_rate_correcto": "VideoAgent",
            "duracion_shots_valida": "EditorAgent",
            "consistencia_visual": "VisualDirectorAgent",
            "prompt_ast_unico": "PromptCompiler",
            "mezcla_balanceada": "AudioEngineerAgent",
            "silencio_critico": "AudioEngineerAgent",
            "foley_amplificado": "AudioEngineerAgent",
            "sub_bass_stinger": "AudioEngineerAgent",
            "music_progression": "MusicSupervisorAgent",
            "continuidad_personajes": "CharacterDirectorAgent",
            "continuidad_localizaciones": "LocationBibleAgent",
            "continuidad_objetos": "ContinuityLockAgent",
            "continuidad_tiempo": "ContinuityLockAgent",
            "formato_plataforma": "VideoAgent",
            "aspect_ratio_correcto": "VideoAgent",
            "safe_zones_respetadas": "PromptCompiler",
            "visual": "VisualDirectorAgent",
            "audio": "AudioEngineerAgent",
            "ritmo": "RetentionEngineAgent",
            "historia": "StoryArchitectAgent",
            "subtítulos": "SubtitleAgent",
            "overall_qc_pass_rate": "PipelineOrchestrator",
            "excessive_regeneration": "SelectiveRegenerationOrchestrator",
            "budget_exceeded": "ModelRouter",
            "budget_warning": "ModelRouter",
            "latency_exceeded": "ModelRouter",
            "ab_test_inconclusive": "AnalyticsEngineV2",
            "ab_test_negative_lift": "AnalyticsEngineV2",
        }
        return mapping.get(dimension, "PipelineOrchestrator")

    def _get_user_feedback_action(self, dimension: str) -> str:
        """Obtiene acción sugerida para feedback de usuario."""
        actions = {
            "visual": "Revisar consistency locks y regenerar shots con referencias de personaje",
            "audio": "Verificar mezcla, niveles y sincronización en AudioEngineerAgent",
            "ritmo": "Ajustar micro-beats y añadir pattern interrupts via RetentionEngineAgent",
            "historia": "Revisar estructura narrativa y giros con StoryArchitectAgent",
            "subtítulos": "Ajustar timing, tamaño y posición en SubtitleAgent"
        }
        return actions.get(dimension, "Investigar feedback de usuario y ajustar agente correspondiente")

    def _cluster_feedback(self, feedback_items: list[FeedbackItem]) -> dict[str, FeedbackCluster]:
        """Agrupa feedback por dimensión/agente."""
        clusters: dict[str, FeedbackCluster] = {}

        for item in feedback_items:
            key = f"{item.target_agent}:{item.dimension}"
            if key not in clusters:
                clusters[key] = FeedbackCluster(
                    dimension=item.dimension,
                    target_agent=item.target_agent
                )

            cluster = clusters[key]
            cluster.items.append(item)

            # Actualizar prioridad agregada (tomar la máxima)
            priority_order = {
                FeedbackPriority.CRITICAL: 4,
                FeedbackPriority.HIGH: 3,
                FeedbackPriority.MEDIUM: 2,
                FeedbackPriority.LOW: 1,
                FeedbackPriority.INFO: 0
            }
            if priority_order[item.priority] > priority_order[cluster.aggregated_priority]:
                cluster.aggregated_priority = item.priority

        # Consolidar acción por cluster
        for cluster in clusters.values():
            cluster.consolidated_action = self._consolidate_actions(cluster)

        return clusters

    def _consolidate_actions(self, cluster: FeedbackCluster) -> str:
        """Consolida acciones para un cluster."""
        actions = [item.suggested_action for item in cluster.items if item.suggested_action]
        unique_actions = list(dict.fromkeys(actions))  # Preservar orden, eliminar duplicados

        if not unique_actions:
            return f"Revisar {cluster.dimension} en {cluster.target_agent}"

        if len(unique_actions) == 1:
            return unique_actions[0]

        return f"ACCIONES MÚLTIPLES para {cluster.target_agent}: " + " | ".join(unique_actions)

    def _generate_instructions(
        self, clusters: dict[str, FeedbackCluster], episode: EpisodeSpecV2 | None
    ) -> list[str]:
        """Genera instrucciones finales a partir de clusters."""
        instructions = []

        # Ordenar por prioridad
        priority_order = {
            FeedbackPriority.CRITICAL: 0,
            FeedbackPriority.HIGH: 1,
            FeedbackPriority.MEDIUM: 2,
            FeedbackPriority.LOW: 3,
            FeedbackPriority.INFO: 4
        }

        sorted_clusters = sorted(
            clusters.values(),
            key=lambda c: priority_order[c.aggregated_priority]
        )

        for cluster in sorted_clusters:
            prefix = {
                FeedbackPriority.CRITICAL: "🔴 CRÍTICO",
                FeedbackPriority.HIGH: "🟠 ALTO",
                FeedbackPriority.MEDIUM: "🟡 MEDIO",
                FeedbackPriority.LOW: "🟢 BAJO",
                FeedbackPriority.INFO: "ℹ️ INFO"
            }[cluster.aggregated_priority]

            instruction = f"{prefix} [{cluster.target_agent}] {cluster.consolidated_action}"
            instructions.append(instruction)

        # Añadir resumen
        total_items = sum(len(c.items) for c in clusters.values())
        critical_count = sum(1 for c in clusters.values() if c.aggregated_priority == FeedbackPriority.CRITICAL)
        high_count = sum(1 for c in clusters.values() if c.aggregated_priority == FeedbackPriority.HIGH)

        summary = f"Resumen: {total_items} items de feedback → {len(clusters)} clusters | Críticos: {critical_count} | Altos: {high_count}"
        instructions.append(summary)

        return instructions

    def mark_resolved(self, dimension: str, action_taken: str, result: str) -> None:
        """Marca un cluster como resuelto."""
        if dimension in self.active_clusters:
            cluster = self.active_clusters[dimension]
            for item in cluster.items:
                item.resolved = True

            self.resolution_log.append({
                "dimension": dimension,
                "target_agent": cluster.target_agent,
                "action_taken": action_taken,
                "result": result,
                "timestamp": time.time(),
                "items_resolved": len(cluster.items)
            })

            del self.active_clusters[dimension]

    def get_unresolved_feedback(self) -> list[FeedbackItem]:
        """Obtiene feedback no resuelto."""
        return [item for item in self.feedback_history if not item.resolved]

    def get_feedback_stats(self) -> dict[str, Any]:
        """Estadísticas de feedback."""
        total = len(self.feedback_history)
        resolved = sum(1 for f in self.feedback_history if f.resolved)

        by_source = {}
        by_priority = {}
        for f in self.feedback_history:
            by_source[f.source.value] = by_source.get(f.source.value, 0) + 1
            by_priority[f.priority.value] = by_priority.get(f.priority.value, 0) + 1

        return {
            "total": total,
            "resolved": resolved,
            "unresolved": total - resolved,
            "resolution_rate": resolved / total if total > 0 else 0,
            "by_source": by_source,
            "by_priority": by_priority,
            "active_clusters": len(self.active_clusters)
        }

    def run(self, input_data: dict[str, Any]) -> FeedbackInstructions:
        """Ejecuta el feedback loop."""
        return self.process(input_data)
