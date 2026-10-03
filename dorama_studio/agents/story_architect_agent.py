"""
StoryArchitectAgent – Genera arcos y personajes de forma dinámica (sin LLM).
"""

from __future__ import annotations

import random
import time
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.core.persistence import persistence
from dorama_studio.core.pipeline_context import AgentResult, PipelineContext

# Códigos de arcos básicos por género (pueden ampliar.)
ARCS_BY_GENRE = {
    "romance_traicion": [
        {
            "arc": "Traición y redención",
            "beats": ["hook", "conflict", "twist", "cliffhanger", "cta"],
        },
        {
            "arc": "Reconciliación perdida",
            "beats": ["hook", "remorse", "reunion", "cliffhanger", "cta"],
        },
    ],
    "thriller_misterio": [
        {
            "arc": "Desenlace inesperado",
            "beats": ["hook", "investigation", "revealed_secret", "cliffhanger", "cta"],
        },
    ],
    "fantasia_épica": [
        {
            "arc": "Lucha por el reino",
            "beats": ["hook", "rise", "battle", "cliffhanger", "cta"],
        },
    ],
}


class StoryArchitectAgent(BaseAgent):
    InputSchema = PipelineContext
    OutputSchema = AgentResult

    def __init__(self):
        super().__init__("StoryArchitectAgent")
        self.agent_name = "StoryArchitectAgent"
        # En producción se cargarían los templates de arcos y beat desde DB

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the story architect agent."""
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
            genre = context.genre
            episode_num = context.episode_num
            # Selección aleatoria de arc dentro del género
            arcs = ARCS_BY_GENRE.get(genre, [{}])
            chosen_arc = random.choice(arcs)
            arc_name = chosen_arc.get("arc", "unknown_arc")
            beats_template = chosen_arc.get("beats", [])

            # Generar un blueprint simplificado con 9 beats (ejemplo)
            blueprint = {
                "episode": episode_num,
                "hook_category": random.choice(["exposición", "revelación", "mistake"]),
                "core_conflict": f"Comunita + {arc_name}",
                "twist": f"El truco de {arc_name.lower()}",
                "cliffhanger": "¿Qué ocurrirá al final?",
                "cta_type": "MORAL_DILEMMA",
                "character_bible": [],  # Se llenará después por CharacterDirector
            }

            # Persistir arcos en tabla `episodes` (beat_id será 0 …) como metadata
            # Aún no hay `arc_id`, pero almacenar en `metadata_json`
            # para usarlo más tarde en los agentes de continuidad

            # Actualiza contexto
            context_updates = {
                "episode_blueprint": blueprint,
                "story_arc_name": arc_name,
                "story_beat_names": beats_template,
            }

            log_id = persistence.log_generation(
                project_id=context.project_id,
                agent_name=self.agent_name,
                input_data={"genre": genre, "episode_num": episode_num},
                output_data=blueprint,
                model_used="generated_arcs_stub",
                latency_ms=int((time.time() - start) * 1000),
                episode_id=context.episode_id or "",
            )

            return AgentResult(
                success=True,
                agent_name=self.agent_name,
                output_data=blueprint,
                context_updates=context_updates,
                logs=[{"id": log_id, "json": blueprint}],
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


# Generaremos personajes usando CharacterDirector (stub) por ahora
# En producción se usaría a CharacterDirectorAgent - se deja el stub
