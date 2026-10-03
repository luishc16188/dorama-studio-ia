"""
Voice Director Agent - Fase 12
Genera dirección vocal para episodios basada en análisis de contenido y emociones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *


@dataclass
class VocalProfile:
    """Perfil vocal para un personaje o escena."""
    character_id: str
    voice_id: str
    description: str
    pitch_range: str  # e.g., "alto", "medio", "bajo", "variado"
    speaking_rate: str  # e.g., "lento", "moderado", "rápido"
    breathiness: float = 0.0  # 0.0 a 1.0
    roughness: float = 0.0  # 0.0 a 1.0
    emotional_range: dict[str, float] = field(default_factory=dict)  # emoción -> intensidad
    accent: str = "neutro"  # e.g., "es-419", "es-ml", "neutral"
    language: str = "español"


class VoiceDirectorAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Voice Director Agent que crea perfiles vocales y directrices de actuación vocal
    para personajes basado en análisis emocional y de contenido.
    """

    def __init__(self):
        super().__init__("VoiceDirectorAgent")

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Genera dirección vocal basada en análisis de contenido y personajes.

        Args:
            validated_input: Diccionario con:
                - characters: Lista de personajes con sus perfiles psicológicos
                - emotion_analysis: Análisis emocional por beat/escena
                - vocal_requirements: Requerimientos vocales específicos
                - genre: Género del contenido
                - scene_data: Datos de la escena/episodio

        Returns:
            Diccionario con perfiles vocales y directrices de actuación
        """
        characters = validated_input.get("characters", [])
        emotion_analysis = validated_input.get("emotion_analysis", {})
        vocal_requirements = validated_input.get("vocal_requirements", {})
        genre = validated_input.get("genre", "romance_traicion")
        scene_data = validated_input.get("scene_data", {})

        # Generar perfiles vocales para cada personaje
        vocal_profiles = self._generate_vocal_profiles(characters, emotion_analysis, genre)

        # Generar directrices de actuación vocal por escena
        vocal_directions = self._generate_vocal_directions(
            vocal_profiles, emotion_analysis, scene_data, vocal_requirements
        )

        # Generar guía de consistencia vocal
        consistency_guide = self._generate_consistency_guide(vocal_profiles)

        result = {
            "vocal_profiles": [self._vocal_profile_to_dict(p) for p in vocal_profiles],
            "vocal_directions": vocal_directions,
            "consistency_guide": consistency_guide,
            "genre_specific_notes": self._get_genre_vocal_notes(genre),
            "recommendations": self._get_vocal_recommendations(vocal_profiles, emotion_analysis)
        }

        return result

    def _generate_vocal_profiles(
        self,
        characters: list[dict[str, Any]],
        emotion_analysis: dict[str, Any],
        genre: str
    ) -> list[VocalProfile]:
        """Genera perfiles vocales para cada personaje basado en su perfil psicológico."""
        profiles = []

        for char_data in characters:
            char_id = char_data.get("character_id", f"CHAR_{len(profiles):03d}")

            # Extraer rasgos psicológicos para determinar características vocales
            psychological = char_data.get("psychological", {})
            want = psychological.get("want", "")
            need = psychological.get("need", "")
            lie = psychological.get("lie", "")
            fear = psychological.get("fear", "")

            # Determinar características vocales basadas en rasgos psicológicos
            pitch_range = self._determine_pitch_range(want, need, lie, fear, genre)
            speaking_rate = self._determine_speaking_rate(want, need, lie, fear)
            breathiness = self._determine_breathiness(want, need, lie, fear)
            roughness = self._determine_roughness(want, need, lie, fear)
            emotional_range = self._determine_emotional_range(want, need, lie, fear)
            accent = self._determine_accent(char_data, genre)

            profile = VocalProfile(
                character_id=char_id,
                voice_id=f"voice_{char_id}",
                description=f"Voz para {char_data.get('name', 'Personaje')} basado en perfil psicológico",
                pitch_range=pitch_range,
                speaking_rate=speaking_rate,
                breathiness=breathiness,
                roughness=roughness,
                emotional_range=emotional_range,
                accent=accent,
                language="español"
            )

            profiles.append(profile)

        return profiles

    def _determine_pitch_range(
        self,
        want: str,
        need: str,
        lie: str,
        fear: str,
        genre: str
    ) -> str:
        """Determina el rango de pitch basado en rasgos psicológicos y género."""
        want_lower = want.lower()
        need_lower = need.lower()
        lie_lower = lie.lower()
        fear_lower = fear.lower()

        # Voces más altas para emociones de miedo, ansiedad, emoción
        high_pitch_indicators = [
            "miedo", "ansiedad", "sorpresa", "emoción", "excitación",
            "juvenil", "innocente", "vulnerable"
        ]

        # Voces más bajas para autoridad, seriedad, amenaza
        low_pitch_indicators = [
            "autoridad", "control", "poder", "seriedad", "amenaza",
            "madurez", "experiencia", "severidad"
        ]

        # Voces medias para equilibrio, neutralidad
        mid_pitch_indicators = [
            "equilibrio", "neutralidad", "estabilidad", "calma",
            "reflexión", "sabiduría"
        ]

        # Contar indicadores
        high_score = sum(1 for indicator in high_pitch_indicators
                        if indicator in want_lower or indicator in need_lower or
                           indicator in lie_lower or indicator in fear_lower)
        low_score = sum(1 for indicator in low_pitch_indicators
                       if indicator in want_lower or indicator in need_lower or
                          indicator in lie_lower or indicator in fear_lower)
        mid_score = sum(1 for indicator in mid_pitch_indicators
                       if indicator in want_lower or indicator in need_lower or
                          indicator in lie_lower or indicator in fear_lower)

        # Determinar rango basado en puntuación
        if high_score > low_score and high_score > mid_score:
            return "alto"
        elif low_score > high_score and low_score > mid_score:
            return "bajo"
        else:
            return "medio"

    def _determine_speaking_rate(
        self,
        want: str,
        need: str,
        lie: str,
        fear: str
    ) -> str:
        """Determina la velocidad de habla basada en rasgos psicológicos."""
        combined = (want + need + lie + fear).lower()

        # Habla rápida para urgencia, ansiedad, emoción
        fast_indicators = ["urgencia", "ansiedad", "pánico", "emoción", "excitación", "rápido"]
        # Habla lenta para tristeza, reflexión, solemnidad
        slow_indicators = ["tristeza", "reflexión", "solemnidad", "melancolía", "lento", "pausado"]

        fast_score = sum(1 for indicator in fast_indicators if indicator in combined)
        slow_score = sum(1 for indicator in slow_indicators if indicator in combined)

        if fast_score > slow_score:
            return "rápido"
        elif slow_score > fast_score:
            return "lento"
        else:
            return "moderado"

    def _determine_breathiness(
        self,
        want: str,
        need: str,
        lie: str,
        fear: str
    ) -> float:
        """Determina la aspireción (breathiness) basada en vulnerabilidad e intimidad."""
        combined = (want + need + lie + fear).lower()

        # Más breathiness para vulnerabilidad, intimidad, ternura
        breathy_indicators = ["vulnerable", "íntimo", "ternura", "suavidad", "cercanía", "confesión"]
        # Menos breathiness para fuerza, autoridad, dureza
        non_breathy_indicators = ["fuerza", "autoridad", "dureza", "rigidez", "control"]

        breathy_score = sum(1 for indicator in breathy_indicators if indicator in combined)
        non_breathy_score = sum(1 for indicator in non_breathy_indicators if indicator in combined)

        # Normalizar a 0-1
        base = 0.3  # Valor base
        if breathy_score > non_breathy_score:
            base += 0.4
        else:
            base -= 0.2

        return max(0.0, min(1.0, base))

    def _determine_roughness(
        self,
        want: str,
        need: str,
        lie: str,
        fear: str
    ) -> float:
        """Determina la aspereza (roughness) basada en dureza y resistencia."""
        combined = (want + need + lie + fear).lower()

        # Más roughness para dureza, resistencia, agresividad
        rough_indicators = ["dureza", "resistencia", "agresividad", "fuerza", "conflicto", "batalla"]
        # Menos roughness para suavidad, ternura, vulnerabilidad
        smooth_indicators = ["suavidad", "ternura", "vulnerabilidad", "dulzura", "caricia"]

        rough_score = sum(1 for indicator in rough_indicators if indicator in combined)
        smooth_score = sum(1 for indicator in smooth_indicators if indicator in combined)

        # Normalizar a 0-1
        base = 0.2  # Valor base
        if rough_score > smooth_score:
            base += 0.5
        else:
            base -= 0.1

        return max(0.0, min(1.0, base))

    def _determine_emotional_range(
        self,
        want: str,
        need: str,
        lie: str,
        fear: str
    ) -> dict[str, float]:
        """Determina el rango emocional basado en el arco del personaje."""
        combined = (want + need + lie + fear).lower()

        # Mapeo básico de rasgos a emociones
        emotion_mapping = {
            "miedo": ["miedo", "ansiedad", "temor"],
            "alegría": ["felicidad", "alegría", "contentamiento"],
            "tristeza": ["tristeza", "melancolía", "dolor"],
            "ira": ["ira", "frustración", "rabia"],
            "sorpresa": ["sorpresa", "asombro", "impacto"],
            "asco": ["asco", "repulsión", "desagrado"],
            "confianza": ["confianza", "seguridad", "fidelidad"],
            "sorpresa": ["sorpresa", "asombro", "impacto"]
        }

        emotional_range = {}
        for emotion, indicators in emotion_mapping.items():
            score = sum(1 for indicator in indicators if indicator in combined)
            if score > 0:
                # Normalizar a 0-1 escala
                emotional_range[emotion] = min(1.0, score * 0.3)

        # Siempre incluir algunas emociones básicas
        if not emotional_range:
            emotional_range = {
                "neutral": 0.5,
                "curiosidad": 0.3,
                "determinación": 0.4
            }

        return emotional_range

    def _determine_accent(self, char_data: dict[str, Any], genre: str) -> str:
        """Determina el acento basado en origen del personaje y género."""
        # En una implementación real, esto vendría de los datos del personaje
        # Por ahora, usar un default basado en género
        genre_accents = {
            "romance_traicion": "es-419",  # Español latino neutro
            "venganza_sofisticada": "es-419",
            "thriller_domestico": "es-419",
            "comedia": "es-419",
            "historico": "es-419",
            "fantasia": "neutro"
        }
        return genre_accents.get(genre, "es-419")

    def _generate_vocal_directions(
        self,
        vocal_profiles: list[VocalProfile],
        emotion_analysis: dict[str, Any],
        scene_data: dict[str, Any],
        vocal_requirements: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Genera directrices de actuación vocal por escena/beat."""
        directions = []

        # Por ahora, generar directrices básicas basadas en el análisis emocional
        beats = emotion_analysis.get("beats", [])
        for i, beat_data in enumerate(beats):
            beat_num = i + 1
            dominant_emotion = beat_data.get("dominant_emotion", "neutral")
            intensity = beat_data.get("intensity", 0.5)

            direction = {
                "beat_number": beat_num,
                "timestamp": f"{i*10}-{(i+1)*10}s",  # Asumiendo beats de 10s
                "dominant_emotion": dominant_emotion,
                "intensity": intensity,
                "vocal_notes": self._get_vocal_notes_for_emotion(dominant_emotion, intensity),
                "recommended_profile": self._get_recommended_profile_for_emotion(
                    vocal_profiles, dominant_emotion
                ) if vocal_profiles else None,
                "technical_notes": self._get_technical_vocal_notes(dominant_emotion)
            }
            directions.append(direction)

        return directions

    def _get_vocal_notes_for_emotion(self, emotion: str, intensity: float) -> list[str]:
        """Obtiene notas técnicas vocales para una emoción específica."""
        emotion_notes = {
            "miedo": [
                "Voz temblorosa o susurrada",
                "Respiración entrecortada",
                "Micro-pausas entre frases",
                "Variación sutil en pitch"
            ],
            "ira": [
                "Proyección fuerte y clara",
                "Enfasis en consonantes",
                "Ritmo acelerado",
                "Volumen variable con énfasis en palabras clave"
            ],
            "tristeza": [
                "Velocidad reducida",
                "Pitch ligeramente descendente al final de frases",
                "Pausas más largas entre frases",
                "Voz más suave y melódica"
            ],
            "sorpresa": [
                "Ataque vocal repentino",
                "Variación rápida en pitch",
                "Enfasis en la primera sílaba",
                "Respiración visible antes de hablar"
            ],
            "felicidad": [
                "Ritmo alegre y variado",
                "Pitch ligeramente ascendente",
                "Enfasis en vocales",
                "Respiración regular y fluida"
            ],
            "neutro": [
                "Voz clara y uniforme",
                "Ritmo constante",
                "Articulación precisa"
            ]
        }

        base_notes = emotion_notes.get(emotion, emotion_notes["neutro"])

        # Ajustar notas basado en intensidad
        if intensity > 0.7:
            # Intensidad alta: enfatizar características
            return [f"[INTENSO] {note}" for note in base_notes]
        elif intensity < 0.3:
            # Intensidad baja: suavizar características
            return [f"[SUAVE] {note}" for note in base_notes]
        else:
            return base_notes

    def _get_recommended_profile_for_emotion(
        self,
        vocal_profiles: list[VocalProfile],
        emotion: str
    ) -> dict[str, Any] | None:
        """Recomienda el perfil vocal más adecuado para una emoción."""
        if not vocal_profiles:
            return None

        # Simple heurística: seleccionar el primer perfil (en una implementación real
        # sería más sofisticado basado en matching emocional)
        profile = vocal_profiles[0]
        return {
            "character_id": profile.character_id,
            "voice_id": profile.voice_id,
            "description": profile.description
        }

    def _get_technical_vocal_notes(self, emotion: str) -> str:
        """Obtiene notas técnicas específicas para ingenieros de audio."""
        technical_notes = {
            "miedo": "Añadir sutil reverb de habitación pequeña, reducir frecuencias bajas (<80Hz)",
            "ira": "Ligeros compresión para controlar picos, aumentar presencia en 2-5kHz",
            "tristeza": "Añadir delay corto (80-120ms), reducir presencia en altas frecuencias",
            "sorpresa": "Transiente rápido de ataque, compresión ligera para control",
            "felicidad": "Añadir brillo sutil en 8-12kHz, compresión mínima para naturalidad",
            "neutro": "Ecualización plana, mínima procesamiento"
        }
        return technical_notes.get(emotion, "Ecualización estándar")

    def _generate_consistency_guide(
        self,
        vocal_profiles: list[VocalProfile]
    ) -> dict[str, Any]:
        """Genera una guía de consistencia vocal para todo el elenco."""
        if not vocal_profiles:
            return {"error": "No hay perfiles vocales disponibles"}

        # Analizar rangos de pitch para evitar conflictos
        pitch_ranges = [p.pitch_range for p in vocal_profiles]
        pitch_distribution = {}
        for pitch in pitch_ranges:
            pitch_distribution[pitch] = pitch_distribution.get(pitch, 0) + 1

        # Analizar velocidades de habla
        speaking_rates = [p.speaking_rate for p in vocal_profiles]
        rate_distribution = {}
        for rate in speaking_rates:
            rate_distribution[rate] = rate_distribution.get(rate, 0) + 1

        return {
            "total_characters": len(vocal_profiles),
            "pitch_distribution": pitch_distribution,
            "speaking_rate_distribution": rate_distribution,
            "recommendations": self._get_consistency_recommendations(
                pitch_distribution, rate_distribution
            ),
            "conflict_warnings": self._get_pitch_conflict_warnings(pitch_distribution)
        }

    def _get_consistency_recommendations(
        self,
        pitch_dist: dict[str, int],
        rate_dist: dict[str, int]
    ) -> list[str]:
        """Genera recomendaciones para mantener consistencia vocal."""
        recommendations = []

        # Recomendaciones de pitch
        if pitch_dist.get("alto", 0) > 3:
            recommendations.append("Considerar variar más los rangos de pitch - demasiados personajes agudos")
        if pitch_dist.get("bajo", 0) > 3:
            recommendations.append("Considerar variar más los rangos de pitch - demasiados personajes graves")

        # Recomendaciones de speaking rate
        if rate_dist.get("rápido", 0) > 3:
            recommendations.append("Muchos personajes con habla rápida - considerar reducir para mejor claridad")
        if rate_dist.get("lento", 0) > 3:
            recommendations.append("Muchos personajes con habla lenta - considerar acelerar ligeramente para dinamismo")

        if not recommendations:
            recommendations.append("Distribución vocal adecuada para el elenco")

        return recommendations

    def _get_pitch_conflict_warnings(self, pitch_dist: dict[str, int]) -> list[str]:
        """Genera advertencias sobre posibles conflictos de pitch."""
        warnings = []
        total = sum(pitch_dist.values())

        # Si más del 60% del elenco está en el mismo rango de pitch, podría haber confusión
        for pitch, count in pitch_dist.items():
            if count / total > 0.6:
                warnings.append(f"Advertencia: {count} personajes ({count/total*100:.0f}%) en rango de pitch '{pitch}' - riesgo de confusión vocal")

        return warnings

    def _get_genre_vocal_notes(self, genre: str) -> str:
        """Obtiene notas específicas de género para dirección vocal."""
        genre_notes = {
            "romance_traicion": "Enfocar en la transición de inocencia a experiencia a través de cambios sutiles en el tono vocal",
            "venganza_sofisticada": "Mantener control vocal incluso en escenas de alta emoción - la calma es más amenazante que el grito",
            "thriller_domestico": "Usar variaciones sutiles en lugar de cambios drásticos - la tensión está en lo no dicho",
            "comedia": "Exagerar características vocales para efecto cómico, pero mantener claridad",
            "historico": "Investigar acentos y modismos del periodo específico para autenticidad",
            "fantasia": "Crear distintividad vocal clara para razas o especies diferentes"
        }
        return genre_notes.get(genre, "Dirección vocal estándar para el género")

    def _get_vocal_recommendations(
        self,
        vocal_profiles: list[VocalProfile],
        emotion_analysis: dict[str, Any]
    ) -> list[str]:
        """Genera recomendaciones generales para dirección vocal."""
        recommendations = []

        if len(vocal_profiles) > 5:
            recommendations.append(f"Elenco grande ({len(vocal_profiles)} personajes) - considerar crear grupos vocales por relaciones")

        # Analizar variedad emocional en la escena
        beats = emotion_analysis.get("beats", [])
        emotions = [beat.get("dominant_emotion", "") for beat in beats if beat.get("dominant_emotion")]
        unique_emotions = set(e for e in emotions if e)

        if len(unique_emotions) >= 6:
            recommendations.append("Gran variedad emocional detectada - asegurar que el rango vocal de cada personaje sea suficiente")
        elif len(unique_emotions) <= 2:
            recommendations.append("Variedad emocional limitada - considerar oportunidades para mostrar más rango emocional")

        # Recomendación general
        recommendations.append("Realizar pruebas de voz grabadas antes de la producción final para asegurar compatibilidad de micrófonos y espacios")

        return recommendations

    def _vocal_profile_to_dict(self, profile: VocalProfile) -> dict[str, Any]:
        """Convierte un VocalProfile a diccionario para serialización."""
        return {
            "character_id": profile.character_id,
            "voice_id": profile.voice_id,
            "description": profile.description,
            "pitch_range": profile.pitch_range,
            "speaking_rate": profile.speaking_rate,
            "breathiness": profile.breathiness,
            "roughness": profile.roughness,
            "emotional_range": profile.emotional_range,
            "accent": profile.accent,
            "language": profile.language
        }

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the voice director agent."""
        return self.process(input_data)
