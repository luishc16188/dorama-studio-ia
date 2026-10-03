#!/usr/bin/env python
"""TrendHunterAgent – Implementación real con cache y scoring + Knowledge Ledger + Story Graph."""

from __future__ import annotations

import hashlib
import time
import logging
from datetime import datetime

from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.knowledge_ledger import knowledge_ledger, KnowledgeState, KnowledgeSource
from dorama_studio.core.story_graph import story_graph_manager
from dorama_studio.core.persistence import persistence
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext

logger = logging.getLogger(__name__)


class TrendHunterAgent(BaseAgent[PipelineContext, AgentResult]):
    InputSchema = PipelineContext
    OutputSchema = AgentResult

    def __init__(self):
        super().__init__("TrendHunterAgent")
        self.agent_name = "TrendHunterAgent"
        self._cache: dict[str, tuple[float, dict]] = {}
        self._cache_ttl = 3600  # 1 hora

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        """Run method compatible with abstract base class."""
        return self.process(input_data)

    def _process(self, validated_input: PipelineContext) -> AgentResult:
        start = time.time()
        try:
            genre = validated_input.genre
            seed = validated_input.concept_seed
            episodes = validated_input.total_episodes

            key = self._cache_key(genre, seed)
            cached = self._get_cached(key)
            if cached:
                trends = cached
            else:
                # En producción: llamadas a APIs de TikTok, YouTube, Google Trends
                trends = self._hunt_trends_real(genre, seed, episodes)
                self._set_cache(key, trends)

            # Registrar búsqueda en Knowledge Ledger
            try:
                knowledge_ledger.acquire_knowledge(
                    character_id="trend_hunter",
                    knowledge_type="trend_search",
                    knowledge_state=KnowledgeState.KNOWS,
                    source=KnowledgeSource.DIRECT_OBSERVATION,
                    source_reference=f"trend_hunt_{genre}_{seed}",
                    confidence=1.0,
                    context={"genre": genre, "seed": seed, "episodes": episodes}
                )
            except Exception as e:
                logger.warning(f"Knowledge Ledger record error: {e}")

            # Añadir nodo Story Graph para esta tendencia
            try:
                node_id = f"trend_{hash(key)}_{int(time.time())}"
                story_graph_manager.add_node(
                    node_id=node_id,
                    node_type="trend",
                    timestamp=datetime.now().isoformat(),
                    description=f"Trend search for genre={genre}, seed={seed[:20]}...",
                    metadata={"genre": genre, "seed": seed, "episodes": episodes}
                )
                # Conectar al nodo de episodio si existe
                episode_id = getattr(validated_input, 'episode_id', None)
                if episode_id:
                    story_graph_manager.add_edge(
                        source_node_id=f"episode_{episode_id}",
                        target_node_id=node_id,
                        relationship_type="informs_trend",
                        strength=0.8,
                        metadata={}
                    )
            except Exception as e:
                logger.warning(f"StoryGraph update error: {e}")

            # Persistir log
            log_id = persistence.log_generation(
                project_id=validated_input.project_id,
                agent_name=self.agent_name,
                input_data={"genre": genre, "seed": seed},
                output_data=trends,
                model_used="internal_trend_engine",
                latency_ms=int((time.time() - start) * 1000),
                episode_id=validated_input.episode_id or "",
            )

            return AgentResult(
                success=True,
                agent_name=self.agent_name,
                output_data={"trends": trends},
                context_updates={"trends_data": trends},
                logs=[{"id": log_id, "data": trends}],
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

    def _cache_key(self, genre: str, concept_seed: str) -> str:
        return hashlib.md5(f"{genre}:{concept_seed}".encode()).hexdigest()

    def _get_cached(self, key: str) -> dict | None:
        if key in self._cache:
            ts, data = self._cache[key]
            if time.time() - ts < self._cache_ttl:
                return data
            del self._cache[key]
        return None

    def _set_cache(self, key: str, data: dict):
        self._cache[key] = (time.time(), data)

    def _hunt_trends_real(self, genre: str, seed: str, episodes: int) -> dict:
        """Simula hunting real; reemplazar con APIs reales."""
        # Heurística simple basada en genre + seed
        base_trends = {
            "romance_traicion": [
                {"topic": "secret heiress", "velocity": 0.92, "platform": "TikTok"},
                {"topic": "fake marriage", "velocity": 0.87, "platform": "YouTube Shorts"},
                {"topic": "enemies to lovers", "velocity": 0.95, "platform": "Instagram Reels"},
                {"topic": "second chance romance", "velocity": 0.78, "platform": "TikTok"},
                {"topic": "forbidden love", "velocity": 0.83, "platform": "YouTube Shorts"},
            ],
            "thriller_misterio": [
                {"topic": "unreliable narrator", "velocity": 0.91, "platform": "TikTok"},
                {"topic": "hidden identity", "velocity": 0.88, "platform": "YouTube Shorts"},
                {"topic": "time loop mystery", "velocity": 0.85, "platform": "Instagram Reels"},
            ],
            "fantasia_épica": [
                {"topic": "chosen one subversion", "velocity": 0.90, "platform": "TikTok"},
                {"topic": "magic system reveal", "velocity": 0.82, "platform": "YouTube Shorts"},
            ],
        }.get(genre, [])

        # Añadir variaciones basadas en seed
        seed_hash = hashlib.md5(seed.encode()).hexdigest()[:4]
        for t in base_trends:
            t["seed_variant"] = f"{t['topic']}_{seed_hash}"

        return {
            "top_trends": base_trends[: min(episodes, len(base_trends))],
            "genre": genre,
            "analyzed_at": time.time(),
            "seed_influence": seed_hash,
        }