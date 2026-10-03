"""
Subtitle Agent – Genera subtítulos alineados a partir de audio master.
Wrapper alrededor de SpeechToTextAgent (Whisper) + formateo SRT/ASS.
"""

from __future__ import annotations

import logging
from pathlib import Path

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.agents.speech_to_text import SpeechToTextAgent
from dorama_studio.contracts.v2_schemas import SubtitleEntry

logger = logging.getLogger(__name__)


class SubtitleAgent(BaseAgent[dict, list[SubtitleEntry]]):
    """Genera track de subtítulos a partir de audio master."""

    def __init__(self, stt_model: str = "base", stt_local: bool = True):
        super().__init__("SubtitleAgent")
        self.stt = SpeechToTextAgent(model=stt_model, use_local=stt_local)

    def run(self, input_data: dict) -> list[SubtitleEntry]:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, payload: dict) -> list[SubtitleEntry]:
        """
        payload:
        - master_audio: str (ruta a archivo .aac/.wav)
        - language: str (opcional, default "es")
        - format: str ("srt" | "ass" | "entries", default "entries")
        - output_path: str (opcional, para guardar archivo)
        """
        master_audio = payload.get("master_audio")
        if not master_audio:
            raise ValueError("master_audio es requerido")

        language = payload.get("language", "es")
        fmt = payload.get("format", "entries")
        output_path = payload.get("output_path")

        logger.info("Generating subtitles for %s", master_audio)

        # Transcribir
        entries = self.stt.process(master_audio)

        # Filtrar entradas vacías
        entries = [e for e in entries if e.text.strip() and e.text != "[Transcripción no disponible]"]

        # Guardar archivo si se solicita
        if output_path and fmt in ("srt", "ass"):
            self._write_subtitle_file(entries, output_path, fmt)

        return entries

    def _write_subtitle_file(self, entries: list[SubtitleEntry], output_path: str, fmt: str):
        """Escribe archivo SRT o ASS."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "srt":
            content = self._to_srt(entries)
        elif fmt == "ass":
            content = self._to_ass(entries)
        else:
            return

        path.write_text(content, encoding="utf-8")
        logger.info("Subtitle file written: %s", path)

    def _to_srt(self, entries: list[SubtitleEntry]) -> str:
        """Convierte a formato SRT."""
        lines = []
        for i, e in enumerate(entries, 1):
            start = self._format_timestamp_srt(e.start)
            end = self._format_timestamp_srt(e.end)
            lines.append(f"{i}\n{start} --> {end}\n{e.text}\n")
        return "\n".join(lines)

    def _to_ass(self, entries: list[SubtitleEntry]) -> str:
        """Convierte a formato ASS (básico)."""
        header = """[Script Info]
Title: Dorama Studio Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,72,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,2,2,20,20,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        lines = [header]
        for e in entries:
            start = self._format_timestamp_ass(e.start)
            end = self._format_timestamp_ass(e.end)
            text = e.text.replace("\n", "\\N")
            lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
        return "\n".join(lines)

    def _format_timestamp_srt(self, seconds: float) -> str:
        """Formato HH:MM:SS,mmm para SRT."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _format_timestamp_ass(self, seconds: float) -> str:
        """Formato H:MM:SS.cc para ASS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centis = int((seconds - int(seconds)) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


# Alias
SubtitleGenerator = SubtitleAgent
