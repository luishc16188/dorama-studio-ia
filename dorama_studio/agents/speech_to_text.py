"""
Speech-to-Text Engine – Wrapper alrededor de Whisper (local) o API externa.
Convierte archivos de audio a texto con timestamps para generar subtítulos.
"""

from __future__ import annotations

import json
import logging
import subprocess
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import SubtitleEntry

logger = logging.getLogger(__name__)


class SpeechToTextAgent(BaseAgent[str, list[SubtitleEntry]]):
    """Transcribe audio a subtítulos con timestamps."""

    def __init__(self, model: str = "base", use_local: bool = True):
        super().__init__("SpeechToTextAgent")
        self.model = model
        self.use_local = use_local

    def run(self, input_data: str) -> list[SubtitleEntry]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, audio_path: str) -> list[SubtitleEntry]:
        if self.use_local:
            return self._transcribe_local(audio_path)
        else:
            return self._transcribe_api(audio_path)

    def _transcribe_local(self, audio_path: str) -> list[SubtitleEntry]:
        """Usa whisper CLI local."""
        try:
            # whisper --model base --output_format json audio.wav
            result = subprocess.run(
                [
                    "whisper",
                    "--model", self.model,
                    "--output_format", "json",
                    audio_path
                ],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                logger.error("Whisper failed: %s", result.stderr)
                return self._fallback_subtitles(audio_path)

            # Parse JSON output
            output_json = result.stdout.strip()
            data = json.loads(output_json)
            return self._parse_whisper_json(data)

        except subprocess.TimeoutExpired:
            logger.error("Whisper timeout")
            return self._fallback_subtitles(audio_path)
        except Exception as e:
            logger.error("Transcription error: %s", e)
            return self._fallback_subtitles(audio_path)

    def _transcribe_api(self, audio_path: str) -> list[SubtitleEntry]:
        """Placeholder para API externa (OpenAI Whisper API, etc.)."""
        logger.info("Using external STT API for %s", audio_path)
        # Implementar llamada a API real aquí
        return self._fallback_subtitles(audio_path)

    def _parse_whisper_json(self, data: dict[str, Any]) -> list[SubtitleEntry]:
        """Convierte salida de Whisper a SubtitleEntry."""
        subtitles = []
        for segment in data.get("segments", []):
            subtitles.append(SubtitleEntry(
                start=segment.get("start", 0.0),
                end=segment.get("end", 0.0),
                text=segment.get("text", "").strip(),
                highlight_words=[],
                animation="",
                position={},
                style={}
            ))
        return subtitles

    def _fallback_subtitles(self, audio_path: str) -> list[SubtitleEntry]:
        """Subtítulos vacíos como fallback."""
        return [SubtitleEntry(
            start=0.0,
            end=10.0,
            text="[Transcripción no disponible]",
            highlight_words=[],
            animation="",
            position={},
            style={}
        )]

# Alias
STT = SpeechToTextAgent
