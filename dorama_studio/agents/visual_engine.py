"""
Visual Engine - Renderiza shots a partir de PromptAST.
Wrapper minimal que llama a una API externa (ej. Midjourney, Stable Diffusion) o a un servicio local.
Devuelve un `VideoArtifact` referenciado por `visual_prompt_ast_id`.
"""

from __future__ import annotations

import logging
import uuid

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import ShotSpec, VideoArtifact

logger = logging.getLogger(__name__)


class VisualEngineAgent(BaseAgent[ShotSpec, VideoArtifact]):
    """Genera artefactos de video para cada shot."""

    def __init__(self, provider: str = "stable-diffusion-local"):
        super().__init__("VisualEngineAgent")
        self.provider = provider

    def run(self, input_data: ShotSpec) -> VideoArtifact:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, shot: ShotSpec) -> VideoArtifact:
        # En producción: llamar al renderer real con shot.visual_prompt_ast_id
        # Aquí devolvemos un placeholder con metadatos mínimos.
        artifact = VideoArtifact(
            artifact_id=f"art_vid_{uuid.uuid4().hex[:8]}",
            artifact_type="video_artifact",
            project_id="proj_test",  # ShotSpec doesn't have project_id in v2_schemas
            season_id="s01",
            episode_id="e01",
            shot_id=shot.shot_id,
            duration_sec=shot.end - shot.start,
            codec="h264",
            resolution="1080x1920",
            uri=f"file:///tmp/render/{shot.shot_id}.mp4",
            meta={"provider": self.provider},
            created_by=self.name,
        )
        logger.info("Rendered shot %s -> %s", shot.shot_id, artifact.uri)
        return artifact

# Alias
VisualEngine = VisualEngineAgent
