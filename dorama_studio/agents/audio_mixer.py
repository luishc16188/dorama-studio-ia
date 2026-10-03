"""
Audio Mixer – Combina pistas de voz, SFX y música en un master final.
Wrapper alrededor de ffmpeg para mezclar múltiples archivos de audio.
"""

from __future__ import annotations

import logging
import subprocess
import tempfile

from dorama_studio.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AudioMixerAgent(BaseAgent[dict, str]):
    """Mezcla pistas de audio y genera archivo master."""

    def __init__(self, sample_rate: int = 48000):
        super().__init__("AudioMixerAgent")
        self.sample_rate = sample_rate

    def run(self, input_data: dict) -> str:
        """Implementación requerida por BaseAgent."""
        return self.process(input_data)

    def _process(self, payload: dict) -> str:
        """
        payload contiene:
        - voice_tracks: list[VoiceDirection] -> archivos de audio generados
        - sfx_layers: list[SFXLayer]
        - music_timeline: list[MusicTimelineEntry]
        - output_path: str (opcional)
        Retorna la ruta al archivo master mezclado.
        """
        voice_tracks = payload.get("voice_tracks", [])
        sfx_layers = payload.get("sfx_layers", [])
        music_timeline = payload.get("music_timeline", [])
        output_path = payload.get("output_path") or self._temp_output()

        # Construir filter_complex para ffmpeg
        filter_parts = []
        input_files = []
        input_index = 0

        # Voice tracks
        for vt in voice_tracks:
            if vt.get("audio_file"):
                input_files.append(vt["audio_file"])
                # Aplicar volume y delay si es necesario
                filter_parts.append(f"[{input_index}:a]volume=1.0[a{input_index}]")
                input_index += 1

        # SFX layers
        for sfx in sfx_layers:
            if sfx.get("sound_file"):
                input_files.append(sfx["sound_file"])
                vol = sfx.get("volume", 1.0)
                start = sfx.get("start_time", 0)
                filter_parts.append(
                    f"[{input_index}:a]volume={vol},adelay={int(start*1000)}|{int(start*1000)}[sfx{input_index}]"
                )
                input_index += 1

        # Music timeline
        for mt in music_timeline:
            if mt.get("audio_file"):
                input_files.append(mt["audio_file"])
                vol_db = mt.get("volume_db", -20)
                # Convertir dB a factor lineal
                vol = 10 ** (vol_db / 20)
                start = mt.get("start_sec", 0)
                filter_parts.append(
                    f"[{input_index}:a]volume={vol},adelay={int(start*1000)}|{int(start*1000)}[mus{input_index}]"
                )
                input_index += 1

        # Mezclar todo
        if filter_parts:
            # Combinar todas las streams etiquetadas
            mix_inputs = "+".join([p.split("[")[1].split("]")[0] for p in filter_parts])
            filter_complex = ";".join(filter_parts) + f";{mix_inputs}amix=inputs={len(filter_parts)}:duration=longest[out]"
        else:
            # Silencio si no hay nada
            filter_complex = "anullsrc=r=48000:cl=stereo[out]"

        # Ejecutar ffmpeg
        cmd = [
            "ffmpeg", "-y",
            *sum([["-i", f] for f in input_files], []),
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-ar", str(self.sample_rate),
            "-ac", "2",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]

        try:
            logger.info("Mixing audio: %s inputs -> %s", len(input_files), output_path)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                logger.error("ffmpeg mix failed: %s", result.stderr)
                raise RuntimeError(f"Audio mix failed: {result.stderr}")
            return output_path
        except subprocess.TimeoutExpired:
            logger.error("Audio mix timeout")
            raise
        except Exception as e:
            logger.error("Audio mix error: %s", e)
            raise

    def _temp_output(self) -> str:
        tmp = tempfile.NamedTemporaryFile(suffix=".aac", delete=False)
        return tmp.name

# Alias
AudioMixer = AudioMixerAgent
