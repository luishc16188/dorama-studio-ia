"""
Editor Agent – Compose final episode from media artifacts using ffmpeg.
Takes EditTimeline (from ShotSpecs) and media files, produces final video.
"""

from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.contracts.v2_schemas import VideoArtifact

logger = logging.getLogger(__name__)


class EditorAgent(BaseAgent[dict, VideoArtifact]):
    """Renderiza timeline final concatenando shots + audio + subtítulos."""

    def __init__(self, fps: int = 24, resolution: str = "1080x1920"):
        super().__init__("EditorAgent")
        self.fps = fps
        self.resolution = resolution

    def run(self, input_data: dict) -> VideoArtifact:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, payload: dict) -> VideoArtifact:
        """
        payload:
        - shots: list[ShotSpec] ordenados
        - video_artifacts: list[VideoArtifact] (uno por shot)
        - master_audio: str (ruta a archivo .aac mezclado)
        - subtitle_file: str (ruta a .srt/.ass, opcional)
        - output_path: str (opcional)
        """
        shots = payload.get("shots", [])
        video_artifacts = payload.get("video_artifacts", [])
        master_audio = payload.get("master_audio")
        subtitle_file = payload.get("subtitle_file")
        output_path = payload.get("output_path") or self._temp_output()

        if not shots or not video_artifacts:
            raise ValueError("Shots y video_artifacts son requeridos")

        # Crear concat file para ffmpeg
        concat_file = self._create_concat_file(video_artifacts)

        # Comando ffmpeg
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_file,
        ]

        if master_audio:
            cmd.extend(["-i", master_audio, "-map", "0:v:0", "-map", "1:a:0"])
        else:
            cmd.extend(["-map", "0:v:0", "-map", "0:a:0"])

        if subtitle_file:
            cmd.extend(["-vf", f"subtitles={subtitle_file}"])

        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", str(self.fps),
            "-s", self.resolution,
            "-movflags", "+faststart",
            output_path
        ])

        try:
            logger.info("Editing episode: %d shots -> %s", len(shots), output_path)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                logger.error("ffmpeg edit failed: %s", result.stderr)
                raise RuntimeError(f"Edit failed: {result.stderr}")
        finally:
            # Cleanup concat file
            Path(concat_file).unlink(missing_ok=True)

        # Retornar artifact final
        from dorama_studio.contracts.v2_schemas import VideoArtifact
        return VideoArtifact(
            artifact_id=f"art_final_{len(shots)}shots",
            artifact_type="video_artifact",
            project_id="proj_test",
            season_id="s01",
            episode_id="e01",
            shot_id="final",
            duration_sec=sum(s.end - s.start for s in shots),
            codec="h264",
            resolution=self.resolution,
            uri=f"file://{output_path}",
            meta={"shots": len(shots)},
            created_by=self.name,
        )

    def _create_concat_file(self, video_artifacts: list[VideoArtifact]) -> str:
        """Crea archivo de lista para ffmpeg concat."""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        for va in video_artifacts:
            uri = va.uri
            if uri.startswith("file://"):
                uri = uri[7:]
            tmp.write(f"file '{uri}'\n")
        tmp.close()
        return tmp.name

    def _temp_output(self) -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        return tmp.name


# Alias
Editor = EditorAgent
