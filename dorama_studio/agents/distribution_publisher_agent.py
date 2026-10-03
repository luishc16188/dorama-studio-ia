"""
Distribution Publisher Agent – Publica episodio final en plataformas.
Wrapper genérico que admite backends: YouTube, TikTok, Instagram, filesystem.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import VideoArtifact

logger = logging.getLogger(__name__)


class DistributionPublisherAgent(BaseAgent[dict, dict]):
    """Publica artefacto final en plataformas destino."""

    def __init__(self, backends: list[str] | None = None):
        super().__init__("DistributionPublisherAgent")
        self.backends = backends or ["filesystem"]
        self.platform_configs = self._default_configs()

    def _default_configs(self) -> dict[str, dict]:
        return {
            "filesystem": {"base_path": "published"},
            "youtube": {"api_key_env": "YOUTUBE_API_KEY", "privacy": "private"},
            "tiktok": {"api_key_env": "TIKTOK_API_KEY"},
            "instagram": {"api_key_env": "INSTAGRAM_API_KEY"},
        }

    def run(self, input_data: dict) -> dict:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, payload: dict) -> dict:
        """
        payload:
        - video_artifact: VideoArtifact (episodio final)
        - quality_report: QualityReport (debe ser PASS)
        - title: str
        - description: str
        - tags: list[str]
        - platforms: list[str] (subset of backends)
        - metadata: dict (extra platform-specific metadata)
        """
        video_artifact = payload.get("video_artifact")
        quality_report = payload.get("quality_report")
        title = payload.get("title", "Untitled Episode")
        description = payload.get("description", "")
        tags = payload.get("tags", [])
        platforms = payload.get("platforms", self.backends)
        metadata = payload.get("metadata", {})

        if not video_artifact:
            raise ValueError("video_artifact es requerido")

        if quality_report and quality_report.state != "pass":
            logger.warning("Publicando a pesar de QC no PASS: %s", quality_report.state)

        results = {}
        for platform in platforms:
            if platform not in self.backends:
                logger.warning("Backend no configurado: %s", platform)
                results[platform] = {"status": "skipped", "reason": "backend not configured"}
                continue

            try:
                result = self._publish_to_platform(
                    platform, video_artifact, title, description, tags, metadata
                )
                results[platform] = result
            except Exception as e:
                logger.error("Error publicando en %s: %s", platform, e)
                results[platform] = {"status": "error", "message": str(e)}

        return {
            "publish_id": f"pub_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "video_artifact_id": video_artifact.artifact_id if video_artifact else None,
            "results": results,
        }

    def _publish_to_platform(
        self,
        platform: str,
        video_artifact: VideoArtifact,
        title: str,
        description: str,
        tags: list[str],
        metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Dispatch al backend correspondiente."""
        method_name = f"_publish_{platform}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(video_artifact, title, description, tags, metadata)
        else:
            return self._publish_filesystem(video_artifact, title, description, tags, metadata)

    def _publish_filesystem(
        self,
        video_artifact: VideoArtifact,
        title: str,
        description: str,
        tags: list[str],
        metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Copia a carpeta local con metadatos JSON."""
        base = Path(self.platform_configs["filesystem"]["base_path"])
        base.mkdir(parents=True, exist_ok=True)

        pub_dir = base / video_artifact.episode_id
        pub_dir.mkdir(exist_ok=True)

        # Copiar video si es local
        src_uri = video_artifact.uri
        if src_uri.startswith("file://"):
            src = Path(src_uri[7:])
            if src.exists():
                dst = pub_dir / f"{video_artifact.artifact_id}{src.suffix}"
                import shutil
                shutil.copy2(src, dst)
                video_artifact.uri = str(dst.absolute())

        # Guardar metadata
        meta = {
            "title": title,
            "description": description,
            "tags": tags,
            "platforms": ["filesystem"],
            "published_at": datetime.utcnow().isoformat() + "Z",
            **metadata,
        }
        (pub_dir / f"{video_artifact.artifact_id}_meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2)
        )

        return {
            "status": "published",
            "platform": "filesystem",
            "path": str(pub_dir),
            "video_uri": video_artifact.uri,
        }

    def _publish_youtube(self, video_artifact, title, description, tags, metadata):
        """Placeholder para YouTube API."""
        logger.info("YouTube publish placeholder for %s", video_artifact.artifact_id)
        return {"status": "pending", "platform": "youtube", "message": "Implement YouTube API"}

    def _publish_tiktok(self, video_artifact, title, description, tags, metadata):
        """Placeholder para TikTok API."""
        logger.info("TikTok publish placeholder for %s", video_artifact.artifact_id)
        return {"status": "pending", "platform": "tiktok", "message": "Implement TikTok API"}

    def _publish_instagram(self, video_artifact, title, description, tags, metadata):
        """Placeholder para Instagram API."""
        logger.info("Instagram publish placeholder for %s", video_artifact.artifact_id)
        return {"status": "pending", "platform": "instagram", "message": "Implement Instagram API"}


# Alias
Publisher = DistributionPublisherAgent
