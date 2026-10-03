"""
Selectively Regenerate Agent – Actúa después de un Quality Check.
Si el `QualityReport` devuelto contiene fallos, decide cuáles partes de la producción
deben re-generarse (ej. `RetentionEngine`-selective, `CliffhangerEngine`,
`DialoguePolisher` de los beats afectados) y lanza los agentes necesarios.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.narrative.cliffhanger_engine import CliffhangerEngineAgent
from dorama_studio.agents.narrative.retention_engine import RetentionEngineAgent
from dorama_studio.contracts.v2_schemas import EpisodeSpecV2, QualityReport

logger = logging.getLogger(__name__)


class SelectiveRegenerationAgent(BaseAgent[dict, dict]):
    """Lleva a cabo la regeneración selectiva de un episodio."""

    def __init__(self):
        super().__init__("SelectiveRegenerationAgent")
        self.retention_engine = RetentionEngineAgent()
        self.cliffhanger_engine = CliffhangerEngineAgent()

    def run(self, input_data: dict) -> dict:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, payload: dict) -> dict:
        report: QualityReport = payload.get("quality_report")
        episode: EpisodeSpecV2 = payload.get("episode")
        if not report or not episode:
            return {
                "status": "invalid_input",
                "message": "Missing quality_report or episode in payload",
            }
        # Simple policy: si fail, regen de retention y cliffhanger sobre el episodio
        if report.state == "fail":
            # Regenerar con las herramientas existentes
            retention_hay = self.retention_engine.process({"microbeats": episode.beats})
            cfft = self.cliffhanger_engine.process({"episode_blueprint": episode})
            # Integrar soluciones sugeridas (solo demo)
            return {
                "status": "regenerated",
                "retention": retention_hay,
                "cliffhanger": cfft,
            }
        return {
            "status": "no_action_needed",
            "quality_report": report,
        }
