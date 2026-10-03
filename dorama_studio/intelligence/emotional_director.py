"""
Emotional Director AI - Diseña curvas emocionales óptimas para maximizar retención y conexión.
Controla: suspenso, romance, tristeza, alegría, ira, sorpresa, esperanza.
Cada episodio debe tener una curva emocional que capture atención, desarrolle tensión y genere necesidad de continuar.
"""

import logging
import random
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class EmotionalPoint:
    """Punto en la curva emocional."""
    time: float  # Segundo en el episodio
    emotion: str  # Una de las 7 emociones básicas
    intensity: float  # 0.0 a 1.0
    trigger: str = ""  # Qué causó este cambio emocional
    notes: str = ""

@dataclass
class EmotionalArc:
    """Curva emocional completa de un episodio."""
    emotion_points: list[EmotionalPoint] = field(default_factory=list)
    dominant_emotion: str = ""
    emotional_range: float = 0.0  # Diferencia entre max y min intensidad
    emotional_volatility: float = 0.0  # Cuánto cambia la emoción por segundo
    resolution_satisfaction: float = 0.0  # Qué tan satisfactoria es la resolución emocional
    hook_emotion: str = ""  # Emoción en los primeros 3 segundos
    cliffhanger_emotion: str = ""  # Emoción en el cliffhanger
    emotional_journey_score: float = 0.0  # Score completo de la jornada emocional

class EmotionalDirectorAI:
    """
    Emotional Director AI que controla las emociones del episodio para maximizar:
    - Captura de atención en los primeros 3 segundos
    - Desarrollo de tensión a lo largo del episodio
    - Necesidad de continuar al final (cliffhanger emocional)
    - Satisfacción en la resolución
    """

    def __init__(self):
        # Las 7 emociones básicas que director debe controlar
        self.core_emotions = [
            "suspense",      # tensión, incertidumbre
            "romance",       # amor, conexión, intimidad
            "sadness",       # tristeza, pérdida, melancolía
            "joy",           # felicidad, celebración, triunfo
            "anger",         # ira, frustración, indignación
            "surprise",      # asombro, revelación, giro
            "hope"           # esperanza, optimismo, resiliencia
        ]

        # Plantillas de curvas emocionales por género
        self.genre_templates = {
            "romance_traicion": {
                "hook": ["surprise", "anger"],  # Descubrimiento de traición
                "development": ["sadness", "anger", "suspense"],  # Procesamiento, confrontación, incertidumbre
                "climax": ["anger", "surprise"],  # Confrontación final + revelación
                "resolution": ["sadness", "hope"],  # Dolor + esperanza de futuro
                "cliffhanger": ["surprise", "suspense"]  # Nueva amenaza o secreto
            },
            "thriller_misterio": {
                "hook": ["surprise", "suspense"],  # Crimen descubierto
                "development": ["suspense", "anger", "surprise"],  # Investigación, frustración, pistas
                "climax": ["fear", "anger"],  # Enfrentamiento peligroso
                "resolution": ["relief", "joy"],  # Justicia hecha, tranquilidad
                "cliffhanger": ["surprise", "suspense"]  # Nuevo caso o implicación
            },
            "fantasia_epica": {
                "hook": ["surprise", "hope"],  # Llamado a la aventura
                "development": ["fear", "anger", "suspense"],  # Pruebas, conflictos, peligros
                "climax": ["anger", "joy"],  # Batalla final + triunfo
                "resolution": ["sadness", "hope"],  # Pérdidas + nuevo comienzo
                "cliffhanger": ["surprise", "suspense"]  # Nueva amenaza en el horizonte
            },
            "drama_medico": {
                "hook": ["surprise", "fear"],  # Diagnóstico grave o emergencia
                "development": ["sadness", "anger", "hope"],  # Lucha, frustración, esperanzas
                "climax": ["fear", "joy"],  # Cirugía crítica + resultado
                "resolution": ["sadness", "joy"],  # Secuelas + recuperación o pérdida
                "cliffhanger": ["surprise", "suspense"]  # Nuevo caso médico misterioso
            }
        }

        logger.info("EmotionalDirectorAI initialized")

    def design_emotional_arc(
        self,
        genre: str = "romance_traicion",
        episode_number: int = 1,
        total_episodes: int = 20,
        story_beats: list[dict[str, Any]] = None,
        character_arcs: dict[str, Any] = None,
        season_emotional_arc: dict[str, Any] = None
    ) -> EmotionalArc:
        """
        Diseña la curva emocional óptima para un episodio.

        Args:
            genre: Género del dorama
            episode_number: Número del episodio (1-based)
            total_episodes: Total de episodios en la temporada
            story_beats: Lista de beats de la historia (si está disponible)
            character_arcs: Arcos emocionales de los personajes
            season_emotional_arc: Arco emocional general de la temporada

        Returns:
            EmotionalArc con la curva emocional diseñada
        """
        logger.info(f"Designing emotional arc for episode {episode_number}/{total_episodes} in {genre} genre")

        # Obtener plantilla base para el género
        template = self.genre_templates.get(genre, self.genre_templates["romance_traicion"])

        # Ajustar según posición en la temporada (arco emocional de temporada)
        season_position = episode_number / total_episodes
        adjusted_template = self._adjust_for_season_position(template, season_position, season_emotional_arc)

        # Si tenemos beats de historia, mapear emociones a esos puntos temporales
        if story_beats:
            emotional_arc = self._map_emotions_to_beats(adjusted_template, story_beats, character_arcs)
        else:
            # Generar curva emocional estándar basada en duración típica (90s)
            emotional_arc = self._generate_standard_emotional_curve(adjusted_template, 90.0)

        # Calcular métricas de la curva emocional
        self._calculate_emotional_metrics(emotional_arc)

        # Calcular score de jornada emocional
        emotional_arc.emotional_journey_score = self._calculate_emotional_journey_score(emotional_arc)

        logger.info(f"Emotional arc designed: {len(emotional_arc.emotion_points)} points, journey score: {emotional_arc.emotional_journey_score:.2f}")
        return emotional_arc

    def _adjust_for_season_position(
        self,
        template: dict[str, list[str]],
        season_position: float,
        season_emotional_arc: dict[str, Any] | None
    ) -> dict[str, list[str]]:
        """Ajusta la plantilla emocional según la posición en la temporada."""
        # Si tenemos arco emocional de temporada, usarlo
        if season_emotional_arc:
            # Esto sería más complejo en implementación real
            pass

        # Ajustes generales por posición:
        # Inicio de temporada (0-0.3): más hope y surprise para enganchar
        # Medio de temporada (0.3-0.7): equilibrio normal
        # Final de temporada (0.7-1.0): más resolución y preparación para finale

        adjusted = template.copy()

        if season_position < 0.3:  # Inicio de temporada
            # Aumentar elementos de enganche
            if "hook" in adjusted:
                adjusted["hook"] = ["surprise", "hope"] + adjusted["hook"]
            if "development" in adjusted:
                adjusted["development"] = ["suspense"] + adjusted["development"]

        elif season_position > 0.7:  # Final de temporada
            # Aumentar elementos de cierre y preparación para finale
            if "resolution" in adjusted:
                adjusted["resolution"] = adjusted["resolution"] + ["hope", "suspense"]
            if "cliffhanger" in adjusted:
                adjusted["cliffhanger"] = ["surprise", "suspense", "anger"]  # Más intenso para finale

        return adjusted

    def _map_emotions_to_beats(
        self,
        template: dict[str, list[str]],
        story_beats: list[dict[str, Any]],
        character_arcs: dict[str, Any] | None
    ) -> EmotionalArc:
        """Mapea las emociones de la plantilla a los beats específicos de la historia."""
        emotional_points = []

        if not story_beats:
            return self._generate_standard_emotional_curve(template, 90.0)

        total_duration = sum(beat.get("duration_sec", 10.0) for beat in story_beats)
        current_time = 0.0

        # Determinar qué fase emocional estamos en basado en el progreso de beats
        beat_progress = 0.0

        for i, beat in enumerate(story_beats):
            beat_duration = beat.get("duration_sec", 10.0)
            beat_progress_start = beat_progress
            beat_progress_end = beat_progress + (beat_duration / total_duration)
            beat_progress_middle = (beat_progress_start + beat_progress_end) / 2

            # Determinar fase emocional (hook, development, climax, resolution)
            phase = self._determine_emotional_phase(beat_progress_middle, len(story_beats))

            # Obtener emociones para esta fase
            phase_emotions = template.get(phase, ["neutral"])

            # Seleccionar emoción basada en contenido del beat y arcos de personaje
            selected_emotion = self._select_emotion_for_beat(
                phase_emotions, beat, character_arcs, i, len(story_beats)
            )

            # Calcular intensidad basada en múltiples factores
            intensity = self._calculate_emotional_intensity(
                beat, selected_emotion, character_arcs, i, len(story_beats)
            )

            # Crear punto emocional
            emotional_point = EmotionalPoint(
                time=current_time,
                emotion=selected_emotion,
                intensity=intensity,
                trigger=beat.get("action", ""),
                notes=f"Beat {i+1}: {beat.get('beat_name', 'unnamed')}"
            )

            emotional_points.append(emotional_point)

            current_time += beat_duration
            beat_progress = beat_progress_end

        # Añadir puntos de transición entre beats si es necesario
        emotional_points = self._add_transition_points(emotional_points, story_beats)

        # Crear y devolver el arco emocional
        arc = EmotionalArc(emotion_points=emotional_points)
        return arc

    def _determine_emotional_phase(self, progress: float, total_beats: int) -> str:
        """Determina en qué fase emocional estamos basado en el progreso."""
        if progress < 0.15:  # Primeros ~15% = hook
            return "hook"
        elif progress < 0.70:  # Hasta ~70% = development
            return "development"
        elif progress < 0.90:  # Hasta ~90% = climax
            return "climax"
        else:  # Últimos ~10% = resolution + cliffhanger setup
            return "resolution"

    def _select_emotion_for_beat(
        self,
        candidate_emotions: list[str],
        beat: dict[str, Any],
        character_arcs: dict[str, Any] | None,
        beat_index: int,
        total_beats: int
    ) -> str:
        """Selecciona la emoción más apropiada para un beat específico."""
        # Factores que influyen en la selección de emoción
        emotion_scores = dict.fromkeys(candidate_emotions, 0.0)

        # Analizar contenido del beat
        action = beat.get("action", "").lower()
        dialogue = beat.get("dialogue", "").lower()
        emotion_field = beat.get("emotion", "").lower()

        # Mapeo de palabras clave a emociones
        emotion_keywords = {
            "surprise": ["sorpresa", "revelación", "giro", "inesperado", "¡", "?", "descubierto", "secreto"],
            "suspense": ["tensión", "incertidumbre", "esperando", "¿qué pasará?", "misterio", "oscuridad"],
            "anger": ["ira", "frustración", "enfadado", "molesto", "injusticia", "grito", "discusión"],
            "sadness": ["tristeza", "llanto", "dolor", "pérdida", "despedida", "extraño", "solo"],
            "joy": ["felicidad", "alegría", "sonrisa", "risa", "fiesta", "celebración", "triunfo", "amor"],
            "fear": ["miedo", "terror", "pánico", "amenaza", "peligro", "oscuridad", "sospecha"],
            "hope": ["esperanza", "optimismo", "fe", "creer", "posible", "mañana", "futuro"],
            "romance": ["amor", "beso", "abrazar", "cariño", "ternura", "cita", "enamorado"]
        }

        # Puntuar cada emoción basada en palabras clave
        text_to_analyze = f"{action} {dialogue} {emotion_field}"
        for emotion, keywords in emotion_keywords.items():
            if emotion in emotion_scores:  # Solo si es una de nuestras emociones candidatas
                score = sum(1 for keyword in keywords if keyword in text_to_analyze)
                emotion_scores[emotion] += score * 2.0  # Peso alto para coincidencias directas

        # Considerar intensidad de la acción
        if any(word in action for word in ["grito", "pelea", "discusión", "conflicto"]):
            emotion_scores["anger"] += 3.0
            emotion_scores["suspense"] += 2.0

        if any(word in action for word in ["beso", "abrazo", "encontrarse", "cita"]):
            emotion_scores["romance"] += 3.0
            emotion_scores["joy"] += 2.0

        if any(word in action for word in ["llanto", "despedida", "pérdida", "se va"]):
            emotion_scores["sadness"] += 3.0
            emotion_scores["anger"] += 1.0  # A veces la tristeza viene con ira

        if any(word in action for word in ["descubrir", "revelar", "secreto", "se sabe"]):
            emotion_scores["surprise"] += 4.0
            emotion_scores["suspense"] += 2.0

        # Considerar posición en el episodio (los cliffhangers necesitan sorpresa/suspense)
        if beat_index == total_beats - 1:  # Último beat
            emotion_scores["surprise"] += 3.0
            emotion_scores["suspense"] += 3.0
            emotion_scores["anger"] += 2.0  # Puede ser ira por traición revelada

        # Considerar arcos de personaje si están disponibles
        if character_arcs:
            # Esto sería más complejo en implementación real
            pass

        # Seleccionar la emoción con mayor puntaje
        if max(emotion_scores.values()) > 0:
            selected_emotion = max(emotion_scores, key=emotion_scores.get)
        else:
            # Default basado en la posición
            if beat_index == 0:
                selected_emotion = "surprise"  # Primer beat suele ser hook
            elif beat_index == total_beats - 1:
                selected_emotion = "surprise"  # Último beat suele ser cliffhanger
            else:
                selected_emotion = random.choice(candidate_emotions) if candidate_emotions else "neutral"

        return selected_emotion

    def _calculate_emotional_intensity(
        self,
        beat: dict[str, Any],
        emotion: str,
        character_arcs: dict[str, Any] | None,
        beat_index: int,
        total_beats: int
    ) -> float:
        """Calcula la intensidad de una emoción en un beat específico."""
        base_intensity = 0.5  # Intensidad base

        # Factores que aumentan intensidad
        intensity_factors = []

        # Duración del beat (beats más largos pueden tener emociones más desarrolladas)
        duration = beat.get("duration_sec", 10.0)
        if duration > 15.0:
            intensity_factors.append(0.2)
        elif duration < 5.0:
            intensity_factors.append(-0.1)  # Beats muy cortos tienen menos espacio para emoción

        # Presencia de elementos específicos que aumentan intensidad emocional
        action = beat.get("action", "").lower()
        dialogue = beat.get("dialogue", "").lower()

        # Elementos que aumentan intensidad para distintas emociones
        if emotion == "anger":
            if any(word in action for word in ["grito", "pelea", "discusión", "confronto"]):
                intensity_factors.append(0.3)
            if any(word in dialogue for word in ["¡", "!", "jamás", "nunca más"]):
                intensity_factors.append(0.2)

        elif emotion == "sadness":
            if any(word in action for word in ["llanto", "despedida", "se va", "extraño"]):
                intensity_factors.append(0.3)
            if any(word in dialogue for word in ["te extraño", "te echo de menos", "no estarás"]):
                intensity_factors.append(0.2)

        elif emotion == "joy":
            if any(word in action for word in ["risa", "baile", "fiesta", "celebración"]):
                intensity_factors.append(0.3)
            if any(word in dialogue for word in ["feliz", "alegre", "mejor día"]):
                intensity_factors.append(0.2)

        elif emotion == "surprise":
            if any(word in action for word in ["descubrir", "revelar", "secreto", "giro"]):
                intensity_factors.append(0.4)
            if any(word in dialogue for word in ["¿qué?", "imposible", "no puede ser"]):
                intensity_factors.append(0.3)

        elif emotion == "suspense":
            if any(word in action for word in ["esperando", "escuchando", "observando", "siguiendo"]):
                intensity_factors.append(0.2)
            if "silencio" in action or "pausa" in action:
                intensity_factors.append(0.3)

        elif emotion == "fear":
            if any(word in action for word in ["huir", "esconderse", "temblar", "sudor frío"]):
                intensity_factors.append(0.3)
            if any(word in dialogue for word in ["miedo", "terror", "no quiero morir"]):
                intensity_factors.append(0.2)

        elif emotion == "hope":
            if any(word in action for word in ["mirar al futuro", "planear", "esperar", "creer"]):
                intensity_factors.append(0.2)
            if any(word in dialogue for word in ["mañana será mejor", "confío en", "sé que"]):
                intensity_factors.append(0.2)

        elif emotion == "romance":
            if any(word in action for word in ["beso", "abrazo", "mano en mano", "mirada prolongada"]):
                intensity_factors.append(0.3)
            if any(word in dialogue for word in ["te amo", "te quiero", "eres mi vida"]):
                intensity_factors.append(0.2)

        # Factores que disminuyen intensidad
        intensity_reducers = []

        # Diálogo expositivo sin carga emocional
        if any(word in dialogue for word in ["es", "está", "fue", "han sido"]) and len(dialogue.split()) > 15:
            intensity_reducers.append(0.2)

        # Acción meramente funcional sin peso emocional
        if any(word in action for word in ["caminar", "conducir", "trabajar", "estudiar"]) and not any(
            emot_word in action for emot_word in ["llanto", "risa", "grito", "descubrir", "pelear"]
        ):
            intensity_reducers.append(0.1)

        # Calcular intensidad final
        final_intensity = base_intensity + sum(intensity_factors) - sum(intensity_reducers)
        return max(0.0, min(1.0, final_intensity))

    def _add_transition_points(
        self,
        emotional_points: list[EmotionalPoint],
        story_beats: list[dict[str, Any]]
    ) -> list[EmotionalPoint]:
        """Añade puntos de transición entre beats para curvas emocionales más suaves."""
        if len(emotional_points) <= 1:
            return emotional_points

        enhanced_points = []

        for i in range(len(emotional_points)):
            enhanced_points.append(emotional_points[i])

            # Añadir punto intermedio entre este beat y el siguiente (si existe)
            if i < len(emotional_points) - 1:
                current_point = emotional_points[i]
                next_point = emotional_points[i + 1]

                # Solo añadir punto intermedio si hay un salto emocional significativo
                emotion_change = abs(
                    self._emotion_to_value(current_point.emotion, current_point.intensity) -
                    self._emotion_to_value(next_point.emotion, next_point.intensity)
                )

                if emotion_change > 0.3:  # Umbral significativo
                    # Crear punto intermedio en tiempo y emoción
                    mid_time = (current_point.time + next_point.time) / 2

                    # Interpolar emoción (simplificado: promedio de intensidad)
                    mid_intensity = (current_point.intensity + next_point.intensity) / 2

                    # Para la emoción, usar la dominante o una mezcla
                    mid_emotion = current_point.emotion if current_point.intensity > next_point.intensity else next_point.emotion

                    mid_point = EmotionalPoint(
                        time=mid_time,
                        emotion=mid_emotion,
                        intensity=mid_intensity,
                        trigger="transición",
                        notes=f"Transición entre beat {i+1} y {i+2}"
                    )

                    enhanced_points.append(mid_point)

        return enhanced_points

    def _emotion_to_value(self, emotion: str, intensity: float) -> float:
        """Convierte una emoción e intensidad a un valor numérico para comparación."""
        # Mapeo de emociones a eje de valencia (positivo-negativo) y arousal (activación)
        emotion_values = {
            "joy": (0.8, 0.6),
            "romance": (0.7, 0.5),
            "hope": (0.6, 0.4),
            "surprise": (0.0, 0.8),  # Puede ser positiva o negativa
            "suspense": (-0.2, 0.7),
            "anger": (-0.7, 0.8),
            "fear": (-0.8, 0.7),
            "sadness": (-0.6, 0.3),
            "neutral": (0.0, 0.1)
        }

        valence, arousal = emotion_values.get(emotion, (0.0, 0.1))
        # Combinar valencia y arousal con intensidad
        return (valence * 0.5 + arousal * 0.5) * intensity

    def _generate_standard_emotional_curve(
        self,
        template: dict[str, list[str]],
        duration_seconds: float
    ) -> EmotionalArc:
        """Genera una curva emocional estándar cuando no se tienen beats específicos."""
        emotional_points = []

        # Dividir el episodio en segmentos según la plantilla
        segments = ["hook", "development", "climax", "resolution"]
        segment_durations = {
            "hook": duration_seconds * 0.15,      # Primeros 15%
            "development": duration_seconds * 0.50,  # Medio 50%
            "climax": duration_seconds * 0.25,    # Último 25% antes del final
            "resolution": duration_seconds * 0.10   # Últimos 10%
        }

        current_time = 0.0

        for segment in segments:
            if segment not in template:
                continue

            segment_duration = segment_durations.get(segment, duration_seconds * 0.1)
            emotions_in_segment = template[segment]

            # Distribuir emociones a lo largo del segmento
            if len(emotions_in_segment) == 1:
                # Una sola emoción en todo el segmento
                emotional_points.append(EmotionalPoint(
                    time=current_time + segment_duration / 2,
                    emotion=emotions_in_segment[0],
                    intensity=0.7,  # Intensidad media-alta
                    trigger=f"segment_{segment}",
                    notes=f"{segment.capitalize()} segment"
                ))
            else:
                # Múltiples emociones, distribuirlas
                time_per_emotion = segment_duration / len(emotions_in_segment)
                for i, emotion in enumerate(emotions_in_segment):
                    emotional_points.append(EmotionalPoint(
                        time=current_time + (i * time_per_emotion) + (time_per_emotion / 2),
                        emotion=emotion,
                        intensity=0.6 + (0.2 * (i / max(len(emotions_in_segment) - 1, 1))),  # Variar intensidad
                        trigger=f"segment_{segment}_{i}",
                        notes=f"{segment.capitalize()} - emotion {i+1}/{len(emotions_in_segment)}"
                    ))

            current_time += segment_duration

        # Añadir punto de cliffhanger al final (últimos segundos)
        cliffhanger_time = duration_seconds - 3.0  # Últimos 3 segundos
        if template.get("cliffhanger"):
            cliffhanger_emotion = template["cliffhanger"][0] if isinstance(template["cliffhanger"], list) else template["cliffhanger"]
            emotional_points.append(EmotionalPoint(
                time=cliffhanger_time,
                emotion=cliffhanger_emotion,
                intensity=0.8,  # Alta intensidad para cliffhanger
                trigger="cliffhanger_setup",
                notes="Cliffhanger emotional setup"
            ))

        # Ordenar puntos por tiempo
        emotional_points.sort(key=lambda p: p.time)

        # Crear y devolver el arco emocional
        arc = EmotionalArc(emotion_points=emotional_points)
        return arc

    def _calculate_emotional_metrics(self, arc: EmotionalArc) -> None:
        """Calcula métricas derivadas del arco emocional."""
        if not arc.emotion_points:
            return

        # Emoción dominante (la que aparece más tiempo o con mayor intensidad)
        emotion_time = {}
        for point in arc.emotion_points:
            # Ponderar por duración hasta el próximo punto o duración restante
            duration = point.time  # Simplificado
            if point.emotion not in emotion_time:
                emotion_time[point.emotion] = 0.0
            emotion_time[point.emotion] += duration

        if emotion_time:
            arc.dominant_emotion = max(emotion_time, key=emotion_time.get)

        # Rango emocional (diferencia entre max y min intensidad)
        intensities = [point.intensity for point in arc.emotion_points]
        if intensities:
            arc.emotional_range = max(intensities) - min(intensities)

        # Volatilidad emocional (cuánto cambia la emoción por segundo)
        if len(arc.emotion_points) > 1:
            total_change = 0.0
            total_time = arc.emotion_points[-1].time - arc.emotion_points[0].time

            for i in range(1, len(emotion_points)):
                prev_point = emotion_points[i-1]
                curr_point = emotion_points[i]

                # Cambio en valor emocional
                prev_value = self._emotion_to_value(prev_point.emotion, prev_point.intensity)
                curr_value = self._emotion_to_value(curr_point.emotion, curr_point.intensity)
                change = abs(curr_value - prev_value)

                time_diff = curr_point.time - prev_point.time
                if time_diff > 0:
                    total_change += change / time_diff

            if total_time > 0:
                arc.emotional_volatility = total_change / (len(emotion_points) - 1)

        # Emoción en los primeros 3 segundos (hook)
        hook_points = [p for p in arc.emotion_points if p.time <= 3.0]
        if hook_points:
            # Tomar la emoción con mayor intensidad en el hook
            hook_point = max(hook_points, key=lambda p: p.intensity)
            arc.hook_emotion = hook_point.emotion

        # Emoción en el cliffhanger (últimos 5 segundos)
        cliff_points = [p for p in arc.emotion_points if p.time >= arc.emotion_points[-1].time - 5.0]
        if cliff_points:
            # Tomar la emoción con mayor intensidad en el cliffhanger
            cliff_point = max(cliff_points, key=lambda p: p.intensity)
            arc.cliffhanger_emotion = cliff_point.emotion

        # Satisfacción de resolución (qué tan bien se resuelve la tensión emocional)
        # Esto sería más complejo en implementación real, usando análisis de resolución
        arc.resolution_satisfaction = 0.7  # Valor placeholder

    def _calculate_emotional_journey_score(self, arc: EmotionalArc) -> float:
        """Calcula un score completo de la calidad de la jornada emocional."""
        if not arc.emotion_points:
            return 0.0

        score = 0.0
        max_score = 100.0

        # 1. Variedad de emociones (0-25 puntos)
        unique_emotions = len(set(point.emotion for point in arc.emotion_points))
        variety_score = min(25.0, (unique_emotions / len(self.core_emotions)) * 25.0)
        score += variety_score

        # 2. Rango emocional adecuado (0-20 puntos)
        # Rango ideal: 0.6-0.9 (ni demasiado plano ni demasiado extremo)
        if 0.6 <= arc.emotional_range <= 0.9:
            range_score = 20.0
        elif arc.emotional_range > 0.9:
            range_score = max(0.0, 20.0 - ((arc.emotional_range - 0.9) * 25.0))  # Penalizar excesivo
        else:
            range_score = (arc.emotional_range / 0.6) * 20.0  # Proporcional si es muy bajo
        score += range_score

        # 3. Apertura fuerte (hook emocional) (0-15 puntos)
        if arc.hook_emotion in ["surprise", "anger", "fear"]:  # Emociones fuertes para hook
            hook_score = 15.0
        elif arc.hook_emotion in ["suspense", "sadness"]:
            hook_score = 10.0
        else:
            hook_score = 5.0
        score += hook_score

        # 4. Cliffhanger emocional efectivo (0-15 puntos)
        if arc.cliffhanger_emotion in ["surprise", "suspense", "anger"]:
            cliffhanger_score = 15.0
        elif arc.cliffhanger_emotion in ["fear", "hope"]:
            cliffhanger_score = 10.0
        else:
            cliffhanger_score = 5.0
        score += cliffhanger_score

        # 5. Progresión lógica (0-15 puntos)
        # Verificar que hay una progresión emocional razonable
        progression_score = self._calculate_progression_score(arc)
        score += progression_score

        # 6. Resolución satisfactoria (0-10 puntos)
        resolution_score = arc.resolution_satisfaction * 10.0
        score += resolution_score

        return min(max_score, score)

    def _calculate_progression_score(self, arc: EmotionalArc) -> float:
        """Evalúa si la progresión emocional es lógica y efectiva."""
        if len(arc.emotion_points) < 2:
            return 0.0

        score = 0.0
        max_score = 15.0

        # Convertir emociones a valores para análisis de progresión
        emotional_values = [
            self._emotion_to_value(point.emotion, point.intensity)
            for point in arc.emotion_points
        ]

        # Buscar patrones de progresión efectiva
        # Ideal: tensión creciente → liberación → tensión renovada → resolución

        # Contar cambios de dirección en la emoción
        direction_changes = 0
        for i in range(2, len(emotional_values)):
            prev_diff = emotional_values[i-1] - emotional_values[i-2]
            curr_diff = emotional_values[i] - emotional_values[i-1]

            # Si cambian de signo, hay un punto de inflexión
            if prev_diff * curr_diff < 0:
                direction_changes += 1

        # Número ideal de puntos de inflexión: 2-4 para un episodio de 90s
        if 2 <= direction_changes <= 4:
            progression_score = 15.0
        elif direction_changes < 2:
            progression_score = (direction_changes / 2.0) * 15.0
        else:
            progression_score = max(0.0, 15.0 - ((direction_changes - 4) * 2.0))

        return progression_score

# Instancia singleton
emotional_director = EmotionalDirectorAI()
