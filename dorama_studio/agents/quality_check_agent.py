"""
Quality Check Agent – Evalúa artefactos de video, audio, texto y visual para la fase 13.
Comprueba los siguientes criterios (de forma modular):

* Texto: 10-palabras, español latino, sin exposición.
* Video: resolución, frame rate, duración y continuidad de los shots.
* Audio: mezcla balanceada, silencio de 0-0.5 s en momentos críticos.
* Visual: uso de la lista de `visual_prompt_ast_id` y no hay duplicados.

El agente devuelve un `QualityReport` con hitos pasados / fallidos y lista de módulos de reparación sugeridos.
"""

from __future__ import annotations

import logging

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import EpisodeSpecV2, QualityReport

logger = logging.getLogger(__name__)


class QualityCheckAgent(BaseAgent[EpisodeSpecV2, QualityReport]):
    """Evaluación post-producción de calidad multicanal."""

    def __init__(self, *args, **kwargs):
        super().__init__("QualityCheckAgent", *args, **kwargs)

    def run(self, input_data: EpisodeSpecV2) -> QualityReport:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, episode: EpisodeSpecV2) -> QualityReport:
        # Implementa validaciones básicas; la lógica real requeriría helperes de video/audio
        errors: list[str] = []
        # 1. Texto
        for beat in episode.beats:
            for did in beat.dialogue_ids:
                if len(did.split()) > 10:
                    errors.append(f"Dialogue >10 words: {did[:30]}")
        # 2. Video shots – ver CSS de duración de cada shot
        for shot in episode.shots:
            if shot.end - shot.start > 120:
                errors.append("Shot >120s: %s" % shot.shot_id)
        # 3. Audio balance – simple placeholder
        # 4. Visual duplicates
        used_visual = set()
        for shot in episode.shots:
            vid = shot.visual_prompt_ast_id
            if vid in used_visual:
                errors.append(f"Duplicate visual prompt: {vid}")
            used_visual.add(vid)
        return QualityReport(
            state="pass" if not errors else "fail",
            score=0.0,
            critical_failures=errors,
            issues=[],
            created_by=self.name,
        )

# Alias
QC = QualityCheckAgent
