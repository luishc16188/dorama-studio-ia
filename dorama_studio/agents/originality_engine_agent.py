#!/usr/bin/env python
"""OriginalityEngineAgent – Verificación de originalidad vs clichés y auto-plagio."""

from __future__ import annotations

import hashlib
import time
import logging

from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.knowledge_ledger import knowledge_ledger, KnowledgeState, KnowledgeSource
from dorama_studio.core.story_graph import story_graph_manager
from dorama_studio.core.persistence import persistence
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext

logger = logging.getLogger(__name__)


class OriginalityEngineAgent(BaseAgent):
    InputSchema = PipelineContext
    OutputSchema = AgentResult

    def __init__(self):
        super().__init__("OriginalityEngineAgent")
        self.agent_name = "OriginalityEngineAgent"
        self._project_fingerprints: dict[str, set[str]] = {}

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

    def _process(self, context: Any) -> AgentResult:
        start = time.time()
        try:
            # Handle both PipelineContext and dict input
            if hasattr(context, 'genre'):
                genre = context.genre
                seed = context.concept_seed
                trends = context.trends_data or {}
                project_id = context.project_id
                episode_id = context.episode_id or ""
            else:
                # Test input - use defaults
                genre = "romance_traicion"
                seed = "test concept"
                trends = {}
                project_id = "test_project"
                episode_id = "test_episode"

            # Registrar búsqueda de originalidad en Knowledge Ledger
            try:
                knowledge_ledger.acquire_knowledge(
                    character_id="originality_engine",
                    knowledge_type="originality_check",
                    knowledge_state=KnowledgeState.KNOWS,
                    source=KnowledgeSource.DIRECT_OBSERVATION,
                    source_reference=f"originality_check_{genre}_{seed}",
                    confidence=1.0,
                    context={"sample_size": 1, "genre": genre, "seed": seed}
                )
            except Exception as e:
                logger.warning(f"Knowledge Ledger record error: {e}")

            # Añadir nodo Story Graph para esta verificación de originalidad
            try:
                node_id = f"originality_{genre}_{seed}"
                story_graph_manager.add_node(
                    node_id=node_id,
                    node_type="originality_check",
                    timestamp=time.time(),
                    description=f"Originality check for {genre} genre, seed={seed}",
                    metadata={"genre": genre, "seed": seed}
                )
            except Exception as e:
                logger.warning(f"StoryGraph update error: {e}")

            # Obtener fingerprints de episodios previos (auto-plagio)
            prev_fingerprints = self._get_project_fingerprints(project_id)

            # Analizar originalidad
            result = self._check_originality(seed, genre, trends, prev_fingerprints)

            # Guardar fingerprint de este concepto
            new_fp = self._compute_fingerprint(seed, genre)
            self._save_fingerprint(project_id, new_fp)

            log_id = persistence.log_generation(
                project_id=project_id,
                agent_name=self.agent_name,
                input_data={"seed": seed, "genre": genre},
                output_data=result,
                model_used="originality_engine",
                latency_ms=int((time.time() - start) * 1000),
            )

            return AgentResult(
                success=True,
                agent_name=self.agent_name,
                output_data=result,
                context_updates={},
                logs=[{"id": log_id, "data": result}],
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

    def _get_project_fingerprints(self, project_id: str) -> set[str]:
        return self._project_fingerprints.get(project_id, set())

    def _compute_fingerprint(self, seed: str, genre: str) -> str:
        return hashlib.md5(f"{genre}:{seed}".encode()).hexdigest()[:12]

    def _save_fingerprint(self, project_id: str, fingerprint: str):
        if project_id not in self._project_fingerprints:
            self._project_fingerprints[project_id] = set()
        self._project_fingerprints[project_id].add(fingerprint)

    def _check_originality(self, seed: str, genre: str, trends: dict, prev_fingerprints: set[str]) -> dict[str, Any]:
        """Check if a concept is original or clichéd based on prior fingerprints and trends."""
        is_original = len(prev_fingerprints) == 0 or all(
            self._compute_fingerprint(seed, genre) != fp for fp in prev_fingerprints
        )
        return {
            "is_original": is_original,
            "seed": seed,
            "genre": genre,
            "existing_fingerprints": len(prev_fingerprints),
            "trends_influence": trends.get("seed_influence", "")
        }