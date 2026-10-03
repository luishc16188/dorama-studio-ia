"""
QualityGateAgent – Evalúa los 15 puntos de la rúbrica y devuelve resultados
En producción debería usar criterios cuantificables T0‑T2
"""

from __future__ import annotations

import time
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.schemas.quality_gate_schemas import (
    QualityGateInput,
    QualityGateOutput,
)
from dorama_studio.core.persistence import persistence
from dorama_studio.core.pipeline_context import AgentResult

# Rúbrica simplificada por ejemplo, reemplazar con métricas realistas
ROUBLE_POINTS = [
    ("hook_0_3s", 20, "Hook con apertura explosiva en primeros 3s"),
    ("conflict", 15, "Conflicto definido"),
    ("protagonist_desire", 15, "Objetivo claro"),
    ("question", 15, "Pregunta abierta al final"),
    ("emotional_impact", 5, "Impacto emocional"),
    ("dialogue_quality", 5, "Diálogo con peso emocional"),
    ("show_dont_tell", 5, "Mostrar no contar"),
]


class QualityGateAgent(BaseAgent):
    InputSchema = QualityGateInput
    OutputSchema = QualityGateOutput

    def __init__(self):
        super().__init__("QualityGateAgent")
        self.agent_name = "QualityGateAgent"

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the quality gate agent."""
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

    def _process(self, context: Any) -> Any:
        start = time.time()
        try:
            # Handle both PipelineContext and QualityGateInput
            if hasattr(context, 'episode_id'):
                # It's a PipelineContext
                episode_id = context.episode_id or ""
                project_id = context.project_id or ""
                beat_names = getattr(context, "story_beat_names", [])
                motto = (
                    context.episode_blueprint.get("hook_category", "")
                    if hasattr(context, "episode_blueprint")
                    else ""
                )
                context_dict = context.to_dict() if hasattr(context, 'to_dict') else {}
                # Return AgentResult for PipelineContext
                return self._process_pipeline_context(
                    episode_id, project_id, beat_names, motto, context_dict, start
                )
            else:
                # It's a QualityGateInput or dict
                episode_num = getattr(context, 'episode_num', 1) or 1
                episode_score = getattr(context, 'episode_score', 0.0) or 0.0
                breakdown = getattr(context, 'breakdown', {}) or {}
                feedback = getattr(context, 'feedback', []) or []
                threshold = getattr(context, 'threshold', 85.0) or 85.0

                # Return QualityGateOutput for QualityGateInput
                return self._process_quality_gate_input(
                    episode_num, episode_score, breakdown, feedback, threshold, start
                )
        except Exception as e:
            # Return appropriate error response based on input type
            if hasattr(context, 'episode_id'):
                return AgentResult(
                    success=False,
                    agent_name=self.agent_name,
                    error=str(e),
                    recoverable=True,
                    latency_ms=int((time.time() - start) * 1000),
                )
            else:
                return QualityGateOutput(
                    verdict="ERROR",
                    passed=False,
                    score=0.0,
                    threshold=getattr(context, 'threshold', 85.0),
                    notes=[f"Processing error: {str(e)}"],
                    status="error"
                )

    def _process_pipeline_context(self, episode_id, project_id, beat_names, motto, context_dict, start):
        """Process PipelineContext and return AgentResult."""
        scored = {}
        for key, pts, desc in ROUBLE_POINTS:
            if key in beat_names or key in motto.lower():
                scored[key] = pts
            else:
                scored[key] = 0
        total = sum(scored.values())
        score = (total / 100) * 100
        passed = score >= 80

        for key, pts, _ in ROUBLE_POINTS:
            persistence.save_quality_gate(
                episode_id=episode_id,
                beat_id=None,
                dimension=key,
                score=scored[key],
                passed=pts if passed else 0,
                feedback="" if passed else "Revisar contenido",
            )

        log_id = persistence.log_generation(
            project_id=project_id,
            agent_name=self.agent_name,
            input_data={"context": context_dict},
            output_data={"quality_score": score, "passed": passed},
            model_used="quality_gates_stub",
            latency_ms=int((time.time() - start) * 1000),
            episode_id=episode_id,
        )

        return AgentResult(
            success=passed,
            agent_name=self.agent_name,
            output_data={"quality_score": score, "passed": passed},
            context_updates={},
            logs=[{"id": log_id}],
            latency_ms=int((time.time() - start) * 1000),
        )

    def _process_quality_gate_input(self, episode_num, episode_score, breakdown, feedback, threshold, start):
        """Process QualityGateInput and return QualityGateOutput."""
        # Use the episode_score directly if provided, otherwise calculate from breakdown
        score = episode_score if episode_score > 0 else sum(breakdown.values()) if breakdown else 0.0
        passed = score >= threshold
        verdict = "PASS" if passed else "FAIL"

        notes = list(feedback) if feedback else []
        if breakdown:
            notes.append(f"Breakdown: {breakdown}")

        return QualityGateOutput(
            verdict=verdict,
            passed=passed,
            score=score,
            threshold=threshold,
            notes=notes,
            status="completed" if passed else "failed"
        )
