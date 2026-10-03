"""
Claude Codex Collaboration Agent - Fase 15
Facilita la colaboración entre Claude (agente local) y Codex (agentes remotos/externos)
para tareas complejas que requieren múltiples perspectivas de IA.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *

logger = logging.getLogger(__name__)


class CollaborationMode(str, Enum):
    """Modos de colaboración entre Claude y Codex."""
    SEQUENTIAL = "sequential"      # Claude → Codex → Claude
    PARALLEL = "parallel"          # Claude y Codex trabajan en paralelo
    CONSENSUS = "consensus"        # Ambos trabajan y luego se ponen de acuerdo
    DEBATE = "debate"              # Debate estructurado entre IA
    PIPELINE = "pipeline"          # Claude prepara, Codex ejecuta, Claude revisa


class TaskComplexity(str, Enum):
    """Niveles de complejidad de tarea."""
    LOW = "low"                    # Tarea simple, un agente basta
    MEDIUM = "medium"              # Requiere dos perspectivas
    HIGH = "high"                  # Necesita debate o consenso
    EXPERT = "expert"              # Requiere múltiples iteraciones


@dataclass
class CollaborationRequest:
    """Solicitud de colaboración entre Claude y Codex."""
    task_id: str
    task_description: str
    task_type: str  # narrative, visual, audio, editing, etc.
    complexity: TaskComplexity
    mode: CollaborationMode
    context: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    priority: str = "medium"
    budget_category: str = "exploration"  # proven, exploration, big_bet


@dataclass
class CollaborationResult:
    """Resultado de una colaboración entre Claude y Codex."""
    task_id: str
    success: bool
    claude_output: Any = None
    codex_output: Any = None
    fused_output: Any = None
    collaboration_mode: CollaborationMode = CollaborationMode.SEQUENTIAL
    iterations: int = 1
    consensus_score: float = 0.0  # 0-1, qué tan alineados estuvieron
    latency_ms: int = 0
    cost_usd: float = 0.0
    notes: list[str] = field(default_factory=list)


class ClaudeCodexCollaborationAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Agente que facilita la colaboración entre Claude (local) y Codex (remoto/externo).
    Implementa patrones de trabajo colaborativo para tareas complejas de producción.
    """

    def __init__(self):
        super().__init__("ClaudeCodexCollaborationAgent")
        # En producción, aquí se inicializarían conexiones a APIs externas
        self.collaboration_history: list[CollaborationResult] = []
        self.performance_metrics: dict[str, Any] = {
            "total_collaborations": 0,
            "successful_collaborations": 0,
            "avg_latency_ms": 0,
            "avg_cost_usd": 0.0
        }

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Ejecuta colaboración entre Claude y Codex para una tarea dada.

        Args:
            validated_input: Dict con:
                - task_description: Descripción de la tarea a realizar
                - task_type: Tipo de tarea (narrative, visual, audio, etc.)
                - context: Contexto necesario para la tarea
                - collaboration_mode: Modo de colaboración (opcional, default=SEQUENTIAL)
                - complexity: Complejidad esperada (opcional, auto-detectada)
                - timeout_seconds: Timeout para la colaboración (default=300)
                - priority: Prioridad de la tarea (default=medium)

        Returns:
            Dict con resultados de la colaboración y métricas de rendimiento
        """
        task_description = validated_input.get("task_description", "")
        task_type = validated_input.get("task_type", "general")
        context = validated_input.get("context", {})
        mode_str = validated_input.get("collaboration_mode", "sequential")
        priority = validated_input.get("priority", "medium")
        timeout = validated_input.get("timeout_seconds", 300)

        # Determinar complejidad si no se proporciona
        complexity_str = validated_input.get("complexity")
        if not complexity_str:
            complexity_str = self._estimate_complexity(task_description, task_type, context)

        try:
            mode = CollaborationMode(mode_str)
            complexity = TaskComplexity(complexity_str)
        except ValueError as e:
            return {
                "status": "error",
                "message": f"Invalid collaboration mode or complexity: {e}",
                "task_id": f"collab_{int(time.time())}"
            }

        # Crear solicitud de colaboración
        collab_request = CollaborationRequest(
            task_id=f"collab_{int(time.time())}_{hash(task_description) % 10000}",
            task_description=task_description,
            task_type=task_type,
            complexity=complexity,
            mode=mode,
            context=context,
            timeout_seconds=timeout,
            priority=priority,
            budget_category=self._determine_budget_category(priority, complexity)
        )

        # Ejecutar colaboración basada en el modo
        start_time = time.time()
        result = self._execute_collaboration(collab_request)
        result.latency_ms = int((time.time() - start_time) * 1000)

        # Actualizar métricas de rendimiento
        self._update_performance_metrics(result)

        # Almacenar en historial
        self.collaboration_history.append(result)

        # Preparar respuesta
        response = {
            "status": "success" if result.success else "failed",
            "task_id": result.task_id,
            "collaboration_mode": result.collaboration_mode.value,
            "iterations": result.iterations,
            "consensus_score": result.consensus_score,
            "latency_ms": result.latency_ms,
            "cost_usd": result.cost_usd,
            "notes": result.notes
        }

        # Incluir outputs si existen
        if result.claude_output is not None:
            response["claude_output"] = result.claude_output
        if result.codex_output is not None:
            response["codex_output"] = result.codex_output
        if result.fused_output is not None:
            response["fused_output"] = result.fused_output

        return response

    def _estimate_complexity(
        self,
        task_description: str,
        task_type: str,
        context: dict[str, Any]
    ) -> str:
        """Estima la complejidad de una tarea basada en su descripción y contexto."""
        # Factores que aumentan complejidad
        complexity_indicators = [
            ("múltiple", "multiple", "various", "diverse"),
            ("complejo", "complex", "intricate", "sophisticated"),
            ("optimizar", "optimize", "refinar", "refine", "mejorar", "improve"),
            ("analizar", "analyze", "evaluar", "evaluate", "comparar", "compare"),
            ("crear", "create", "generar", "generate", "diseñar", "design"),
            ("integrar", "integrate", "combinar", "combine", "fusionar", "fuse"),
            ("depurar", "debug", "solucionar", "solve", "arreglar", "fix")
        ]

        # Factores que indican tareas simples
        simplicity_indicators = [
            ("simple", "basic", "straightforward", "direct"),
            ("listar", "list", "enumerar", "enumerate"),
            ("obtener", "get", "fetch", "retrieve", "consultar", "query"),
            ("mostrar", "show", "display", "visualizar", "visualize")
        ]

        text = (task_description + " " + str(context)).lower()

        complexity_score = 0
        simplicity_score = 0

        for indicators in complexity_indicators:
            if any(indicator in text for indicator in indicators):
                complexity_score += 1

        for indicators in simplicity_indicators:
            if any(indicator in text for indicator in indicators):
                simplicity_score += 1

        # Determinar complejidad basada en puntuación
        if complexity_score >= 3:
            return TaskComplexity.HIGH.value
        elif complexity_score >= 1 and simplicity_score == 0:
            return TaskComplexity.MEDIUM.value
        else:
            return TaskComplexity.LOW.value

    def _determine_budget_category(
        self,
        priority: str,
        complexity: str
    ) -> str:
        """Determina la categoría de presupuesto basada en prioridad y complejidad."""
        # Mapeo de prioridad + complejidad a categoría de presupuesto Creative Genome
        budget_mapping = {
            ("high", "high"): "big_bet",      # Alta prioridad + alta complejidad = experimento arriesgado
            ("high", "medium"): "proven",     # Alta prioridad + complejidad media = método probado
            ("high", "low"): "proven",        # Alta prioridad + baja complejidad = método probado
            ("medium", "high"): "exploration", # Media prioridad + alta complejidad = exploración
            ("medium", "medium"): "exploration", # Media ambas = exploración
            ("medium", "low"): "proven",      # Media prioridad + baja complejidad = probado
            ("low", "high"): "exploration",   # Baja prioridad + alta complejidad = exploración (riesgo controlado)
            ("low", "medium"): "exploration", # Baja ambas = exploración
            ("low", "low"): "proven"          # Baja ambas = método probado y seguro
        }

        return budget_mapping.get((priority, complexity), "exploration")

    def _execute_collaboration(
        self,
        request: CollaborationRequest
    ) -> CollaborationResult:
        """Ejecuta la colaboración basada en el modo solicitado."""
        result = CollaborationResult(
            task_id=request.task_id,
            success=False,
            collaboration_mode=request.mode
        )

        try:
            if request.mode == CollaborationMode.SEQUENTIAL:
                result = self._execute_sequential(request)
            elif request.mode == CollaborationMode.PARALLEL:
                result = self._execute_parallel(request)
            elif request.mode == CollaborationMode.CONSENSUS:
                result = self._execute_consensus(request)
            elif request.mode == CollaborationMode.DEBATE:
                result = self._execute_debate(request)
            elif request.mode == CollaborationMode.PIPELINE:
                result = self._execute_pipeline(request)
            else:
                # Default a secuencial
                result = self._execute_sequential(request)

            result.success = True

        except Exception as e:
            result.success = False
            result.notes.append(f"Collaboration failed: {str(e)}")
            logger.error(f"Collaboration execution failed: {e}")

        return result

    def _execute_sequential(
        self,
        request: CollaborationRequest
    ) -> CollaborationResult:
        """Ejecuta colaboración secuencial: Claude → Codex → Claude."""
        result = CollaborationResult(
            task_id=request.task_id,
            success=False,
            collaboration_mode=CollaborationMode.SEQUENTIAL
        )

        # Paso 1: Claude procesa la tarea inicial
        claude_start = time.time()
        claude_output = self._claude_process_task(request)
        claude_latency = int((time.time() - claude_start) * 1000)
        result.claude_output = claude_output

        # Paso 2: Codex revisa y mejora el output de Claude
        codex_start = time.time()
        codex_output = self._codex_improve_output(request, claude_output)
        codex_latency = int((time.time() - codex_start) * 1000)
        result.codex_output = codex_output

        # Paso 3: Claude integra las mejoras de Codex
        fused_start = time.time()
        fused_output = self._claude_integrate_improvements(request, claude_output, codex_output)
        fused_latency = int((time.time() - fused_start) * 1000)
        result.fused_output = fused_output

        # Calcular score de consenso (qué tan diferentes fueron los outputs)
        result.consensus_score = self._calculate_consensus(
            claude_output, codex_output, fused_output
        )
        result.iterations = 1  # Una pasada secuencial

        # Latencia y costo total
        result.latency_ms = claude_latency + codex_latency + fused_latency
        result.cost_usd = 0.0  # freellmapi = costo 0 local

        result.notes.extend([
            f"Claude processing: {claude_latency}ms",
            f"Codex improvement: {codex_latency}ms",
            f"Claude integration: {fused_latency}ms",
            f"Consensus score: {result.consensus_score:.2f}"
        ])

        return result

    def _execute_parallel(
        self,
        request: CollaborationRequest
    ) -> CollaborationResult:
        """Ejecuta colaboración paralela: Claude y Codex trabajan independientemente."""
        result = CollaborationResult(
            task_id=request.task_id,
            success=False,
            collaboration_mode=CollaborationMode.PARALLEL
        )

        # Ambos trabajan en paralelo en la misma tarea
        claude_start = time.time()
        claude_output = self._claude_process_task(request)
        claude_latency = int((time.time() - claude_start) * 1000)

        codex_start = time.time()
        codex_output = self._codex_process_task(request)  # Codex hace lo mismo que Claude
        codex_latency = int((time.time() - codex_start) * 1000)

        # Luego fusionamos los mejores aspectos
        fused_start = time.time()
        fused_output = self._fuse_parallel_outputs(request, claude_output, codex_output)
        fused_latency = int((time.time() - fused_start) * 1000)

        result.claude_output = claude_output
        result.codex_output = codex_output
        result.fused_output = fused_output
        result.consensus_score = self._calculate_consensus(
            claude_output, codex_output, fused_output
        )
        result.iterations = 1

        result.latency_ms = max(claude_latency, codex_latency) + fused_latency  # Paralelo = tiempo máximo
        result.cost_usd = 0.0

        result.notes.extend([
            f"Parallel Claude: {claude_latency}ms",
            f"Parallel Codex: {codex_latency}ms",
            f"Fusion: {fused_latency}ms",
            f"Consensus score: {result.consensus_score:.2f}"
        ])

        return result

    def _execute_consensus(
        self,
        request: CollaborationRequest
    ) -> CollaborationResult:
        """Ejecuta colaboración por consenso: iterar hasta acuerdo."""
        result = CollaborationResult(
            task_id=request.task_id,
            success=False,
            collaboration_mode=CollaborationMode.CONSENSUS
        )

        best_claude = None
        best_codex = None
        best_fused = None
        best_consensus = 0.0
        max_iterations = min(request.timeout_seconds // 30, 5)  # Máx 5 iteraciones o según timeout

        for iteration in range(max_iterations):
            # Claude propone
            claude_output = self._claude_process_task(request)

            # Codex propone independientemente
            codex_output = self._codex_process_task(request)

            # Intentamos fusionar y medir consenso
            fused_output = self._fuse_parallel_outputs(request, claude_output, codex_output)
            consensus_score = self._calculate_consensus(
                claude_output, codex_output, fused_output
            )

            # Guardamos la mejor iteración basada en consenso
            if consensus_score > best_consensus:
                best_consensus = consensus_score
                best_claude = claude_output
                best_codex = codex_output
                best_fused = fused_output

            # Si alcanzamos buen consenso, terminamos temprano
            if consensus_score >= 0.8:
                break

        result.claude_output = best_claude
        result.codex_output = best_codex
        result.fused_output = best_fused
        result.consensus_score = best_consensus
        result.iterations = iteration + 1

        # Latencia acumulada
        result.latency_ms = result.iterations * 2000  # Estimado ~2s por iteración
        result.cost_usd = 0.0

        result.notes.extend([
            f"Iterations: {result.iterations}",
            f"Best consensus: {result.consensus_score:.2f}",
            f"Early termination: {result.consensus_score >= 0.8}"
        ])

        return result

    def _execute_debate(
        self,
        request: CollaborationRequest
    ) -> CollaborationResult:
        """Ejecuta colaboración mediante debate estructurado."""
        result = CollaborationResult(
            task_id=request.task_id,
            success=False,
            collaboration_mode=CollaborationMode.DEBATE
        )

        # Estructura de debate: posición, réplica, réplica final
        debate_rounds = [
            ("posición_inicial", "Posiciones iniciales"),
            ("réplica", "Réplicas a las posiciones iniciales"),
            ("réplica_final", "Réplicas finales y conclusiones")
        ]

        claude_positions = []
        codex_positions = []

        for round_name, round_description in debate_rounds:
            # Claude presenta su posición
            claude_pos = self._claude_debate_round(request, round_name, round_description)
            claude_positions.append(claude_pos)

            # Codex responde/replica
            codex_pos = self._codex_debate_round(request, round_name, round_description)
            codex_positions.append(codex_pos)

        # Después del debate, sintetizamos la mejor posición
        fused_output = self._synthesize_debate_outcome(
            request, claude_positions, codex_positions
        )

        result.claude_output = claude_positions
        result.codex_output = codex_positions
        result.fused_output = fused_output
        result.consensus_score = self._calculate_debate_consensus(
            claude_positions, codex_positions
        )
        result.iterations = len(debate_rounds)

        result.latency_ms = len(debate_rounds) * 1500  # ~1.5s por ronda de debate
        result.cost_usd = 0.0

        result.notes.extend([
            f"Debate rounds: {len(debate_rounds)}",
            f"Rounds: {[r[0] for r in debate_rounds]}",
            f"Consensus score: {result.consensus_score:.2f}"
        ])

        return result

    def _execute_pipeline(
        self,
        request: CollaborationRequest
    ) -> CollaborationResult:
        """Ejecuta colaboración en pipeline: Claude prepara, Codex ejecuta, Claude revisa."""
        result = CollaborationResult(
            task_id=request.task_id,
            success=False,
            collaboration_mode=CollaborationMode.PIPELINE
        )

        # Etapa 1: Claude prepara el brief/plan detallado
        prep_start = time.time()
        claude_prep = self._claude_prepare_task(request)
        prep_latency = int((time.time() - prep_start) * 1000)

        # Etapa 2: Codex ejecuta basado en el brief de Claude
        exec_start = time.time()
        codex_exec = self._codex_execute_from_brief(request, claude_prep)
        exec_latency = int((time.time() - exec_start) * 1000)

        # Etapa 3: Claude revisa y aprueba el trabajo de Codex
        review_start = time.time()
        claude_review = self._claude_review_work(request, claude_prep, codex_exec)
        review_latency = int((time.time() - review_start) * 1000)

        result.claude_output = {
            "preparation": claude_prep,
            "review": claude_review
        }
        result.codex_output = codex_exec
        result.fused_output = claude_review  # El output final es lo aprobado por Claude

        # En pipeline, el consenso es qué tan bien aprobó Claude el trabajo
        result.consensus_score = self._calculate_approval_score(
            claude_prep, codex_exec, claude_review
        )
        result.iterations = 1

        result.latency_ms = prep_latency + exec_latency + review_latency
        result.cost_usd = 0.0

        result.notes.extend([
            f"Preparation: {prep_latency}ms",
            f"Execution: {exec_latency}ms",
            f"Review: {review_latency}ms",
            f"Approval score: {result.consensus_score:.2f}"
        ])

        return result

    # Métodos helper para simular el trabajo de Claude y Codex
    # En producción, estos harían llamadas reales a las APIs respectivas

    def _claude_process_task(self, request: CollaborationRequest) -> Any:
        """Simula el procesamiento de una tarea por Claude."""
        # En producción: llamada a Claude API con el contexto
        return {
            "agent": "claude",
            "task_type": request.task_type,
            "approach": "methodical_and_creative",
            "key_insights": [
                f"Idea principal para {request.task_type}",
                f"Consideración de contexto: {list(request.context.keys())[:3]}",
                "Enfoque balanceado entre creatividad y restricciones"
            ],
            "output_structure": "well_organized",
            "confidence": 0.8
        }

    def _codex_process_task(self, request: CollaborationRequest) -> Any:
        """Simula el procesamiento de una tarea por Codex."""
        # En producción: llamada a Codex API con el contexto
        return {
            "agent": "codex",
            "task_type": request.task_type,
            "approach": "technical_and_precise",
            "key_insights": [
                f"Implementación técnica para {request.task_type}",
                "Optimización de recursos y rendimiento",
                "Consideración de casos edge y robustez"
            ],
            "output_structure": "technically_sound",
            "confidence": 0.75
        }

    def _claude_improve_output(
        self,
        request: CollaborationRequest,
        codex_output: Any
    ) -> Any:
        """Claude mejora el output de Codex."""
        return {
            "agent": "claude_improving_codex",
            "base_output": codex_output,
            "improvements": [
                "Mejor flujo narrativo y coherencia",
                "Mayor enfoque en experiencia de usuario",
                "Mejor manejo de casos emocionales y narrativos"
            ],
            "final_quality": "enhanced"
        }

    def _codex_improve_output(
        self,
        request: CollaborationRequest,
        claude_output: Any
    ) -> Any:
        """Codex mejora el output de Claude."""
        return {
            "agent": "codex_improving_claude",
            "base_output": claude_output,
            "improvements": [
                "Mayor eficiencia técnica y rendimiento",
                "Mejor manejo de errores y casos edge",
                "Optimización de uso de recursos"
            ],
            "final_quality": "optimized"
        }

    def _claude_integrate_improvements(
        self,
        request: CollaborationRequest,
        claude_output: Any,
        codex_output: Any
    ) -> Any:
        """Claude integra las mejoras de Codex en su trabajo original."""
        return {
            "agent": "claude_final_integration",
            "claude_base": claude_output,
            "codex_improvements": codex_output.get("improvements", []) if isinstance(codex_output, dict) else [],
            "integrated_approach": "best_of_both_worlds",
            "quality_score": 0.85
        }

    def _fuse_parallel_outputs(
        self,
        request: CollaborationRequest,
        claude_output: Any,
        codex_output: Any
    ) -> Any:
        """Fusiona outputs paralelos de Claude y Codex."""
        return {
            "agent": "fused_claude_codex",
            "claude_perspective": claude_output,
            "codex_perspective": codex_output,
            "fusion_method": "weighted_average",
            "weights": {"claude": 0.6, "codex": 0.4},  # Claude ligeramente preferido para narrativa
            "combined_insights": list(set(
                (claude_output.get("key_insights", []) if isinstance(claude_output, dict) else []) +
                (codex_output.get("key_insights", []) if isinstance(codex_output, dict) else [])
            ))[:5],
            "quality_score": 0.82
        }

    def _claude_prepare_task(self, request: CollaborationRequest) -> Any:
        """Claude prepara un brief detallado para la tarea."""
        return {
            "agent": "claude_preparation",
            "task_brief": f"Detailed brief for {request.task_type}: {request.task_description}",
            "requirements": list(request.context.keys()),
            "constraints": ["time_limit", "quality_standards", "budget_limits"],
            "success_criteria": ["meets_objectives", "passes_quality_gates", "within_budget"],
            "creative_direction": "balanced_approach"
        }

    def _codex_execute_from_brief(
        self,
        request: CollaborationRequest,
        claude_brief: Any
    ) -> Any:
        """Codex ejecuta la tarea basado en el brief de Claude."""
        return {
            "agent": "codex_execution",
            "brief_source": "claude_preparation",
            "execution_approach": "systematic_and_precise",
            "technical_specs": {
                "methodology": "step_by_step_implementation",
                "quality_checks": ["unit_tests", "integration_checks"],
                "optimization_goals": ["performance", "memory_efficiency"]
            },
            "deliverables": ["working_solution", "documentation", "test_suite"],
            "readiness": "production_ready"
        }

    def _claude_review_work(
        self,
        request: CollaborationRequest,
        claude_brief: Any,
        codex_deliverable: Any
    ) -> Any:
        """Claude revisa el trabajo ejecutado por Codex."""
        approval_score = 0.8  # Base approval score

        # Ajustar basado en qué tan bien cumple con el brief
        if isinstance(claude_brief, dict) and isinstance(codex_deliverable, dict):
            brief_keys = set(claude_brief.get("requirements", []))
            deliverable_keys = set(codex_deliverable.get("deliverables", []))
            overlap = len(brief_keys & deliverable_keys) / len(brief_keys) if brief_keys else 0.5
            approval_score = 0.5 + (overlap * 0.5)  # Rango 0.5-1.0

        return {
            "agent": "claude_final_approval",
            "brief_reviewed": claude_brief,
            "work_reviewed": codex_deliverable,
            "approval_score": approval_score,
            "approved": approval_score >= 0.7,
            "feedback": [
                "Work meets technical specifications",
                "Minor improvements suggested in documentation",
                "Ready for production deployment"
            ] if approval_score >= 0.7 else [
                "Needs improvement in requirement coverage",
                "Requires additional testing",
                "Not ready for production yet"
            ],
            "final_decision": "approved" if approval_score >= 0.7 else "needs_revision"
        }

    def _synthesize_debate_outcome(
        self,
        request: CollaborationRequest,
        claude_positions: list[Any],
        codex_positions: list[Any]
    ) -> Any:
        """Sintetiza el resultado final de un debate entre Claude y Codex."""
        return {
            "agent": "debate_synthesis",
            "claude_arguments": claude_positions,
            "codex_arguments": codex_positions,
            "synthesis_method": "principle_based_integration",
            "core_principles_extracted": [
                "Maintain narrative coherence",
                "Ensure technical feasibility",
                "Optimize for audience engagement",
                "Minimize production risks"
            ],
            "final_position": "balanced_approach_that_addresses_both_perspectives",
            "quality_score": 0.88
        }

    def _calculate_consensus(
        self,
        claude_out: Any,
        codex_out: Any,
        fused_out: Any
    ) -> float:
        """Calcula qué tan de acuerdo estuvieron Claude y Codex."""
        # Simplificado: comparamos si hay elementos clave en común
        claude_set = set()
        codex_set = set()

        if isinstance(claude_out, dict):
            claude_set.update(claude_out.get("key_insights", []))
            claude_set.add(str(claude_out.get("approach", "")))
        if isinstance(codex_out, dict):
            codex_set.update(codex_out.get("key_insights", []))
            codex_set.add(str(codex_out.get("approach", "")))

        if not claude_set and not codex_set:
            return 0.5  # Neutral si no hay datos para comparar

        union = claude_set | codex_set
        intersection = claude_set & codex_set

        return len(intersection) / len(union) if union else 1.0

    def _calculate_debate_consensus(
        self,
        claude_positions: list[Any],
        codex_positions: list[Any]
    ) -> float:
        """Calcula consenso basado en convergencia a lo largo del debate."""
        # Simplificado: si las posiciones finales son más similares que las iniciales
        if not claude_positions or not codex_positions:
            return 0.5

        # Comparar primera vs última posición de cada agente
        claude_first = str(claude_positions[0]) if claude_positions else ""
        claude_last = str(claude_positions[-1]) if claude_positions else ""
        codex_first = str(codex_positions[0]) if codex_positions else ""
        codex_last = str(codex_positions[-1]) if codex_positions else ""

        # Medir cambio (cuanto más cambio, más interacción significativa hubo)
        claude_change = 1.0 - (len(set(claude_first) & set(claude_last)) / max(len(set(claude_first) | set(claude_last)), 1)) if claude_first or claude_last else 0.5
        codex_change = 1.0 - (len(set(codex_first) & set(codex_last)) / max(len(set(codex_first) | set(codex_last)), 1)) if codex_first or codex_last else 0.5

        # Consenso alto cuando ambos mostraron disposición a cambiar (indicando escucha)
        return min(claude_change, codex_change) + 0.3  # Base 0.3 + crédito por adaptación

    def _calculate_approval_score(
        self,
        claude_prep: Any,
        codex_exec: Any,
        claude_review: Any
    ) -> float:
        """Calcula cuán satisfecho está Claude con el trabajo de Codex."""
        if isinstance(claude_review, dict):
            return claude_review.get("approval_score", 0.5)
        return 0.5  # Default neutral

    def _update_performance_metrics(
        self,
        result: CollaborationResult
    ) -> None:
        """Actualiza métricas de rendimiento interno."""
        self.performance_metrics["total_collaborations"] += 1
        if result.success:
            self.performance_metrics["successful_collaborations"] += 1

        # Promedio móvil simple
        total = self.performance_metrics["total_collaborations"]
        current_avg_latency = self.performance_metrics["avg_latency_ms"]
        self.performance_metrics["avg_latency_ms"] = (
            (current_avg_latency * (total - 1) + result.latency_ms) / total
        )

        current_avg_cost = self.performance_metrics["avg_cost_usd"]
        self.performance_metrics["avg_cost_usd"] = (
            (current_avg_cost * (total - 1) + result.cost_usd) / total
        )

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Ejecuta el agente de colaboración Claude-Codex."""
        return self.process(input_data)


# Funciones de conveniencia
def collaborate_on_task(
    task_description: str,
    task_type: str = "general",
    context: dict[str, Any] | None = None,
    mode: str = "sequential",
    complexity: str | None = None,
    priority: str = "medium",
    timeout_seconds: int = 300
) -> dict[str, Any]:
    """
    Función de conveniencia para iniciar una colaboración Claude-Codex.
    """
    agent = ClaudeCodexCollaborationAgent()
    return agent.run({
        "task_description": task_description,
        "task_type": task_type,
        "context": context or {},
        "collaboration_mode": mode,
        "complexity": complexity,
        "priority": priority,
        "timeout_seconds": timeout_seconds
    })


def quick_collab(task_description: str) -> dict[str, Any]:
    """Colaboración rápida para tareas simples."""
    return collaborate_on_task(
        task_description=task_description,
        task_type="general",
        mode="sequential",
        priority="medium"
    )
