"""
Sound Designer Agent - Fase 12
Diseña el paisaje sonoro incluyendo foley, ambience y efectos de sonido.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dorama_studio.agents.base_agent import BaseAgent
from dorama_studio.data.schemas import *


@dataclass
class SoundLayer:
    """Una capa de sonido en el paisaje sonoro."""
    layer_id: str
    name: str
    description: str
    sound_type: str  # foley, ambience, fx, music, dialogue
    intensity: float  # 0.0 a 1.0
    spatial_position: dict[str, float]  # left, right, center, height
    frequency_range: str  # low, mid, high, full
    duration: float | None = None  # en segundos, si es un evento puntual
    loop: bool = False  # si debe repetirse
    volume_envelope: dict[str, float] = field(default_factory=dict)  # attack, decay, sustain, release
    triggers: list[str] = field(default_factory=list)  # qué eventos desencadenan este sonido
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Soundscape:
    """Paisaje sonoro completo para una escena o beat."""
    soundscape_id: str
    scene_beat: str  # identificador de la escena/beat
    description: str
    layers: list[SoundLayer] = field(default_factory=list)
    overall_mood: str = "neutral"  # tense, calm, energetic, etc.
    complexity_level: int = 1  # 1-5 scale
    transition_notes: str = ""  # notas para transición al siguiente soundscape


class SoundDesignerAgent(BaseAgent[dict[str, Any], dict[str, Any]]):
    """
    Sound Designer Agent que crea paisajes sonoros detallados incluyendo
    foley, ambiente, efectos de sonido y capas de audio para cada escena.
    """

    def __init__(self):
        super().__init__("SoundDesignerAgent")

    def _process(self, validated_input: dict[str, Any]) -> dict[str, Any]:
        """
        Diseña el paisaje sonoro basado en análisis de escena y requerimientos.

        Args:
            validated_input: Diccionario con:
                - scene_analysis: Análisis de la escena/beat
                - emotion_analysis: Análisis emocional por beat
                - action_sequences: Secuencias de acción que requieren foley
                - location_info: Información de la locación
                - time_of_day: Hora del día
                - weather_conditions: Condiciones climáticas
                - genre: Género del contenido
                - sound_requirements: Requerimientos específicos de sonido

        Returns:
            Diccionario con el soundscape diseñado y recomendaciones de producción
        """
        scene_analysis = validated_input.get("scene_analysis", {})
        emotion_analysis = validated_input.get("emotion_analysis", {})
        action_sequences = validated_input.get("action_sequences", [])
        location_info = validated_input.get("location_info", {})
        time_of_day = validated_input.get("time_of_day", "day")
        weather_conditions = validated_input.get("weather_conditions", "clear")
        genre = validated_input.get("genre", "romance_traicion")
        sound_requirements = validated_input.get("sound_requirements", {})

        # Diseñar el soundscape principal
        soundscape = self._design_soundscape(
            scene_analysis, emotion_analysis, action_sequences,
            location_info, time_of_day, weather_conditions, genre, sound_requirements
        )

        # Generar capas de sonido específicas
        foley_layers = self._design_foley_layers(action_sequences, location_info)
        ambience_layers = self._design_ambience_layers(location_info, time_of_day, weather_conditions)
        fx_layers = self._design_fx_layers(scene_analysis, emotion_analysis, genre)
        dialogue_layers = self._design_dialogue_enhancements(scene_analysis, emotion_analysis)

        # Combinar todas las capas
        all_layers = foley_layers + ambience_layers + fx_layers + dialogue_layers
        soundscape.layers = all_layers

        # Optimizar y balancear el soundscape
        optimized_layers = self._optimize_soundscape(all_layers, genre)
        soundscape.layers = optimized_layers

        # Generar guía de producción
        production_guide = self._generate_production_guide(soundscape, genre)

        result = {
            "soundscape": self._soundscape_to_dict(soundscape),
            "production_guide": production_guide,
            "layer_breakdown": self._get_layer_breakdown(optimized_layers),
            "technical_specs": self._get_technical_specs(optimized_layers),
            "budget_estimate": self._estimate_sound_budget(optimized_layers),
            "recommendations": self._get_sound_recommendations(soundscape, genre)
        }

        return result

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run the sound designer agent."""
        return self.process(input_data)

    def _design_soundscape(
        self,
        scene_analysis: dict[str, Any],
        emotion_analysis: dict[str, Any],
        action_sequences: list[dict[str, Any]],
        location_info: dict[str, Any],
        time_of_day: str,
        weather_conditions: str,
        genre: str,
        sound_requirements: dict[str, Any]
    ) -> Soundscape:
        """Diseña el soundscape base basado en todos los factores de entrada."""

        # Determinar el mood general basado en el análisis emocional
        beats = emotion_analysis.get("beats", [])
        dominant_emotions = [beat.get("dominant_emotion", "neutral") for beat in beats]
        overall_mood = self._determine_overall_mood(dominant_emotions)

        # Determinar complejidad basada en acción y ubicación
        complexity = self._calculate_complexity(action_sequences, location_info, genre)

        soundscape = Soundscape(
            soundscape_id=f"ss_{scene_analysis.get('scene_id', 'unknown')}",
            scene_beat=scene_analysis.get("scene_id", "unknown"),
            description=f"Paisaje sonoro para escena {scene_analysis.get('scene_id', 'unknown')} - {overall_mood}",
            overall_mood=overall_mood,
            complexity_level=complexity
        )

        return soundscape

    def _determine_overall_mood(self, emotions: list[str]) -> str:
        """Determina el mood general basado en las emociones predominantes."""
        if not emotions:
            return "neutral"

        # Mapeo de emociones a moods sonoros
        emotion_to_mood = {
            "miedo": "tense",
            "ansiedad": "tense",
            "ira": "aggressive",
            "frustración": "tense",
            "tristeza": "melancholic",
            "melancolía": "melancholic",
            "felicidad": "bright",
            "alegría": "bright",
            "excitación": "energetic",
            "sorpresa": "startling",
            "asco": "unpleasant",
            "confianza": "stable",
            "amor": "romantic",
            "pasión": "intense"
        }

        # Contar ocurrencias de cada mood
        mood_counts = {}
        for emotion in emotions:
            mood = emotion_to_mood.get(emotion, "neutral")
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        # Devolver el mood más frecuente
        if mood_counts:
            return max(mood_counts, key=mood_counts.get)
        return "neutral"

    def _calculate_complexity(
        self,
        action_sequences: list[dict[str, Any]],
        location_info: dict[str, Any],
        genre: str
    ) -> int:
        """Calcula el nivel de complejidad del soundscape (1-5)."""
        base_complexity = 1

        # Incrementar por secuencias de acción
        action_complexity = min(len(action_sequences) // 2, 2)  # Máximo +2 por acción

        # Incrementar por tipo de ubicación
        location_type = location_info.get("type", "interior")
        location_complexity = {
            "interior": 0,
            "exterior_urbano": 1,
            "exterior_natural": 2,
            "multilocacion": 2
        }.get(location_type, 0)

        # Incrementar por género
        genre_complexity = {
            "thriller_domestico": 1,
            "venganza_sofisticada": 1,
            "romance_traicion": 0,
            "accion": 2,
            "horror": 2,
            "fantasia": 2,
            "ciencia_ficcion": 2
        }.get(genre, 0)

        total = base_complexity + action_complexity + location_complexity + genre_complexity
        return min(max(total, 1), 5)  # Asegurar rango 1-5

    def _design_foley_layers(
        self,
        action_sequences: list[dict[str, Any]],
        location_info: dict[str, Any]
    ) -> list[SoundLayer]:
        """Diseña capas de foley basado en acciones y ubicación."""
        foley_layers = []

        # Foley genérico basado en ubicación
        location_type = location_info.get("type", "interior")
        location_foley = {
            "interior": [
                ("pisos_madera", "Pasos en piso de madera", 0.6),
                ("puerta_interior", "Apertura/cierre de puerta interior", 0.4),
                ("mano_sobre_mesa", "Manos sobre superficie de mesa", 0.3),
                ("ropa_tela", "Rozamiento de ropa", 0.2)
            ],
            "exterior_urbano": [
                ("pasos_concreto", "Pasos en concreto/asfalto", 0.7),
                ("transito_distante", "Tráfico urbano distante", 0.5),
                ("viento_ciudad", "Viento entre edificios", 0.3)
            ],
            "exterior_natural": [
                ("pasos_tierra", "Pasos en tierra o grava", 0.6),
                ("hojas_viento", "Hojas moviéndose por viento", 0.4),
                ("pajaros_distantes", "Pájaros en fondo", 0.3),
                ("agua_arroyo", "Sonido de agua corriente", 0.2)
            ]
        }

        base_foley = location_foley.get(location_type, location_foley["interior"])

        for i, (sound_id, description, intensity) in enumerate(base_foley):
            layer = SoundLayer(
                layer_id=f"foley_{location_type}_{i:02d}",
                name=description.split()[0].title(),  # Primera palabra capitalizada
                description=description,
                sound_type="foley",
                intensity=intensity,
                spatial_position={"left": 0.0, "right": 0.0, "center": 1.0, "height": 0.0},
                frequency_range="mid",
                loop=True,
                triggers=["scene_ambient"]
            )
            foley_layers.append(layer)

        # Foley específico basado en secuencias de acción
        for i, action in enumerate(action_sequences):
            action_type = action.get("type", "generic")
            intensity = action.get("intensity", 0.5)

            action_foley_map = {
                "pelea": [("golpe", "Golpe de puño o cuerpo", 0.8), ("rozo_tela", "Rozamiento de tela durante movimiento", 0.4)],
                "carrera": [("pisos_acelerados", "Pasos rápidos", 0.7), ("respiración_jadeante", "Respiración entrecortada", 0.6)],
                "rompimiento": [("vidrio_roto", "Vidrio rompiéndose", 0.9), ("metal_torcido", "Metal deformándose", 0.7)],
                "llanto": [("sollozos", "Sollozos y respiración entrecortada", 0.7)],
                "beso": [("labios", "Contacto suave de labios", 0.3), ("respiración_compartida", "Respiración compartida", 0.2)]
            }

            specific_foley = action_foley_map.get(action_type, [])
            for j, (sound_id, description, base_intensity) in enumerate(specific_foley):
                layer = SoundLayer(
                    layer_id=f"foley_action_{action_type}_{i:02d}_{j:02d}",
                    name=description.split()[0].title(),
                    description=description,
                    sound_type="foley",
                    intensity=base_intensity * intensity,
                    spatial_position={"left": 0.0, "right": 0.0, "center": 1.0, "height": 0.0},
                    frequency_range="mid",
                    duration=2.0,  # Foley típico es corto
                    loop=False,
                    triggers=[f"action_{i}"]
                )
                foley_layers.append(layer)

        return foley_layers

    def _design_ambience_layers(
        self,
        location_info: dict[str, Any],
        time_of_day: str,
        weather_conditions: str
    ) -> list[SoundLayer]:
        """Diseña capas de ambiente basado en ubicación, tiempo y clima."""
        ambience_layers = []

        # Ambience basado en ubicación
        location_type = location_info.get("type", "interior")
        location_ambience = {
            "interior": [
                ("habitacion_tone", "Tono de habitación (refrigerador lejano, electricidad)", 0.2),
                ("reverb_sutil", "Reverberación natural del espacio", 0.3)
            ],
            "exterior_urbano": [
                ("ciudad_distante", "Zumbido urbano distante", 0.4),
                ("viento_edificios", "Viento entre edificios", 0.3),
                ("sirenas_lejanas", "Sirenas muy distantes", 0.1)
            ],
            "exterior_natural": [
                ("viento_sutil", "Viento suave en fondo", 0.3),
                ("insectos_nocturnos" if time_of_day == "night" else "insectos_diurnos",
                 "Insectos según hora del día", 0.4),
                ("pajaros_ambiente", "Pájaros en ambiente", 0.3)
            ]
        }

        base_ambience = location_ambience.get(location_type, location_ambience["interior"])

        # Ajustar por tiempo de día
        time_modifiers = {
            "night": 0.7,  # Más ambiente nocturno generalmente
            "dawn_dusk": 0.8,
            "day": 1.0,
            "morning": 0.9
        }
        time_mod = time_modifiers.get(time_of_day, 1.0)

        # Ajustar por clima
        weather_modifiers = {
            "rain": 1.5,
            "storm": 2.0,
            "wind": 1.3,
            "fog": 1.2,
            "clear": 1.0,
            "snow": 1.1
        }
        weather_mod = weather_modifiers.get(weather_conditions, 1.0)

        for i, (sound_id, description, base_intensity) in enumerate(base_ambience):
            adjusted_intensity = min(base_intensity * time_mod * weather_mod, 1.0)
            layer = SoundLayer(
                layer_id=f"ambience_{location_type}_{i:02d}",
                name=description.split()[0].title(),
                description=description,
                sound_type="ambience",
                intensity=adjusted_intensity,
                spatial_position={"left": -0.3, "right": 0.3, "center": 0.0, "height": 0.0},
                frequency_range="full",
                loop=True,
                triggers=["scene_ambient"]
            )
            ambience_layers.append(layer)

        return ambience_layers

    def _design_fx_layers(
        self,
        scene_analysis: dict[str, Any],
        emotion_analysis: dict[str, Any],
        genre: str
    ) -> list[SoundLayer]:
        """Diseña capas de efectos de sonido basado en escena y emociones."""
        fx_layers = []

        # Efectos basados en emociones dominantes
        beats = emotion_analysis.get("beats", [])
        for i, beat in enumerate(beats):
            emotion = beat.get("dominant_emotion", "neutral")
            intensity = beat.get("intensity", 0.5)

            emotion_fx_map = {
                "miedo": [
                    ("heartbeat", "Latido del corazón amplificado", 0.6),
                    ("breath_tremor", "Respiración temblorosa", 0.4),
                    ("subtle_sting", "Estímulo sutil de tensión", 0.3)
                ],
                "ira": [
                    ("impact_hit", "Impacto fuerte o golpe", 0.7),
                    ("metal_clang", "Choque metálico", 0.5),
                    ("breath_forceful", "Respiración forzada", 0.4)
                ],
                "tristeza": [
                    ("single_note", "Nota sostenida melancólica", 0.3),
                    ("soft_pad", "Pad suave de fondo", 0.2),
                    ("distant_chime", "Campanilleo distante", 0.1)
                ],
                "sorpresa": [
                    ("whoosh", "Whoosh súbito", 0.6),
                    ("impact_soft", "Impacto suave", 0.4),
                    ("high_sting", "Estímulo agudo", 0.5)
                ],
                "felicidad": [
                    ("bright_chime", "Campanilleo brillante", 0.3),
                    ("light_percussion", "Percusión ligera", 0.2),
                    ("positive_sting", "Estímulo positivo", 0.2)
                ]
            }

            fx_list = emotion_fx_map.get(emotion, [])
            for j, (sound_id, description, base_intensity) in enumerate(fx_list):
                layer = SoundLayer(
                    layer_id=f"fx_emotion_{emotion}_{i:02d}_{j:02d}",
                    name=description.split()[0].title(),
                    description=description,
                    sound_type="fx",
                    intensity=base_intensity * intensity,
                    spatial_position={"left": 0.0, "right": 0.0, "center": 1.0, "height": 0.2},
                    frequency_range=self._get_fx_frequency_range(sound_id),
                    duration=1.5,
                    loop=False,
                    triggers=[f"beat_{i}"]
                )
                fx_layers.append(layer)

        # Efectos específicos de género
        genre_fx = {
            "thriller_domestico": [
                ("heartbeat_slow", "Latido lento y ominoso", 0.4),
                ("creaking_door", "Puerta crujiendo lentamente", 0.3),
                ("phone_ring", "Teléfono sonando (distorsionado)", 0.2)
            ],
            "horror": [
                ("infrasound", "Frecuencias muy bajas subaudibles", 0.5),
                ("reverse_reverb", "Reverb invertido", 0.4),
                ("scratch", "Rasguño en superficie", 0.3)
            ],
            "romance_traicion": [
                ("heartbeat_fast", "Latido acelerado por emoción", 0.3),
                ("breath_close", "Respiración cercana íntima", 0.2),
                ("string_swell", "Swells de cuerdas sutiles", 0.2)
            ]
        }

        genre_effects = genre_fx.get(genre, [])
        for i, (sound_id, description, intensity) in enumerate(genre_effects):
            layer = SoundLayer(
                layer_id=f"fx_genre_{genre}_{i:02d}",
                name=description.split()[0].title(),
                description=description,
                sound_type="fx",
                intensity=intensity,
                spatial_position={"left": 0.0, "right": 0.0, "center": 1.0, "height": 0.0},
                frequency_range="low" if "infrasound" in sound_id or "heartbeat" in sound_id else "mid",
                duration=2.0,
                loop=True if "heartbeat" in sound_id or "infrasound" in sound_id else False,
                triggers=["scene_ambient"]
            )
            fx_layers.append(layer)

        return fx_layers

    def _get_fx_frequency_range(self, sound_id: str) -> str:
        """Determina el rango de frecuencia apropiado para un FX."""
        if any(x in sound_id.lower() for x in ["heartbeat", "bass", "rumble", "infrasound"]):
            return "low"
        elif any(x in sound_id.lower() for x in ["whoosh", "sting", "hit", "impact", "chime"]):
            return "high"
        else:
            return "mid"

    def _design_dialogue_enhancements(
        self,
        scene_analysis: dict[str, Any],
        emotion_analysis: dict[str, Any]
    ) -> list[SoundLayer]:
        """Diseja mejoras para el diálogo basado en emociones."""
        dialogue_layers = []

        # Mejoras sutiles para diálogo basadas en emoción
        beats = emotion_analysis.get("beats", [])
        for i, beat in enumerate(beats):
            emotion = beat.get("dominant_emotion", "neutral")
            intensity = beat.get("intensity", 0.5)

            # Solo agregar mejoras si la intensidad es significativa
            if intensity > 0.4:
                enhancement_map = {
                    "miedo": ("breath_yellow", "Respiración ligeramente amarillenta (tensión)", 0.3),
                    "ira": ("voice_grit", "Ligero grano en la voz (fuerza)", 0.2),
                    "tristeza": ("voice_breathy", "Voz ligeramente breathy (vulnerabilidad)", 0.2),
                    "felicidad": ("voice_bright", "Voz ligeramente más brillante (alegría)", 0.1),
                    "sorpresa": ("voice_gasp", "Ligero jadeo en la voz (sorpresa)", 0.2)
                }

                if emotion in enhancement_map:
                    sound_id, description, base_intensity = enhancement_map[emotion]
                    layer = SoundLayer(
                        layer_id=f"dialogue_enhance_{emotion}_{i:02d}",
                        name=description.split()[0].title(),
                        description=description,
                        sound_type="dialogue",
                        intensity=base_intensity * intensity,
                        spatial_position={"left": 0.0, "right": 0.0, "center": 1.0, "height": 0.0},
                        frequency_range="mid",
                        duration=3.0,  # Asumiendo diálogo de varios segundos
                        loop=False,
                        triggers=[f"dialogue_beat_{i}"]
                    )
                    dialogue_layers.append(layer)

        return dialogue_layers

    def _optimize_soundscape(
        self,
        layers: list[SoundLayer],
        genre: str
    ) -> list[SoundLayer]:
        """Optimiza y balancea el soundscape evitando conflictos y excesos."""
        if not layers:
            return layers

        optimized = layers.copy()

        # 1. Limitar intensidad total por rango de frecuencia
        freq_intensity = {"low": 0.0, "mid": 0.0, "high": 0.0, "full": 0.0}
        for layer in optimized:
            freq_intensity[layer.frequency_range] += layer.intensity

        # 2. Reducir capas si alguna frecuencia está sobrecargada (>1.5)
        max_allowed = {"low": 1.2, "mid": 1.5, "high": 1.0, "full": 1.3}
        for freq, total_intensity in freq_intensity.items():
            if total_intensity > max_allowed[freq]:
                # Reducir proporzionalmente las capas de esta frecuencia
                excess = total_intensity - max_allowed[freq]
                reduction_factor = max_allowed[freq] / total_intensity

                for layer in optimized:
                    if layer.frequency_range == freq:
                        layer.intensity *= reduction_factor

        # 3. Eliminar capas con intensidad muy baja (<0.1) a menos que sean críticas
        critical_types = ["ambience"]  # El ambiente siempre es importante
        optimized = [
            layer for layer in optimized
            if layer.intensity >= 0.1 or layer.sound_type in critical_types
        ]

        # 4. Limitar número total de capas para evitar sobrecarga
        max_layers_by_genre = {
            "thriller_domestico": 8,
            "horror": 10,
            "romance_traicion": 6,
            "accion": 12,
            "comedia": 6
        }
        max_layers = max_layers_by_genre.get(genre, 8)

        if len(optimized) > max_layers:
            # Ordenar por importancia y tomar las top capas
            optimized.sort(key=lambda x: (
                x.sound_type != "ambience",  # El ambiente primero
                -x.intensity  # Luego por intensidad descendente
            ))
            optimized = optimized[:max_layers]

        return optimized

    def _generate_production_guide(
        self,
        soundscape: Soundscape,
        genre: str
    ) -> dict[str, Any]:
        """Genera una guía de producción para el equipo de sonido."""
        return {
            "recording_approach": self._get_recording_approach(genre),
            "library_suggestions": self._get_library_suggestions(genre),
            "processing_chain": self._get_processing_chain(soundscape.layers),
            "mixing_notes": self._get_mixing_notes(soundscape),
            "delivery_format": "24-bit/48kHz WAV, stems separados por tipo",
            "qa_checklist": self._get_qa_checklist(soundscape)
        }

    def _get_recording_approach(self, genre: str) -> str:
        """Obtiene el enfoque de grabación basado en el género."""
        approaches = {
            "thriller_domestico": "Grabación cercana y íntima con énfasis en detalles sutiles",
            "horror": "Grabación de fuentes inusuales y procesamiento extremo",
            "romance_traicion": "Grabación natural con enfoque en emociones vocales",
            "accion": "Grabación de impacto alto y bibliotecas de efectos especializadas",
            "comedia": "Grabación limpia con énfasis en timing y claridad",
            "fantasia": "Combinación de grabación de campo y síntesis creativa"
        }
        return approaches.get(genre, "Grabación estándar de campo y biblioteca")

    def _get_library_suggestions(self, genre: str) -> list[str]:
        """Sugiere bibliotecas de sonido apropiadas."""
        libraries = {
            "thriller_domestico": ["Boom Library - Atmospheres", "Soundly - Tension", "BBC Sound Effects"],
            "horror": ["Wave Alchemy - Evolve", "Boom Library - Horror", "Soundsnap - Horror FX"],
            "romance_traicion": ["Hollywood Edge - Romance", "Soundsnap - Emotional", "Pro Sound Effects"],
            "accion": ["Boom Library - Destruction", "Soundly - Impacts", "Hollywood Edge - Action"],
            "comedia": ["Soundsnap - Comedy", "BBC Sound Effects - Cartoon", "Pro Sound Effects - Funny"],
            "fantasia": ["Boom Library - Fantasy", "Soundsnap - Magical", "Wave Alchemy - Texture"]
        }
        return libraries.get(genre, ["General Purpose SFX Libraries"])

    def _get_processing_chain(self, layers: list[SoundLayer]) -> list[str]:
        """Obtiene la cadena de procesamiento recomendada."""
        chain = [
            "1. Gain staging y limpieza de ruido",
            "2. Ecualización quirúrgica para espacio en frecuencia",
            "3. Compresión ligera para control dinámico",
            "4. Reverb y delay según espacialidad requerida",
            "5. Saturación armónica opcional para calor",
            "6. Limitador de pico final"
        ]
        return chain

    def _get_mixing_notes(self, soundscape: Soundscape) -> list[str]:
        """Obtiene notas de mezcla para el soundscape."""
        notes = [
            f"Mood general: {soundscape.overall_mood}",
            f"Complejidad: {soundscape.complexity_level}/5",
            "Mantener el diálogo siempre por encima de -12dBFS",
            "El ambiente debe estar entre -24dBFS y -18dBFS",
            "Los efectos de impacto no deben superar -6dBFS",
            "Verificar correlación de fase en elementos estéreo"
        ]

        # Notas específicas por capas
        foley_count = len([l for l in soundscape.layers if l.sound_type == "foley"])
        if foley_count > 3:
            notes.append("Considerar compresión de grupo para capas de foley")

        ambience_count = len([l for l in soundscape.layers if l.sound_type == "ambience"])
        if ambience_count > 2:
            notes.append("Verificar que capas de ambiente no enmascaren diálogo")

        return notes

    def _get_qa_checklist(self, soundscape: Soundscape) -> list[str]:
        """Obtiene lista de verificación de calidad."""
        return [
            "Verificar que todos los triggers tengan correspondencia en timeline",
            "Chequear que no haya frecuencias enmascarando diálogo crítico",
            "Confirmar que los niveles de ambience apoyen sin dominar",
            "Probar en múltiples sistemas de reproducción (TV, audífonos, altavoces)",
            "Verificar consistencia con escenas adyacentes",
            "Chequear que no haya clicks o pops en ediciones",
            "Confirmar que todos los archivos estén en 24-bit/48kHz",
            "Validar que metadata incluya descripción correcta"
        ]

    def _get_layer_breakdown(self, layers: list[SoundLayer]) -> dict[str, Any]:
        """Obtiene desglose por tipo de capa."""
        breakdown = {}
        for layer in layers:
            sound_type = layer.sound_type
            if sound_type not in breakdown:
                breakdown[sound_type] = {"count": 0, "total_intensity": 0.0, "layers": []}

            breakdown[sound_type]["count"] += 1
            breakdown[sound_type]["total_intensity"] += layer.intensity
            breakdown[sound_type]["layers"].append({
                "id": layer.layer_id,
                "name": layer.name,
                "intensity": layer.intensity
            })

        # Calcular promedios
        for sound_type in breakdown:
            count = breakdown[sound_type]["count"]
            if count > 0:
                breakdown[sound_type]["avg_intensity"] = breakdown[sound_type]["total_intensity"] / count
            else:
                breakdown[sound_type]["avg_intensity"] = 0.0

        return breakdown

    def _get_technical_specs(self, layers: list[SoundLayer]) -> dict[str, Any]:
        """Obtiene especificaciones técnicas."""
        sample_rate = 48000
        bit_depth = 24

        # Calcular ancho de banda estimado
        total_layers = len(layers)
        estimated_track_count = min(total_layers, 16)  # Máximo práctico de pistas

        return {
            "sample_rate": f"{sample_rate} Hz",
            "bit_depth": f"{bit_depth}-bit",
            "recommended_track_count": estimated_track_count,
            "file_format": "WAV (Broadcast Wave Format)",
            "naming_convention": "SS_SceneID_LayerType_Description.wav",
            "metadata_required": ["Description", "Origin", "Recording Date", "Engineer"],
            "delivery_method": "Entrega individual por capa + mezclas de stem"
        }

    def _estimate_sound_budget(self, layers: list[SoundLayer]) -> dict[str, Any]:
        """Estima el presupuesto de sonido."""
        # Costos base por hora (estimados)
        recording_hourly = 150  # dólares/hora
        editing_hourly = 100    # dólares/hora
        mixing_hourly = 120     # dólares/hora

        # Estimación de tiempo basada en complejidad
        recording_hours = len(layers) * 0.5  # 30 minutos por capa en promedio
        editing_hours = len(layers) * 0.3    # 18 minutos por capa
        mixing_hours = 2.0                   # Tiempo base de mezcla

        # Ajustar por tipo de capa
        fx_layers = len([l for l in layers if l.sound_type == "fx"])
        foley_layers = len([l for l in layers if l.sound_type == "foley"])

        recording_hours += fx_layers * 0.3   # FX toman más tiempo para diseñar
        editing_hours += foley_layers * 0.2  # Foley requiere edición detallada

        total_hours = recording_hours + editing_hours + mixing_hours
        total_cost = (
            recording_hours * recording_hourly +
            editing_hours * editing_hourly +
            mixing_hours * mixing_hourly
        )

        return {
            "recording_hours": round(recording_hours, 1),
            "editing_hours": round(editing_hours, 1),
            "mixing_hours": round(mixing_hours, 1),
            "total_hours": round(total_hours, 1),
            "estimated_cost_usd": round(total_cost, 2),
            "cost_breakdown": {
                "recording": round(recording_hours * recording_hourly, 2),
                "editing": round(editing_hours * editing_hourly, 2),
                "mixing": round(mixing_hours * mixing_hourly, 2)
            }
        }

    def _get_sound_recommendations(
        self,
        soundscape: Soundscape,
        genre: str
    ) -> list[str]:
        """Obtiene recomendaciones generales de sonido."""
        recommendations = [
            f"Enfocar en apoyar el mood {soundscape.overall_mood} sin sobrecargar",
            "Mantener biblioteca personalizada de sonidos característicos para el género",
            "Considerar grabación de location-specific ambience cuando sea posible",
            "Verificar compatibilidad con diálogos en todas las etapas de producción",
            "Crear versiones alternativas de sonidos críticos para opciones de mezcla"
        ]

        # Recomendaciones específicas por género
        if genre == "thriller_domestico":
            recommendations.extend([
                "Explorar sonidos domésticos familiares pero distorsionados",
                "Usar espacios reverberantes para crear sensación de vigilancia",
                "Considerar infrasonido subliminal para tensión subconsciente"
            ])
        elif genre == "romance_traicion":
            recommendations.extend([
                "Enfocar en texturas íntimas y cálidas",
                "Considerar uso sutil de instrumentos acústicos",
                "Crear contrastes entre sonidos puros y distorsionados para reflejar la traición"
            ])
        elif genre == "horror":
            recommendations.extend([
                "Experimentar con frecuencias extremas (muy bajas y muy altas)",
                "Crear biblioteca de sonidos orgánicos distorsionados",
                "Usar silencio como elemento sonoro activo"
            ])

        return recommendations

    def _soundscape_to_dict(self, soundscape: Soundscape) -> dict[str, Any]:
        """Convierte un Soundscape a diccionario para serialización."""
        return {
            "soundscape_id": soundscape.soundscape_id,
            "scene_beat": soundscape.scene_beat,
            "description": soundscape.description,
            "overall_mood": soundscape.overall_mood,
            "complexity_level": soundscape.complexity_level,
            "transition_notes": soundscape.transition_notes,
            "layers": [
                {
                    "layer_id": layer.layer_id,
                    "name": layer.name,
                    "description": layer.description,
                    "sound_type": layer.sound_type,
                    "intensity": layer.intensity,
                    "spatial_position": layer.spatial_position,
                    "frequency_range": layer.frequency_range,
                    "duration": layer.duration,
                    "loop": layer.loop,
                    "volume_envelope": layer.volume_envelope,
                    "triggers": layer.triggers,
                    "metadata": layer.metadata
                }
                for layer in soundscape.layers
            ]
        }
